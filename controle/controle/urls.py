from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect # <--- ADICIONE ESTA IMPORTAÇÃO

# Função auxiliar para redirecionar quem acessa a raiz do site
def redirect_to_login(request):
    return redirect('contas:login')

urlpatterns = [
    # Rota para a página inicial (vazia) -> Redireciona para o Login
    path('', redirect_to_login, name='home'), 

    path('admin/', admin.site.urls),
    
    # Rota para o app de Contas (Login/Logout)
    path('contas/', include('contas.urls')), 
    
    # Rota para o app de Dispositivos
    path('dispositivos/', include('dispositivos.urls')),
    
    # Rota para o app de Funcionários
    path('funcionarios/', include('funcionarios.urls')),
    
    # Rota para o app de Equipamentos
    path('equipamentos/', include('equipamentos.urls')),
]