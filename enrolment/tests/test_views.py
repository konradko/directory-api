from unittest.mock import Mock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.core.urlresolvers import reverse

from company.models import Company
from enrolment.tests import factories, VALID_REQUEST_DATA
from enrolment.tests.factories import TrustedSourceSignupCodeFactory
from user.models import User as Supplier


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('boto3.resource')
def test_enrolment_viewset_create(boto_mock):
    client = APIClient()
    response = client.post(
        reverse('enrolment'), VALID_REQUEST_DATA, format='json'
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Company.objects.filter(
        number=VALID_REQUEST_DATA['company_number']
    ).exists()
    assert Supplier.objects.filter(
        sso_id=VALID_REQUEST_DATA['sso_id'],
    ).exists()


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_enrolment_viewset_create_invalid_data():
    client = APIClient()
    invalid_data = VALID_REQUEST_DATA.copy()
    del invalid_data['company_number']
    response = client.post(
        reverse('enrolment'), invalid_data, format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'company_number': ['This field is required.']
    }


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_trusted_source_signup_retrieve():
    api_client = APIClient()
    trusted_source_code = factories.TrustedSourceSignupCodeFactory.create()

    url = reverse(
        'trusted-source-signup-code', kwargs={'code': trusted_source_code.code}
    )

    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_enrolment_create_disables_signup_code_single_code():
    trusted_source_signup_code = TrustedSourceSignupCodeFactory.create(
        company_number=VALID_REQUEST_DATA['company_number']
    )
    assert trusted_source_signup_code.is_active is True

    api_client = APIClient()
    url = reverse('enrolment')
    response = api_client.post(url, VALID_REQUEST_DATA, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    trusted_source_signup_code.refresh_from_db()
    assert trusted_source_signup_code.is_active is False


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_trusted_source_signup_retrieve_inactive_token():
    api_client = APIClient()
    trusted_source_code = factories.TrustedSourceSignupCodeFactory.create(
        is_active=False
    )

    url = reverse(
        'trusted-source-signup-code', kwargs={'code': trusted_source_code.code}
    )

    response = api_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_trusted_source_signup_unsafe():
    api_client = APIClient()
    trusted_source_code = factories.TrustedSourceSignupCodeFactory.create()

    url = reverse(
        'trusted-source-signup-code', kwargs={'code': trusted_source_code.code}
    )

    for method in [api_client.post, api_client.patch, api_client.delete]:
        response = method(url)
        assert response.status_code == 405


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_enrolment_create_disables_signup_code_multiple_codes():
    trusted_source_signup_code_one = TrustedSourceSignupCodeFactory.create(
        company_number=VALID_REQUEST_DATA['company_number']
    )
    trusted_source_signup_code_two = TrustedSourceSignupCodeFactory.create(
        company_number=VALID_REQUEST_DATA['company_number']
    )
    assert trusted_source_signup_code_one.is_active is True
    assert trusted_source_signup_code_two.is_active is True

    api_client = APIClient()
    url = reverse('enrolment')
    api_client.post(url, VALID_REQUEST_DATA, format='json')

    trusted_source_signup_code_one.refresh_from_db()
    trusted_source_signup_code_two.refresh_from_db()
    assert trusted_source_signup_code_one.is_active is False
    assert trusted_source_signup_code_two.is_active is False
