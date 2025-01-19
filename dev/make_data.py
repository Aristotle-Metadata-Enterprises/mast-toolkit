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
    from mast_toolkit import models, consts

    survey,_ = models.Survey.objects.get_or_create(
        id=survey1_id,
        defaults=dict(
            share_link=survey1_share_id,
            title="Veridian Dynamics - Data Maturity Assessment",
            email="ted@veridiandynamics.com",
            organisation="Veridian Dynamics",
        )
    )

    business_units = [
        {'name': 'Admininstration', "weights": ['911001','331119','920000','111112', '352101','352101','352101','352101','352101']},
        {'name': 'IT', "weights": ['951103','951103','951103','951103', '123211','123211','631111','310001','127211']},
        {'name': 'Medical Research',  "weights": ['004790','004790','004790','144771', '113990','116990','3531110','3531110','333210']},
        {'name': 'Biomedical Research',  "weights": ['004790','004790','951103','144771', '113990','116990','3531110','3531110','123211']},
    ]
    business_unit_selection = [None]
    for i, unit in enumerate(business_units):
        business_unit = models.BusinessUnit.objects.get_or_create(
            survey=survey,
            order=i,
            name=unit['name']
        )[0]
        business_unit.weights = unit['weights']
        business_unit_selection.append(business_unit)

    def weighted(choices, weights):
        if weights is None:
            weights = "332110"
        opts = []
        selectable_values = [c[0] for c in choices]
        for val, weight in zip(selectable_values, weights):
            opts = opts + [val] * int(weight)
        return random.choice(opts)

    models.Response.objects.all().delete()
    for i in range(75):
        team = random.choice(business_unit_selection)
        if team is None:
            team_weights = [None]*9
        else:
            team_weights = team.weights
        obj = models.Response.objects.create(
            email = "test@test.com",
            team = team,
            phase = None,
            survey = survey,

            beliefs_metadata_1 = weighted(models.Likert.choices, team_weights[0]),
            beliefs_analysis_1 = weighted(models.Likert.choices, team_weights[1]),
            beliefs_standards_1 = weighted(models.Likert.choices, team_weights[2]),
            beliefs_teamwork_1 = weighted(models.Likert.choices, team_weights[3]),

            beliefs_metadata_2 = weighted(models.Likert.choices, team_weights[0]),
            beliefs_analysis_2 = weighted(models.Likert.choices, team_weights[1]),
            beliefs_standards_2 = weighted(models.Likert.choices, team_weights[2]),
            beliefs_teamwork_2 = weighted(models.Likert.choices, team_weights[3]),

            actions_inventory_1 = weighted(models.Response.actions_inventory_1.field.choices, team_weights[4]),
            actions_inventory_2 = weighted(models.Response.actions_inventory_2.field.choices, team_weights[4]),
            actions_inventory_qual = "",

            actions_document_1 = weighted(models.Response.actions_document_1.field.choices, team_weights[5]),
            actions_document_2 = weighted(models.Response.actions_document_2.field.choices, team_weights[5]),
            actions_document_qual = "",

            actions_endorse_1 = weighted(models.Response.actions_endorse_1.field.choices, team_weights[6]),
            actions_endorse_2 = weighted(models.Response.actions_endorse_2.field.choices, team_weights[6]),
            actions_endorse_qual = "",

            actions_audit_1 = weighted(models.Response.actions_audit_1.field.choices, team_weights[7]),
            actions_audit_2 = weighted(models.Response.actions_audit_2.field.choices, team_weights[7]),
            actions_audit_qual = "",

            actions_leadership_1 = weighted(models.Response.actions_leadership_1.field.choices, team_weights[8]),
            actions_leadership_2 = weighted(models.Response.actions_leadership_2.field.choices, team_weights[8]),
            actions_leadership_qual = "",
        )
        num_activities = random.randint(1, 6)
        activities = random.sample([a[0] for a in consts.ACTIVITY_TYPES], num_activities)
        obj.data_uses.set(models.ActivityType.objects.filter(code__in=activities))

        # We need to use update to bypass the django signal
        models.Response.objects.filter(pk=obj.pk).update(
            response_date = timezone.now() - datetime.timedelta(days=random.randint(0, 21))
        )

make_simple_survey()
make_complex_survey()