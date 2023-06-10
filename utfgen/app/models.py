from django.db import models
import uuid

# Create your tests here.

class Professor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)

class Disciplina(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200)
    carga = models.IntegerField(default=30)
    requirement = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True)
    dificuldade = models.IntegerField(default=30)
    periodo = models.IntegerField(default=1)
    tag = models.CharField(max_length=7, default="CCCCC")
    professor = models.ForeignKey(Professor, on_delete=models.DO_NOTHING)

class ProfessorHorario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professor = models.ForeignKey(Professor, on_delete=models.DO_NOTHING)
    horario_from = models.TimeField(default='00:00:00')
    horario_to = models.TimeField(default='00:00:00')
    day = models.IntegerField(default=1)
