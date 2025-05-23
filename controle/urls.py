from django.urls import path
from . import views
from .views import importar_horarios_trabalho
from .views import ficha_funcionario
from .views import relatorio_personalizado_funcionarios

urlpatterns = [
    path('folha-frequencia/<int:funcionario_id>/<int:mes>/<int:ano>/', views.gerar_folha_frequencia, name='folha_frequencia'),
    path('selecionar-folhas/', views.selecionar_funcionarios, name='selecionar_funcionarios'),
    path('folhas-geradas/', views.listar_folhas, name='listar_folhas'),
    path('folha/<int:folha_id>/', views.visualizar_folha_salva, name='visualizar_folha_salva'),
    path('gerar-folhas-lote/', views.gerar_folhas_em_lote, name='gerar_folhas_lote'),
    path('cadastrar-funcionario/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('funcionarios/', views.listar_funcionarios, name='listar_funcionarios'),
    path('funcionario/<int:funcionario_id>/editar/', views.editar_funcionario, name='editar_funcionario'),
    path('cadastrar-horario/', views.cadastrar_horario, name='cadastrar_horario'),
    path('feriados/', views.cadastrar_feriado, name='cadastrar_feriado'),
    path('painel/', views.painel_controle, name='painel_controle'),
    path('feriado/<int:feriado_id>/editar/', views.editar_feriado, name='editar_feriado'),
    path('feriado/<int:feriado_id>/excluir/', views.excluir_feriado, name='excluir_feriado'),
    path('excluir-funcionario/<int:id>/', views.excluir_funcionario, name='excluir_funcionario'),
    path('editar-horario/<int:funcionario_id>/', views.editar_horario, name='editar_horario'),
    path('excluir-folha/<int:folha_id>/', views.excluir_folha, name='excluir_folha'),
    path('listar-folhas/', views.listar_folhas, name='listar_folhas'),
    path('importar_funcionarios/', views.importar_funcionarios, name='importar_funcionarios'),
    path('importar-horarios/', importar_horarios_trabalho, name='importar_horarios_trabalho'),
    path('livro-ponto/selecionar-capa/', views.selecionar_setor_capa, name='selecionar_capa'),
    path('livro-ponto/capas/', views.capas_livro_ponto, name='capas_livro_ponto'),
    path('funcionario/<int:funcionario_id>/ficha/', ficha_funcionario, name='imprimir_ficha_funcionario'),
    path('relatorio-personalizado/', relatorio_personalizado_funcionarios, name='relatorio_personalizado_funcionarios'),
    path('relatorio-professores/', views.relatorio_professores, name='relatorio_professores'),
    path('relatorios-funcionarios/', views.relatorios_funcionarios, name='relatorios_funcionarios'),





    

    

]
