from django.contrib import admin
from django.urls import path, include

# Importamos a função home que definimos no arquivo acima
from core.views import home 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ROTA PRINCIPAL: Define que o site vazio ('') abre a Home (os cards)
    # O name='home' é importante para o LOGIN_REDIRECT_URL funcionar
    path('', home, name='home'), 

    # Seus outros aplicativos
    path('contas/', include('contas.urls')), 
    path('dispositivos/', include('dispositivos.urls')), 
    path('funcionarios/', include('funcionarios.urls')), 
    path('equipamentos/', include('equipamentos.urls')),
]