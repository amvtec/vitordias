# Generated by Django 5.1.6 on 2025-03-30 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0015_escola_email_escola_telefone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funcionario',
            name='funcao',
            field=models.CharField(choices=[('Diretor(a)', 'Diretor(a)'), ('Secretario(a)', 'Secretário(a)'), ('Coordenador(a)', 'Coordenador(a)'), ('Agente Administrativo', 'Agente Administrativo')], max_length=30),
        ),
    ]
