from rest_framework import serializers

from company.models import Company
from enrolment import models


class CompanyEnrolmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='name')
    company_number = serializers.CharField(source='number')
    contact_email_address = serializers.EmailField(source='email_address')

    class Meta:
        model = Company
        fields = [
            'export_status',
            'company_name',
            'company_number',
            'contact_email_address',
        ]

    def create(self, validated_data):
        queryset = models.PreVerifiedCompany.objects.filter(
            company_number=validated_data['number'],
            email_address=validated_data['email_address'],
            is_active=True
        )
        validated_data['verified_with_trade_association'] = queryset.exists()
        company = super().create(validated_data)
        queryset.update(is_active=False)
        return company
