import logging

from django.contrib import admin
from django.utils.html import format_html
from django.core.management import call_command

#from tucat.core.admin import TucatExportAdmin, download, run, stop

# Register your models here.
from tucat.twitter_streaming.models import ExportationFormat, TwitterListStreaming, TwitterListStreamingExport


logger = logging.getLogger('core')

def run(modeladmin, request, queryset):
    logger.info('Command run %s %s', request, queryset)

    for obj in queryset:
        logger.debug('Command export run %s', obj)
        call_command('export_twitter_streaming', obj=obj, run='run')
run.short_description = "Run the export"

def stop(modeladmin, request, queryset):
    logger.info('Command run %s %s', request, queryset)

    for obj in queryset:
        logger.debug('Command export stop %s', obj)
        call_command('export_twitter_streaming', obj=obj, stop='stop')
stop.short_description = "Stop the export"

def download(modeladmin, request, queryset):

    site = str(get_current_site(request))
    for obj in queryset:
        try:
            logger.debug('Command export download for %s', str(obj.file) )
            response = FileResponse(obj.file, as_attachment=True)

            return response
        except Exception as e:
            logger.exception(e)

download.short_description = "Download this export file (one at a time)"


class TwitterListStreamingAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'list_name', 'status', 'modified', 'is_enabled')
    readonly_fields = ('modified', 'status')

class TwitterListStreamingExportAdmin(admin.ModelAdmin):
    actions = [run, stop, download]

    readonly_fields = ('task_id', 'status', 'file',)
    list_display = ('list', 'export_format', 'before', 'after', 'task_id', 'status', 'download')

    class Media:
        # Adds the js script to the HTML admin view
        # https://docs.djangoproject.com/en/2.1/topics/forms/media/
        js = ("js/project.js",)

    def download(self, obj):
        button_html = '<button type="submit" class="button" type="button" onclick="download_file(%d)">Download</button>' % obj.id
        return format_html(button_html)

    class Meta:
        abstract = False

admin.site.register(TwitterListStreaming, TwitterListStreamingAdmin)
admin.site.register(TwitterListStreamingExport, TwitterListStreamingExportAdmin)
admin.site.register(ExportationFormat)
