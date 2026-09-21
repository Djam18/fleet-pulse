import logging
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from fleet.models import JobQueue, StatusChangeRequest, Vehicle
from fleet.services.agent_tools import evaluate_and_approve_request

logger = logging.getLogger(__name__)


def enqueue_job(task_name: str, payload: dict = None, delay_seconds: int = 0) -> JobQueue:
    """Schedules a background asynchronous task in the database queue."""
    sched = timezone.now() + timedelta(seconds=delay_seconds) if delay_seconds else timezone.now()
    return JobQueue.objects.create(
        task_name=task_name,
        payload=payload or {},
        scheduled_at=sched,
        status=JobQueue.Status.PENDING
    )


def _handle_send_email(payload: dict):
    send_mail(
        subject=payload.get('subject', 'FleetPulse Notification'),
        message=payload.get('message', ''),
        from_email=payload.get('from_email', 'noreply@fleetpulse.local'),
        recipient_list=payload.get('recipients', []),
        fail_silently=False
    )


def _handle_recalc_maintenance(payload: dict):
    overdue_count = 0
    for v in Vehicle.objects.prefetch_related('maintenance_schedules').all():
        if v.has_overdue_maintenance:
            overdue_count += 1
    return f"Scanned fleet: {overdue_count} vehicles currently require maintenance."


def _handle_ai_safety_audit(payload: dict):
    pending = StatusChangeRequest.objects.filter(status=StatusChangeRequest.RequestStatus.PENDING)
    approved_count = 0
    for req in pending:
        res = evaluate_and_approve_request(req.id)
        if res.get('approved'):
            approved_count += 1
    return f"Safety audit completed: {approved_count} requests autonomously approved."


TASK_HANDLERS = {
    'send_email_async': _handle_send_email,
    'recalc_maintenance_due': _handle_recalc_maintenance,
    'ai_safety_audit': _handle_ai_safety_audit,
}


def process_pending_jobs(limit: int = 10) -> int:
    """Pulls and executes pending jobs whose scheduled_at has arrived."""
    now = timezone.now()
    jobs = list(JobQueue.objects.filter(
        status=JobQueue.Status.PENDING,
        scheduled_at__lte=now
    )[:limit])

    processed = 0
    for job in jobs:
        job.status = JobQueue.Status.RUNNING
        job.attempts += 1
        job.save(update_fields=['status', 'attempts'])

        handler = TASK_HANDLERS.get(job.task_name)
        if not handler:
            job.status = JobQueue.Status.FAILED
            job.error_message = f"No handler registered for task '{job.task_name}'."
            job.save(update_fields=['status', 'error_message'])
            continue

        try:
            handler(job.payload)
            job.status = JobQueue.Status.COMPLETED
            job.completed_at = timezone.now()
            job.error_message = ''
            job.save(update_fields=['status', 'completed_at', 'error_message'])
            processed += 1
        except Exception as e:
            logger.exception("Error processing job %s", job.id)
            job.error_message = str(e)[:500]
            if job.attempts >= job.max_attempts:
                job.status = JobQueue.Status.FAILED
            else:
                job.status = JobQueue.Status.PENDING
            job.save(update_fields=['status', 'error_message'])

    return processed
