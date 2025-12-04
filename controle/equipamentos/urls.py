from django.urls import path
from . import views

# O app_name é essencial para usar {% url 'equipamentos:nome_da_url' %}
app_name = 'equipamentos'

urlpatterns = [
    # Rotas de Listagem (que também fazem o cadastro via POST)
    # Note que mudei 'pessoa' para 'funcionario' para manter o padrão novo
    path('funcionario/<int:funcionario_id>/', views.equipamentos_funcionario, name='equipamentos_funcionario'),
    path('dispositivo/<int:dispositivo_id>/', views.equipamentos_dispositivo, name='equipamentos_dispositivo'),

    # Rotas que FALTAVAM (Ações)
    path('editar/<int:id>/', views.editar_equipamento, name='editar_equipamento'),
    path('deletar/<int:id>/', views.deletar_equipamento, name='deletar_equipamento'),
    path('desvincular/<int:id>/', views.desvincular_equipamento, name='desvincular_equipamento'),
]