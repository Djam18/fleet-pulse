import time
from django.core.management.base import BaseCommand
from fleet.services.queue import process_pending_jobs


class Command(BaseCommand):
    help = 'Executes pending background queue jobs (emails, maintenance audits, AI sweeps).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Process pending jobs once and exit immediately.'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Polling interval in seconds when running in worker daemon mode.'
        )

    def handle(self, *args, **options):
        once = options.get('once')
        interval = options.get('interval')

        self.stdout.write(self.style.NOTICE("FleetPulse background job worker started."))

        if once:
            count = process_pending_jobs()
            self.stdout.write(self.style.SUCCESS(f"Processed {count} background job(s)."))
            return

        self.stdout.write(f"Listening for queued jobs (polling every {interval}s). Press Ctrl+C to stop.")
        try:
            while True:
                count = process_pending_jobs()
                if count > 0:
                    self.stdout.write(self.style.SUCCESS(f"[{time.strftime('%X')}] Processed {count} job(s)."))
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Job worker stopped by operator."))
