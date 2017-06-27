from django.conf import settings
from django.utils import timezone

from company.utils import send_verification_letter


def send_first_verification_letter(sender, instance, *args, **kwargs):
    should_send_letter = all([
        settings.FEATURE_VERIFICATION_LETTERS_ENABLED,
        not instance.is_verification_letter_sent,
        not instance.verified_with_preverified_enrolment,
        instance.has_valid_address(),
    ])
    if should_send_letter:
        send_verification_letter(company=instance)


def publish_companies_that_meet_criteria(sender, instance, *args, **kwargs):
    if not instance.is_published:
        preverified_enrolment = instance.verified_with_preverified_enrolment
        instance.is_published = preverified_enrolment or bool(
            (instance.description or instance.summary) and
            instance.email_address and instance.verified_with_code)


def store_date_published(sender, instance, *args, **kwargs):
    if instance.is_published and not instance.date_published:
        instance.date_published = timezone.now()


def save_to_elasticsearch(sender, instance, *args, **kwargs):
    if instance.is_published:
        instance.to_doc_type().save()
