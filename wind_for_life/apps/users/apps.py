from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "wind_for_life.apps.users"
    verbose_name = _("Users")
