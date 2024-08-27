import smtplib
from email.mime.text import MIMEText

from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from authentication.models import UserSignupEmailSenderModel
from authentication.token import account_activation_token

smtp_host = settings.EMAIL_HOST
smtp_port = settings.EMAIL_PORT
smtp_user = settings.EMAIL_HOST_USER
smtp_password = settings.EMAIL_HOST_PASSWORD


def sent_user_verify_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    UserSignupEmailSenderModel.objects.update_or_create(
        uid=uidb64,
        defaults={'token': token}
    )

    smtp = smtplib.SMTP(smtp_host, smtp_port)
    smtp.starttls()
    smtp.login(smtp_user, smtp_password)

    mail_subject = 'Activate your Chat App Account'
    email_body = (
            settings.CLIENT_URL + 'auth/verify?' + token + token + token + '&uid=' + uidb64 + '&token=' + token + '&'
            + token + token)

    msg = MIMEText(email_body)
    msg['Subject'] = mail_subject
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = user.email

    smtp.sendmail(settings.EMAIL_HOST_USER, [user.email], msg.as_string())
    smtp.quit()
