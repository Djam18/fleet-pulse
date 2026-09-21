from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView


class FleetLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('fleet:dashboard')


class FleetLogoutView(LogoutView):
    next_page = reverse_lazy('fleet:login')


class FleetRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('fleet:dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='fleet.auth_backend.EmailOrUsernameModelBackend')
        return redirect(self.success_url)


class FleetPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('fleet:password_reset_done')


class FleetPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class FleetPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('fleet:password_reset_complete')


class FleetPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
