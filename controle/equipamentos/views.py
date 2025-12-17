from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q

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
            # messages.error(request, "Nome e tipo são obrigatórios.")
            print("Nome e tipo obrigátorios")
        else:
            EquipamentoAuxiliar.objects.create(
                nome=nome,
                tipo_equipamento_aux=tipo,
                funcionario=funcionario
            )
            # messages.success(request, f"Equipamento adicionado para {funcionario.nome}.")
        
        return redirect('equipamentos:equipamentos_funcionario', funcionario_id=funcionario_id)

    return render(request, "equipamentos/listar.html", {
        "funcionario": funcionario,
        "equipamentos": equipamentos,
        "tipos_aux": TIPO_EQUIPAMENTO_AUX_CHOICES,
        "status_list": STATUS_CHOICES,
    })

@login_required
def equipamentos_dispositivo(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)

    # 1. PROCESSAMENTO DO VÍNCULO (POST)
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        
        if item_id:
            # Pega o item do estoque
            item = get_object_or_404(EquipamentoAuxiliar, id=item_id)
            
            # Vincula ao dispositivo
            item.dispositivo = dispositivo
            if dispositivo.funcionario:
                item.funcionario = dispositivo.funcionario
            
            item.save() 
            # messages.success(request, f"{item.nome} vinculado com sucesso!")
        
        # O else foi removido pois estava vazio (apenas comentários) e causava erro
            
        return redirect('dispositivos:listar_dispositivos')

    # 2. PREPARAÇÃO DOS DADOS (GET)
    equipamentos_vinculados = EquipamentoAuxiliar.objects.filter(dispositivo_id=dispositivo_id)
    
    # IMPORTANTE: Busca itens DISPONÍVEIS para preencher o select do modal
    estoque_disponivel = EquipamentoAuxiliar.objects.filter(status='DISPONIVEL').order_by('nome')

    return render(request, "equipamentos/por_dispositivo.html", {
        "dispositivo": dispositivo,
        "equipamentos": equipamentos_vinculados,
        "estoque": estoque_disponivel, 
    })

@login_required
def editar_equipamento(request, id):
    equipamento = get_object_or_404(EquipamentoAuxiliar, id=id)
    redirect_func_id = equipamento.funcionario.id if equipamento.funcionario else None

    if request.method == "POST":
        equipamento.nome = request.POST.get("nome") or equipamento.nome
        equipamento.tipo_equipamento_aux = request.POST.get("tipo_equipamento_aux") or equipamento.tipo_equipamento_aux
        equipamento.save()
        # messages.success(request, "Equipamento atualizado.")
        
        if redirect_func_id:
            return redirect('equipamentos:equipamentos_funcionario', funcionario_id=redirect_func_id)
        return redirect('dispositivos:listar_dispositivos')

    return redirect('dispositivos:listar_dispositivos')

@login_required
def deletar_equipamento(request, id):
    equipamento = get_object_or_404(EquipamentoAuxiliar, id=id)
    redirect_func_id = equipamento.funcionario.id if equipamento.funcionario else None
    
    equipamento.delete()
    # messages.info(request, "Equipamento removido.")
    
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
    
    # messages.success(request, "Equipamento desvinculado e devolvido ao estoque.")
    
    if redirect_func_id:
        return redirect('equipamentos:equipamentos_funcionario', funcionario_id=redirect_func_id)
    return redirect('dispositivos:listar_dispositivos')

# --- DASHBOARD E ESTOQUE ---

@login_required
def dashboard_estoque(request):
    metricas = EquipamentoAuxiliar.objects.values('tipo_equipamento_aux').annotate(
        total=Count('id'),
        disponiveis=Count('id', filter=Q(status='DISPONIVEL')),
        ativos=Count('id', filter=Q(status='ATIVO')),
        manutencao=Count('id', filter=Q(status='MANUTENCAO'))
    ).order_by('tipo_equipamento_aux')

    return render(request, 'equipamentos/dashboard.html', {
        'metricas': metricas,
        'tipos_aux': TIPO_EQUIPAMENTO_AUX_CHOICES, 
    })

@login_required
def entrada_estoque(request):
    if request.method == "POST":
        tipo = request.POST.get('tipo_equipamento_aux')
        quantidade = int(request.POST.get('quantidade') or 0)
        prefixo_nome = request.POST.get('prefixo_nome') or "Item de Estoque"

        if quantidade < 1:
            # messages.error(request, "A quantidade deve ser maior que zero.")
            return redirect('equipamentos:dashboard_estoque')

        novos_itens = []
        for i in range(quantidade):
            # --- MUDANÇA AQUI ---
            # Antes estava: nome_final = f"{prefixo_nome} - {i+1}"
            # Agora usamos apenas o nome puro:
            nome_final = prefixo_nome 
            
            novos_itens.append(EquipamentoAuxiliar(
                nome=nome_final,
                tipo_equipamento_aux=tipo,
                status='DISPONIVEL',
                funcionario=None,
                dispositivo=None
            ))
        
        EquipamentoAuxiliar.objects.bulk_create(novos_itens)
        
        # messages.success(request, f"{quantidade} novos itens adicionados!")
        return redirect('equipamentos:dashboard_estoque')

    return redirect('equipamentos:dashboard_estoque')

# --- MANUTENÇÃO ---

@login_required
def listar_equipamentos_por_tipo(request, tipo_codigo):
    itens = EquipamentoAuxiliar.objects.filter(tipo_equipamento_aux=tipo_codigo).order_by('status', 'nome')
    nome_tipo = dict(TIPO_EQUIPAMENTO_AUX_CHOICES).get(tipo_codigo, tipo_codigo)

    return render(request, 'equipamentos/lista_por_tipo.html', {
        'itens': itens,
        'tipo_codigo': tipo_codigo,
        'nome_tipo': nome_tipo
    })

@login_required
def acao_manutencao_equipamento(request, id):
    item = get_object_or_404(EquipamentoAuxiliar, id=id)
    
    if item.status == 'MANUTENCAO':
        item.status = 'DISPONIVEL'
        # messages.success(request, f"{item.nome} retornou da manutenção.")
    else:
        item.status = 'MANUTENCAO'
        # messages.warning(request, f"{item.nome} enviado para manutenção.")
    
    item.save()
    return redirect('equipamentos:listar_por_tipo', tipo_codigo=item.tipo_equipamento_aux)