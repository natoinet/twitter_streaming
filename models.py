from django.db import models

from tucat.application.models import TucatElement
from tucat.core.models import TucatTask


class TwitterListStreaming(TucatElement):
    owner_name = models.CharField(max_length=200)
    list_name = models.CharField(max_length=200)

    def __str__(self):
        return self.owner_name + ' > ' + self.list_name

    class Meta:
        abstract = False


class ExportationFormat(models.Model):
    name = models.CharField(max_length=200)
    format = models.CharField(max_length=200)
    fields = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class TwitterListStreamingExport(TucatTask):
    list = models.ForeignKey(TwitterListStreaming, on_delete=models.CASCADE)
    export_format = models.ForeignKey(ExportationFormat, on_delete=models.CASCADE)
    before = models.DateField(blank=True, null=True)
    after = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='output/', blank=True, null=True, default=None)

    class Meta:
        abstract = False
