from django.db import models
from django.utils.translation import gettext_lazy as _

DEFAULT_SURVEY_PREAMBLE = """
    <p>
        Thank you for taking the time to participate in our survey of data asset knowledge and management.
    </p><p>
        Your input will help us gain an understanding of how your organisation manages its data assets. A data asset is a collection of data that is developed for a broad purpose. This information will help your organisation recognise how data assets can be used to support strategic plans and goals.
    </p><p>
        This survey should take less than ten minutes to complete. We’ve designed it to be as straightforward as possible, and your responses will be kept strictly confidential.
    </p>
"""

DEFAULT_SURVEY_CONFIRMATION_HTML = """
    <p>
        Thank you for taking the time to complete this survey.
    </p><p>
        Your input will help us understand how we handle and manage data.
    </p><p>
        Your responses will be kept strictly confidential, and only made available to the administrator who set up this survey.
    </p>
"""

class RoleChoices(models.TextChoices):
    ANALYSE = 'A', _("I analyse data for research purposes")
    CREATE_ASSETS = 'B', _("I create new data assets")
    APPROVE = 'C', _("I approve the release of data assets")
    COLLECT = 'D', _("I collect data from people")
    REVIEW_QUALITY = 'E', _("I review data quality")
    DASHBOARDS = 'F', _("I make dashboards or reports")
    DECISION_MAKING = 'G', _("I read data reports for decision making purposes")
    MANAGE = 'H', _("I manage data in a technical system, such as a database or data catalogue")
    DOCUMENT = 'I', _("I document data to assist other areas")


class Qualitative(models.IntegerChoices):
    SHOW = 1, _("Show free-text qualitative options")
    HIDE = 2, _("Hide free-text qualitative options")


class DataUsed(models.IntegerChoices):
    SHOW = 1, _("Show question on data used and created by the respondent")
    HIDE = 2, _("Hide question on data used and created by the respondent")


ACTIVITY_TYPES = [
    ('A', "I analyse data for research purposes"),
    ('B', "I create new data assets"),
    ('C', "I approve the release of data assets"),
    ('D', "I collect data from people"),
    ('E', "I review data quality"),
    ('F', "I make dashboards or reports"),
    ('G', "I read data reports for decision making purposes"),
    ('H', "I manage data in a technical system, such as a database or data catalogue"),
    ('I', "I document data to assist other areas"),
    ('X', "I don't use data in my role"),
    ('Z', "Other activities (please provide more details below)"),
]


class ISICChoices(models.TextChoices):
    # From ISIC: https://unstats.un.org/unsd/classifications/Econ/isic

    I = "I", _("Accommodation and food service activities")
    N = "N", _("Administrative and support service activities")
    A = "A", _("Agriculture, forestry and fishing")
    R = "R", _("Arts, entertainment and recreation")
    F = "F", _("Construction")
    P = "P", _("Education")
    D = "D", _("Electricity, gas, steam and air conditioning supply")
    K = "K", _("Financial and insurance activities")
    Q = "Q", _("Human health and social work activities")
    J = "J", _("Information and communication")
    C = "C", _("Manufacturing")
    L = "L", _("Real estate activities")
    B = "B", _("Mining and quarrying")
    M = "M", _("Professional, scientific and technical activities")
    O = "O", _("Public administration and defence; compulsory social security")
    H = "H", _("Transportation and storage")
    E = "E", _("Water supply; sewerage, waste management and remediation activities")
    G = "G", _("Wholesale and retail trade; repair of motor vehicles and motorcycles")
    S = "S", _("Other service activities")
    # T = "T", _("Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use")
    # U = "U", _("Activities of extraterritorial organizations and bodies")

NO_TEAM_SELECTED = 9999
NO_ACTIVITY_SELECTED = 9998
