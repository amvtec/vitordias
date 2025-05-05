from django.contrib import admin
from .models import Funcionario, FolhaMensal

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'funcao', 'carga_horaria_semanal', 'carga_horaria_mensal']
    search_fields = ['nome', 'funcao']

@admin.register(FolhaMensal)
class FolhaMensalAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'mes', 'ano', 'faltas', 'diarias_qtd', 'diarias_horas']
    list_filter = ['mes', 'ano']
    search_fields = ['funcionario__nome']
