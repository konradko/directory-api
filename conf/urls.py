import django
from django.conf.urls import url, include
from django.contrib import admin

import activitystream.views
import buyer.views
import company.views
import contact.views
import enrolment.views
import exportopportunity.views
import exportreadiness.views
import healthcheck.views
import notifications.views
import supplier.views
import testapi.views

from django.conf import settings


admin.autodiscover()


urlpatterns = [
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^healthcheck/database/$',
        healthcheck.views.DatabaseAPIView.as_view(),
        name='health-check-database'
    ),
    url(
        r'^healthcheck/cache/$',
        healthcheck.views.CacheAPIView.as_view(),
        name='health-check-cache'
    ),
    url(
        r'^healthcheck/single-sign-on/$',
        healthcheck.views.SingleSignOnAPIView.as_view(),
        name='health-check-single-sign-on'
    ),
    url(
        r'^healthcheck/elasticsearch/$',
        healthcheck.views.ElasticsearchAPIView.as_view(),
        name='health-check-elastic-search'
    ),
    url(
        r'^healthcheck/ping/$',
        healthcheck.views.PingAPIView.as_view(),
        name='health-check-ping'
    ),
    url(
        r'^enrolment/$',
        enrolment.views.EnrolmentCreateAPIView.as_view(),
        name='enrolment'
    ),
    url(
        r'^pre-verified-enrolment/$',
        enrolment.views.PreVerifiedEnrolmentRetrieveView.as_view(),
        name='pre-verified-enrolment',
    ),
    url(
        r'^external/supplier-sso/$',
        supplier.views.SupplierSSOListExternalAPIView.as_view(),
        name='external-supplier-sso-list'
    ),
    url(
        r'^external/supplier/$',
        supplier.views.SupplierRetrieveExternalAPIView.as_view(),
        name='external-supplier-details'
    ),
    url(
        r'^supplier/gecko/total-registered/$',
        supplier.views.GeckoTotalRegisteredSuppliersView.as_view(),
        name='gecko-total-registered-suppliers'
    ),
    url(
        r'^supplier/company/$',
        company.views.CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'^supplier/company/verify/$',
        company.views.VerifyCompanyWithCodeAPIView.as_view(),
        name='company-verify'
    ),
    url(
        r'^supplier/company/verify/companies-house/$',
        company.views.VerifyCompanyWithCompaniesHouseView.as_view(),
        name='company-verify-companies-house'
    ),
    url(
        r'^supplier/company/case-study/$',
        company.views.CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    url(
        r'^supplier/company/transfer-ownership-invite/(?P<uuid>.*)/$',
        company.views.TransferOwnershipInviteRetrieveUpdateAPIView.as_view(),
        name='transfer-ownership-invite-detail'
    ),
    url(
        r'^supplier/company/transfer-ownership-invite/$',
        company.views.TransferOwnershipInviteCreateView.as_view(),
        name='transfer-ownership-invite'
    ),
    url(
        r'^supplier/company/collaboration-invite/$',
        company.views.CollaboratorInviteCreateView.as_view(),
        name='collaboration-invite-create'
    ),
    url(
        r'^supplier/company/collaboration-invite/(?P<uuid>.*)/',
        company.views.CollaboratorInviteRetrieveUpdateAPIView.as_view(),
        name='collaboration-invite-detail'
    ),
    url(
        r'^supplier/company/remove-collaborators/',
        company.views.RemoveCollaboratorsView.as_view(),
        name='remove-collaborators'
    ),
    url(
        r'^supplier/company/case-study/(?P<pk>[0-9]+)/$',
        company.views.CompanyCaseStudyViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='company-case-study-detail',
    ),
    url(
        r'^supplier/company/collaborators/$',
        supplier.views.CompanyCollboratorsListView.as_view(),
        name='supplier-company-collaborators-list'
    ),
    url(
        r'^supplier/$',
        supplier.views.SupplierRetrieveUpdateAPIView.as_view(),
        name='supplier'
    ),
    url(
        r'^supplier/unsubscribe/$',
        supplier.views.UnsubscribeSupplierAPIView.as_view(),
        name='unsubscribe-supplier'
    ),
    url(
        r'^public/case-study/(?P<pk>.*)/$',
        company.views.PublicCaseStudyViewSet.as_view({'get': 'retrieve'}),
        name='public-case-study-detail'
    ),
    url(
        r'^public/company/(?P<companies_house_number>.*)/$',
        company.views.CompanyPublicProfileViewSet.as_view({'get': 'retrieve'}),
        name='company-public-profile-detail'
    ),
    url(
        r'^public/company/$',
        company.views.CompanyPublicProfileViewSet.as_view({'get': 'list'}),
        name='company-public-profile-list'
    ),
    url(
        r'^validate/company-number/$',
        company.views.CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number'
    ),
    url(
        r'^buyer/$',
        buyer.views.BuyerCreateAPIView.as_view(),
        name='buyer-create',
    ),
    url(
        r'^contact/supplier/$',
        contact.views.CreateMessageToSupplierAPIView.as_view(),
        name='company-public-profile-contact-create'
    ),
    url(
        r'^notifications/anonymous-unsubscribe/$',
        notifications.views.AnonymousUnsubscribeCreateAPIView.as_view(),
        name='anonymous-unsubscribe'
    ),
    url(
        r'^company/search/$',
        company.views.CompanySearchAPIView.as_view(),
        name='company-search'
    ),
    url(
        r'^case-study/search/$',
        company.views.CaseStudySearchAPIView.as_view(),
        name='case-study-search',
    ),
    url(
        r'^export-opportunity/food/$',
        exportopportunity.views.ExportOpportunityFoodCreateAPIView.as_view(),
        name='export-opportunity-food-create'
    ),
    url(
        r'^export-opportunity/legal/$',
        exportopportunity.views.ExportOpportunityLegalCreateAPIView.as_view(),
        name='export-opportunity-legal-create'
    ),
    url(
        r'export-readiness/triage/$',
        exportreadiness.views.TriageResultCreateRetrieveView.as_view(),
        name='export-readiness-triage-create-retrieve'
    ),
    url(
        r'export-readiness/article-read/$',
        exportreadiness.views.ArticleReadCreateRetrieveView.as_view(),
        name='export-readiness-article-read-create-retrieve'
    ),
    url(
        r'export-readiness/task-completed/$',
        exportreadiness.views.TaskCompletedCreateRetrieveView.as_view(),
        name='export-readiness-task-completed-create-retrieve'
    ),
    url(
        r'^activity-stream/',
        activitystream.views.ActivityStreamViewSet.as_view({'get': 'list'}),
        name='activity-stream'
    ),
    url(
        r'buyer/csv-dump/$',
        buyer.views.BuyerCSVDownloadAPIView.as_view(),
        name='buyer-csv-dump'
    ),
    url(
        r'supplier/csv-dump/$',
        supplier.views.SupplierCSVDownloadAPIView.as_view(),
        name='supplier-csv-dump'
    ),
    url(
        r'^testapi/company/(?P<ch_id>.*)/$',
        testapi.views.CompanyTestAPIView.as_view(),
        name='company_by_ch_id'
    ),
    url(
        r'^testapi/companies/published/$',
        testapi.views.PublishedCompaniesTestAPIView.as_view(),
        name='published_companies'
    ),
]

if settings.STORAGE_CLASS_NAME == 'local-storage':
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$',
            django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT},
            name='media'
        ),
    ]
