from django.contrib import admin

from .models import CRECScraperResult


class CRECScraperResultAdmin(admin.ModelAdmin):

      list_display = ('date', 'success', 'message', 'num_crec_files_uploaded')


admin.site.register(CRECScraperResult, CRECScraperResultAdmin)
