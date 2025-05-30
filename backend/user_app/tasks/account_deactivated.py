import logging


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

User = get_user_model()
logger = logging.getLogger(__name__)

email_config = EmailConfig().get_email_service_config()
language_config = LanguageConfig().get_language_config()
site_config = SiteConfig().get_site_config()

@shared_task(bind=True,default_retry_delay=300, max_retries=5)
def account_deactivated(self,subject, user_id):
    try:
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user_id)
            user_serializer = UserSerializer(instance=user).data
            context = {
                'subject': subject,
                'user':user_serializer,
                'language': user_serializer['language'] or language_config['LANGUAGE_CODE'],
                'frontend_url':site_config['FRONTEND_URL'],
                'site_name':site_config['SITE_NAME'],
                'reset_password_url':site_config['RESET_PASSWORD_URL']
            }
            with get_connection(
                    **email_config
            ) as connection:
                with translation.override(context['language']):
                    html_content = render_to_string('user_app/login_failed_deactivate.html', context)
                    plain_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user_serializer['email'],],
                    connection=connection,
                )
                email.attach_alternative(html_content,'text/html')
                email.send(fail_silently=False)
            logger.info(f"Successfully sent deactivation email to {user_serializer['email']} (User ID: {user_id}).")
    except User.DoesNotExist:
        logger.error(f"User ID {user_id} not found for deactivation email. Aborting task.", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to send deactivation email for User ID {user_id}. Error: {e}", exc_info=True)
        try:
            logger.info(
                f"Retrying deactivation email task for User ID {user_id} (attempt {self.request.retries + 1}/{self.max_retries})...")
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for deactivation email to User ID {user_id}. Email sending failed definitively.")
    return