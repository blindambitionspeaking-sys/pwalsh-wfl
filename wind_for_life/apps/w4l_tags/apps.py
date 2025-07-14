from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TagsConfig(AppConfig):
    name = "wind_for_life.apps.w4l_tags"
    verbose_name = _("Tags")
