# Generated by Django 5.1.6 on 2025-04-11 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funcionarios', '0002_alter_folhamensal_funcionario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='funcionario',
            name='data_nascimento',
            field=models.DateField(blank=True, null=True),
        ),
    ]
