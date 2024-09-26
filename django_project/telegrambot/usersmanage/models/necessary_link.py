from django.db import (
    models,
)

from django_project.telegrambot.usersmanage.models.base import (
    TimeBasedModel,
)


class NecessaryLink(TimeBasedModel):
    class Meta:
        verbose_name = "Необходимая ссылка"
        verbose_name_plural = "Необходимые ссылки"

    id = models.AutoField(primary_key=True)
    link = models.URLField(verbose_name="t.me/fwabasee")
    telegram_link_id = models.BigIntegerField(verbose_name="-1001771712186")
    title = models.CharField(
        verbose_name="FWA COMMUNITY", max_length=50
    )
