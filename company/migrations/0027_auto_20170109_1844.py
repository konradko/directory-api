# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-01-09 18:44
from __future__ import unicode_literals

import company.helpers
import directory_validators.enrolment
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0026_auto_20170105_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='employees',
            field=models.CharField(blank=True, choices=[('', 'Please select'), ('1-10', '1-10'), ('11-50', '11-50'), ('51-200', '51-200'), ('201-500', '201-500'), ('501-1000', '501-1,000'), ('1001-10000', '1,001-10,000'), ('10001+', '10,001+')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='company',
            name='export_status',
            field=models.CharField(choices=[('', ''), ('YES', 'Yes, in the last year.'), ('ONE_TWO_YEARS_AGO', 'Yes, 1-2 years ago.'), ('OVER_TWO_YEARS_AGO', 'Yes, over 2 years ago.'), ('NOT_YET', 'Not yet.'), ('NO_INTENTION', 'No, and we have no intention to.')], max_length=20, validators=[directory_validators.enrolment.export_status_intention]),
        ),
        migrations.AlterField(
            model_name='companycasestudy',
            name='image_one_caption',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='companycasestudy',
            name='image_two',
            field=models.FileField(blank=True, default='', upload_to=company.helpers.PathAndRename(sub_path='/supplier_case_study')),
        ),
        migrations.AlterField(
            model_name='companycasestudy',
            name='sector',
            field=models.CharField(choices=[('', ''), ('AEROSPACE', 'Aerospace'), ('AGRICULTURE_HORTICULTURE_AND_FISHERIES', 'Agriculture, Horticulture and Fisheries'), ('AIRPORTS', 'Airports'), ('AUTOMOTIVE', 'Automotive'), ('BIOTECHNOLOGY_AND_PHARMACEUTICALS', 'Biotechnology and Pharmaceuticals'), ('BUSINESS_AND_CONSUMER_SERVICES', 'Business and Consumer Services'), ('CHEMICALS', 'Chemicals'), ('CLOTHING_FOOTWEAR_AND_FASHION', 'Clothing, Footwear and Fashion'), ('COMMUNICATIONS', 'Communications'), ('CONSTRUCTION', 'Construction'), ('CREATIVE_AND_MEDIA', 'Creative and Media'), ('DEFENCE', 'Defence'), ('EDUCATION_AND_TRAINING', 'Education and Training'), ('ELECTRONICS_AND_IT_HARDWARE', 'Electronics and IT Hardware'), ('ENVIRONMENT', 'Environment'), ('FINANCIAL_AND_PROFESSIONAL_SERVICES', 'Financial and Professional Services'), ('FOOD_AND_DRINK', 'Food and Drink'), ('GIFTWARE_JEWELLERY_AND_TABLEWARE', 'Giftware, Jewellery and Tableware'), ('GLOBAL_SPORTS_INFRASTRUCTURE', 'Global Sports Infrastructure'), ('HEALTHCARE_AND_MEDICAL', 'Healthcare and Medical'), ('HOUSEHOLD_GOODS_FURNITURE_AND_FURNISHINGS', 'Household Goods, Furniture and Furnishings'), ('LEISURE_AND_TOURISM', 'Leisure and Tourism'), ('MARINE', 'Marine'), ('MECHANICAL_ELECTRICAL_AND_PROCESS_ENGINEERING', 'Mechanical Electrical and Process Engineering'), ('METALLURGICAL_PROCESS_PLANT', 'Metallurgical Process Plant'), ('METALS_MINERALS_AND_MATERIALS', 'Metals, Minerals and Materials'), ('MINING', 'Mining'), ('OIL_AND_GAS', 'Oil and Gas'), ('PORTS_AND_LOGISTICS', 'Ports and Logistics'), ('POWER', 'Power'), ('RAILWAYS', 'Railways'), ('RENEWABLE_ENERGY', 'Renewable Energy'), ('RETAIL_AND_LUXURY', 'Retail and Luxury'), ('SECURITY', 'Security'), ('SOFTWARE_AND_COMPUTER_SERVICES', 'Software and Computer Services'), ('TEXTILES_INTERIOR_TEXTILES_AND_CARPETS', 'Textiles, Interior Textiles and Carpets'), ('WATER', 'Water')], max_length=100),
        ),
    ]
