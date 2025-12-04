from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EquipamentoAuxiliar, TIPO_EQUIPAMENTO_AUX_CHOICES
from dispositivos.models import STATUS_CHOICES, Dispositivo
from funcionarios.models import Funcionario

@login_required
def equipamentos_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    equipamentos = EquipamentoAuxiliar.objects.filter(funcionario_id=funcionario_id)

    if request.method == "POST":
        nome = (request.POST.get("nome") or "").strip()
        tipo = request.POST.get("tipo_equipamento_aux")

        if not nome or not tipo:
            messages.error(request, "Nome e tipo são obrigatórios.")
        else:
            EquipamentoAuxiliar.objects.create(
                nome=nome,
                tipo_equipamento_aux=tipo,
                funcionario=funcionario
            )
            messages.success(request, f"Equipamento adicionado para {funcionario.nome}.")
        return redirect('equipamentos:equipamentos_funcionario', funcionario_id=funcionario_id)

    return render(request, "equipamentos/listar.html", {
        "funcionario": funcionario,
        "equipamentos": equipamentos,
        "tipos_aux": TIPO_EQUIPAMENTO_AUX_CHOICES,
        "status_list": STATUS_CHOICES,
    })

# --- ESSA É A FUNÇÃO QUE ESTAVA FALTANDO OU COM NOME ERRADO ---
@login_required
def equipamentos_dispositivo(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    # Note que usamos 'dispositivo_id' para filtrar
    equipamentos = EquipamentoAuxiliar.objects.filter(dispositivo_id=dispositivo_id)

    # O template deve ser aquele fragmento HTML que criamos (por_dispositivo.html)
    return render(request, "equipamentos/por_dispositivo.html", {
        "dispositivo": dispositivo,
        "equipamentos": equipamentos,
    })
# ---------------------------------------------------------------

@login_required
def editar_equipamento(request, id):
    equipamento = get_object_or_404(EquipamentoAuxiliar, id=id)
    # Guarda o ID para redirecionar de volta corretamente depois
    redirect_func_id = equipamento.funcionario.id if equipamento.funcionario else None

    if request.method == "POST":
        equipamento.nome = request.POST.get("nome") or equipamento.nome
        equipamento.tipo_equipamento_aux = request.POST.get("tipo_equipamento_aux") or equipamento.tipo_equipamento_aux
        equipamento.save()
        messages.success(request, "Equipamento atualizado.")
        
        if redirect_func_id:
            return redirect('equipamentos:equipamentos_funcionario', funcionario_id=redirect_func_id)
        # Se não tem funcionário, assume que veio da tela de dispositivos
        return redirect('dispositivos:listar_dispositivos')

    # Se for GET ou outro método, redireciona para algum lugar seguro
    return redirect('dispositivos:listar_dispositivos')

@login_required
def deletar_equipamento(request, id):
    equipamento = get_object_or_404(EquipamentoAuxiliar, id=id)
    redirect_func_id = equipamento.funcionario.id if equipamento.funcionario else None
    
    equipamento.delete()
    messages.info(request, "Equipamento removido.")
    
    if redirect_func_id:
        return redirect('equipamentos:equipamentos_funcionario', funcionario_id=redirect_func_id)
    return redirect('dispositivos:listar_dispositivos')

@login_required
def desvincular_equipamento(request, id):
    equipamento = get_object_or_404(EquipamentoAuxiliar, id=id)
    redirect_func_id = equipamento.funcionario.id if equipamento.funcionario else None
    
    equipamento.funcionario = None
    equipamento.dispositivo = None
    equipamento.save()
    
    messages.success(request, "Equipamento desvinculado e devolvido ao estoque.")
    
    if redirect_func_id:
        return redirect('equipamentos:equipamentos_funcionario', funcionario_id=redirect_func_id)
    return redirect('dispositivos:listar_dispositivos')