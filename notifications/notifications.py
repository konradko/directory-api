from datetime import timedelta, datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from directory_sso_api_client.client import DirectorySSOAPIClient
from directory_validators.constants import choices

from buyer.models import Buyer
from company.models import Company
from notifications import models, constants
from user.models import User as Supplier


sso_api_client = DirectorySSOAPIClient(
    base_url=settings.SSO_API_CLIENT_BASE_URL,
    api_key=settings.SSO_API_CLIENT_KEY,
)


def send_email_notifications(
    recipient_name, recipient_email, text_template, html_template, subject,
    notification_category, extra_context
):
    context = {
        'full_name': recipient_name,
        'zendesk_url': settings.ZENDESK_URL,
        **extra_context
    }
    text_body = render_to_string(text_template, context)
    html_body = render_to_string(html_template, context)
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        to=[recipient_email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()


def record_supplier_notification_sent(supplier, category):
    models.SupplierEmailNotification.objects.create(
        supplier=supplier, category=category,
    )


def record_anonymous_notification_sent(email, category):
    models.AnonymousEmailNotification.objects.create(
        email=email, category=category,
    )


def no_case_studies():
    days_ago = datetime.utcnow() - timedelta(
        days=settings.NO_CASE_STUDIES_DAYS)
    suppliers = Supplier.objects.filter(
        company__supplier_case_studies__isnull=True,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
        unsubscribed=False,
    ).exclude(
        supplieremailnotification__category=constants.NO_CASE_STUDIES,
    )
    notification_category = constants.NO_CASE_STUDIES
    for supplier in suppliers:
        send_email_notifications(
            recipient_name=supplier.name,
            recipient_email=supplier.company_email,
            text_template='no_case_studies_email.txt',
            html_template='no_case_studies_email.html',
            subject=settings.NO_CASE_STUDIES_SUBJECT,
            notification_category=notification_category,
            extra_context={'case_study_url': settings.NO_CASE_STUDIES_URL},
        )
        record_supplier_notification_sent(supplier, notification_category)


def hasnt_logged_in():
    days_ago = datetime.utcnow() - timedelta(
        days=settings.HASNT_LOGGED_IN_DAYS)
    start_datetime = days_ago.replace(
        hour=0, minute=0, second=0, microsecond=0)
    end_datetime = days_ago.replace(
        hour=23, minute=59, second=59, microsecond=999999)
    login_data = sso_api_client.user.get_last_login(
        start=start_datetime, end=end_datetime).json()
    supplier_ids = [supplier['id'] for supplier in login_data]
    suppliers = Supplier.objects.filter(
        sso_id__in=supplier_ids
    ).exclude(
        supplieremailnotification__category=constants.HASNT_LOGGED_IN,
    )
    notification_category = constants.HASNT_LOGGED_IN
    for supplier in suppliers:
        send_email_notifications(
            recipient_name=supplier.name,
            recipient_email=supplier.company_email,
            text_template='hasnt_logged_in_email.txt',
            html_template='hasnt_logged_in_email.html',
            subject=settings.HASNT_LOGGED_IN_SUBJECT,
            notification_category=notification_category,
            extra_context={'login_url': settings.HASNT_LOGGED_IN_URL},
        )
        record_supplier_notification_sent(supplier, notification_category)


def verification_code_not_given():
    extra_context = {
        'verification_url': settings.VERIFICATION_CODE_URL,
    }

    # 1st email (after 8 days)
    days_ago = datetime.utcnow() - timedelta(
        days=settings.VERIFICATION_CODE_NOT_GIVEN_DAYS)
    suppliers = Supplier.objects.filter(
        company__verified_with_code=False,
        company__date_verification_letter_sent__year=days_ago.year,
        company__date_verification_letter_sent__month=days_ago.month,
        company__date_verification_letter_sent__day=days_ago.day,
        unsubscribed=False,
    ).exclude(
        supplieremailnotification__category=constants.
        VERIFICATION_CODE_NOT_GIVEN,
    )
    notification_category = constants.VERIFICATION_CODE_NOT_GIVEN
    for supplier in suppliers:
        send_email_notifications(
            recipient_name=supplier.name,
            recipient_email=supplier.company_email,
            text_template='verification_code_not_given_email.txt',
            html_template='verification_code_not_given_email.html',
            subject=settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
            notification_category=notification_category,
            extra_context=extra_context,
        )
        record_supplier_notification_sent(supplier, notification_category)

    # 2nd email (after 16 days)
    days_ago = datetime.utcnow() - timedelta(
        days=settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL)
    suppliers = Supplier.objects.filter(
        company__verified_with_code=False,
        company__date_verification_letter_sent__year=days_ago.year,
        company__date_verification_letter_sent__month=days_ago.month,
        company__date_verification_letter_sent__day=days_ago.day,
        unsubscribed=False,
    ).exclude(
        supplieremailnotification__category=constants.
        VERIFICATION_CODE_2ND_EMAIL,
    )
    notification_category = constants.VERIFICATION_CODE_2ND_EMAIL
    for supplier in suppliers:
        send_email_notifications(
            recipient_name=supplier.name,
            recipient_email=supplier.company_email,
            text_template='verification_code_not_given_2nd_email.txt',
            html_template='verification_code_not_given_2nd_email.html',
            subject=settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL,
            notification_category=notification_category,
            extra_context=extra_context,
        )
        record_supplier_notification_sent(supplier, notification_category)


def new_companies_in_sector():
    days = settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS
    date_published = datetime.utcnow() - timedelta(days=days)
    notification_category = constants.NEW_COMPANIES_IN_SECTOR
    profile_url_template = settings.FAS_COMPANY_PROFILE_URL
    unsubscribed_emails = (
        models.AnonymousUnsubscribe.objects.all()
        .values_list('email', flat=True)
    )
    for industry, label in choices.COMPANY_CLASSIFICATIONS:
        companies = Company.objects.filter(
            sectors__contains='"{value}"'.format(value=industry),
            date_published__year=date_published.year,
            date_published__month=date_published.month,
            date_published__day=date_published.day,
        )
        extra_context = {
            'company_list_url': settings.FAS_COMPANY_LIST_URL,
            'companies': [
                {
                    'url': profile_url_template.format(number=company.number),
                    'instance': company,

                }
                for company in companies
            ]
        }
        buyers = (
            Buyer.objects
            .filter(sector=industry)
            .exclude(email__in=unsubscribed_emails)
        )
        for buyer in buyers:
            send_email_notifications(
                recipient_name=buyer.name,
                recipient_email=buyer.email,
                text_template='new_companies_in_sector_email.txt',
                html_template='new_companies_in_sector_email.html',
                subject=settings.NEW_COMPANIES_IN_SECTOR_SUBJECT,
                notification_category=notification_category,
                extra_context=extra_context,
            )
            record_anonymous_notification_sent(
                email=buyer.email, category=notification_category
            )
