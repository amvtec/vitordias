# Generated by Django 5.1.6 on 2025-04-10 00:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feriado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(unique=True)),
                ('descricao', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('funcao', models.CharField(max_length=100)),
                ('cargo', models.CharField(max_length=100)),
                ('matricula', models.CharField(max_length=20, unique=True)),
                ('data_admissao', models.DateField()),
                ('planejamento', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Setor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='HorarioTrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turno', models.CharField(choices=[('Manhã', 'Manhã'), ('Tarde', 'Tarde')], max_length=10)),
                ('horario_inicio', models.TimeField()),
                ('horario_fim', models.TimeField()),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='controle.funcionario')),
            ],
        ),
        migrations.AddField(
            model_name='funcionario',
            name='setor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='controle.setor'),
        ),
        migrations.CreateModel(
            name='FolhaFrequencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes', models.IntegerField()),
                ('ano', models.IntegerField()),
                ('data_geracao', models.DateTimeField(auto_now_add=True)),
                ('html_armazenado', models.TextField()),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='controle.funcionario')),
            ],
            options={
                'unique_together': {('funcionario', 'mes', 'ano')},
            },
        ),
    ]
