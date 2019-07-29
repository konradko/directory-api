from directory_constants import company_types

from django.core.management.base import BaseCommand

from company import helpers, models


class Command(BaseCommand):
    help = 'Retrieves company status from companies house'

    def handle(self, *args, **options):
        queryset = models.Company.objects.filter(
            company_type=company_types.COMPANIES_HOUSE
        )
        failed = 0
        succeded = 0
        for company in queryset:
            try:
                profile = helpers.get_companies_house_profile(company.number)
                if profile.get('company_status'):
                    company.companies_house_company_status = profile.get('company_status')
                else:
                    company.companies_house_company_status = ''
                company.save()
                message = f'Company {company.name} updated'
                self.stdout.write(self.style.SUCCESS(message))
                succeded += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
                failed += 1
        self.stdout.write(self.style.SUCCESS(f'{succeded} companies updated'))
        self.stdout.write(self.style.WARNING(f'{failed} companies failed'))
