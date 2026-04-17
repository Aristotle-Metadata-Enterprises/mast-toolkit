from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView, TemplateView
from django.views import View
from django.http import HttpResponse
from mast_toolkit import models as mast
import mast_toolkit.forms
import mast_toolkit.consts
import datetime
import csv
from django.db.models import Count
from django import forms
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

import  plotly.express      as      px
from    plotly.offline      import  plot
from    plotly.graph_objs   import  Figure
import plotly.graph_objects as go
import pandas as pd


class ResponseBase:
    @cached_property
    def survey(self):
        return get_object_or_404(mast.Survey, share_link=self.kwargs['survey_pk'])

    def get_context_data(self, **kwargs):
        kwargs['survey'] = self.survey
        kwargs['default_texts'] = {
            'preamble': mast_toolkit.consts.DEFAULT_SURVEY_PREAMBLE,
            'confirmation': mast_toolkit.consts.DEFAULT_SURVEY_CONFIRMATION_HTML,
        }
        return super().get_context_data(**kwargs)


class ResponseCreateView(ResponseBase, CreateView):
    model = mast.Response
    form_class = mast_toolkit.forms.ResponseForm
    template_name = "mast/response/create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['survey'] = self.survey
        return kwargs

    def form_valid(self, form):
        form.instance.survey = self.survey
        form.instance.phase = None
        # form.instance.team = None
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('survey_respond_thanks', args=[self.survey.share_link])

    def get_context_data(self, **kwargs):
        kwargs['survey'] = self.survey
        kwargs['has_teams'] = self.survey.teams.all().exists()
        kwargs['show_qualitative'] = self.survey.qualitative == mast_toolkit.consts.Qualitative.SHOW
        kwargs['show_data_used_field'] = self.survey.include_data_used_or_created == mast_toolkit.consts.DataUsed.SHOW
        kwargs['is_organisation_only'] = self.survey.benchmark_scope == mast_toolkit.consts.BenchmarkScope.ORGANISATION_ONLY
        kwargs['is_industry_wide'] = self.survey.benchmark_scope == mast_toolkit.consts.BenchmarkScope.INDUSTRY_WIDE
        return super().get_context_data(**kwargs)


class ResponseStep1View(ResponseBase, View):
    """Step 1: Beliefs - creates a new Response and saves beliefs data."""
    template_name = "mast/response/step1.html"

    def get(self, request, *args, **kwargs):
        form = mast_toolkit.forms.ResponseStep1Form()
        return render(request, self.template_name, self._context(form))

    def post(self, request, *args, **kwargs):
        form = mast_toolkit.forms.ResponseStep1Form(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.survey = self.survey
            response.is_complete = False
            response.save()
            return redirect('survey_respond_step2', survey_pk=self.survey.share_link, response_pk=response.pk)
        return render(request, self.template_name, self._context(form))

    def _context(self, form):
        return {
            'form': form,
            'survey': self.survey,
            'step': 1,
        }


class ResponseStep2View(ResponseBase, View):
    """Step 2: Actions - updates existing Response with actions data."""
    template_name = "mast/response/step2.html"

    def get_response_obj(self):
        return get_object_or_404(mast.Response, pk=self.kwargs['response_pk'], survey=self.survey, is_complete=False)

    def get(self, request, *args, **kwargs):
        response_obj = self.get_response_obj()
        form = mast_toolkit.forms.ResponseStep2Form(instance=response_obj)
        return render(request, self.template_name, self._context(form))

    def post(self, request, *args, **kwargs):
        response_obj = self.get_response_obj()
        form = mast_toolkit.forms.ResponseStep2Form(request.POST, instance=response_obj)
        if form.is_valid():
            form.save()
            return redirect('survey_respond_step3', survey_pk=self.survey.share_link, response_pk=response_obj.pk)
        return render(request, self.template_name, self._context(form))

    def _context(self, form):
        return {
            'form': form,
            'survey': self.survey,
            'step': 2,
            'show_qualitative': self.survey.qualitative == mast_toolkit.consts.Qualitative.SHOW,
        }


class ResponseStep3View(ResponseBase, View):
    """Step 3: Role & Activities - updates Response and marks complete."""
    template_name = "mast/response/step3.html"

    def get_response_obj(self):
        return get_object_or_404(mast.Response, pk=self.kwargs['response_pk'], survey=self.survey, is_complete=False)

    def get(self, request, *args, **kwargs):
        response_obj = self.get_response_obj()
        form = mast_toolkit.forms.ResponseStep3Form(instance=response_obj, survey=self.survey)
        return render(request, self.template_name, self._context(form))

    def post(self, request, *args, **kwargs):
        response_obj = self.get_response_obj()
        form = mast_toolkit.forms.ResponseStep3Form(request.POST, instance=response_obj, survey=self.survey)
        if form.is_valid():
            response_obj = form.save(commit=False)
            response_obj.is_complete = True
            response_obj.save()
            form.save_m2m()
            return redirect('survey_respond_thanks', survey_pk=self.survey.share_link)
        return render(request, self.template_name, self._context(form))

    def _context(self, form):
        return {
            'form': form,
            'survey': self.survey,
            'step': 3,
            'has_teams': self.survey.teams.all().exists(),
            'is_organisation_only': self.survey.benchmark_scope == mast_toolkit.consts.BenchmarkScope.ORGANISATION_ONLY,
            'is_industry_wide': self.survey.benchmark_scope == mast_toolkit.consts.BenchmarkScope.INDUSTRY_WIDE,
            'show_data_used_field': self.survey.include_data_used_or_created == mast_toolkit.consts.DataUsed.SHOW,
        }


class ResponseThanksView(ResponseBase, TemplateView):
    template_name = "mast/response/thanks.html"


class SurveyCreateMixin:
    def get_context_data(self, **kwargs):
        kwargs['qualitative_questions'] = [
            field.verbose_name
            for field in mast.Response._meta.fields
            if field.name.endswith('_qual')
        ]
        kwargs['data_uses_question'] = mast.Response._meta.get_field('data_used_or_created').verbose_name
        kwargs['default_texts'] = {
            'preamble': mast_toolkit.consts.DEFAULT_SURVEY_PREAMBLE,
            'confirmation': mast_toolkit.consts.DEFAULT_SURVEY_CONFIRMATION_HTML,
        }
        kwargs.setdefault('existing_custom_industries', [])
        return super().get_context_data(**kwargs)


class SurveyCreateView(SurveyCreateMixin, CreateView):
    model = mast.Survey
    template_name = "mast/create_survey.html"
    form_class = mast_toolkit.forms.SurveyCreateForm

    def form_valid(self, form):
        response = super().form_valid(form)
        custom_industries = self.request.POST.getlist('custom_industries')
        for name in custom_industries:
            name = name.strip()
            if name:
                mast.CustomIndustry.objects.create(survey=self.object, name=name)
        return response


class DashboardMixin:
    def get_context_data(self, **kwargs):
        kwargs['active_dashboard_tab'] = self.active_dashboard_tab
        kwargs['survey_pk'] = self.kwargs['survey_pk']
        kwargs['survey'] = self.survey
        return super().get_context_data(**kwargs)

    @cached_property
    def survey(self):
        return get_object_or_404(mast.Survey, pk=self.kwargs['survey_pk'])


IDEAL_LABELS = [
            'Investigate & Inventory<br>',
            'Document <br>Data & Metadata',
            'Endorse & Publish',
            'Audit & Harmonise',
            'Leadership & <br> Long-term strategy '
        ]


def ideal_polar_plot(metrics):
    df = pd.DataFrame(
        dict(
            r=list(metrics['IDEAL'].values()),
            theta=IDEAL_LABELS,
        )
    )
    fig = px.line_polar(
        df, r='r', theta='theta', line_close=True,
        range_r=[0,5],
    )
    fig.update_polars(dict(
        radialaxis=dict(
            angle=90,
            tickangle=90, # for the axis ticks to stay horizontal 
        )
    ))
    fig.update_layout(showlegend=False)
    return fig


def mast_bar_plot(metrics, name="Organisation"):
    bar_plot = Figure(
        data=[go.Bar(
            x = list(metrics['MAST'].keys()), 
            y = list(metrics['MAST'].values()),
            textposition = 'auto',
            name=name
            )
        ]
    )
    bar_plot.update_layout(yaxis_range=[0, 5])
    bar_plot.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
        ),
        margin=dict(t=10, b=50, l=10, r=10)
    )

    return bar_plot




class SurveyUpdateView(DashboardMixin, SurveyCreateMixin, UpdateView):
    model = mast.Survey
    template_name = "mast/dashboard/update.html"
    active_dashboard_tab = "edit"
    pk_url_kwarg = 'survey_pk'
    form_class = mast_toolkit.forms.SurveyManageForm

    def get_context_data(self, **kwargs):
        kwargs['is_organisation_only'] = self.survey.benchmark_scope == mast_toolkit.consts.BenchmarkScope.ORGANISATION_ONLY
        kwargs['is_industry_wide'] = self.survey.benchmark_scope == mast_toolkit.consts.BenchmarkScope.INDUSTRY_WIDE
        kwargs['existing_custom_industries'] = self.survey.custom_industries.all()
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.custom_industries.all().delete()
        custom_industries = self.request.POST.getlist('custom_industries')
        for name in custom_industries:
            name = name.strip()
            if name:
                mast.CustomIndustry.objects.create(survey=self.object, name=name)
        return response

    def get_success_url(self):
        return reverse('survey_manage', args=[self.survey.pk])


class SurveyDetailView(DashboardMixin, DetailView):
    model = mast.Survey
    template_name = "mast/dashboard/detail.html"
    active_dashboard_tab = "dashboard"
    pk_url_kwarg = 'survey_pk'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        survey = self.get_object()

        context['plot'] = plot(mast_bar_plot(survey.metrics), output_type="div", include_plotlyjs=False)
        context['radar'] = plot(ideal_polar_plot(survey.metrics), output_type="div", include_plotlyjs=False)

        agg_dates = {
            i['date']: i['count']
            for i in survey.metrics['RECENT_RESPONSES'].filter(response_date__gt = datetime.datetime.now() - datetime.timedelta(days=14))
        }

        recent_responses = Figure(
            data=[go.Line(
                x = list(agg_dates.keys()), 
                y = list(agg_dates.values()),
                # textposition = 'auto',
                )
            ]
        )
        context['recent_responses'] = plot(recent_responses, output_type="div", include_plotlyjs=False)
        context['recent_responses_data'] = agg_dates
        context['metrics'] = survey.metrics

        return context


class SurveyDeleteView(DashboardMixin, DeleteView):
    model = mast.Survey
    template_name = "mast/dashboard/delete.html"
    active_dashboard_tab = "delete"
    pk_url_kwarg = 'survey_pk'
    success_url = reverse_lazy('survey_deleted_confirmation')


class SurveyCSVExportView(DashboardMixin, View):
    active_dashboard_tab = "report"

    def get(self, request, *args, **kwargs):
        survey = self.survey
        metrics = survey.metrics
        responses = survey.responses.filter(is_complete=True)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{survey.title}_report.csv"'

        writer = csv.writer(response)

        questions = {f.name: f.verbose_name for f in mast.Response._meta.fields}

        # === Section 1: Overview ===
        writer.writerow(['REPORT SUMMARY'])
        writer.writerow(['Organisation', survey.organisation])
        writer.writerow(['Survey Title', survey.title])
            
        writer.writerow([])

        # === Section 2: MAST Beliefs Scores + Detail ===
        writer.writerow(['MAST BELIEFS SCORES (1-5)'])
        writer.writerow(['Dimension', 'Score'])
        mast_dimensions = ['metadata', 'analysis', 'standards', 'teamwork']
        for dim in mast_dimensions:
            dim_score = round(metrics['MAST'][dim], 2)
            writer.writerow([dim.title(), dim_score])

            q1_key = f'beliefs_{dim}_1'
            q2_key = f'beliefs_{dim}_2'
            q1_score = round(metrics['MAST_DEPTH'][q1_key], 2)
            q2_score = round(metrics['MAST_DEPTH'][q2_key], 2)
            writer.writerow([questions.get(q1_key, q1_key), q1_score])
            writer.writerow([questions.get(q2_key, q2_key), q2_score])
        writer.writerow([])

        # === Section 3: IDEAL Behaviour Scores + Detail ===
        writer.writerow(['IDEAL BEHAVIOUR SCORES (1-5)'])
        writer.writerow(['Dimension', 'Score'])
        ideal_dimensions = ['inventory', 'document', 'endorse', 'audit', 'leadership']
        for dim in ideal_dimensions:
            dim_score = round(metrics['IDEAL'][dim], 2)
            writer.writerow([dim.title(), dim_score])

            q1_key = f'actions_{dim}_1'
            q2_key = f'actions_{dim}_2'
            q1_score = round(metrics['IDEAL_DEPTH'][q1_key], 2)
            q2_score = round(metrics['IDEAL_DEPTH'][q2_key], 2)
            writer.writerow([questions.get(q1_key, q1_key), q1_score])
            writer.writerow([questions.get(q2_key, q2_key), q2_score])
        writer.writerow([])

        # === Section 4: Results by Activity ===
        writer.writerow(['RESULTS BY ACTIVITY'])
        mast_dimensions = ['metadata', 'analysis', 'standards', 'teamwork']
        ideal_dimensions = ['inventory', 'document', 'endorse', 'audit', 'leadership']

        header = ['', 'Response'] + [d.title() for d in mast_dimensions] + [d.title() for d in ideal_dimensions]
        writer.writerow(header)

        all_activities = list(mast.ActivityType.objects.all()) + [None]
        # "Total" row first
        total_metrics = survey.generate_basic_metrics()
        total_row = ['Total', responses.count()]
        for dim in mast_dimensions:
            total_row.append(round(total_metrics['MAST'][dim], 2))
        for dim in ideal_dimensions:
            total_row.append(round(total_metrics['IDEAL'][dim], 2))
        writer.writerow(total_row)

        for activity_type in all_activities:
            if activity_type is None:
                activity_name = "No activities selected"
            else:
                activity_name = activity_type.activity
            activity_metrics = survey.generate_basic_metrics(activity_type=activity_type)
            row = [activity_name, activity_metrics['OVERALL']['total_responses']]
            for dim in mast_dimensions:
                row.append(round(activity_metrics['MAST'][dim], 2))
            for dim in ideal_dimensions:
                row.append(round(activity_metrics['IDEAL'][dim], 2))
            writer.writerow(row)
        writer.writerow([])

        return response


class SurveyResponseListView(DashboardMixin, ListView):
    model = mast.Response
    template_name = "mast/dashboard/responses_list.html"
    active_dashboard_tab = "responses"

    def get_queryset(self):
        return super().get_queryset().filter(survey=self.kwargs['survey_pk'], is_complete=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qual_fields = [
            'actions_inventory_qual',
            'actions_document_qual',
            'actions_endorse_qual',
            'actions_audit_qual',
            'actions_leadership_qual',
        ]
        context['qual_labels'] = {
            f: mast.Response._meta.get_field(f).verbose_name.replace('(Optional) ', '')
            for f in qual_fields
        }
        return context


def report_histogram(x, y):
    bar_plot = Figure(
            data=[go.Bar(
                x = x, 
                y = y,
                textposition = 'auto',)
            ]
        )
    bar_plot.update_layout(
        margin=dict(t=10)
    )
    return plot(bar_plot, output_type="div", include_plotlyjs=False)


class SurveyReportDetailView(DashboardMixin, DetailView):
    model = mast.Survey
    template_name = "mast/dashboard/report.html"
    active_dashboard_tab = "report"
    pk_url_kwarg = 'survey_pk'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        survey = self.get_object()
        report_metrics = survey.report_metrics
        context['metrics'] = survey.metrics
        context['report_metrics'] = report_metrics
        context['questions'] = {
            field.name: field.verbose_name
            for field in 
            mast.Response._meta.fields
        }
        context['graphics'] = {
            'outcomes_value': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['outcomes_value']['histogram']]
                )
            },
            'outcomes_security': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['outcomes_security']['histogram']]
                )
            },
            'outcomes_trust': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['outcomes_trust']['histogram']]
                )
            },
            'beliefs_metadata_1': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_metadata_1']['histogram']]
                )
            },
            'beliefs_analysis_1': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_analysis_1']['histogram']]
                )
            },
            'beliefs_standards_1': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_standards_1']['histogram']]
                )
            },
            'beliefs_teamwork_1': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_teamwork_1']['histogram']]
                )
            },
            'beliefs_metadata_2': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_metadata_2']['histogram']]
                )
            },
            'beliefs_analysis_2': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_analysis_2']['histogram']]
                )
            },
            'beliefs_standards_2': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_standards_2']['histogram']]
                )
            },
            'beliefs_teamwork_2': {
                "histogram": report_histogram(
                    mast.Likert.display_labels_dk_first(),
                    [x['count'] for x in report_metrics['beliefs_teamwork_2']['histogram']]
                )
            }
            
        }
        context['plot'] = plot(mast_bar_plot(survey.metrics), output_type="div", include_plotlyjs=False)
        context['radar'] = plot(ideal_polar_plot(survey.metrics), output_type="div", include_plotlyjs=False)

        team_data = []
        teams = list(survey.teams.all())
        for team in teams + [None]:
            if team is None:
                team_name = "No team provided"
            else:
                team_name = team.name
            team_metrics = survey.generate_basic_metrics(team=team)

            data = list(team_metrics['IDEAL'].values())
            data.append(data[0])  # Close the plot, otherwise there is a gap
            ideal_radar = ideal_polar_plot(survey.metrics)
            ideal_radar.add_trace(go.Scatterpolar(
                r=data,
                theta=IDEAL_LABELS+IDEAL_LABELS[0:1],
                # fill='toself',
                name=team_name
            ))

            mast_bar = mast_bar_plot(survey.metrics, name=survey.organisation)
            mast_bar.add_trace(go.Bar(
                    x = list(team_metrics['MAST'].keys()), 
                    y = list(team_metrics['MAST'].values()),
                    textposition = 'auto',
                    name=team_name
                )  
            )

            team_data.append({
                "team": team,
                "name": team_name,
                "ideal_plot": plot(ideal_radar, output_type="div", include_plotlyjs=False),
                "mast_plot": plot(mast_bar, output_type="div", include_plotlyjs=False),
                "metrics": team_metrics
            })
        if teams:
            context['team_data'] = team_data

        activity_data = []
        for activity_type in list(mast.ActivityType.objects.all()) + [None]:
            if activity_type is None:
                activity_type_name = "No activities selected"
            else:
                activity_type_name = activity_type.activity
            activity_type_metrics = survey.generate_basic_metrics(activity_type=activity_type)
            activity_data.append({
                "activity": activity_type,
                "activity_type_name": activity_type_name,
                "metrics": activity_type_metrics
            })
        context['activity_data'] = activity_data

        return context


class SurveyAddTeamView(DashboardMixin, CreateView):
    model = mast.BusinessUnit
    fields = ['name']
    template_name = "mast/dashboard/teams/create.html"
    active_dashboard_tab = "edit"

    def form_valid(self, form):
        form.instance.survey = self.survey
        form.instance.order = 0
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('survey_manage', args=[self.survey.pk]) + "#teams"


class SurveyDeleteTeamView(DashboardMixin, DeleteView):
    model = mast.BusinessUnit
    template_name = "mast/dashboard/teams/delete.html"
    active_dashboard_tab = "edit"
    pk_url_kwarg = "team_pk"

    def form_valid(self, form):
        if self.request.GET.get('delete_responses', None) == 'yes':
            team = get_object_or_404(mast.BusinessUnit, pk=self.kwargs['team_pk'])
            team.responses.all().delete()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('survey_manage', args=[self.survey.pk]) + "#teams"


class SurveyAddIndustryView(DashboardMixin, CreateView):
    model = mast.CustomIndustry
    fields = ['name']
    template_name = "mast/dashboard/teams/create.html"
    active_dashboard_tab = "edit"

    def form_valid(self, form):
        form.instance.survey = self.survey
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('survey_manage', args=[self.survey.pk]) + "#industries"


class SurveyDeleteIndustryView(DashboardMixin, DeleteView):
    model = mast.CustomIndustry
    template_name = "mast/dashboard/teams/delete.html"
    active_dashboard_tab = "edit"
    pk_url_kwarg = "industry_pk"

    def get_success_url(self):
        return reverse('survey_manage', args=[self.survey.pk]) + "#industries"

