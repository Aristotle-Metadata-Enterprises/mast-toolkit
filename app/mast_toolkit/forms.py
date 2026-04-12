from django import forms
from mast_toolkit import models as mast
from mast_toolkit.consts import BenchmarkScope, ISICChoices


class SurveyCreateForm(forms.ModelForm):
    class Meta:
        model = mast.Survey
        fields = "__all__"
        widgets = {
            "qualitative": forms.RadioSelect,
            "include_data_used_or_created": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),
            "benchmark_scope": forms.RadioSelect,
            "use_custom_industries": forms.HiddenInput,
        }


class SurveyManageForm(forms.ModelForm):
    class Meta:
        model = mast.Survey
        fields = "__all__"
        widgets = {
            "qualitative": forms.RadioSelect,
            "include_data_used_or_created": forms.RadioSelect,
            "industry": forms.Select(attrs={"class": "form-select"}),
            "benchmark_scope": forms.RadioSelect,
            "use_custom_industries": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

            "seniority": forms.RadioSelect(attrs={"required": True}),
            "tools": forms.TextInput(attrs={"class": "form-control"}),
            "industry": forms.Select(attrs={"class": "form-select", "required": True}),

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
        self.fields['seniority'].choices = [
            c for c in self.fields['seniority'].choices if c[0] != ''
        ]
        self.fields['seniority'].required = True
        self.fields['data_uses'].required = True
        if survey.use_custom_industries and survey.custom_industries.exists():
            choices = [('', '---------')] + [(ci.name, ci.name) for ci in survey.custom_industries.all()]
        else:
            choices = [('', '---------')] + [(c.value, c.label) for c in ISICChoices]
        self.fields['industry'].choices = choices
        self.fields['industry'].widget.choices = choices
        if survey.benchmark_scope == BenchmarkScope.INDUSTRY_WIDE:
            self.fields['industry'].required = True


class ResponseStep1Form(forms.ModelForm):
    """Step 1: Beliefs questions"""
    class Meta:
        model = mast.Response
        fields = [
            "beliefs_metadata_1", "beliefs_metadata_2",
            "beliefs_analysis_1", "beliefs_analysis_2",
            "beliefs_standards_1", "beliefs_standards_2",
            "beliefs_teamwork_1", "beliefs_teamwork_2",
            "self_assess_value", "self_assess_trust", "self_assess_secure",
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
            "self_assess_value": forms.RadioSelect,
            "self_assess_trust": forms.RadioSelect,
            "self_assess_secure": forms.RadioSelect
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
            "tools",
            "data_used_or_created",
        ]
        widgets = {
            "team": forms.Select(attrs={"class": "form-select"}),
            "data_used_or_created": forms.Textarea(attrs={"class": "form-control"}),
            "data_uses": forms.CheckboxSelectMultiple,
            "seniority": forms.RadioSelect(attrs={"required": True}),
            "tools": forms.TextInput(attrs={"class": "form-control"}),
            "industry": forms.Select(attrs={"class": "form-select", "required": True}),
            
        }

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop("survey")
        super().__init__(*args, **kwargs)
        self.fields['team'].queryset = self.fields['team'].queryset.filter(survey=survey)
        self.fields['seniority'].choices = [
            c for c in self.fields['seniority'].choices if c[0] != ''
        ]
        self.fields['seniority'].required = True
        self.fields['data_uses'].required = True
        if survey.use_custom_industries and survey.custom_industries.exists():
            choices = [('', '---------')] + [(ci.name, ci.name) for ci in survey.custom_industries.all()]
        else:
            choices = [('', '---------')] + [(c.value, c.label) for c in ISICChoices]
        self.fields['industry'].choices = choices
        self.fields['industry'].widget.choices = choices
        if survey.benchmark_scope == BenchmarkScope.INDUSTRY_WIDE:
            self.fields['industry'].required = True
