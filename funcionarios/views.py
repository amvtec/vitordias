from django.shortcuts import render, redirect
from .models import Funcionario, FolhaMensal
from .forms import FolhaMensalForm
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from .models import Funcionario
from django.contrib.auth.decorators import login_required


@login_required
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


@login_required
def selecionar_funcionario(request):
    funcionarios = Funcionario.objects.all()
    return render(request, 'funcionarios/selecionar_funcionario.html', {'funcionarios': funcionarios})
@login_required
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
@login_required
def imprimir_folha(request):
    folhas = []
    mes_selecionado = None
    ano_selecionado = None
    setor_selecionado = None

    if request.method == 'POST':
        mes_selecionado = request.POST.get('mes')
        ano_selecionado = request.POST.get('ano')
        setor_selecionado = request.POST.get('setor')

        funcionarios = Funcionario.objects.filter(setor=setor_selecionado).order_by('nome')
        folhas = []

        for funcionario in funcionarios:
            folha = FolhaMensal.objects.filter(
                funcionario=funcionario,
                mes=mes_selecionado,
                ano=ano_selecionado
            ).first()

            if folha:
                folhas.append(folha)
            else:
                folha_fake = FolhaMensal(
                    funcionario=funcionario,
                    mes=mes_selecionado,
                    ano=ano_selecionado,
                    faltas='-',
                    diarias_qtd='-',
                    diarias_horas='-',
                    servidor_substituto=None,
                    observacoes=''
                )
                folhas.append(folha_fake)

    MESES = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    ANOS = list(range(datetime.now().year, 2031))  # do ano atual até 2030

    return render(request, 'funcionarios/imprimir_folha.html', {
        'meses': MESES,
        'anos': ANOS,
        'folhas': folhas,
        'mes_selecionado': mes_selecionado,
        'ano_selecionado': int(ano_selecionado) if ano_selecionado else None,
        'setor_selecionado': setor_selecionado,
        'now': datetime.now(),
    })

from .forms import FuncionarioForm
@login_required
def cadastrar_novo_funcionario(request):  # Novo nome da função
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pagina_inicial')  # Redireciona após salvar
    else:
        form = FuncionarioForm()
    
    return render(request, 'funcionarios/cadastrar_novo_funcionario.html', {'form': form})

@login_required
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
@login_required
def excluir_folha(request, folha_id):
    folha = get_object_or_404(FolhaMensal, id=folha_id)
    if request.method == "POST":
        folha.delete()
        return redirect('imprimir_folha')
    return render(request, 'funcionarios/excluir_folha.html', {'folha': folha})
@login_required
def ver_funcionarios(request):
    funcionarios = Funcionario.objects.all().order_by('nome')
    return render(request, 'funcionarios/listar_funcionarios.html', {'funcionarios': funcionarios})
@login_required
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
@login_required
def excluir_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    funcionario.delete()
    return redirect('listar_funcionarios')

@login_required
def importar_funcionarios(request):
    if request.method == 'POST' and request.FILES.get('arquivo'):
        arquivo = request.FILES['arquivo']

        if not arquivo.name.endswith(('.xlsx', '.xls', '.csv')):
            messages.error(request, "Formato inválido. Envie um arquivo .xlsx, .xls ou .csv.")
            return redirect('importar_funcionarios')

        try:
            # Lê e padroniza colunas
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)

            df.columns = df.columns.str.strip().str.lower()  # normaliza os nomes de coluna
            print("📄 Colunas do arquivo:", df.columns.tolist())  # LOG PARA CONFERIR

            total_importados = 0

            for index, row in df.iterrows():
                nome = str(row.get('nome')).strip() if row.get('nome') else ''

                if nome == '':
                    print(f"⛔ Linha {index+2} ignorada (nome vazio)")
                    continue

                Funcionario.objects.create(nome=nome)
                print(f"✅ Importado: {nome}")
                total_importados += 1

            messages.success(request, f"{total_importados} funcionário(s) importado(s) com sucesso.")
            return redirect('ver_funcionarios')

        except Exception as e:
            messages.error(request, f"Erro ao importar: {str(e)}")
            print(f"❌ Erro ao importar: {e}")
            return redirect('importar_funcionarios')

    return render(request, 'funcionarios/importar_funcionarios.html')