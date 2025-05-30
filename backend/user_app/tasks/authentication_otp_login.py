import logging
import math

from django.core.mail import EmailMultiAlternatives,get_connection
from django.db import transaction
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import translation
from django.utils.html import strip_tags
from celery import shared_task
from base.config import EmailConfig, LanguageConfig, SiteConfig
from ..serializers import UserSerializer
import datetime

User = get_user_model()
logger = logging.getLogger(__name__)

email_config = EmailConfig().get_email_service_config()
language_config = LanguageConfig().get_language_config()
site_config = SiteConfig().get_site_config()

@shared_task(bind=True,default_retry_delay=30, max_retries=5)
def authentication_otp_login(self,subject,user_id,otp_code,otp_expiry_minutes):
    try:
        with transaction.atomic():
            user = User.objects.select_related('profile').get(pk=user_id)
            context = {
                'subject': subject,
                'user':user,
                'language': user.profile.language  or language_config['LANGUAGE_CODE'],
                'site_name':site_config['SITE_NAME'],
                'otp_code':otp_code,
                'otp_expiry_minutes': int(math.floor(otp_expiry_minutes)),
                'current_year': datetime.date.today().year
            }
            with get_connection(
                    **email_config
            ) as connection:
                with translation.override(context['language']):
                    html_content = render_to_string('user_app/authentication_otp_login.html', context)
                    plain_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email,],
                    connection=connection,
                )
                email.attach_alternative(html_content,'text/html')
                email.send(fail_silently=False)
            logger.info(f"Successfully sent otp login to {user.email} (User ID: {user_id}). (Name: {user.profile.first_name} {user.profile.last_name})")
    except User.DoesNotExist:
        logger.error(f"User ID {user_id} not found for otp login email. Aborting task.", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to send otp login to email for User ID {user_id}. Error: {e}", exc_info=True)
        try:
            logger.info(
                f"Retrying send otp login to email task for User ID {user_id} (attempt {self.request.retries + 1}/{self.max_retries})...")
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for sending otp login email to User ID {user_id}. Email sending failed definitively.")
    return