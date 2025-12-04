from django.urls import path
from . import views

app_name = 'equipamentos'

urlpatterns = [
    # Rota Principal do Estoque (Dashboard)
    path('dashboard/', views.dashboard_estoque, name='dashboard_estoque'),
    
    # Rota para dar entrada (Processamento do formulário)
    path('entrada/', views.entrada_estoque, name='entrada_estoque'),

    # ... (Mantenha suas rotas antigas de editar, deletar, etc) ...
    path('funcionario/<int:funcionario_id>/', views.equipamentos_funcionario, name='equipamentos_funcionario'),
    path('dispositivo/<int:dispositivo_id>/', views.equipamentos_dispositivo, name='equipamentos_dispositivo'),
    path('editar/<int:id>/', views.editar_equipamento, name='editar_equipamento'),
    path('deletar/<int:id>/', views.deletar_equipamento, name='deletar_equipamento'),
    path('desvincular/<int:id>/', views.desvincular_equipamento, name='desvincular_equipamento'),
]