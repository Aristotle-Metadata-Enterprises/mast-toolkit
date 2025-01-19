from django import forms
from mast_toolkit import models as mast


class SurveyManageForm(forms.ModelForm):
    class Meta:
        model = mast.Survey
        fields = "__all__"
        widgets = {
            "qualitative": forms.RadioSelect,
            "include_data_used_or_created": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),
        }


class ResponseForm(forms.ModelForm):
    class Meta:
        model = mast.Response
        # fields = "__all__"
        exclude = ["response_date", "survey", "phase"]
        widgets = {
            "team": forms.Select(attrs={"class": "form-select"}),
            "other_data_activity": forms.Select(attrs={"class": "form-control"}),
            "data_used_or_created": forms.Textarea(attrs={"class": "form-control"}),

            "beliefs_metadata_1": forms.RadioSelect,
            "beliefs_analysis_1": forms.RadioSelect,
            "beliefs_standards_1": forms.RadioSelect,
            "beliefs_teamwork_1": forms.RadioSelect,

            "beliefs_metadata_2": forms.RadioSelect,
            "beliefs_analysis_2": forms.RadioSelect,
            "beliefs_standards_2": forms.RadioSelect,
            "beliefs_teamwork_2": forms.RadioSelect,

            "actions_inventory_1": forms.RadioSelect,
            "actions_inventory_2": forms.RadioSelect,

            "actions_document_1": forms.RadioSelect,
            "actions_document_2": forms.RadioSelect,

            "actions_endorse_1": forms.RadioSelect,
            "actions_endorse_2": forms.RadioSelect,

            "actions_audit_1": forms.RadioSelect,
            "actions_audit_2": forms.RadioSelect,

            "actions_leadership_1": forms.RadioSelect,
            "actions_leadership_2": forms.RadioSelect,

            "data_uses": forms.CheckboxSelectMultiple,

            # "actions_inventory_qual
            # "actions_document_qual
            # "actions_endorse_qual
            # "actions_audit_qual
            # "actions_leadership_qual"
        }

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop("survey")
        super().__init__(*args, **kwargs)
        self.fields['team'].queryset = self.fields['team'].queryset.filter(survey=survey)
