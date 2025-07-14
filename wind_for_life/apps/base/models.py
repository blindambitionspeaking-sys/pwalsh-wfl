import uuid

from django.db.models import Model, UUIDField


class BaseModel(Model):
    """Base model for all django objects"""

    id = UUIDField(
        primary_key=True,
        null=False,
        blank=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    class Meta:
        abstract = True
