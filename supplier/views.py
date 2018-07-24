from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from django.http import Http404

from core import authentication
from core.permissions import IsAuthenticatedSSO
from core.views import CSVDumpAPIView
from supplier import gecko, serializers, permissions
from supplier.models import Supplier
from notifications import notifications


class SupplierRetrieveExternalAPIView(APIView):
    serializer_class = serializers.ExternalSupplierSerializer
    authentication_classes = [
        authentication.Oauth2AuthenticationSSO,
        authentication.SessionAuthenticationSSO,
    ]

    def get(self, request):
        if not self.request.user.supplier:
            raise Http404()
        serializer = self.serializer_class(request.user.supplier)
        return Response(serializer.data)


class SupplierSSOListExternalAPIView(ListAPIView):
    queryset = Supplier.objects.all()
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # normally DRF loops over the queryset and calls the serializer on each
        # supplier- which is much less performant than calling `values_list`
        sso_ids = self.queryset.values_list('sso_id', flat=True)
        return Response(data=sso_ids)


class SupplierRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = serializers.SupplierSerializer

    def get_object(self):
        if not self.request.user.supplier:
            raise Http404()
        return self.request.user.supplier


class GeckoTotalRegisteredSuppliersView(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (authentication.GeckoBasicAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ("get", )

    def get(self, request, format=None):
        return Response(gecko.total_registered_suppliers())


class UnsubscribeSupplierAPIView(APIView):

    http_method_names = ("post", )

    def post(self, request, *args, **kwargs):
        """Unsubscribes supplier from notifications"""
        supplier = self.request.user.supplier
        supplier.unsubscribed = True
        supplier.save()
        notifications.supplier_unsubscribed(supplier=supplier)
        return Response(
            data={
                "status_code": status.HTTP_200_OK,
                "detail": "Supplier unsubscribed"
            },
            status=status.HTTP_200_OK,
        )


class CompanyCollboratorsListView(ListAPIView):
    permission_classes = [
        IsAuthenticatedSSO,
        permissions.IsCompanyProfileOwner
    ]
    serializer_class = serializers.SupplierSerializer

    def get_queryset(self):
        return Supplier.objects.filter(
            company_id=self.request.user.supplier.company_id,
            is_company_owner=False
        )


class SupplierCSVDownloadAPIView(CSVDumpAPIView):
    bucket = settings.CSV_DUMP_BUCKET_NAME
    key = settings.SUPPLIERS_CSV_FILE_NAME
    filename = settings.SUPPLIERS_CSV_FILE_NAME
