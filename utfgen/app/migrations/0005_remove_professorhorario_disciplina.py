# Generated by Django 4.2.1 on 2023-06-01 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_professorhorario_horario_from_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professorhorario',
            name='disciplina',
        ),
    ]
