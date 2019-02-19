from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.core.urlresolvers import reverse

from company.models import Company
from enrolment.tests import VALID_REQUEST_DATA
from enrolment.tests.factories import PreVerifiedEnrolmentFactory
from supplier.models import Supplier


@pytest.mark.django_db
def test_enrolment_viewset_create():
    client = APIClient()
    data = {
        'address_line_1': '123 Fake street',
        'address_line_2': 'The Lane',
        'company_name': 'Example Corp.',
        'company_number': '07504387',
        'company_email': 'jim@example.com',
        'contact_email_address': 'jim@example.com',
        'country': 'UK',
        'has_exported_before': True,
        'locality': 'London',
        'po_box': 'PO 344',
        'postal_code': 'E14 POX',
        'sso_id': 1
    }
    response = client.post(reverse('enrolment'), data, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    company = Company.objects.get(number='07504387')
    assert company.address_line_1 == data['address_line_1']
    assert company.address_line_2 == data['address_line_2']
    assert company.name == data['company_name']
    assert company.number == data['company_number']
    assert company.email_address == data['contact_email_address']
    assert company.country == data['country']
    assert company.has_exported_before == data['has_exported_before']
    assert company.locality == data['locality']
    assert company.po_box == data['po_box']
    assert company.postal_code == data['postal_code']

    supplier = Supplier.objects.get(sso_id=1)
    assert supplier.company == company
    assert supplier.company_email == data['contact_email_address']
    assert supplier.sso_id == data['sso_id']
    assert supplier.is_company_owner is True


@pytest.mark.django_db
def test_enrolment_viewset_create_optional_fields_unset():
    client = APIClient()
    data = {
        'company_name': 'Example Corp.',
        'company_number': '07504387',
        'company_email': 'jim@example.com',
        'contact_email_address': 'jim@example.com',
        'has_exported_before': True,
        'sso_id': 1
    }
    response = client.post(reverse('enrolment'), data, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    company = Company.objects.get(number='07504387')
    assert company.address_line_1 == ''
    assert company.address_line_2 == ''
    assert company.name == data['company_name']
    assert company.number == data['company_number']
    assert company.email_address == data['contact_email_address']
    assert company.country == ''
    assert company.has_exported_before == data['has_exported_before']
    assert company.locality == ''
    assert company.po_box == ''
    assert company.postal_code == ''

    supplier = Supplier.objects.get(sso_id=1)
    assert supplier.company == company
    assert supplier.company_email == data['contact_email_address']
    assert supplier.sso_id == data['sso_id']


@pytest.mark.django_db
def test_enrolment_viewset_create_invalid_data():
    client = APIClient()
    invalid_data = VALID_REQUEST_DATA.copy()
    del invalid_data['company_name']
    response = client.post(
        reverse('enrolment'), invalid_data, format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'company_name': ['This field is required.']
    }


@pytest.mark.django_db
@patch('enrolment.serializers.CompanyEnrolmentSerializer.create')
def test_enrolment_create_company_exception_rollback(mock_create):
    api_client = APIClient()
    url = reverse('enrolment')
    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        api_client.post(url, VALID_REQUEST_DATA, format='json')

    assert Company.objects.count() == 0
    assert Supplier.objects.count() == 0


@pytest.mark.django_db
@patch('supplier.serializers.SupplierSerializer.create')
def test_enrolment_create_supplier_exception_rollback(mock_create):
    api_client = APIClient()
    url = reverse('enrolment')
    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        api_client.post(url, VALID_REQUEST_DATA, format='json')

    assert Company.objects.count() == 0
    assert Supplier.objects.count() == 0


@pytest.mark.django_db
def test_enrolment_create_disables_single_preverified_enrolment():
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=VALID_REQUEST_DATA['company_number'],
        email_address=VALID_REQUEST_DATA['contact_email_address'],
    )
    assert preverified_enrolment.is_active is True

    api_client = APIClient()
    url = reverse('enrolment')
    response = api_client.post(url, VALID_REQUEST_DATA, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    company = Company.objects.last()
    preverified_enrolment.refresh_from_db()
    assert preverified_enrolment.is_active is False
    assert company.verified_with_preverified_enrolment is True


@pytest.mark.django_db
def test_enrolment_create_preverified_enrolment_different_email(authed_client):
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=VALID_REQUEST_DATA['company_number'],
        email_address='jim@thing.com',
    )
    assert preverified_enrolment.is_active is True

    url = reverse('enrolment')
    response = authed_client.post(url, VALID_REQUEST_DATA, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    company = Company.objects.last()
    preverified_enrolment.refresh_from_db()
    assert preverified_enrolment.is_active is True
    assert company.verified_with_preverified_enrolment is False


@pytest.mark.django_db
def test_preverified_enrolment_retrieve_not_found(authed_client):
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=VALID_REQUEST_DATA['company_number'],
        email_address='jim@thing.com',
    )

    url = reverse('pre-verified-enrolment')
    params = {
        'email_address': preverified_enrolment.email_address,
        'company_number': '1122',
    }
    response = authed_client.get(url, params)

    assert response.status_code == 404


@pytest.mark.django_db
def test_preverified_enrolment_retrieve_found(authed_client):
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=VALID_REQUEST_DATA['company_number'],
        email_address=VALID_REQUEST_DATA['contact_email_address']
    )

    url = reverse('pre-verified-enrolment')
    params = {
        'email_address': preverified_enrolment.email_address,
        'company_number': preverified_enrolment.company_number,
    }
    response = authed_client.get(url, params)

    assert response.status_code == 200
