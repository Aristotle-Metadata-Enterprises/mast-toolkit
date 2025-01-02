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
