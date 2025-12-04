from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Funcionario, UnidadeTrabalho, HistoricoFuncionario

# IMPORTANTE: Importar os modelos dos outros apps para desvincular
from dispositivos.models import Dispositivo
from equipamentos.models import EquipamentoAuxiliar

@login_required
def listar_funcionarios(request):
    ativos = Funcionario.objects.filter(status="ATIVO").order_by("nome")
    demitidos = Funcionario.objects.filter(status="DEMITIDO").order_by("nome")
    unidades = UnidadeTrabalho.objects.all().order_by("nome")

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
    unidade_id = request.POST.get("unidade_trabalho")

    if not nome or not email:
        messages.error(request, "Nome e email são obrigatórios.")
        return redirect("funcionarios:listar_funcionarios")

    if Funcionario.objects.filter(email=email).exists():
        messages.error(request, "Já existe um funcionário com este email.")
        return redirect("funcionarios:listar_funcionarios")

    novo_func = Funcionario.objects.create(
        nome=nome,
        email=email,
        unidade_trabalho_id=unidade_id,
        status="ATIVO"
    )

    HistoricoFuncionario.objects.create(
        funcionario=novo_func,
        acao="CONTRATADO",
        descricao=f"Funcionário {nome} admitido."
    )

    messages.success(request, "Funcionário contratado com sucesso.")
    return redirect("funcionarios:listar_funcionarios")

# --- ESSA ERA A FUNÇÃO QUE FALTAVA ---
@login_required
def get_funcionario_json(request, id):
    """Retorna dados JSON para preencher o modal de edição"""
    funcionario = get_object_or_404(Funcionario, id=id)
    
    return JsonResponse({
        "id": funcionario.id,
        "nome": funcionario.nome,
        "email": funcionario.email,
        # Retorna o ID da unidade ou string vazia se for null
        "unidade_trabalho": funcionario.unidade_trabalho.id if funcionario.unidade_trabalho else ""
    })
# -------------------------------------

@login_required
def editar_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)

    if request.method == "POST":
        old_unidade = funcionario.unidade_trabalho
        
        funcionario.nome = request.POST.get("nome") or funcionario.nome
        funcionario.email = request.POST.get("email") or funcionario.email
        new_unidade_id = request.POST.get("unidade_trabalho")
        
        if new_unidade_id and str(old_unidade.id if old_unidade else '') != str(new_unidade_id):
             HistoricoFuncionario.objects.create(
                funcionario=funcionario,
                acao="TRANSFERIDO",
                descricao=f"Mudou de {old_unidade} para nova unidade."
            )
        
        funcionario.unidade_trabalho_id = new_unidade_id or None
        funcionario.save()
        messages.success(request, "Dados atualizados.")

    return redirect("funcionarios:listar_funcionarios")

@login_required
def demitir_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)

    # 1. Desvincular Dispositivos
    dispositivos = Dispositivo.objects.filter(funcionario=funcionario)
    for d in dispositivos:
        d.funcionario = None
        d.status = 'DISPONIVEL'
        d.save()

    # 2. Desvincular Equipamentos
    equipamentos = EquipamentoAuxiliar.objects.filter(funcionario=funcionario)
    for e in equipamentos:
        e.funcionario = None
        e.save()

    # 3. Demitir (Model)
    funcionario.demitir()

    messages.warning(request, f"{funcionario.nome} foi demitido. Dispositivos desvinculados.")
    return redirect("funcionarios:listar_funcionarios")

@login_required
def reativar_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    funcionario.reativar()
    messages.success(request, f"{funcionario.nome} foi reativado.")
    return redirect("funcionarios:listar_funcionarios")

@login_required
def get_historico_json(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    historico = funcionario.historico.all()
    
    return render(request, "funcionarios/partials/historico_conteudo.html", {
        "funcionario": funcionario,
        "historico": historico
    })