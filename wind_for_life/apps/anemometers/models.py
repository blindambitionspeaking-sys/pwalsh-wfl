from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from slugify import slugify
from taggit.managers import TaggableManager

from wind_for_life.apps.base.models import BaseModel
from wind_for_life.apps.w4l_tags.models import UUIDTaggedItem

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180


def validate_latitude_range(value: float) -> None:
    if value < MIN_LATITUDE or value > MAX_LATITUDE:
        msg = "This field's value must be between -90 and 90."
        raise ValidationError(msg)


def validate_longitude_range(value: float) -> None:
    if value < MIN_LONGITUDE or value > MAX_LONGITUDE:
        msg = "This field's value must be between -180 and 180."
        raise ValidationError(msg)


class Anemometer(BaseModel):
    name = models.CharField(
        max_length=100,
        help_text="Defines slug, does not take unicode",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Value ranges from -180 to 180",
        validators=[validate_longitude_range],
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Value ranges from -90 to 90",
        validators=[validate_latitude_range],
    )

    class Meta:  # type: ignore  # noqa: PGH003
        verbose_name = _("anemometer")
        verbose_name_plural = _("anemometers")

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}): {self.id}"

    @property
    def slug(self) -> str:
        return slugify(self.name)


class Reading(BaseModel):
    speed = models.FloatField(help_text="Speed measurement in knots")
    recorded_at = models.DateTimeField(
        default=now,
        editable=False,
        help_text="Timezone dependant",
    )
    anemometer = models.ForeignKey(
        "Anemometer",
        on_delete=models.CASCADE,
        related_name="readings",
    )
    tags = TaggableManager(
        through=UUIDTaggedItem,
        help_text="A comma-separated list of tags.",
    )

    class Meta:  # type: ignore  # noqa: PGH003
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["anemometer", "recorded_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id}): {self.speed}"
