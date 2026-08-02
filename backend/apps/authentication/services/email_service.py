import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_verification_email(user, token):
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        context = {
            'full_name': EmailService._display_name(user),
            'email': user.email,
            'verification_url': verification_url,
            'expiry_hours': settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS,
        }
        EmailService._send(
            subject='Verify your email address - Candidate Screening',
            recipient=user.email,
            text_body=(
                f"Welcome to Candidate Screening. Verify your email here: {verification_url}. "
                f"This link expires in {context['expiry_hours']} hours."
            ),
            template='emails/registration_verification.html',
            context=context,
        )

    @staticmethod
    def send_status_update_email(candidate_name, candidate_email, job_title, new_status):
        status_label = dict({
            'applied': 'Application Received',
            'shortlisted': 'Shortlisted',
            'interview': 'Interview Scheduled',
            'hired': 'Hired - Congratulations!',
            'rejected': 'Application Update',
        }).get(new_status, 'Application Update')
        context = {
            'candidate_name': candidate_name,
            'job_title': job_title,
            'new_status': new_status,
            'status_label': status_label,
            'application_url': f"{settings.FRONTEND_URL}/my-applications",
        }
        EmailService._send(
            subject=f'{status_label} - {job_title}',
            recipient=candidate_email,
            text_body=f'Your application for {job_title} is now {status_label}.',
            template='emails/status_update.html',
            context=context,
        )

    @staticmethod
    def _display_name(user):
        profile_name = ''
        if user.role == 'candidate' and hasattr(user, 'candidate_profile'):
            profile_name = user.candidate_profile.full_name
        elif user.role == 'recruiter' and hasattr(user, 'recruiter_profile'):
            profile_name = user.recruiter_profile.full_name
        return profile_name or user.email.split('@')[0]

    @staticmethod
    def _send(subject, recipient, text_body, template, context):
        html_content = render_to_string(template, context)
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=False)
        logger.info("Email '%s' sent to %s", subject, recipient)
