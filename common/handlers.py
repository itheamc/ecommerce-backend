import random
import string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage

# Class to handle the mail sending
from django.core.signing import TimestampSigner

from authentication.models import TempASquareUser
from common.literals import OTP_SALT


class MailHandler:

    # Sending Normal Email
    @staticmethod
    def send_mail(to, subject, body, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        email = EmailMessage(subject=subject, body=body, from_email=from_email, to=[to], **kwargs)
        email.send(fail_silently=True)

    # Sending Email with attachments
    @staticmethod
    def send_mail_with_attachment(to, subject, body, attachments, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        email = EmailMessage(subject=subject, body=body, from_email=from_email, to=[to], attachments=attachments,
                             **kwargs)
        email.send(fail_silently=True)

    # Sending HTML Email
    @staticmethod
    def send_mail_with_html(to, subject, body, html, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        email = EmailMultiAlternatives(subject=subject, body=body, from_email=from_email, to=[to], **kwargs)
        email.attach_alternative(html, "text/html")
        email.send(fail_silently=True)

    # Sending HTML Email with attachments
    @staticmethod
    def send_mail_with_html_attachment(to, subject, body, html, attachments, from_email=settings.DEFAULT_FROM_EMAIL,
                                       **kwargs):
        email = EmailMultiAlternatives(subject=subject, body=body, from_email=from_email, to=[to],
                                       attachments=attachments, **kwargs)
        email.attach_alternative(html, "text/html")
        email.send(fail_silently=True)

    # Sending Email with OTP code
    @staticmethod
    def generate_n_send_otp(to, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        # Generating 5 digit random otp and encrypting it using the timestamp signer with max_age of 10 minutes
        otp = ''.join(random.choice(string.digits) for _ in range(5))
        signer = TimestampSigner(salt=OTP_SALT)
        encrypted_otp = signer.sign(otp)

        # Storing the encrypted otp in the database
        (temp, _) = TempASquareUser.objects.get_or_create(email=to.email)
        temp.otp = encrypted_otp
        temp.save()

        subject = 'Verify Your Seller Account'
        body = 'Your OTP is {}'.format(otp)
        html_body = f'''
        <div style="font-family: Helvetica,Arial,sans-serif;overflow:auto;line-height:2">
            <div style="margin:50px auto;width:70%;padding:20px 0;">
                <div style="border-bottom:1px solid #eee">
                    <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">XYZ Ecommerce</a>
                </div>
                <p style="font-size:large">Hey {to.first_name},</p>
                <p>Welcome to XYZ Ecommerce Platform. Your seller account has been created successfully. Thanks for choosing
                    our platform to take a step to make your business
                    online. Verify your account to access your seller dashboard. </p>
                <h2 style="background: #00466a;margin: 50px auto;width: max-content;padding: 0 25px;color: #fff;border-radius: 4px;text-decoration: none;">{otp}</h2>
                <hr style="border:none;border-top:1px solid #eee" />
                <div style="float:right;padding:8px 0;color:#aaa;font-size:x-small;line-height:1;font-weight:300">
                    <p style="font-weight: 900">ASquare Infotech</p>
                    <p style="line-height: 1rem;">Gadhawa, Deukhuri, Dang <br />Lumbini, Nepal 22414</p>
                </div>
            </div>
        </div>
        '''
        MailHandler.send_mail_with_html(to=to.email, subject=subject, body=body, html=html_body, from_email=from_email,
                                        **kwargs)
