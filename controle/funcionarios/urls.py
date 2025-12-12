from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    # Listagem principal
    path("", views.listar_funcionarios, name="listar_funcionarios"),
    
    # Ações do CRUD
    path("novo/", views.criar_funcionario, name="criar_funcionario"),
    path("editar/<int:id>/", views.editar_funcionario, name="editar_funcionario"),
    path("demitir/<int:id>/", views.demitir_funcionario, name="demitir_funcionario"),
    path("reativar/<int:id>/", views.reativar_funcionario, name="reativar_funcionario"),
    
    # --- ROTAS DE API (AJAX) ---
    
    # 1. Busca dados para preencher o modal de Edição (ESSA ESTAVA FALTANDO)
    path("api/get/<int:id>/", views.get_funcionario_json, name="get_funcionario_json"),

    # 2. Busca o HTML do histórico
    path('historico/<int:id>/', views.historico_funcionario, name='historico_funcionario'),]