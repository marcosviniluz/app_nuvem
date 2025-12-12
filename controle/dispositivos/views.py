import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.db.models import Count, Q 

# Importa os models locais
from .models import Dispositivo, STATUS_CHOICES, TIPO_DISPOSITIVO_CHOICES

# Importa o model de Funcionários
from funcionarios.models import Funcionario

@login_required
def listar_dispositivos(request):
    # Busca todos os dispositivos ordenados pelo código
    dispositivos = Dispositivo.objects.all().order_by('codigo')
    
    # Busca apenas funcionários ATIVOS para preencher o <select>
    funcionarios = Funcionario.objects.filter(status='ATIVO').order_by('nome')

    return render(request, 'dispositivos/listar_dispositivos.html', {
        'dispositivos': dispositivos,
        'tipos': TIPO_DISPOSITIVO_CHOICES,
        'funcionarios': funcionarios,
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

    # Define status inicial: Se tem dono, ATIVO, senão DISPONIVEL
    status = "ATIVO" if funcionario_id else "DISPONIVEL"

    Dispositivo.objects.create(
        codigo=codigo,
        tipo_dispositivo=tipo,
        funcionario_id=funcionario_id,
        status=status
    )

    messages.success(request, "Dispositivo cadastrado com sucesso.")
    return redirect('dispositivos:listar_dispositivos')

@login_required
def editar_dispositivo(request, id):
    dispositivo = get_object_or_404(Dispositivo, id=id)

    # SE FOR GET: Retorna os dados para preencher o Modal (AJAX)
    if request.method == "GET":
        return JsonResponse({
            "id": dispositivo.id,
            "codigo": dispositivo.codigo,
            "tipo_dispositivo": dispositivo.tipo_dispositivo,
            "funcionario_id": dispositivo.funcionario.id if dispositivo.funcionario else "",
            "status": dispositivo.status,
        })

    # SE FOR POST: Salva as alterações
    if request.method == "POST":
        novo_codigo = (request.POST.get("codigo") or "").strip()
        novo_funcionario_id = request.POST.get("funcionario") or None
        novo_status = request.POST.get("status") or dispositivo.status

        if not novo_codigo:
            messages.error(request, "Código é obrigatório.")
            return redirect('dispositivos:listar_dispositivos')

        # Verifica duplicidade de código (excluindo o próprio dispositivo)
        if Dispositivo.objects.exclude(id=dispositivo.id).filter(codigo__iexact=novo_codigo).exists():
            messages.error(request, "Já existe outro dispositivo com esse código.")
            return redirect('dispositivos:listar_dispositivos')

        dispositivo.codigo = novo_codigo

        # Lógica de Status e Manutenção
        if novo_status == "MANUTENCAO" and dispositivo.status != "MANUTENCAO":
            dispositivo.enviar_manutencao()
        
        elif dispositivo.status == "MANUTENCAO" and novo_status != "MANUTENCAO":
            dispositivo.retornar_da_manutencao()
            # Se voltou da manutenção e selecionou alguém
            if novo_funcionario_id:
                dispositivo.funcionario_id = novo_funcionario_id
                dispositivo.status = "ATIVO"
            
        else:
            # Edição normal
            dispositivo.funcionario_id = novo_funcionario_id
            # Se mudou manualmente o status, respeita. Se não, calcula baseado no dono.
            if novo_status:
                dispositivo.status = novo_status
            else:
                dispositivo.status = "ATIVO" if novo_funcionario_id else "DISPONIVEL"

        dispositivo.save()

        messages.success(request, "Dispositivo atualizado com sucesso.")
        return redirect('dispositivos:listar_dispositivos')

    return HttpResponseBadRequest("Método não suportado.")

@login_required
def deletar_dispositivo(request, id):
    dispositivo = get_object_or_404(Dispositivo, id=id)
    dispositivo.delete()
    messages.success(request, f"Dispositivo {dispositivo.codigo} excluído permanentemente.")
    return redirect('dispositivos:listar_dispositivos')

@login_required
def desvincular_dispositivo(request, id):
    dispositivo = get_object_or_404(Dispositivo, id=id)
    dispositivo.desvincular()
    messages.info(request, f"Dispositivo {dispositivo.codigo} desvinculado e devolvido ao estoque.")
    return redirect('dispositivos:listar_dispositivos')

@login_required
def exportar_dispositivos_csv(request):
    """
    Gera e baixa um arquivo CSV com a lista de dispositivos E seus equipamentos auxiliares.
    """
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lista_dispositivos_completa.csv"'
    
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow(['Código', 'Tipo', 'Status', 'Funcionário Responsável', 'Equipamentos Auxiliares'])
    
    
    dispositivos = Dispositivo.objects.all().select_related('funcionario').prefetch_related('equipamentoauxiliar_set').order_by('codigo')
    
    for d in dispositivos:
        nome_func = d.funcionario.nome if d.funcionario else 'Não atribuído'
        
        #
        lista_equipamentos = [str(eq) for eq in d.equipamentoauxiliar_set.all()] 
        
       
        equipamentos_str = " | ".join(lista_equipamentos) if lista_equipamentos else "Nenhum"
        
        writer.writerow([
            d.codigo,
            d.get_tipo_dispositivo_display(),
            d.get_status_display(),
            nome_func,
            equipamentos_str 
        ])
        
    return response

@login_required
def dashboard_dispositivos(request):
    # 1. Totais Gerais (Os 3 Cards)
    dados_gerais = Dispositivo.objects.aggregate(
        total=Count('id'),
        ativos=Count('id', filter=Q(status='ATIVO')),
        disponiveis=Count('id', filter=Q(status='DISPONIVEL')),
        manutencao=Count('id', filter=Q(status='MANUTENCAO'))
    )

    # 2. Distribuição por Tipo
    por_tipo = Dispositivo.objects.values('tipo_dispositivo').annotate(
        qtd=Count('id')
    ).order_by('-qtd')

    return render(request, 'dispositivos/dashboard.html', {
        'dados': dados_gerais,
        'por_tipo': por_tipo,
    })