import logging
from django.core.mail import EmailMultiAlternatives,get_connection
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import translation
from django.utils.html import strip_tags
from celery import shared_task
import datetime
from base.config import EmailConfig, LanguageConfig, SiteConfig
from ..serializers import UserSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

email_config = EmailConfig().get_email_service_config()
language_config = LanguageConfig().get_language_config()
site_config = SiteConfig().get_site_config()

@shared_task(bind=True,default_retry_delay=300, max_retries=5)
def send_mail_otp_forgot_password(self,subject,user_id,otp_code,otp_expiry_minutes,language_code):
    try:
        user  = User.objects.select_for_update().get(email=user_id)
        context = {
            'subject': subject,
            'user':user,
            'language': language_code  or language_config['LANGUAGE_CODE'],
            'site_name':site_config['SITE_NAME'],
            'otp_code':otp_code,
            'otp_expiry_minutes': otp_expiry_minutes,
            'current_year': datetime.date.today().year
        }
        with get_connection(
                **email_config
        ) as connection:
            with translation.override(context['language']):
                html_content = render_to_string('user_app/otp_forgot_password.html', context)
                plain_content = strip_tags(html_content)
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email, ],
                connection=connection,
            )
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=False)
            logger.info(f"Successfully sent otp to {user.email} (User ID: {user_id}).")
    except User.DoesNotExist:
        logger.error(f"User ID {user_id} not found for otp email. Aborting task.", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to send otp email for User ID {user_id}. Error: {e}", exc_info=True)
        try:
            logger.info(
                f"Retrying otp email task for User ID {user_id} (attempt {self.request.retries + 1}/{self.max_retries})...")
            self.retry(exc=e, countdown=30)
        except self.MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for otp email to User ID {user_id}. Email sending failed definitively.")