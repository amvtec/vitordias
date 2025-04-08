from django.contrib import admin
from .models import Aluno, Professor, Turma, Escola, Funcionario

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'data_nascimento', 'cidade', 'turma')
    search_fields = ('nome', 'aluno_id')
    list_filter = ('status', 'turma')

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especializacao', 'email')
    search_fields = ('nome', 'email')

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'serie', 'professor', 'max_alunos')
    search_fields = ('nome', 'serie')
    list_filter = ('serie',)
    filter_horizontal = ('alunos',)

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'funcao', 'numero_matricula', 'decreto_nomeacao')
    search_fields = ('nome', 'numero_matricula')
    list_filter = ('funcao',)

