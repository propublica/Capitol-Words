from django.contrib import admin

from .models import CRECScraperResult
from .models import CRECParserResult


class CRECScraperResultAdmin(admin.ModelAdmin):

      list_display = ('date', 'success', 'message', 'num_crec_files_uploaded')

class CRECParserResultAdmin(admin.ModelAdmin):

      list_display = ('date', 'success', 'message', 'crec_s3_key')


admin.site.register(CRECScraperResult, CRECScraperResultAdmin)
admin.site.register(CRECParserResult, CRECParserResultAdmin)
