# Generated by Django 5.1.6 on 2025-03-29 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0006_aluno_ano_rematricula'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_alunos/'),
        ),
    ]
