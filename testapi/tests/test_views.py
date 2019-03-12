import datetime

import pytest
from django.core.urlresolvers import reverse
from rest_framework import status

from company import models
from company.tests import factories
from supplier.tests.factories import SupplierFactory


@pytest.mark.django_db
def test_get_existing_company_by_ch_id(authed_client, authed_supplier):
    url = reverse(
        'company_by_ch_id', kwargs={'ch_id': authed_supplier.company.number})
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_check_contents_of_get_existing_company_by_ch_id(
        authed_client, authed_supplier):
    email_address = 'test@user.com'
    verification_code = '1234567890'
    company = factories.CompanyFactory(
        name='Test Company', date_of_creation=datetime.date(2000, 10, 10),
        email_address='test@user.com', verification_code=verification_code,
        is_verification_letter_sent=False
    )
    authed_supplier.company = company
    authed_supplier.save()
    company.refresh_from_db()
    assert company.verification_code
    url = reverse(
        'company_by_ch_id', kwargs={'ch_id': authed_supplier.company.number})
    response = authed_client.get(url)
    assert 'letter_verification_code' in response.json()
    assert response.json()['company_email'] == email_address
    assert response.json()['letter_verification_code'] == verification_code
    assert not response.json()['is_verification_letter_sent']


@pytest.mark.django_db
def test_get_company_by_ch_id_with_disabled_test_api(client, settings):
    settings.FEATURE_TEST_API_ENABLED = False
    url = reverse('company_by_ch_id', kwargs={'ch_id': '12345678'})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_existing_company_by_ch_id_with_disabled_test_api(
        authed_client, authed_supplier, settings):
    settings.FEATURE_TEST_API_ENABLED = False
    url = reverse(
        'company_by_ch_id', kwargs={'ch_id': authed_supplier.company.number})
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_company_by_non_existing_ch_id(client):
    url = reverse('company_by_ch_id', kwargs={'ch_id': 'nonexisting'})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_existing_company_by_ch_id(authed_client, authed_supplier):
    number = authed_supplier.company.number
    url = reverse(
        'company_by_ch_id', kwargs={'ch_id': number})
    response = authed_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert models.Company.objects.filter(number=number).exists() is False


@pytest.mark.django_db
def test_delete_non_existing_company_by_ch_id(authed_client):
    url = reverse(
        'company_by_ch_id', kwargs={'ch_id': 'invalid'})
    response = authed_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_existing_company_by_ch_id_with_disabled_testapi(
        authed_client, authed_supplier, settings):
    settings.FEATURE_TEST_API_ENABLED = False
    url = reverse(
        'company_by_ch_id', kwargs={'ch_id': authed_supplier.company.number})
    response = authed_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_published_companies_without_optional_parameters(authed_client):
    url = reverse('published_companies')
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.parametrize(
    ['limit', 'minimal_number_of_sectors', 'expected_status_code'],
    [
        (1, 0, status.HTTP_200_OK),
        (0, 8, status.HTTP_200_OK),
        (0, 0, status.HTTP_200_OK),
        (0, 0, status.HTTP_200_OK),
        (-1, 0, status.HTTP_200_OK),
        (-1, -1, status.HTTP_200_OK),
        (None, 0, status.HTTP_200_OK),
        (1, None, status.HTTP_200_OK),
    ])
@pytest.mark.django_db
def test_get_published_companies_use_optional_parameters(
        authed_client, limit, minimal_number_of_sectors, expected_status_code):
    url = reverse('published_companies')
    params = {
        'limit': limit,
        'minimal_number_of_sectors': minimal_number_of_sectors
    }
    response = authed_client.get(url, params=params)
    assert response.status_code == expected_status_code
    assert response.json() == []


@pytest.mark.django_db
def test_get_published_companies_with_disabled_test_api(
        authed_client, settings):
    settings.FEATURE_TEST_API_ENABLED = False
    url = reverse('published_companies')
    response = authed_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_published_companies_with_disabled_test_api_and_unsigned_client(
        client, settings):
    settings.FEATURE_TEST_API_ENABLED = False
    url = reverse('published_companies')
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_published_companies_check_response_contents(
        authed_client, authed_supplier):
    name = 'Test Company'
    number = '12345678'
    email = 'test@user.com'
    sectors = ["AEROSPACE", "AUTOMOTIVE", "BIOTECHNOLOGY_AND_PHARMACEUTICALS"]
    employees = '1-10'
    website = 'http://test.com'
    keywords = 'keyword1,keyword2,keyword3'
    facebook_url = 'http://www.facebook.com/testcompany'
    linkedin_url = 'http://www.linkedin.com/testcompany'
    twitter_url = 'http://www.twitter.com/testcompany'
    summary = 'few words about our company'
    description = 'we sell cars'
    is_published_investment_support_directory = True
    expected_number_of_results = 1
    expected_number_of_keys = 12
    company = factories.CompanyFactory(
        name=name, number=number, email_address=email, sectors=sectors,
        employees=employees, website=website, keywords=keywords,
        facebook_url=facebook_url, linkedin_url=linkedin_url,
        twitter_url=twitter_url, summary=summary, description=description,
        is_published_investment_support_directory=is_published_investment_support_directory)
    authed_supplier.company = company
    authed_supplier.save()
    company.refresh_from_db()
    url = reverse('published_companies')
    response = authed_client.get(url)
    assert len(response.json()) == expected_number_of_results
    found_company = response.json()[0]
    assert len(found_company.keys()) == expected_number_of_keys
    assert found_company['name'] == name
    assert found_company['number'] == number
    assert found_company['company_email'] == email
    assert found_company['sectors'] == sectors
    assert found_company['employees'] == employees
    assert found_company['keywords'] == keywords
    assert found_company['website'] == website
    assert found_company['facebook_url'] == facebook_url
    assert found_company['twitter_url'] == twitter_url
    assert found_company['linkedin_url'] == linkedin_url
    assert found_company['summary'] == summary
    assert found_company['description'] == description


@pytest.mark.parametrize(
    ['limit', 'minimal_number_of_sectors', 'expected_number_of_results'],
    [
        (3, 0, 2),
        (2, 0, 2),
        (None, 3, 1),
        (None, 2, 2),
        (1, 0, 1),
        (0, 8, 0),
    ])
@pytest.mark.django_db
def test_get_published_companies_use_optional_filters(
        authed_client, limit, minimal_number_of_sectors,
        expected_number_of_results):
    sectors_1 = ["AEROSPACE", "AUTOMOTIVE", "DEFENCE"]
    sectors_2 = ["AEROSPACE", "AUTOMOTIVE"]
    company_1 = factories.CompanyFactory(is_published_investment_support_directory=True, sectors=sectors_1)
    company_2 = factories.CompanyFactory(is_published_investment_support_directory=True, sectors=sectors_2)
    supplier_1 = SupplierFactory.create(sso_id=777)
    supplier_2 = SupplierFactory.create(sso_id=888)
    supplier_1.company = company_1
    supplier_1.save()
    supplier_2.company = company_2
    supplier_2.save()
    url = reverse('published_companies')
    params = {}
    if limit is not None:
        params.update({'limit': limit})
    if minimal_number_of_sectors is not None:
        params.update(
            {'minimal_number_of_sectors': minimal_number_of_sectors})
    response = authed_client.get(url, data=params)
    assert len(response.json()) == expected_number_of_results
