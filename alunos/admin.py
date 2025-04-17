from django.contrib import admin
from .models import Aluno, Professor, Turma, Escola, Funcionario
from .models import DocumentoAluno


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

@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ('nome_escola', 'nome_secretaria', 'cnpj', 'cidade', 'uf')
    search_fields = ('nome_escola', 'cnpj')
    list_filter = ('uf',)

@admin.register(DocumentoAluno)
class DocumentoAlunoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'tipo', 'data_geracao', 'assinada_diretor', 'assinada_secretario')
    list_filter = ('tipo', 'assinada_diretor', 'assinada_secretario')
    search_fields = ('aluno__nome',)

