# Generated by Django 5.1.6 on 2025-03-30 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0007_aluno_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='turno',
            field=models.CharField(blank=True, choices=[('matutino', 'Matutino'), ('vespertino', 'Vespertino')], max_length=10, null=True),
        ),
    ]
