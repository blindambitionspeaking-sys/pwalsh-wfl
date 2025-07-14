from django.apps import AppConfig as BaseConfig
from django.utils.translation import gettext_lazy as _


class BaseAppConfig(BaseConfig):
    name = "wind_for_life.apps.base"
    verbose_name = _("Wind For Life base")
