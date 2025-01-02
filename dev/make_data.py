import os
import django
from django.db import transaction
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()

# These were generated with:
# python -c"import shortuuid as s; print(s.uuid)"
survey1_id="WRESR57Pf6jfoQGomUoQ79"
survey1_share_id="TdBvsRgUwiTSS8dZbhHQF4"
survey2_id="DpMxJpnim6BDgeQU5LJebT"
survey2_share_id="dWwnxGTLriZALTRbkRt7Qg"


def make_simple_survey():
    from mast_toolkit import models

    survey,_ = models.Survey.objects.get_or_create(
        id=survey2_id,
        defaults=dict(
            share_link=survey2_share_id,
            title="Imcompleted Data Maturity Assessment",
            email="james@stjames.hospital",
            organisation="St. James Hospital",
        )
    )


def make_complex_survey():
    from mast_toolkit import models

    survey,_ = models.Survey.objects.get_or_create(
        id=survey1_id,
        defaults=dict(
            share_link=survey1_share_id,
            title="Project Uplift - Data Maturity Assessment",
            email="james@stjames.hospital",
            organisation="St. James Hospital",
        )
    )

    business_units = ['Admininstration', 'IT', 'Medical Research']
    business_unit_selection = [None]
    for i, unit in enumerate(business_units):
        business_unit_selection.append(
            models.BusinessUnit.objects.get_or_create(
                survey=survey,
                order=i,
                name=unit
            )[0]
        )

    models.Response.objects.all().delete()
    for i in range(50):
        
        obj = models.Response.objects.create(
            email = "test@test.com",
            team = random.choice(business_unit_selection),
            phase = None,
            survey = survey,

            beliefs_metadata_1 = random.choice(models.Response.beliefs_metadata_1.field.choices)[0],
            beliefs_analysis_1 = random.choice(models.Response.beliefs_metadata_1.field.choices)[0],
            beliefs_standards_1 = random.choice(models.Response.beliefs_standards_1.field.choices)[0],
            beliefs_teamwork_1 = random.choice(models.Response.beliefs_teamwork_1.field.choices)[0],

            actions_inventory_1 = random.choice(models.Response.actions_inventory_1.field.choices)[0],
            actions_inventory_2 = random.choice(models.Response.actions_inventory_2.field.choices)[0],
            actions_inventory_qual = "",

            actions_document_1 = random.choice(models.Response.actions_document_1.field.choices)[0],
            actions_document_2 = random.choice(models.Response.actions_document_2.field.choices)[0],
            actions_document_qual = "",

            actions_endorse_1 = random.choice(models.Response.actions_endorse_1.field.choices)[0],
            actions_endorse_2 = random.choice(models.Response.actions_endorse_2.field.choices)[0],
            actions_endorse_qual = "",

            actions_audit_1 = random.choice(models.Response.actions_audit_1.field.choices)[0],
            actions_audit_2 = random.choice(models.Response.actions_audit_2.field.choices)[0],
            actions_audit_qual = "",

            actions_leadership_1 = random.choice(models.Response.actions_leadership_1.field.choices)[0],
            actions_leadership_2 = random.choice(models.Response.actions_leadership_2.field.choices)[0],
            actions_leadership_qual = "",
        )
        models.Response.objects.filter(pk=obj.pk).update(
            response_date = timezone.now() - datetime.timedelta(days=random.randint(0, 14))
        )

make_simple_survey()
make_complex_survey()