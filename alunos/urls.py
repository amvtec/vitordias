from django.urls import path
from . import views
from .views import cadastrar_funcionario_views
from .views import logout_view
from .views import gerar_relatorio_por_turma
from .views import relatorio_rematricula
from .views import aniversariantes_view
from .views import relatorio_alunos_por_idade





urlpatterns = [
    path('matricula/', views.pagina_matricula, name='pagina_matricula'),
    path('rematricula/', views.buscar_aluno_rematricula, name='buscar_aluno_rematricula'),
    path('rematricula/<int:aluno_id>/', views.rematricula_formulario, name='rematricula_formulario'),
    path('cadastrar/', views.cadastrar_aluno, name='cadastrar_aluno'),
    path('cadastrado/<int:aluno_id>/', views.aluno_cadastrado, name='aluno_cadastrado'),
    path('imprimir-matricula/<int:aluno_id>/', views.imprimir_matricula, name='imprimir_matricula'),
    path('matricula/pdf/<int:aluno_id>/', views.gerar_pdf_matricula, name='gerar_pdf_matricula'),
    path('alunos/editar/<int:aluno_id>/', views.atualizar_aluno, name='atualizar_aluno'),
    path('painel/', views.painel_alunos, name='painel_alunos'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('rematricula/confirmacao/<int:aluno_id>/', views.rematricula_confirmacao, name='rematricula_confirmacao'),
    path('rematricula/sucesso/<int:aluno_id>/', views.rematricula_sucesso, name='rematricula_sucesso'),
    path('alunos/pesquisar/', views.pesquisar_aluno_sidebar, name='pesquisar_aluno_sidebar'),
    path('alunos/ficha/<int:aluno_id>/', views.visualizar_ficha_aluno, name='visualizar_ficha_aluno'),
    path('alunos/ficha/<int:aluno_id>/', views.visualizar_ficha_aluno, name='ficha_aluno'),
    path('importar-alunos/', views.import_alunos, name='importar_alunos'),
    path('declaracao_matricula/<int:aluno_id>/', views.gerar_declaracao_matricula, name='gerar_declaracao_matricula'),
    path('aluno/<int:aluno_id>/editar/', views.editar_aluno, name='editar_aluno'),
    path('novo-funcionario/', cadastrar_funcionario_views, name='novo_funcionario'),
    path('pesquisar-funcionario/', views.pesquisar_funcionario, name='pesquisar_funcionario'),
    path('listar-funcionarios/', views.listar_funcionarios, name='listar_funcionarios'),
    path('funcionario/<int:funcionario_id>/editar/', views.editar_funcionario, name='editar_funcionario'),
    path('funcionario/<int:funcionario_id>/excluir/', views.excluir_funcionario, name='excluir_funcionario'),
    path('logout/', logout_view, name='logout'),
    path('emitir-documentos/', views.emitir_documentos, name='emitir_documentos'),
    path('relatorio/turma/', views.relatorio_por_turma_view, name='relatorio_por_turma_view'),
    path('relatorio/turma/', views.relatorio_por_turma_view, name='relatorio_por_turma'),
    path('relatorio/turma/gerar/', gerar_relatorio_por_turma, name='gerar_relatorio_por_turma'),
    path('relatorio/rematricula/', relatorio_rematricula, name='relatorio_rematricula'),
    path('alocar-alunos/', views.alocar_alunos_turma, name='alocar_alunos_turma'),
    path('relatorio-alocados/', views.relatorio_alunos_alocados, name='relatorio_alocados'),
    path('alocar-alunos/', views.alocar_alunos_turma, name='alocar_alunos'),
    path('pesquisar-alunos/', views.pesquisar_alunos, name='pesquisar_alunos'),
    path('aniversariantes/', aniversariantes_view, name='aniversariantes_view'),
    path('relatorios-personalizados/', views.relatorios_personalizados, name='relatorios_personalizados'),
    path('relatorio/idade/', relatorio_alunos_por_idade, name='relatorio_alunos_por_idade'),

 

]

