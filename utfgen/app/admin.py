from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Professor)
admin.site.register(Disciplina)
admin.site.register(ProfessorHorario)
