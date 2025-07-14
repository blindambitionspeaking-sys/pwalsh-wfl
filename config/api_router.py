from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_nested import routers

from wind_for_life.apps.anemometers.api.views import (
    AnemometerReadingViewSet,
    AnemometerViewSet,
    ReadingViewSet,
)
from wind_for_life.apps.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("anemometers", AnemometerViewSet, basename="anemometers")
router.register("readings", ReadingViewSet, basename="readings")

anemometers_router = routers.NestedSimpleRouter(
    router,
    r"anemometers",
    lookup="anemometer",
)
anemometers_router.register(
    r"readings",
    AnemometerReadingViewSet,
    basename="anemometers-readings",
)

app_name = "api"
urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(anemometers_router.urls)),
]
