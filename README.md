# mast-toolkit

---

## Changelog — `kathy-test-branch`

All changes below are relative to the `master` branch.  
Feature tag: `Select Organisation Only or Industry Benchmarking - 160326 Kathy`

#### Table of Contents
- [v0.2.1 — Survey Wording & Tools Field Update](#v021--2026-03-16-survey-wording--tools-field-update)
- [v0.2.0 — Multi-step Response + Survey Type](#v020--2026-03-16-multi-step-response--survey-type)

---

### v0.2.0 — 2026-03-16 (Multi-step Response + Survey Type)

#### Summary
- Added **Organisation-Only / Industry-Wide** survey type selection on survey creation
- Split response form into **3 server-side steps** (Beliefs → Actions → Details)
- Each step saves to DB independently; only completed responses (`is_complete=True`) appear in reports
- Industry-Wide surveys show additional fields: Seniority, Industry, Tools
- Mandatory field validation on Step 3 with red border + error message
- Teams section hidden on edit page for Industry-Wide surveys
- DB Migrations 0002–0007 added

#### 1. New Feature: Survey Type (Benchmark Scope)

Surveys can now be created as **Organisation-Only** or **Industry-Wide**.

**`app/mast_toolkit/consts.py`** — New constants added:
- `BenchmarkScope(IntegerChoices)`: `ORGANISATION_ONLY = 1`, `INDUSTRY_WIDE = 2`
- `SeniorityChoices(TextChoices)`: CXO (15+ yrs), Senior (8–15 yrs), Mid-Level (3–7 yrs), Junior (0–2 yrs)
- `ToolChoices(TextChoices)`: SharePoint, Collibra, Microsoft Purview, Aristotle Metadata, Informatica, Data.gov.au, Other

**`app/mast_toolkit/models.py`** — Survey model:
- Added `benchmark_scope` field (PositiveIntegerField, choices=BenchmarkScope, default=ORGANISATION_ONLY)

**`app/mast_toolkit/models.py`** — Response model:
- Added `seniority` (CharField, choices=SeniorityChoices)
- Added `tools` (CharField, choices=ToolChoices)
- Added `other_tool` (CharField, max_length=2048)
- Added `industry` (CharField, choices=ISICChoices)
- Added `is_complete` (BooleanField, default=False) — tracks multi-step form completion
- All `beliefs_*` and `actions_*` PositiveIntegerField changed to `null=True` for partial saves

**`app/mast_toolkit/models.py`** — Metrics & Reports:
- `generate_basic_metrics()`, `generate_report_metrics()`, `response_dates`: filtered to `is_complete=True` only
- Incomplete responses excluded from all dashboard metrics/reports

---

#### 2. New Feature: Multi-Step Response Form (3 pages, server-side)

Single-page response form split into 3 separate Django views. Each step saves to DB before proceeding.

| Step | URL | Content |
|------|-----|---------|
| 1 | `/survey/response/<survey_pk>` | Beliefs (8 likert questions) — creates `Response` with `is_complete=False` |
| 2 | `/survey/response/<survey_pk>/step2/<response_pk>` | Actions / IDEAL (10 radio + 5 optional textarea) |
| 3 | `/survey/response/<survey_pk>/step3/<response_pk>` | Role & Activities — sets `is_complete=True` on submit |

**Mandatory fields on Step 3:** Seniority `*`, Tasks (data_uses) `*`, Industry `*` (Industry-Wide only)  
Error display: red border + pink background + "This field is required." message

**New template files:**
- `app/mast_toolkit/templates/mast/response/step1.html`
- `app/mast_toolkit/templates/mast/response/step2.html`
- `app/mast_toolkit/templates/mast/response/step3.html`

**`app/mast_toolkit/forms.py`** — New forms:
- `SurveyCreateForm` — includes `benchmark_scope` as RadioSelect
- `SurveyManageForm` — `benchmark_scope` disabled (read-only on edit page)
- `ResponseStep1Form` — beliefs fields only
- `ResponseStep2Form` — actions fields only
- `ResponseStep3Form` — role/activity fields with mandatory validation

**`app/mast_toolkit/views.py`** — New views:
- `ResponseStep1View` — POST creates Response, redirects to step 2
- `ResponseStep2View` — POST updates Response with actions, redirects to step 3
- `ResponseStep3View` — POST updates Response, marks `is_complete=True`, redirects to Thanks

**`app/web/urls.py`** — New URL patterns:
- `survey/response/<survey_pk>` → `ResponseStep1View` (replaces old `ResponseCreateView`)
- `survey/response/<survey_pk>/step2/<response_pk>` → `ResponseStep2View`
- `survey/response/<survey_pk>/step3/<response_pk>` → `ResponseStep3View`

---

#### 3. Survey Edit Page Changes

- **`templates/components/survey_management_form.html`**: Added Survey Type radio buttons
- **`templates/mast/dashboard/update.html`**: Teams section hidden for Industry-Wide surveys (`{% if is_organisation_only %}`)
- **`views.py` — `SurveyUpdateView`**: Added `is_organisation_only`/`is_industry_wide` context

---

#### 4. Styling Changes

**`templates/base.html`**:
- Added `.seniority-choices label, .tool-choices label { font-weight: normal; }` CSS

---

#### 5. Migrations (0002–0007)

| Migration | Changes |
|-----------|---------|
| `0002` | Added `Survey.benchmark_scope` |
| `0003` | Auto-generated field alterations |
| `0004` | Added `Response.industry`, `Response.seniority`, `Response.tools` |
| `0005` | Added `Response.other_tool`, altered `Response.tools` max_length=2 |
| `0006` | Auto-generated field alterations |
| `0007` | Added `Response.is_complete`, all beliefs/actions fields → `null=True` |

---

### v0.2.1 — 2026-03-16 (Survey Wording & Tools Field Update)

#### Summary
- Changed intro wording from "first four questions" to "first section"
- Renamed tools question and converted from radio select to free-text textarea
- Made "What data do you use or create…" question always visible (removed conditional toggle)

#### 1. Wording Changes

**`templates/mast/response/step1.html`** and **`templates/mast/response/create.html`**:
- `"The first four questions in this survey are about your beliefs…"` → `"The first section in this survey is about your beliefs…"`

#### 2. Tools Field — Radio → Free-text Textarea

**`app/mast_toolkit/models.py`**:
- `tools` field changed from `CharField(max_length=2, choices=ToolChoices)` → `TextField(blank=True)`
- `verbose_name` changed from `"What tools do you use to work with data in the organisation?"` → `"What tools do you use to document and organise data at your organisation?"`

**`app/mast_toolkit/forms.py`**:
- `ResponseForm`: tools widget changed from `RadioSelect` → `TextInput`; removed `tools.choices` filtering in `__init__`
- `ResponseStep3Form`: tools widget changed from `RadioSelect` → `TextInput`; removed `tools.choices` filtering in `__init__`

**`templates/mast/response/step3.html`** and **`templates/mast/response/create.html`**:
- Tools field rendered via `textarea.html` helper (same style as `data_used_or_created`)
- Removed "Other tools" sub-section and related JavaScript toggle

#### 3. Data Used Question — Always Visible

**`templates/mast/response/step3.html`**:
- Removed `{% if show_data_used_field %}` conditional; `data_used_or_created` textarea now always displays on Step 3

#### 4. Migration Required

Model field change (`tools`: CharField → TextField) requires a new migration:
```
PYTHONPATH=./app DJANGO_SETTINGS_MODULE=web.settings django-admin makemigrations mast_toolkit
```