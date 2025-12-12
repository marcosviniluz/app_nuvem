from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Funcionario, HistoricoFuncionario

from dispositivos.models import Dispositivo
from equipamentos.models import EquipamentoAuxiliar

@login_required
def listar_funcionarios(request):
    ativos = Funcionario.objects.filter(status="ATIVO").order_by("nome")
    demitidos = Funcionario.objects.filter(status="DEMITIDO").order_by("nome")
    
    unidades = Funcionario.UNIDADE_CHOICES

    return render(request, "funcionarios/funcionarios.html", {
        "ativos": ativos,
        "demitidos": demitidos,
        "unidades": unidades,
    })

@login_required
def criar_funcionario(request):
    if request.method != "POST":
        return redirect("funcionarios:listar_funcionarios")

    nome = (request.POST.get("nome") or "").strip()
    email = (request.POST.get("email") or "").strip()
    unidade_code = request.POST.get("unidade_trabalho") 

    if not nome or not email:
        messages.error(request, "Nome e email são obrigatórios.")
        return redirect("funcionarios:listar_funcionarios")

    if Funcionario.objects.filter(email=email).exists():
        messages.error(request, "Já existe um funcionário com este email.")
        return redirect("funcionarios:listar_funcionarios")

    novo_func = Funcionario.objects.create(
        nome=nome,
        email=email,
        unidade_trabalho=unidade_code, 
        status="ATIVO"
    )

    HistoricoFuncionario.objects.create(
        funcionario=novo_func,
        acao="CONTRATADO",
        descricao=f"Admitido."
    )

    messages.success(request, "Funcionário contratado com sucesso.")
    return redirect("funcionarios:listar_funcionarios")

@login_required
def get_funcionario_json(request, id):
    """API para preencher o modal de edição"""
    func = get_object_or_404(Funcionario, id=id)
    return JsonResponse({
        "id": func.id,
        "nome": func.nome,
        "email": func.email,
        "unidade_trabalho": func.unidade_trabalho 
    })

@login_required
def editar_funcionario(request, id):
    func = get_object_or_404(Funcionario, id=id)

    if request.method == "POST":
        func.nome = request.POST.get("nome") or func.nome
        func.email = request.POST.get("email") or func.email
        func.unidade_trabalho = request.POST.get("unidade_trabalho") 
        
        func.save()
        messages.success(request, "Dados atualizados.")

    return redirect("funcionarios:listar_funcionarios")

@login_required
def demitir_funcionario(request, id):
    func = get_object_or_404(Funcionario, id=id)

    dispositivos = Dispositivo.objects.filter(funcionario=func)
    for d in dispositivos:
        d.funcionario = None
        d.status = 'DISPONIVEL' 
        d.save()

    equipamentos = EquipamentoAuxiliar.objects.filter(funcionario=func)
    for e in equipamentos:
        e.funcionario = None
        e.status = 'DISPONIVEL'
        e.save()

    func.demitir()

    messages.warning(request, f"{func.nome} foi demitido. Todos os itens foram devolvidos ao estoque.")
    return redirect("funcionarios:listar_funcionarios")

@login_required
def reativar_funcionario(request, id):
    func = get_object_or_404(Funcionario, id=id)
    func.reativar()
    messages.success(request, f"{func.nome} foi reativado.")
    return redirect("funcionarios:listar_funcionarios")


@login_required
def historico_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    
    dispositivos = Dispositivo.objects.filter(funcionario=funcionario)
    perifericos = EquipamentoAuxiliar.objects.filter(funcionario=funcionario)
    
    lista_itens = []

    for d in dispositivos:
        lista_itens.append({
            'categoria': 'Principal',
            'nome': d.codigo, 
            'detalhe': d.get_tipo_dispositivo_display(),
            'icone': 'bi-laptop',
            'cor': 'text-primary'
        })

    for p in perifericos:
        lista_itens.append({
            'categoria': 'Acessório',
            'nome': p.nome,
            'detalhe': p.get_tipo_equipamento_aux_display(),
            'icone': 'bi-usb-plug',
            'cor': 'text-secondary'
        })

    return JsonResponse({
        'nome_funcionario': funcionario.nome,
        'unidade': funcionario.get_unidade_trabalho_display(),
        'total': len(lista_itens),
        'itens': lista_itens
    })