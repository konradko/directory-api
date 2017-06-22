from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction

from enrolment import models, serializers
from supplier.serializers import SupplierSerializer


class EnrolmentCreateAPIView(APIView):

    http_method_names = ("post", )
    company_serializer_class = serializers.CompanyEnrolmentSerializer
    supplier_serializer_class = SupplierSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        company_serializer = self.company_serializer_class(data=request.data)
        company_serializer.is_valid(raise_exception=True)
        company = company_serializer.save()

        supplier_serializer = self.supplier_serializer_class(
            data={'company': company.id, **request.data}
        )
        supplier_serializer.is_valid(raise_exception=True)
        supplier_serializer.save()

        signup_codes = models.TrustedSourceSignupCode.objects.filter(
            company_number=company.number
        )
        signup_codes.update(is_active=False)

        return Response(status=status.HTTP_201_CREATED)


class TrustedSourceSignupCodeRetrieveView(RetrieveAPIView):
    http_method_names = ("get", )
    queryset = models.TrustedSourceSignupCode.objects.filter(is_active=True)
    serializer_class = serializers.TrustedSourceSignupCodeSerializer
    lookup_field = 'code'
