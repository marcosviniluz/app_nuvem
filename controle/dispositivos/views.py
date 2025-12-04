from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Dispositivo, STATUS_CHOICES, TIPO_DISPOSITIVO_CHOICES
from funcionarios.models import Funcionario

@login_required
def listar_dispositivos(request):
    dispositivos = Dispositivo.objects.all().order_by('codigo')
    
    # CORREÇÃO: Carregar apenas funcionários ATIVOS para o modal de cadastro
    funcionarios_ativos = Funcionario.objects.filter(status='ATIVO').order_by('nome')

    return render(request, 'dispositivos/listar_dispositivos.html', {
        'dispositivos': dispositivos,
        'tipos': TIPO_DISPOSITIVO_CHOICES,
        'funcionarios': funcionarios_ativos, # Usamos essa lista filtrada
        'status': STATUS_CHOICES,
    })

@login_required
def criar_dispositivo(request):
    if request.method != "POST":
        return redirect('dispositivos:listar_dispositivos')

    codigo = (request.POST.get("codigo") or "").strip()
    tipo = request.POST.get("tipo_dispositivo")
    funcionario_id = request.POST.get("funcionario") or None 

    if not codigo:
        messages.error(request, "O código do dispositivo é obrigatório.")
        return redirect('dispositivos:listar_dispositivos')

    if Dispositivo.objects.filter(codigo__iexact=codigo).exists():
        messages.error(request, "Já existe um dispositivo com esse código.")
        return redirect('dispositivos:listar_dispositivos')

    # Status inicial
    status = "ATIVO" if funcionario_id else "DISPONIVEL"

    Dispositivo.objects.create(
        codigo=codigo,
        tipo_dispositivo=tipo, # Ajustado para o nome do campo no seu model
        funcionario_id=funcionario_id,
        status=status
    )

    messages.success(request, "Dispositivo cadastrado.")
    return redirect('dispositivos:listar_dispositivos')

@login_required
def editar_dispositivo(request, id):
    dispositivo = get_object_or_404(Dispositivo, id=id)

    if request.method == "GET":
        return JsonResponse({
            "id": dispositivo.id,
            "codigo": dispositivo.codigo,
            "tipo_dispositivo": dispositivo.tipo_dispositivo,
            "funcionario_id": dispositivo.funcionario.id if dispositivo.funcionario else "",
            "status": dispositivo.status,
        })

    if request.method == "POST":
        novo_codigo = (request.POST.get("codigo") or "").strip()
        novo_funcionario_id = request.POST.get("funcionario") or None
        novo_status = request.POST.get("status") or dispositivo.status

        # Validação de Código Único (exceto o atual)
        if Dispositivo.objects.exclude(id=dispositivo.id).filter(codigo__iexact=novo_codigo).exists():
            messages.error(request, "Já existe outro dispositivo com esse código.")
            return redirect('dispositivos:listar_dispositivos')

        dispositivo.codigo = novo_codigo

        # Lógica de Manutenção vs Vínculo
        if novo_status == "MANUTENCAO" and dispositivo.status != "MANUTENCAO":
            dispositivo.enviar_manutencao()
        
        elif dispositivo.status == "MANUTENCAO" and novo_status != "MANUTENCAO":
            dispositivo.retornar_da_manutencao()
            # Se voltou da manutenção e selecionou alguém
            if novo_funcionario_id:
                dispositivo.funcionario_id = novo_funcionario_id
                dispositivo.status = "ATIVO"
        else:
            # Fluxo normal
            dispositivo.funcionario_id = novo_funcionario_id
            dispositivo.status = "ATIVO" if novo_funcionario_id else "DISPONIVEL"

        dispositivo.save()
        messages.success(request, "Dispositivo atualizado.")
        return redirect('dispositivos:listar_dispositivos')
        
    return HttpResponseBadRequest("Método inválido")

@login_required
def deletar_dispositivo(request, id):
    dispositivo = get_object_or_404(Dispositivo, id=id)
    dispositivo.delete()
    messages.success(request, "Dispositivo excluído.")
    return redirect('dispositivos:listar_dispositivos')

@login_required
def desvincular_dispositivo(request, id):
    dispositivo = get_object_or_404(Dispositivo, id=id)
    dispositivo.desvincular()
    messages.info(request, "Dispositivo desvinculado.")
    return redirect('dispositivos:listar_dispositivos')