from django.urls import path
from . import views

app_name = 'equipamentos'

urlpatterns = [
    # --- ROTAS DO DASHBOARD E ESTOQUE ---
    path('dashboard/', views.dashboard_estoque, name='dashboard_estoque'),
    path('entrada/', views.entrada_estoque, name='entrada_estoque'),

    # --- ROTAS QUE FALTAVAM (MANUTENÇÃO E DETALHES) ---
    # Essas rotas são obrigatórias para o botão "Gerenciar" do Dashboard funcionar
    path('lista/<str:tipo_codigo>/', views.listar_equipamentos_por_tipo, name='listar_por_tipo'),
    path('manutencao/<int:id>/', views.acao_manutencao_equipamento, name='acao_manutencao'),

    # --- ROTAS DE VÍNCULO E CRUD (ANTIGAS) ---
    path('funcionario/<int:funcionario_id>/', views.equipamentos_funcionario, name='equipamentos_funcionario'),
    path('dispositivo/<int:dispositivo_id>/', views.equipamentos_dispositivo, name='equipamentos_dispositivo'),
    path('editar/<int:id>/', views.editar_equipamento, name='editar_equipamento'),
    path('deletar/<int:id>/', views.deletar_equipamento, name='deletar_equipamento'),
    path('desvincular/<int:id>/', views.desvincular_equipamento, name='desvincular_equipamento'),
]