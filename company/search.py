from urllib.parse import urljoin

from elasticsearch_dsl import Document, field, InnerDoc

from django.conf import settings

from company import helpers, serializers


class CaseStudyFieldsMixin:
    wildcard = field.Text()
    pk = field.Integer(index=False)
    title = field.Text(copy_to='wildcard')
    short_summary = field.Text(copy_to='wildcard')
    description = field.Text(copy_to='wildcard')
    sector = field.Text(copy_to='wildcard')
    keywords = field.Text(copy_to='wildcard')
    image = field.Text(index=False)
    company_number = field.Text(index=False)
    image_one_caption = field.Text(copy_to='wildcard')
    image_two_caption = field.Text(copy_to='wildcard')
    image_three_caption = field.Text(copy_to='wildcard')
    testimonial = field.Text(copy_to='wildcard')
    slug = field.Text(index=False)


class CaseStudyDocument(CaseStudyFieldsMixin, Document):

    class Meta:
        index = settings.ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS


class CaseStudyInnerDoc(CaseStudyFieldsMixin, InnerDoc):
    pass


class CompanyDocument(Document):
    wildcard = field.Text()
    case_study_count = field.Integer()
    date_of_creation = field.Date(index=False)
    description = field.Text(copy_to='wildcard')
    has_description = field.Boolean()
    employees = field.Text(index=False)
    facebook_url = field.Text(index=False)
    pk = field.Integer(index=False)
    keywords = field.Text(copy_to='wildcard')
    linkedin_url = field.Text(index=False)
    logo = field.Text(index=False)
    has_single_sector = field.Boolean()
    modified = field.Date(index=False)
    name = field.Text(copy_to='wildcard')
    number = field.Text(copy_to='wildcard')
    sectors = field.Text(multi=True, copy_to='wildcard')
    sectors_label = field.Text(multi=True, copy_to='wildcard')
    expertise_industries = field.Text(multi=True, copy_to='wildcard')
    expertise_regions = field.Text(multi=True, copy_to='wildcard')
    expertise_languages = field.Text(multi=True, copy_to='wildcard')
    expertise_countries = field.Text(multi=True, copy_to='wildcard')
    # Represents Dict as it's the primitive datatype for this field
    expertise_products_services = field.Object()
    expertise_products_services_labels = field.Text(
        multi=True, copy_to='wildcard'
    )
    expertise_labels = field.Text(multi=True, copy_to='wildcard')
    slug = field.Text(copy_to='wildcard')
    summary = field.Text(copy_to='wildcard')
    twitter_url = field.Text(index=False)
    website = field.Text(copy_to='wildcard')
    supplier_case_studies = field.Nested(
        properties={
            'pk': field.Integer(index=False),
            'title': field.Text(copy_to='wildcard'),
            'short_summary': field.Text(copy_to='wildcard'),
            'description': field.Text(copy_to='wildcard'),
            'sector': field.Text(copy_to='wildcard'),
            'keywords': field.Text(copy_to='wildcard'),
            'image_one_caption': field.Text(copy_to='wildcard'),
            'image_two_caption': field.Text(copy_to='wildcard'),
            'image_three_caption': field.Text(copy_to='wildcard'),
            'testimonial': field.Text(copy_to='wildcard'),
            'slug': field.Text(copy_to='wildcard'),
        }
    )
    is_showcase_company = field.Boolean()
    is_published_investment_support_directory = field.Boolean()
    is_published_find_a_supplier = field.Boolean()

    class Meta:
        index = settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS


def get_absolute_url(url):
    if settings.STORAGE_CLASS_NAME == 'local-storage':
        return urljoin(settings.LOCAL_STORAGE_DOMAIN, url)
    return url


def company_model_to_doc_type(
    company, index=settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS
):
    # getattr is used on the company to allow this functionton be used in
    # migrations (historic models wont have all the fields listed below).
    company_fields = {
        'date_of_creation',
        'description',
        'company_type',
        'employees',
        'facebook_url',
        'keywords',
        'linkedin_url',
        'modified',
        'name',
        'number',
        'sectors',
        'expertise_industries',
        'expertise_regions',
        'expertise_languages',
        'expertise_countries',
        'expertise_products_services',
        'slug',
        'summary',
        'twitter_url',
        'website',
        'is_showcase_company',
        'is_published_investment_support_directory',
        'is_published_find_a_supplier',
    }
    case_study_fields = {
        'description',
        'image_one_caption',
        'image_three_caption',
        'image_two_caption',
        'keywords',
        'pk',
        'sector',
        'short_summary',
        'slug',
        'testimonial',
        'testimonial_company',
        'testimonial_job_title',
        'testimonial_name',
        'title',
        'website',
    }
    has_description = getattr(company, 'description', '') != ''
    company_data_dict = serializers.CompanySerializer(company).data
    company_parser = helpers.CompanyParser(company_data_dict)
    expertise_products_services_labels = []
    for key, values in company.expertise_products_services.items():
        expertise_products_services_labels += values

    company_doc_type = CompanyDocument(
        meta={'id': company.pk, '_index': index},
        pk=str(company.pk),
        case_study_count=company.supplier_case_studies.count(),
        has_single_sector=len(company.sectors) == 1,
        has_description=has_description,
        logo=get_absolute_url(company.logo.url if company.logo else ''),
        sectors_label=[
            helpers.get_sector_label(v) for v in company.sectors
        ],
        expertise_products_services_labels=expertise_products_services_labels,
        expertise_labels=company_parser.expertise_labels_for_search,
        **{key: getattr(company, key, '') for key in company_fields},
    )
    for case_study in company.supplier_case_studies.all():
        company_doc_type.supplier_case_studies.append({
            key: getattr(case_study, key, '') for key in case_study_fields
        })

    return company_doc_type


def case_study_model_to_doc_type(
    case_study, index=settings.ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS,
):
    # getattr is used on the case study to allow this functionton be used in
    # migrations (historic models wont have all the fields listed below).
    fields = {
        'description',
        'image_one_caption',
        'image_three_caption',
        'image_two_caption',
        'keywords',
        'pk',
        'sector',
        'short_summary',
        'slug',
        'title',
    }
    return CaseStudyDocument(
        meta={'id': case_study.pk, '_index': index},
        image=get_absolute_url(
            case_study.image_one.url if case_study.image_one else '',
        ),
        company_number=case_study.company.number,
        **{key: getattr(case_study, key, '') for key in fields},
    )
