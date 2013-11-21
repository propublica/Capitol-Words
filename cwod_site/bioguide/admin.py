from django.contrib import admin
from bioguide.models import Legislator, LegislatorRole, ChangedBioguide


class LegislatorAdmin(admin.ModelAdmin):
    list_display = ('bioguide_id', '__unicode__', 'birth_death', 'position', 'party', 'state', 'congress',)
    list_filter = ('congress', 'position', 'party', 'state','bioguide_id',)
    search_fields = ('bioguide_id', 'first', 'last', 'position', 'party', 'state', 'congress',)


class LegislatorRoleAdmin(admin.ModelAdmin):
    list_display = ('bioguide_id', '__unicode__', 'congress', 'chamber', 'party', 'title', 'state', 'district', 'begin_date', 'end_date',)
    list_filter = ('congress', 'chamber', 'party', 'title', 'state', 'district', 'begin_date', 'end_date', 'bioguide_id',)
    date_hierarchy = 'begin_date'
    search_fields = ('bioguide_id', 'first', 'last', 'congress', 'chamber', 'party', 'title', 'state', 'district',)


class ChangedBioguideAdmin(admin.ModelAdmin):
    list_display = ('old_bioguide_id', 'new_bioguide_id')
    list_filter = ('old_bioguide_id', 'new_bioguide_id')
    search_fields = ('old_bioguide_id', 'new_bioguide_id')


admin.site.register(Legislator, LegislatorAdmin)
admin.site.register(LegislatorRole, LegislatorRoleAdmin)
admin.site.register(ChangedBioguide, ChangedBioguideAdmin)
