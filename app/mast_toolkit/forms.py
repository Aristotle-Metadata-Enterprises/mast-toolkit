from django import forms
from mast_toolkit import models as mast


class SurveyManageForm(forms.ModelForm):
    class Meta:
        model = mast.Survey
        fields = "__all__"
        widgets = {
            "qualitative": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),
        }


class ResponseForm(forms.ModelForm):
    class Meta:
        model = mast.Response
        # fields = "__all__"
        exclude = ["response_date", "survey", "phase"]
        widgets = {
            "beliefs_metadata_1": forms.RadioSelect,
            "beliefs_analysis_1": forms.RadioSelect,
            "beliefs_standards_1": forms.RadioSelect,
            "beliefs_teamwork_1": forms.RadioSelect,

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

            # "actions_inventory_qual
            # "actions_document_qual
            # "actions_endorse_qual
            # "actions_audit_qual
            # "actions_leadership_qual"
        }

