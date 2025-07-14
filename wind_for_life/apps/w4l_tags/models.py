from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.models import GenericUUIDTaggedItemBase, TagBase


class W4LTag(TagBase):
    pass


class UUIDTaggedItem(GenericUUIDTaggedItemBase):
    tag = models.ForeignKey(
        W4LTag,
        related_name="tagged_readings",
        on_delete=models.CASCADE,
    )

    class Meta:  # type: ignore  # noqa: PGH003
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
