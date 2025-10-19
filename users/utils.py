from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings

from smtplib import SMTPRecipientsRefused
from django.core.mail import BadHeaderError
def send_otp_email(email, code):
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    print("Sending email...",{message})
    
    try:
        send_mail(subject, message, from_email, recipient_list)
    except SMTPRecipientsRefused:
        print("⚠️ The recipient's email is temporarily not accepting messages.")
    except BadHeaderError:
        print("⚠️ Invalid header found.")
    except Exception as e:

        print(f"⚠️ Unexpected email sending error: {e}")

        print(f"⚠️ Unexpected email sending error: {e}")
 
