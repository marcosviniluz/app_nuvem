from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dispositivos:listar_dispositivos')

        messages.error(request, "Usuário ou senha incorretos.")
    else:
        form = AuthenticationForm()

    return render(request, 'contas/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('contas:login')
