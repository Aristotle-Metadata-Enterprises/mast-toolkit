from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.db.models import Case, When, Value, IntegerField, Avg, F

import shortuuid
import uuid
import mast_toolkit.consts

import datetime
from django.db.models.functions import TruncDate
from django.db.models import Count


class Likert(models.IntegerChoices):
    DISAGREESTRONGLY = 1, _("Strongly Disagree")
    DISAGREE = 2, _("Disagree")
    NN = 3, _("Neither Agree nor Disagree")
    AGREE = 4, _("Agree")
    AGREESTRONGLY = 5, _("Strongly Agree")
    DONTKNOW = 9, _("Don't Know")

    @classmethod
    def labels(cls):
        return [str(choice[1]) for choice in cls.choices]

    @classmethod
    def display_labels_dk_first(cls):
        labels = [str(choice[1]) for choice in cls.choices]
        labels.insert(0, labels.pop(-1))
        return labels


def censor_dk_as_midpoint(field_name):
    return Case(
        When(**{field_name: Likert.DONTKNOW.value}, then=Value(1.5)),
        default=F(field_name),  # Default value if no conditions match
        output_field=models.FloatField()
    )

def CensoredAvg(field_name, default=0):
    return Avg(
        censor_dk_as_midpoint(field_name),
        default=default,
    )


class Survey(models.Model):
    id = models.CharField(primary_key=True, default=shortuuid.uuid, editable=False, max_length=256)
    share_link = models.CharField(default=shortuuid.uuid, editable=False, max_length=256)
    # report_link = models.CharField(default=shortuuid.uuid, editable=False, max_length=256)
    title = models.CharField(
        max_length=1024, verbose_name="Survey title",
        help_text="This is name of your maturity assessment and is shown to users when they fill in your assessment survey."
    )
    email = models.EmailField()
    organisation = models.CharField(max_length=2048,
        help_text="The name of your organisation. We collect this to let users know they are responding to the correct survey."
    )
    preamble = models.TextField(
        verbose_name="Introductory text",
        blank=True,
        help_text="This is a closing paragraph that is shown to respondents at the start of the assessment survey."
    )
    confirmation_message = models.TextField(
        blank=True,
        help_text="This is a closing paragraph shown to respondents after they have completed their survey."
    )
    qualitative = models.PositiveIntegerField(
        verbose_name="Include qualitative questions",
        choices=mast_toolkit.consts.Qualitative,
        default=mast_toolkit.consts.Qualitative.SHOW,
        help_text="If selected, we will ask additional questions for each of the 'I-D-E-A-L' behaviours that can be downloaded and analysed."
    )
    industry = models.CharField(
        max_length=1, null=True, choices=mast_toolkit.consts.ISICChoices, blank=True, default=None,
        help_text="We collect the industry of your organisation to provide you with industry comparables."
    )
    include_data_used_or_created = models.PositiveIntegerField(
        verbose_name="Ask respondents about data they use",
        choices=mast_toolkit.consts.DataUsed,
        default=mast_toolkit.consts.DataUsed.HIDE,
        help_text="If selected, we will ask additional questions for each of the 'I-D-E-A-L' behaviours that can be downloaded and analysed."
    )

    # size = ???
    # tools = ???
    # purpose = ???

    def get_absolute_url(self):
        return reverse("survey_dashboard", args=[self.id])

    @cached_property
    def response_count(self):
        return self.responses.all().count()


    @cached_property
    def metrics(self):
        return self.generate_basic_metrics()

    def generate_basic_metrics(self, team=mast_toolkit.consts.NO_TEAM_SELECTED, activity_type=mast_toolkit.consts.NO_ACTIVITY_SELECTED):
        qs = self.responses.all()

        if team != mast_toolkit.consts.NO_TEAM_SELECTED:
            # We check for False, as "None" as a team is a valid filter to find users who didn't select a team.
            qs = qs.filter(team=team)

        if activity_type is None:
            qs = qs.filter(data_uses__isnull=True)
        elif activity_type != mast_toolkit.consts.NO_ACTIVITY_SELECTED:
            # We check for False, as "None" as a team is a valid filter to find users who didn't select a team.
            qs = qs.filter(data_uses=activity_type)
        
        total_responses = qs.count()

        responses = qs.aggregate(

            Avg('beliefs_metadata_1', default=0),
            Avg('beliefs_analysis_1', default=0),
            Avg('beliefs_standards_1', default=0),
            Avg('beliefs_teamwork_1', default=0),
            
            Avg('beliefs_metadata_2', default=0),
            Avg('beliefs_analysis_2', default=0),
            Avg('beliefs_standards_2', default=0),
            Avg('beliefs_teamwork_2', default=0),
            
            Avg('actions_inventory_1', default=0),
            Avg('actions_inventory_2', default=0),
            Avg('actions_document_1', default=0),
            Avg('actions_document_2', default=0),
            Avg('actions_endorse_1', default=0),
            Avg('actions_endorse_2', default=0),
            Avg('actions_audit_1', default=0),
            Avg('actions_audit_2', default=0),
            Avg('actions_leadership_1', default=0),
            Avg('actions_leadership_2', default=0),

            beliefs_metadata_1_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_metadata_1'),
                default=0,
            ),
            beliefs_analysis_1_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_analysis_1'),
                default=0,
            ),
            beliefs_standards_1_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_standards_1'),
                default=0,
            ),
            beliefs_teamwork_1_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_teamwork_1'),
                default=0,
            ),
            beliefs_metadata_2_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_metadata_2'),
                default=0,
            ),
            beliefs_analysis_2_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_analysis_2'),
                default=0,
            ),
            beliefs_standards_2_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_standards_2'),
                default=0,
            ),
            beliefs_teamwork_2_dk__avg = Avg(
                censor_dk_as_midpoint('beliefs_teamwork_2'),
                default=0,
            ),

        )

        response_dates = self.responses.all().annotate(
            date=TruncDate('response_date')
        ).values('date').annotate(count=Count('date')).order_by('date')

        _metrics = {
            "OVERALL": {
                "total_responses": total_responses,
            },
            "MAST": {
                "metadata": (((responses['beliefs_metadata_1_dk__avg']+responses['beliefs_metadata_2_dk__avg'])/2)**2)/5,
                "analysis": (((responses['beliefs_analysis_1_dk__avg']+responses['beliefs_analysis_2_dk__avg'])/2)**2)/5,
                "standards": (((responses['beliefs_standards_1_dk__avg']+responses['beliefs_standards_2_dk__avg'])/2)**2)/5,
                "teamwork": (((responses['beliefs_teamwork_1_dk__avg']+responses['beliefs_teamwork_2_dk__avg'])/2)**2)/5,
            },
            "MAST_DEPTH": {
                "beliefs_metadata_1": responses['beliefs_metadata_1_dk__avg'],
                "beliefs_analysis_1": responses['beliefs_analysis_1_dk__avg'],
                "beliefs_standards_1": responses['beliefs_standards_1_dk__avg'],
                "beliefs_teamwork_1": responses['beliefs_teamwork_1_dk__avg'],
                "beliefs_metadata_2": responses['beliefs_metadata_2_dk__avg'],
                "beliefs_analysis_2": responses['beliefs_analysis_2_dk__avg'],
                "beliefs_standards_2": responses['beliefs_standards_2_dk__avg'],
                "beliefs_teamwork_2": responses['beliefs_teamwork_2_dk__avg'],
            },
            "IDEAL": {
                # Aggregates responses at the IDEAL level
                "inventory": (((responses['actions_inventory_1__avg']+responses['actions_inventory_2__avg'])/2)**2)/5,
                "document": (((responses['actions_document_1__avg']+responses['actions_document_2__avg'])/2)**2)/5,
                "endorse": (((responses['actions_endorse_1__avg']+responses['actions_endorse_2__avg'])/2)**2)/5,
                "audit": (((responses['actions_audit_1__avg']+responses['actions_audit_2__avg'])/2)**2)/5,
                "leadership": (((responses['actions_leadership_1__avg']+responses['actions_leadership_1__avg'])/2)**2)/5,
            },
            "IDEAL_DEPTH": {
                # Aggregates each response
                "actions_inventory_1": responses['actions_inventory_1__avg'],
                "actions_inventory_2": responses['actions_inventory_2__avg'],
                "actions_document_1": responses['actions_document_1__avg'],
                "actions_document_2": responses['actions_document_2__avg'],
                "actions_endorse_1": responses['actions_endorse_1__avg'],
                "actions_endorse_2": responses['actions_endorse_2__avg'],
                "actions_audit_1": responses['actions_audit_1__avg'],
                "actions_audit_2": responses['actions_audit_2__avg'],
                "actions_leadership_1": responses['actions_leadership_1__avg'],                
                "actions_leadership_2": responses['actions_leadership_2__avg'],                
            },
            "RECENT_RESPONSES": response_dates.filter(response_date__gt = datetime.datetime.now() - datetime.timedelta(days=14))
        }

        return _metrics

    @cached_property
    def report_metrics(self):
        return self.generate_report_metrics()

    def generate_report_metrics(self, team=False):
        qs = self.responses.all()
        total_count_of_responses = qs.count() or 1

        def likert_histogram_results(field):
            values = list(qs.values(field).annotate(count=Count(field)).order_by(field))
            data = {opt.value: 0 for opt in Likert}
            for v in values:
                data[v[field]] = v['count']
            print(data)
            values = [
                {field: value, 'count': count}
                for value, count in data.items()
            ]
            if values:
                # Move don't know from end, to start
                values.insert(0, values.pop(-1))
            return values
                
        def actions_histogram_results(field):
            # This gets the raw data from the db and annotates it with the response text
            values = dict(qs.values_list(field).annotate(count=Count(field)).order_by(field))
            # Pad max value to ensure histogram looks nice
            top_value = max(values.values()) * 1.1
            data = {
                choice[0]: {
                    'code': choice[0],
                    'label': choice[1],
                    'count': values.get(choice[0], 0),
                    'percent': int(values.get(choice[0], 0)/total_count_of_responses*100),
                    'percent_of_max': int(values.get(choice[0], 0)/top_value*100)
                }
                for choice in Response._meta.get_field(field).choices
            }
            
            return data

        _metrics = {}
        _metrics['beliefs_metadata_1'] = {
            "histogram": likert_histogram_results('beliefs_metadata_1'),
        }
        _metrics['beliefs_analysis_1'] = {
            "histogram": likert_histogram_results('beliefs_analysis_1')
        }
        _metrics['beliefs_standards_1'] = {
            "histogram": likert_histogram_results('beliefs_standards_1')
        }
        _metrics['beliefs_teamwork_1'] = {
            "histogram": likert_histogram_results('beliefs_teamwork_1')
        }

        _metrics['beliefs_metadata_2'] = {
            "histogram": likert_histogram_results('beliefs_metadata_2'),
        }
        _metrics['beliefs_analysis_2'] = {
            "histogram": likert_histogram_results('beliefs_analysis_2')
        }
        _metrics['beliefs_standards_2'] = {
            "histogram": likert_histogram_results('beliefs_standards_2')
        }
        _metrics['beliefs_teamwork_2'] = {
            "histogram": likert_histogram_results('beliefs_teamwork_2')
        }

        _metrics['actions_inventory_1'] = {
            "data": actions_histogram_results('actions_inventory_1'),
        }
        _metrics['actions_inventory_2'] = {
            "data": actions_histogram_results('actions_inventory_2'),
        }
        _metrics['actions_document_1'] = {
            "data": actions_histogram_results('actions_document_1'),
        }
        _metrics['actions_document_2'] = {
            "data": actions_histogram_results('actions_document_2'),
        }
        _metrics['actions_endorse_1'] = {
            "data": actions_histogram_results('actions_endorse_1'),
        }
        _metrics['actions_endorse_2'] = {
            "data": actions_histogram_results('actions_endorse_2'),
        }
        _metrics['actions_audit_1'] = {
            "data": actions_histogram_results('actions_audit_1'),
        }
        _metrics['actions_audit_2'] = {
            "data": actions_histogram_results('actions_audit_2'),
        }
        _metrics['actions_leadership_1'] = {
            "data": actions_histogram_results('actions_leadership_1'),
        }
        _metrics['actions_leadership_2'] = {
            "data": actions_histogram_results('actions_leadership_2'),
        }

        return _metrics


class BusinessUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="teams")
    order = models.PositiveIntegerField()
    name = models.CharField(max_length=2048)
    # detail = models.CharField(max_length=2048)

    def __str__(self):
        return self.name


class Wave(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=2048)
    # open_date = models.DateField(null=True, auto_now_add=True)
    close_date = models.DateField(null=True, help_text="When do you want to stop recieving responses? Leave blank to keep the phase open indefinitely.")
    expected_responses = models.PositiveIntegerField(help_text="What is the expected number of responses you expect to get in this phase?")


class ActivityType(models.Model):
    code = models.CharField(primary_key=True, max_length=1)
    activity = models.CharField(max_length=256)

    def __str__(self):
        return self.activity


class Response(models.Model):
    id = models.CharField(primary_key=True, default=shortuuid.uuid, editable=False, max_length=256)
    email = models.EmailField(blank=True)
    team = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, blank=True, null=True, related_name="responses")
    phase = models.ForeignKey(Wave, null=True, on_delete=models.CASCADE, blank=True, related_name="responses")
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    response_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-response_date']

    data_uses = models.ManyToManyField(
        ActivityType,
        verbose_name="What activities do you perform with data as part of your role in the organisation"
    )
    other_data_activity = models.CharField(blank=True, max_length=2048)
    data_used_or_created = models.TextField(blank=True,
        verbose_name="What data do you use or create as part of your role in the organisation?"
    )

    beliefs_metadata_1 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="My organisation understands how data documentation supports the delivery of core functions and outcomes.",
        choices=Likert
    )
    beliefs_metadata_2 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="It is easy for me to find data I need for my role.",
        choices=Likert
    )
    beliefs_analysis_1 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="My organisation documents why data is collected, along with what is stored.",
        choices=Likert
    )
    beliefs_analysis_2 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="It is easy for me to find documentation that describes what data means.",
        choices=Likert
    )
    beliefs_standards_1 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="My organisation has a consistent approach to data documentation.",
        choices=Likert
    )
    beliefs_standards_2 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="It is easy for me to find, link and compare related data using common terms.",
        choices=Likert
    )
    beliefs_teamwork_1 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="Teams in my organisation are encouraged to create, review and share documentation for their data assets.",
        choices=Likert
    )
    beliefs_teamwork_2 = models.PositiveIntegerField(max_length=2, blank=False, default=None,
        verbose_name="It is easy is it for me to talk about data with others across my organisation.",
        choices=Likert
    )

    actions_inventory_1 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="How do you most commonly discover other data assets in the organisation?",
        choices={
            1: "I don't do this as part of my current role",
            2: "I will speak directly to a person who I think knows about this data",
            3: "I have access to a list of data assets managed by my team, but I am not aware of data outside my team",
            4: "I have access to a list of data assets that is shared by members of my organisation",
            5: "I can search for data within a central data inventory that returns results based on my needs and permissions",
        },
        help_text="If more than one is applicable, select the activity you most commonly perform."
    )
    actions_inventory_2 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="How do you most commonly record the existence of data assets within your team?",
        choices={
            1: "I don't do this as part of my current role",
            2: "I do not have a tool for recording documentation about data assets made within my team",
            3: "I use ad hoc systems like Excel or Word etc.",
            4: "I use generalised documentation systems such as SharePoint or Confluence",
            5: "I use specialised data cataloguing tools for documenting data assets",
        },
        help_text="If more than one is applicable, select the activity you most commonly perform."
    )

    actions_inventory_qual = models.TextField(
        verbose_name="(Optional) Please include a list of processes, systems or tools you use to find data in your organisation. If this includes emailing people you know, you can just include 'email' as one of your processes.",
        blank=True
    )

    actions_document_1 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="What information do you usually record for data assets created within your team?",
        choices={
            1: "I don't do this as part of my current role",
            2: "I do not document data assets at this point in time",
            3: "I document data based on my own needs or requirements",
            4: "I follow processes my team has developed for documenting data",
            5: "I follow organisational standards for recording information about data assets",
        },
        help_text="If more than one is applicable, select the activity you most commonly perform."
    )
    actions_document_2 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="What information do you or your team commonly record about fields within a data asset, such as describing columns in a spreadsheet or database table?",
        choices={
            1: "I don't do this as part of my current role",
            2: "I do not record information at this level about our data",
            3: "I record the names and descriptions of columns",
            4: "I record the names, descriptions, and any codes or data types for each column",
            5: "I record the names, descriptions and codes for each column, and include links to common data glossary defintions",
        },
        help_text="If more than one is applicable, select the activity you most commonly perform."
    )
    actions_document_qual = models.TextField(
        verbose_name="(Optional) Please include a list of systems or tools you use to document data in your organisation. If this includes tools like Word, Excel, Sharepoint or other similar knowledge management tools, include these as tools you use.",
        blank=True
    )

    actions_endorse_1 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="Who is responsible for reviewing data documentation in your team or organisation?",
        choices={
            1: "I don't do this as part of my current role",
            2: "Data documentation does not get reviewed at this point in time",
            3: "Data documentation is reviewed on an informal basis by my peers",
            4: "My team has a process for reviewing data documentation",
            5: "Data governance team(s) within the organisation review data documentation",
        },
        help_text="If more than one is applicable, select the answer that matches you usual routine."
    )
    actions_endorse_2 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="How can you find out who has signed off on approval/review of data assets in the organisation?",
        choices={
            1: "I don't do this as part of my current role",
            2: "I do not have access to documentation from other teams",
            3: "I can view information about data assets, but am unable to see approval documentation",
            4: "I can view approval processes for data documentation within my team",
            5: "Approval processes for all data I use is documented in a formal register in the organisation",
        }
    )
    actions_endorse_qual = models.TextField(
        verbose_name="(Optional) Please tell us about business areas you engage with to assist with publication of data documentation, and any internal or external stakeholders who you think would find your data documentation useful.",
        blank=True
    )

    actions_audit_1 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="How do you manage commonly referenced data terms?",
        choices={
            1: "I don't do this as part of my current role",
            2: "I do not manage common data terms at this point in time",
            3: "I use methods such as copying and pasting existing definitions from existing records for consistency when documenting new data assets",
            4: "I refer to a list of data terms that my team manages internally",
            5: "I use data terms from a governed central system that records and links these terms to data assets",
        }
    )
    actions_audit_2 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="How do you reuse common data terms from a data glossary?",
        choices={
            1: "I don't do this as part of my current role",
            2: "I do not use a data glossary as part of my work ",
            3: "I use methods such as copying and pasting definitions from a data glossary",
            4: "I copy and paste definitions and include a link to the source, such as a document or data glossary web page",
            5: "I reference glossary terms from a central source that provides links between data assets and data terms",
        }
    )
    actions_audit_qual = models.TextField(
        verbose_name="(Optional) Please tell us about terms you use commonly in your work that may not be understood by users of your data, or may not be used the same way as another team. Examples could include terms like supplier, staff member or identifier.",
        blank=True
    )

    actions_leadership_1 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="Are you aware of policies for managing data assets within your organisation?",
        choices={
            1: "I do not manage data in my role, and am not impacted by data policies",
            2: "I am not aware of policies for managing data assets at the present time",
            3: "I am aware of internal policies my team has developed for managing data assets",
            4: "I am aware of policies for managing data assets, but am not aware of how they relate to my role",
            5: "I am aware of our organisation's data governance and data management policies, and my responsiblity for data safety",
        }
    )
    actions_leadership_2 = models.PositiveIntegerField(blank=False, default=None,
        verbose_name="How does your organisation's leadership promote metadata adoption?",
        choices={
            1: "I do not use metadata in my role",
            2: "I am not aware of metadata promotion within the organisation at the present time",
            3: "Metadata is promoted within my team but not at an organisational level",
            4: "Metadata is promoted internally e.g. through the organisation’s intranet",
            5: "Metadata is promoted both internally and externally, e.g. in the annual report or on our website",
        }
    )
    actions_leadership_qual = models.TextField(
        verbose_name="(Optional) Please tell us about policies around data use and access that impact you in your role.",
        blank=True
    )
