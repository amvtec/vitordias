from django.shortcuts import render, redirect
from .models import Funcionario, FolhaMensal
from .forms import FolhaMensalForm
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from .models import Funcionario

def pagina_inicial(request):
    # Data de hoje
    hoje = datetime.now()
    mes_atual = hoje.month
    dia_atual = hoje.day
    
    # Buscar aniversariantes do mês
    aniversariantes_mes = Funcionario.objects.filter(data_nascimento__month=mes_atual)
    
    # Buscar aniversariantes do dia
    aniversariantes_dia = Funcionario.objects.filter(data_nascimento__month=mes_atual, data_nascimento__day=dia_atual)

    return render(request, 'funcionarios/index.html', {
        'aniversariantes_mes': aniversariantes_mes,
        'aniversariantes_dia': aniversariantes_dia
    })



def selecionar_funcionario(request):
    funcionarios = Funcionario.objects.all()
    return render(request, 'funcionarios/selecionar_funcionario.html', {'funcionarios': funcionarios})

def lancar_folha_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    MESES = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    if request.method == 'POST':
        form = FolhaMensalForm(request.POST)
        if form.is_valid():
            folha = form.save(commit=False)
            folha.funcionario = funcionario
            folha.mes = request.POST.get('mes')  # <-- ESSENCIAL
            folha.save()
            return redirect('pagina_inicial')
    else:
        form = FolhaMensalForm()

    return render(request, 'funcionarios/lancar_folha.html', {
        'funcionario': funcionario,
        'form': form,
        'meses': MESES,
    })


from django.db.models import Q

def imprimir_folha(request):
    folhas = []
    mes_selecionado = None
    ano_selecionado = None

    if request.method == 'POST':
        mes_selecionado = request.POST.get('mes')
        ano_selecionado = request.POST.get('ano')

        folhas = FolhaMensal.objects.filter(
            Q(mes=mes_selecionado) & Q(ano=ano_selecionado)
        ).order_by('funcionario__nome')

    MESES = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    return render(request, 'funcionarios/imprimir_folha.html', {
        'meses': MESES,
        'folhas': folhas,
        'mes_selecionado': mes_selecionado,
        'ano_selecionado': ano_selecionado,
    })

from .forms import FuncionarioForm

def cadastrar_novo_funcionario(request):  # Novo nome da função
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pagina_inicial')  # Redireciona após salvar
    else:
        form = FuncionarioForm()
    
    return render(request, 'funcionarios/cadastrar_novo_funcionario.html', {'form': form})


def editar_folha(request, folha_id):
    folha = get_object_or_404(FolhaMensal, id=folha_id)
    funcionario = folha.funcionario
    MESES = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    if request.method == 'POST':
        form = FolhaMensalForm(request.POST, instance=folha)
        if form.is_valid():
            folha = form.save(commit=False)
            # Captura o mês que foi enviado no select
            folha.mes = request.POST.get('mes')
            folha.save()
            return redirect('imprimir_folha')
    else:
        form = FolhaMensalForm(instance=folha)
    return render(request, 'funcionarios/editar_folha.html', {
        'form': form,
        'folha': folha,
        'funcionario': funcionario,
        'meses': MESES,
    })

def excluir_folha(request, folha_id):
    folha = get_object_or_404(FolhaMensal, id=folha_id)
    if request.method == "POST":
        folha.delete()
        return redirect('imprimir_folha')
    return render(request, 'funcionarios/excluir_folha.html', {'folha': folha})

def ver_funcionarios(request):
    funcionarios = Funcionario.objects.all().order_by('nome')
    return render(request, 'funcionarios/listar_funcionarios.html', {'funcionarios': funcionarios})

def editar_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')
    else:
        form = FuncionarioForm(instance=funcionario)
    return render(request, 'funcionarios/editar_funcionario.html', {'form': form, 'funcionario': funcionario})

def excluir_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    funcionario.delete()
    return redirect('listar_funcionarios')