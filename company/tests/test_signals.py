import datetime
from unittest import mock

import elasticsearch
from freezegun import freeze_time
import pytest

from django.utils import timezone

from company.search import CompanyDocType
from company.tests import factories


@pytest.mark.django_db
def test_sends_verification_letter_post_save(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = factories.CompanyFactory()

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
        company = factories.CompanyFactory(name="Original name")
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
        company = factories.CompanyFactory(verification_code='test')

    company.refresh_from_db()
    assert company.verification_code == 'test'


@pytest.mark.django_db
@mock.patch('company.signals.send_verification_letter')
def test_does_not_send_if_letter_already_sent(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    factories.CompanyFactory(
        is_verification_letter_sent=True,
        verification_code='test',
    )

    mock_send_letter.assert_not_called()


@pytest.mark.django_db
@freeze_time()
@mock.patch('company.signals.send_verification_letter')
def test_letter_sent(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    company = factories.CompanyFactory(verification_code='test')

    mock_send_letter.assert_called_with(company=company)


@pytest.mark.django_db
@mock.patch('company.signals.send_verification_letter')
@mock.patch(
    'company.models.Company.has_valid_address',
    mock.Mock(return_value=False)
)
def test_unknown_address_not_send_letters(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    factories.CompanyFactory()

    mock_send_letter.send_letter.assert_not_called()


test_publish_params = [
    # has_contact
    ['',  '',  '',         False, False],
    ['',  '',  'a@e.com',  False, False],
    # has_synopsis
    ['d', '',  '',         False, False],
    ['d', '',  'a@e.com',  False, False],
    ['d', 's',  '',        False, False],
    ['',  's',  '',        False, False],
    ['d', 's',  'a@e.com', False, False],
    ['',  's',  'a@e.com', False, False],
    # is_verified
    ['',  '',  '',         True,  False],
    ['',  '',  'a@e.com',  True,  False],
    ['d', '',  '',         True,  False],
    ['d', '',  'a@e.com',  True,  True],
    ['d', 's',  '',        True,  False],
    ['',  's',  '',        True,  False],
    ['d', 's',  'a@e.com', True,  True],
    ['',  's',  'a@e.com', True,  True],
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'desciption,summary,email,is_verified,expected', test_publish_params
)
def test_publish(desciption, summary, email, is_verified, expected, settings):
    settings.FEATURE_MANUAL_PUBLISH_ENABLED = False
    fields = {
        'description': desciption,
        'summary': summary,
        'email_address': email
    }
    mock_verifed = mock.PropertyMock(return_value=is_verified)
    with mock.patch('company.models.Company.is_verified', mock_verifed):
        company = factories.CompanyFactory(**fields)
        # create
        assert company.is_published is expected
        # update
        for field, value in fields.items():
            setattr(company, field, value)
        company.save()
        company.refresh_from_db()
        assert company.is_published is expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    'desciption,summary,email,is_verified,expected',
    test_publish_params
)
def test_publish_feature_flagged(
    desciption, summary, email, is_verified, expected, settings
):
    settings.FEATURE_MANUAL_PUBLISH_ENABLED = True
    fields = {
        'description': desciption,
        'summary': summary,
        'email_address': email
    }
    mock_verifed = mock.PropertyMock(return_value=is_verified)
    with mock.patch('company.models.Company.is_verified', mock_verifed):
        company = factories.CompanyFactory(**fields)
        # create
        assert company.is_published is False
        # update
        for field, value in fields.items():
            setattr(company, field, value)
        company.save()
        company.refresh_from_db()
        assert company.is_published is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    'desciption,'
    'summary,email,'
    'is_verified,'
    'is_published_investment_support_directory,'
    'is_published_find_a_supplier',
    [
        # has_contact
        ['',  '',  '',         False, True, True],
        ['',  '',  'a@e.com',  False, True, True],
        # has_synopsis
        ['d', '',  '',         False, True, True],
        ['d', '',  'a@e.com',  False, True, True],
        ['d', 's',  '',        False, True, True],
        ['',  's',  '',        False, True, True],
        ['d', 's',  'a@e.com', False, True, True],
        ['',  's',  'a@e.com', False, True, True],
        # is_verified
        ['',  '',  '',         True, True, True],
        ['',  '',  'a@e.com',  True, True, True],
        ['d', '',  '',         True, True, True],
        ['d', '',  'a@e.com',  True, True, True],
        ['d', 's',  '',        True, True, True],
        ['',  's',  '',        True, True, True],
        ['d', 's',  'a@e.com', True, True, True],
        ['',  's',  'a@e.com', True, True, True],
    ]
)
def test_publish_published(
        desciption,
        summary,
        email,
        is_verified,
        is_published_investment_support_directory,
        is_published_find_a_supplier
):
    fields = {
        'description': desciption,
        'summary': summary,
        'email_address': email,
        'is_published_investment_support_directory':
            is_published_investment_support_directory,
        'is_published_find_a_supplier': is_published_find_a_supplier
    }
    mock_verifed = mock.PropertyMock(return_value=is_verified)
    with mock.patch('company.models.Company.is_verified', mock_verifed):
        company = factories.CompanyFactory(**fields)
        # create
        assert company.is_published is True
        # update
        for field, value in fields.items():
            setattr(company, field, value)
        company.save()
        company.refresh_from_db()
        assert company.is_published is True


@pytest.mark.django_db
def test_store_date_published_unpublished_company():
    company = factories.CompanyFactory(
        is_published_investment_support_directory=False,
        is_published_find_a_supplier=False,
    )

    assert company.date_published is None


@pytest.mark.django_db
@freeze_time()
def test_store_date_published_published_company_isd_without_date():
    company = factories.CompanyFactory(
        is_published_investment_support_directory=True,
        date_published=None
    )

    assert company.date_published == timezone.now()


@pytest.mark.django_db
@freeze_time()
def test_store_date_published_published_company_fab_without_date():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True,
        date_published=None
    )

    assert company.date_published == timezone.now()


@pytest.mark.django_db
def test_store_date_published_published_isd_company_with_date():
    expected_date = timezone.now()

    company = factories.CompanyFactory(
        is_published_investment_support_directory=True,
        date_published=expected_date
    )

    assert company.date_published == expected_date


@pytest.mark.django_db
def test_store_date_published_published_fab_company_with_date():
    expected_date = timezone.now()

    company = factories.CompanyFactory(
        is_published_find_a_supplier=True,
        date_published=expected_date
    )

    assert company.date_published == expected_date


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_published_investment_support_directory,'
    'call_count',
    [
        (False, 0),
        (True, 1),
    ]
)
def test_save_company_changes_to_elasticsearch(
    is_published_investment_support_directory,
    call_count,
    mock_elasticsearch_company_save,
):
    factories.CompanyFactory(
        is_published_investment_support_directory=(
            is_published_investment_support_directory
        )
    )

    assert mock_elasticsearch_company_save.call_count == call_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_published_investment_support_directory,call_count',
    [(False, 0), (True, 2)]
)
def test_save_case_study_changes_to_elasticsearch(
    is_published_investment_support_directory,
    call_count,
    mock_elasticsearch_company_save,
):
    company = factories.CompanyFactory(
        is_published_investment_support_directory=(
            is_published_investment_support_directory
        )
    )
    factories.CompanyCaseStudyFactory(company=company)

    assert mock_elasticsearch_company_save.call_count == call_count


@pytest.mark.django_db
def test_delete_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_investment_support_directory=True
    )
    company_pk = company.pk

    CompanyDocType.get(id=company_pk)  # not raises if exists

    company.delete()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        CompanyDocType.get(id=company_pk)


@pytest.mark.django_db
def test_delete_unpublished_isd_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_investment_support_directory=False
    )
    company_pk = company.pk

    company.delete()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        CompanyDocType.get(id=company_pk)


@pytest.mark.django_db
def test_delete_unpublish_isd_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_investment_support_directory=True
    )
    company_pk = company.pk

    CompanyDocType.get(id=company_pk)  # not raises if exists

    company.is_published_investment_support_directory = False
    company.save()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        CompanyDocType.get(id=company_pk)


@pytest.mark.django_db
def test_delete_unpublished_fab_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=False
    )
    company_pk = company.pk

    company.delete()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        CompanyDocType.get(id=company_pk)


@pytest.mark.django_db
def test_delete_unpublish_fab_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True
    )
    company_pk = company.pk

    CompanyDocType.get(id=company_pk)  # not raises if exists

    company.is_published_find_a_supplier = False
    company.save()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        CompanyDocType.get(id=company_pk)


@pytest.mark.django_db
@mock.patch('company.signals.OwnershipChangeNotification')
def test_account_ownership_transfer_email_notification(mocked_notification):
    factories.OwnershipInviteFactory()
    assert mocked_notification().send_async.called is True


@pytest.mark.django_db
@mock.patch('company.signals.CollaboratorNotification')
def test_account_collaborator_email_notification(mocked_notification):
    factories.CollaboratorInviteFactory()
    assert mocked_notification().send_async.called is True


@pytest.mark.django_db
@mock.patch('company.signals.CollaboratorNotification')
def test_account_collaborator_email_notification_modified(mocked_notification):
    invite = factories.CollaboratorInviteFactory()

    # now modify it

    invite.accepted = True
    invite.save()

    assert mocked_notification().send_async.call_count == 1
