from django.http import Http404
from rest_framework.generics import (
    get_object_or_404,
    DestroyAPIView,
    RetrieveAPIView
)
from rest_framework.request import Request
from rest_framework.response import Response

from django.conf import settings
from api.signature import SignatureCheckPermission
from company.models import Company
from testapi.serializers import CompanySerializer


class CompanyTestAPIView(RetrieveAPIView, DestroyAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [SignatureCheckPermission]
    lookup_field = 'number'
    http_method_names = ('get', 'delete')

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)

    def get(self, request: Request, ch_id: str):
        company = get_object_or_404(Company, number=ch_id)
        response_data = {
            'letter_verification_code': company.verification_code,
            'company_email': company.email_address,
            'is_verification_letter_sent': company.is_verification_letter_sent
        }
        return Response(response_data)

    def delete(self, request: Request, ch_id: str):
        try:
            company = get_object_or_404(Company, number=ch_id)
            company.delete()
        except Http404:
            raise Http404()
        return Response(status=204)
