# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import CongressPerson, State, Term, ExternalId

admin.site.register(CongressPerson)
admin.site.register(State)
admin.site.register(Term)
admin.site.register(ExternalId)