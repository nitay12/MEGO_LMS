from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_activation_mail(email_address, password):
    subject = 'מערכת תרגילים MeGo'
    user_pass = password
    message = render_to_string('activation_email.html', {
        'user_pass': user_pass
    })
    email = EmailMessage(
        subject,
        message,
        to=[email_address],
    )
    email.content_subtype = "html"
    email.send()
