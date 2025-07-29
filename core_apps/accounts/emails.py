from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from loguru import logger


def send_account_creation_email(user, bank_account):
    subject = _("Your New Bank Account has been Created.")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    context = {
        "user": user,
        "account": bank_account,
        "site_name": settings.SITE_NAME,
    }

    try:
        html_email = render_to_string("email/account_created.html", context)
        plain_email = strip_tags(html_email)

        email = EmailMultiAlternatives(subject, plain_email, from_email, recipient_list)
        email.attach_alternative(html_email, "text/html")
        email.send()

        logger.info(f"Account creation email sent to {user.email}")
    except Exception as e:
        logger.error(
            f"Failed to send account creation email to {user.email}. Error: {str(e)}"
        )
