# Generated by Django 5.1.7 on 2025-03-28 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0004_alter_aluno_ano_serie'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='situacao',
            field=models.CharField(choices=[('ativo', 'Ativo'), ('inativo', 'Inativo'), ('transferido', 'Transferido')], default='ativo', max_length=15),
        ),
    ]
