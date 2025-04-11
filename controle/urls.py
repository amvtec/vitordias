from django.urls import path
from . import views

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

    

]
