from django import forms
from mast_toolkit import models as mast
from mast_toolkit.consts import BenchmarkScope


# Select Organisation Only or Industry Benchmarking - 160326 Kathy
class SurveyCreateForm(forms.ModelForm):
    class Meta:
        model = mast.Survey
        fields = "__all__"
        widgets = {
            "qualitative": forms.RadioSelect,
            "include_data_used_or_created": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),
            "benchmark_scope": forms.RadioSelect,
        }


# Select Organisation Only or Industry Benchmarking - 160326 Kathy
class SurveyManageForm(forms.ModelForm):
    class Meta:
        model = mast.Survey
        fields = "__all__"
        widgets = {
            "qualitative": forms.RadioSelect,
            "include_data_used_or_created": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),
            "benchmark_scope": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Select Organisation Only or Industry Benchmarking - 160326 Kathy
        self.fields['benchmark_scope'].disabled = True
        self.fields['benchmark_scope'].help_text = "This can only be changed when the survey is first created."


class ResponseForm(forms.ModelForm):
    class Meta:
        model = mast.Response
        # fields = "__all__"
        exclude = ["response_date", "survey", "phase", "is_complete"]
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

            # Select Organisation Only or Industry Benchmarking - 160326 Kathy
            "seniority": forms.RadioSelect,
            "tools": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),

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
        # Select Organisation Only or Industry Benchmarking - 160326 Kathy
        self.fields['seniority'].choices = [
            c for c in self.fields['seniority'].choices if c[0] != ''
        ]
        self.fields['tools'].choices = [
            c for c in self.fields['tools'].choices if c[0] != ''
        ]
        # Make seniority, tasks, and industry mandatory - 160326 Kathy
        self.fields['seniority'].required = True
        self.fields['data_uses'].required = True
        if survey.benchmark_scope == BenchmarkScope.INDUSTRY_WIDE:
            self.fields['industry'].required = True


# --- Multi-step response forms - 160326 Kathy ---

class ResponseStep1Form(forms.ModelForm):
    """Step 1: Beliefs questions"""
    class Meta:
        model = mast.Response
        fields = [
            "beliefs_metadata_1", "beliefs_metadata_2",
            "beliefs_analysis_1", "beliefs_analysis_2",
            "beliefs_standards_1", "beliefs_standards_2",
            "beliefs_teamwork_1", "beliefs_teamwork_2",
        ]
        widgets = {
            "beliefs_metadata_1": forms.RadioSelect,
            "beliefs_analysis_1": forms.RadioSelect,
            "beliefs_standards_1": forms.RadioSelect,
            "beliefs_teamwork_1": forms.RadioSelect,
            "beliefs_metadata_2": forms.RadioSelect,
            "beliefs_analysis_2": forms.RadioSelect,
            "beliefs_standards_2": forms.RadioSelect,
            "beliefs_teamwork_2": forms.RadioSelect,
        }


class ResponseStep2Form(forms.ModelForm):
    """Step 2: Actions questions (IDEAL framework)"""
    class Meta:
        model = mast.Response
        fields = [
            "actions_inventory_1", "actions_inventory_2", "actions_inventory_qual",
            "actions_document_1", "actions_document_2", "actions_document_qual",
            "actions_endorse_1", "actions_endorse_2", "actions_endorse_qual",
            "actions_audit_1", "actions_audit_2", "actions_audit_qual",
            "actions_leadership_1", "actions_leadership_2", "actions_leadership_qual",
        ]
        widgets = {
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
        }


class ResponseStep3Form(forms.ModelForm):
    """Step 3: Role & Activities"""
    class Meta:
        model = mast.Response
        fields = [
            "email", "team", "industry", "seniority",
            "data_uses", "other_data_activity",
            "tools", "other_tool",
            "data_used_or_created",
        ]
        widgets = {
            "team": forms.Select(attrs={"class": "form-select"}),
            "data_used_or_created": forms.Textarea(attrs={"class": "form-control"}),
            "data_uses": forms.CheckboxSelectMultiple,
            "seniority": forms.RadioSelect,
            "tools": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop("survey")
        super().__init__(*args, **kwargs)
        self.fields['team'].queryset = self.fields['team'].queryset.filter(survey=survey)
        self.fields['seniority'].choices = [
            c for c in self.fields['seniority'].choices if c[0] != ''
        ]
        self.fields['tools'].choices = [
            c for c in self.fields['tools'].choices if c[0] != ''
        ]
        # Make seniority, tasks, and industry mandatory - 160326 Kathy
        self.fields['seniority'].required = True
        self.fields['data_uses'].required = True
        if survey.benchmark_scope == BenchmarkScope.INDUSTRY_WIDE:
            self.fields['industry'].required = True
