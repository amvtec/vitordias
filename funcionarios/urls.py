from django.urls import path
from . import views

urlpatterns = [
    path('selecionar-funcionario/', views.selecionar_funcionario, name='selecionar_funcionario'),
    path('lancar-folha/<int:funcionario_id>/', views.lancar_folha_funcionario, name='lancar_folha_funcionario'),
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('selecionar-funcionario/', views.selecionar_funcionario, name='selecionar_funcionario'),
    path('imprimir-folha/', views.imprimir_folha, name='imprimir_folha'),
    path('cadastrar-novo-funcionario/', views.cadastrar_novo_funcionario, name='cadastrar_novo_funcionario'),
    path('editar-folha/<int:folha_id>/', views.editar_folha, name='editar_folha'),
    path('excluir-folha/<int:folha_id>/', views.excluir_folha, name='excluir_folha'),
    path('ver-funcionarios/', views.ver_funcionarios, name='ver_funcionarios'),
    path('editar-funcionario/<int:funcionario_id>/', views.editar_funcionario, name='editar_funcionario'),
    path('excluir-funcionario/<int:funcionario_id>/', views.excluir_funcionario, name='excluir_funcionario'),




]
