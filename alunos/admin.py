from django.contrib import admin
from .models import Aluno, Professor, Turma
from .models import Escola

# Registrar Aluno no Admin
@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'data_nascimento', 'cidade', 'turma')
    search_fields = ('nome', 'aluno_id')
    list_filter = ('status', 'turma')

# Registrar Professor no Admin
@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especializacao', 'email')
    search_fields = ('nome', 'email')

# Registrar Turma no Admin
@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'serie', 'professor', 'max_alunos')
    search_fields = ('nome', 'serie')
    list_filter = ('serie',)

    # Permitindo selecionar alunos para cada turma
    filter_horizontal = ('alunos',)



admin.site.register(Escola)