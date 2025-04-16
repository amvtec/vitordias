from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('selecionar-funcionario/', views.selecionar_funcionario, name='selecionar_funcionario'),
    path('lancar-folha/<int:funcionario_id>/', views.lancar_folha_funcionario, name='lancar_folha_funcionario'),
    path('imprimir-folha/', views.imprimir_folha, name='imprimir_folha'),
    path('cadastrar-novo-funcionario/', views.cadastrar_novo_funcionario, name='cadastrar_novo_funcionario'),
    path('editar-folha/<int:folha_id>/', views.editar_folha, name='editar_folha'),
    path('deletar-folha/<int:folha_id>/', views.deletar_folha, name='deletar_folha'),
    path('ver-funcionarios/', views.ver_funcionarios, name='ver_funcionarios'),
    path('alterar-funcionario/<int:funcionario_id>/', views.alterar_funcionario, name='alterar_funcionario'),
    path('deletar-funcionario/<int:funcionario_id>/', views.deletar_funcionario, name='deletar_funcionario'),
    path('importar-funcionarios/', views.importar_funcionarios, name='importar_funcionarios'),
    path('folhas-geradas/', views.listar_folhas, name='ver_folhas'),
    path('folha/<str:mes>/<int:ano>/<str:setor>/', views.ver_folha_detalhada, name='ver_folha_detalhada'),
    path('reimprimir/<str:mes>/<int:ano>/<str:setor>/', views.reimprimir_folha, name='reimprimir_folha'),
    path('funcionarios/baixar-folha/', views.baixar_folha_pagamento, name='baixar_folha_pagamento'),





]
