from django.apps import AppConfig


def load_activity_types(**kwargs):
    from mast_toolkit.models import ActivityType
    from mast_toolkit.consts import ACTIVITY_TYPES
    for activity_type in ACTIVITY_TYPES:
        obj, created = ActivityType.objects.get_or_create(
            code = activity_type[0],
            activity = activity_type[1]
        )
        if created:
            print(f"Created ({activity_type[0]}) - {activity_type[1]}")


class MastToolkitConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mast_toolkit"

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(load_activity_types, sender=self)

