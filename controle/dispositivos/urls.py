from django.urls import path
from . import views

# O app_name ajuda a organizar as URLs (ex: no html usar 'dispositivos:listar')
app_name = 'dispositivos'

urlpatterns = [
  
    path('', views.listar_dispositivos, name='listar_dispositivos'),
    
    path('add/', views.criar_dispositivo, name='criar_dispositivo'),
    
    path('edit/<int:id>/', views.editar_dispositivo, name='editar_dispositivo'),
    
    path('delete/<int:id>/', views.deletar_dispositivo, name='deletar_dispositivo'),
    
    path('desvincular/<int:id>/', views.desvincular_dispositivo, name='desvincular_dispositivo'),

    path('exportar-csv/', views.exportar_dispositivos_csv, name='exportar_csv'),
    
    path('dashboard/', views.dashboard_dispositivos, name='dashboard_dispositivos'),

    path('api/dashboard-data/', views.api_dados_dashboard, name='api_dados_dashboard'),
]