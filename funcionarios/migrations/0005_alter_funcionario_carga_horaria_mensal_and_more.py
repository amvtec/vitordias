# Generated by Django 5.1.6 on 2025-04-16 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funcionarios', '0004_funcionario_setor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funcionario',
            name='carga_horaria_mensal',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='carga_horaria_semanal',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='funcao',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='setor',
            field=models.CharField(blank=True, choices=[('Administrativo', 'Administrativo'), ('Pedagógico', 'Pedagógico')], max_length=20, null=True),
        ),
    ]
