from django.contrib import admin

from .models import CRECParserResult


class CRECParserResultAdmin(admin.ModelAdmin):

      list_display = ('date', 'success', 'message', 'crec_s3_key')


admin.site.register(CRECParserResult, CRECParserResultAdmin)
