from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView, TemplateView
from mast_toolkit import models as mast
import mast_toolkit.forms
import mast_toolkit.consts
import datetime
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
        return super().get_context_data(**kwargs)


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
        return super().get_context_data(**kwargs)


class SurveyCreateView(SurveyCreateMixin, CreateView):
    model = mast.Survey
    template_name = "mast/create_survey.html"
    form_class = mast_toolkit.forms.SurveyManageForm


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


class SurveyResponseListView(DashboardMixin, ListView):
    model = mast.Response
    template_name = "mast/dashboard/responses_list.html"
    active_dashboard_tab = "responses"

    def get_queryset(self):
        return super().get_queryset().filter(survey=self.kwargs['survey_pk'])


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

