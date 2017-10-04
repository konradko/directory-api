from urllib.parse import urljoin

from elasticsearch_dsl import field, DocType

from django.conf import settings

from company import helpers


class FormattedDate(field.Date):
    def __init__(self, date_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_format = date_format

    def _deserialize(self, *args, **kwargs):
        date = super()._deserialize(*args, **kwargs)
        if date:
            return date.strftime(self.date_format)

    def to_dict(self, *args, **kwargs):
        value = super().to_dict(*args, **kwargs)
        del value['date_format']
        return value


class CompanyDocType(DocType):
    case_study_count = field.Integer()
    date_of_creation = FormattedDate(date_format='%Y-%m-%d', index='no')
    description = field.Text()
    has_description = field.Boolean()
    employees = field.Text(index='no')
    facebook_url = field.Text(index='no')
    pk = field.Integer(index='no')
    keywords = field.Text()
    linkedin_url = field.Text(index='no')
    logo = field.Text(index='no')
    has_single_sector = field.Boolean()
    modified = FormattedDate(date_format='%Y-%m-%dT%H:%M:%S.%fZ', index='no')
    name = field.Text()
    number = field.Text()
    sectors = field.Text(multi=True)
    sectors_label = field.Text(multi=True)
    slug = field.Text()
    summary = field.Text()
    twitter_url = field.Text(index='no')
    website = field.Text()
    campaign_tag = field.Text()
    supplier_case_studies = field.Nested(
        properties={
            'pk': field.Integer(index='no'),
            'title': field.Text(),
            'short_summary': field.Text(),
            'description': field.Text(),
            'sector': field.Text(),
            'keywords': field.Text(),
            'image_one_caption': field.Text(),
            'image_two_caption': field.Text(),
            'image_three_caption': field.Text(),
            'testimonial': field.Text(),
            'slug': field.Text(),
        }
    )

    class Meta:
        index = settings.ELASTICSEARCH_COMPANY_INDEX


class CaseStudyDocType(DocType):
    pk = field.Integer(index='no')
    title = field.Text()
    short_summary = field.Text()
    description = field.Text()
    sector = field.Text()
    keywords = field.Text()
    image = field.Text(index='no')
    company_number = field.Text(index='no')
    image_one_caption = field.Text()
    image_two_caption = field.Text()
    image_three_caption = field.Text()
    testimonial = field.Text()
    slug = field.Text(index='no')
    campaign_tag = field.Text()

    class Meta:
        index = settings.ELASTICSEARCH_CASE_STUDY_INDEX


def get_absolute_url(url):
    if settings.STORAGE_CLASS_NAME == 'local-storage':
        return urljoin(settings.LOCAL_STORAGE_DOMAIN, url)
    return url


def company_model_to_doc_type(company):
    company_doc_type = CompanyDocType(
        meta={'id': company.pk},
        case_study_count=company.supplier_case_studies.count(),
        date_of_creation=company.date_of_creation,
        description=company.description,
        has_description=company.description != '',
        employees=company.employees,
        facebook_url=company.facebook_url,
        has_single_sector=len(company.sectors) == 1,
        keywords=company.keywords,
        linkedin_url=company.linkedin_url,
        logo=get_absolute_url(company.logo.url if company.logo else ''),
        modified=company.modified,
        name=company.name,
        number=company.number,
        pk=str(company.pk),
        sectors=company.sectors,
        sectors_label=[helpers.get_sector_label(v) for v in company.sectors],
        slug=company.slug,
        summary=company.summary,
        twitter_url=company.twitter_url,
        website=company.website,
        campaign_tag=company.campaign_tag,
    )
    for case_study in company.supplier_case_studies.all():
        company_doc_type.supplier_case_studies.append({
            'description': case_study.description,
            'image_one_caption': case_study.image_one_caption,
            'image_three_caption': case_study.image_three_caption,
            'image_two_caption': case_study.image_two_caption,
            'keywords': case_study.keywords,
            'pk': case_study.pk,
            'sector': case_study.sector,
            'short_summary': case_study.short_summary,
            'slug': case_study.slug,
            'testimonial': case_study.testimonial,
            'testimonial_company': case_study.testimonial_company,
            'testimonial_job_title': case_study.testimonial_job_title,
            'testimonial_name': case_study.testimonial_name,
            'title': case_study.title,
            'website': case_study.website,
        })
    return company_doc_type


def case_study_model_to_doc_type(case_study):
    case_study_doc_type = CaseStudyDocType(
        meta={'id': case_study.pk},
        description=case_study.description,
        image_one_caption=case_study.image_one_caption,
        image_three_caption=case_study.image_three_caption,
        image_two_caption=case_study.image_two_caption,
        keywords=case_study.keywords,
        pk=case_study.pk,
        sector=case_study.sector,
        short_summary=case_study.short_summary,
        slug=case_study.slug,
        title=case_study.title,
        company_number=case_study.company.number,
        image=get_absolute_url(
            case_study.image_one.url if case_study.image_one else '',
        ),
        campaign_tag=case_study.campaign_tag,
    )
    return case_study_doc_type
