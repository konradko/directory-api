import datetime
from unittest import mock

from freezegun import freeze_time
import pytest

from django.utils import timezone

from company.tests.factories import CompanyFactory
from enrolment.tests.factories import TrustedSourceSignupCodeFactory


@pytest.mark.django_db
def test_sends_verification_letter_post_save(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = CompanyFactory()

    company.refresh_from_db()
    assert company.verification_code

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'test': True,
            'recipient[company_name]': company.name,
            'recipient[country]': company.country,
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': company.address_line_1,
            'recipient[full_name]': company.postal_full_name,
            'recipient[city]': company.locality,
            'recipient[company]': company.name,
            'recipient[postcode]': company.postal_code,
            'recipient[title]': company.postal_full_name,
            'recipient[address2]': company.address_line_2,
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
        },
    )


@pytest.mark.django_db
def test_does_not_send_verification_letter_on_update(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = CompanyFactory(name="Original name")
        company.name = "Changed name"
        company.save()

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'test': True,
            'recipient[company_name]': 'Original name',
            'recipient[country]': company.country,
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': company.address_line_1,
            'recipient[full_name]': company.postal_full_name,
            'recipient[city]': company.locality,
            'recipient[company]': 'Original name',
            'recipient[postcode]': company.postal_code,
            'recipient[title]': company.postal_full_name,
            'recipient[address2]': company.address_line_2,
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
        },
    )


@pytest.mark.django_db
def test_does_not_overwrite_verification_code_if_already_set(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post'):
        company = CompanyFactory(verification_code='test')

    company.refresh_from_db()
    assert company.verification_code == 'test'


@pytest.mark.django_db
@mock.patch('company.signals.send_verification_letter')
def test_does_not_send_if_letter_already_sent(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    CompanyFactory(
        is_verification_letter_sent=True,
        verification_code='test',
    )

    mock_send_letter.assert_not_called()


@pytest.mark.django_db
@freeze_time()
@mock.patch('company.signals.send_verification_letter')
def test_letter_sent(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    company = CompanyFactory(verification_code='test')

    mock_send_letter.assert_called_with(company=company)


@pytest.mark.django_db
@mock.patch('company.signals.send_verification_letter')
@mock.patch(
    'company.models.Company.has_valid_address',
    mock.Mock(return_value=False)
)
def test_unknown_address_not_send_letters(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    CompanyFactory()

    mock_send_letter.send_letter.assert_not_called()


@pytest.mark.django_db
def test_automatic_publish_create():
    should_be_published = [
        {
            'description': 'description',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
        {
            'summary': 'summary',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
    ]

    should_be_unpublished = [
        {
            'description': '',
            'summary': '',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
        {
            'description': 'description',
            'summary': 'summary',
            'email_address': '',
            'verified_with_code': True,
        },
        {
            'description': 'description',
            'summary': 'summary',
            'email_address': 'jim@example.com',
            'verified_with_code': False,
        },
    ]

    should_be_force_published = [
        {**item, 'is_published': True}
        for item in should_be_unpublished
    ]

    for kwargs in should_be_published:
        assert CompanyFactory(**kwargs).is_published is True

    for kwargs in should_be_unpublished:
        assert CompanyFactory(**kwargs).is_published is False

    for kwargs in should_be_force_published:
        assert CompanyFactory(**kwargs).is_published is True


@pytest.mark.django_db
def test_automatic_publish_update():
    should_be_published = [
        {
            'description': 'description',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
        {
            'summary': 'summary',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
    ]

    should_be_unpublished = [
        {
            'description': '',
            'summary': '',
            'email_address': 'thing@example.com',
            'verified_with_code': True,
        },
        {
            'description': 'description',
            'summary': 'summary',
            'email_address': '',
            'verified_with_code': True,
        },
        {
            'description': 'description',
            'summary': 'summary',
            'email_address': 'jim@example.com',
            'verified_with_code': False,
        },
    ]

    should_be_force_published = [
        {**item, 'is_published': True}
        for item in should_be_unpublished
    ]

    for kwargs in should_be_published:
        company = CompanyFactory()
        assert company.is_published is False
        for field, value in kwargs.items():
            setattr(company, field, value)
        company.save()
        company.refresh_from_db()
        assert company.is_published is True

    for kwargs in should_be_unpublished:
        company = CompanyFactory()
        assert company.is_published is False
        for field, value in kwargs.items():
            setattr(company, field, value)
        company.save()
        company.refresh_from_db()
        assert company.is_published is False

    for kwargs in should_be_force_published:
        company = CompanyFactory()
        assert company.is_published is False
        for field, value in kwargs.items():
            setattr(company, field, value)
        company.save()
        company.refresh_from_db()
        assert company.is_published is True


@pytest.mark.django_db
def test_store_date_published_unpublished_company():
    company = CompanyFactory(is_published=False)

    assert company.date_published is None


@pytest.mark.django_db
@freeze_time()
def test_store_date_published_published_company_without_date():
    company = CompanyFactory(is_published=True, date_published=None)

    assert company.date_published == timezone.now()


@pytest.mark.django_db
def test_store_date_published_published_company_with_date():
    expected_date = timezone.now()

    company = CompanyFactory(is_published=True, date_published=expected_date)

    assert company.date_published == expected_date


@pytest.mark.django_db
def test_save_to_elasticsearch_published(mock_elasticsearch_company_save):
    CompanyFactory(is_published=True)

    assert mock_elasticsearch_company_save.call_count == 1


@pytest.mark.django_db
def test_save_to_elasticsearch_unpublished(mock_elasticsearch_company_save):
    CompanyFactory(is_published=False)

    assert mock_elasticsearch_company_save.call_count == 0


@pytest.mark.django_db
def test_deactivate_trusted_source_signup_code_single_code():
    trusted_source_signup_code = TrustedSourceSignupCodeFactory.create(
        company_number='00000001'
    )
    assert trusted_source_signup_code.is_active is True

    CompanyFactory(is_published=False, number='00000001')

    trusted_source_signup_code.refresh_from_db()
    assert trusted_source_signup_code.is_active is False


@pytest.mark.django_db
def test_deactivate_trusted_source_signup_code_multiple_codes():
    trusted_source_signup_code_one = TrustedSourceSignupCodeFactory.create(
        company_number='00000001'
    )
    trusted_source_signup_code_two = TrustedSourceSignupCodeFactory.create(
        company_number='00000001'
    )
    assert trusted_source_signup_code_one.is_active is True
    assert trusted_source_signup_code_two.is_active is True

    CompanyFactory(is_published=False, number='00000001')

    trusted_source_signup_code_one.refresh_from_db()
    trusted_source_signup_code_two.refresh_from_db()
    assert trusted_source_signup_code_one.is_active is False
    assert trusted_source_signup_code_two.is_active is False
