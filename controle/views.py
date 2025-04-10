from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from calendar import monthrange, day_name
from datetime import date
import calendar
from .forms import HorarioTrabalhoForm
from .forms import FeriadoForm
from .models import Setor
from .models import Funcionario, Feriado, HorarioTrabalho, FolhaFrequencia
from django.shortcuts import render
from .models import FolhaFrequencia
from django.db.models import Q
import locale


# Mapeamento manual dos dias da semana em português
dias_da_semana_pt = {
    0: 'segunda-feira',
    1: 'terça-feira',
    2: 'quarta-feira',
    3: 'quinta-feira',
    4: 'sexta-feira',
    5: 'sábado',
    6: 'domingo'
}

# Mapeamento manual dos meses (opcional para garantir capitalização correta)
meses_pt = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

from datetime import date
from calendar import monthrange

# Função de gerar a folha de frequência
from .models import SabadoLetivo

from .models import Escola

def gerar_folha_frequencia(request, funcionario_id, mes, ano):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)

    # Obter as informações da escola
    escola = Escola.objects.first()  # Se houver mais de uma escola, ajuste conforme necessário

    # Obter todos os dias do mês
    total_dias = monthrange(ano, mes)[1]
    datas_do_mes = [date(ano, mes, dia) for dia in range(1, total_dias + 1)]

    # Feriados cadastrados
    feriados = Feriado.objects.filter(data__month=mes, data__year=ano)
    feriados_dict = {f.data: f.descricao for f in feriados}

    # Sábados Letivos
    sabados_letivos = SabadoLetivo.objects.filter(data__month=mes, data__year=ano)
    sabados_letivos_dict = {sabado.data: sabado.descricao for sabado in sabados_letivos}

    # Horários atribuídos ao funcionário
    horarios = HorarioTrabalho.objects.filter(funcionario=funcionario)
    horario_manha = horarios.filter(turno='Manhã').first()
    horario_tarde = horarios.filter(turno='Tarde').first()

    dias_uteis = []
    for data_atual in datas_do_mes:
        dia_semana = dias_da_semana_pt[data_atual.weekday()]

        # Verificando se é sábado letivo e tratando como dia normal
        if data_atual.weekday() == 5 and data_atual in sabados_letivos_dict:
            # Tratar como dia normal (não feriado)
            dias_uteis.append({
                'data': data_atual,
                'dia_semana': dia_semana,
                'manha': horario_manha,
                'tarde': horario_tarde,
                'feriado': False,
                'sabado_letivo': True
            })
        elif data_atual in feriados_dict:
            dias_uteis.append({
                'data': data_atual,
                'dia_semana': dia_semana,
                'feriado': True,
                'descricao': feriados_dict[data_atual]
            })
        elif data_atual.weekday() < 5:  # Segunda a sexta
            dias_uteis.append({
                'data': data_atual,
                'dia_semana': dia_semana,
                'manha': horario_manha,
                'tarde': horario_tarde,
                'feriado': False
            })

    # Planejamento (somente para professores com planejamento)
    planejamento = []
    if funcionario.funcao.lower() == "professor(a)" and funcionario.tem_planejamento:
        for d in datas_do_mes:
            # Verificando se é segunda-feira e se não é feriado
            if d.weekday() == 0 and d not in feriados_dict:
                planejamento.append({
                    'data': d,
                    'dia_semana': dias_da_semana_pt[d.weekday()],
                    'horario': funcionario.horario_planejamento  # Exibe o horário de planejamento do funcionário
                })

    # Preparar contexto para o template
    context = {
        'funcionario': funcionario,
        'dias': dias_uteis,
        'planejamento': planejamento,
        'mes': mes,
        'ano': ano,
        'nome_mes': meses_pt[mes],  # Nome do mês por extenso
        'escola': escola,  # Adicionando os dados da escola
    }

    # Gerar HTML e salvar no banco
    html_renderizado = render_to_string('controle/folha_frequencia.html', context)
    FolhaFrequencia.objects.update_or_create(
        funcionario=funcionario,
        mes=mes,
        ano=ano,
        defaults={'html_armazenado': html_renderizado}
    )

    # Retornar a folha na tela para visualização/impressão
    return HttpResponse(html_renderizado)



def selecionar_funcionarios(request):
    setores = Setor.objects.all()
    funcionarios = []

    # Lista de meses para o template
    meses = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]

    if request.method == 'POST':
        setor_id = request.POST.get('setor')
        mes = int(request.POST.get('mes'))
        ano = int(request.POST.get('ano'))
        ids_funcionarios = request.POST.getlist('funcionarios')

        # Redireciona para a folha de um selecionado (ajustável)
        if ids_funcionarios:
            return HttpResponseRedirect(
                reverse('folha_frequencia', args=[ids_funcionarios[0], mes, ano])
            )

    elif request.method == 'GET' and 'setor' in request.GET:
        setor_id = request.GET.get('setor')
        if setor_id:
            funcionarios = Funcionario.objects.filter(setor__id=setor_id)

    return render(request, 'controle/selecionar_funcionarios.html', {
        'setores': setores,
        'funcionarios': funcionarios,
        'meses': meses,
    })


def listar_folhas(request):
    # Obtendo o nome do funcionário da barra de pesquisa (se houver)
    nome_funcionario = request.GET.get('nome', '')

    # Filtrando as folhas de acordo com o nome do funcionário, se o nome for fornecido
    if nome_funcionario:
        folhas = FolhaFrequencia.objects.filter(
            Q(funcionario__nome__icontains=nome_funcionario)
        )
    else:
        folhas = FolhaFrequencia.objects.all()

    return render(request, 'controle/listar_folhas.html', {'folhas': folhas})


def visualizar_folha_salva(request, folha_id):
    folha = get_object_or_404(FolhaFrequencia, id=folha_id)
    return HttpResponse(folha.html_armazenado)

from django.utils.safestring import mark_safe

# Mapeamento manual dos dias da semana
dias_da_semana_pt = {
    0: 'segunda-feira',
    1: 'terça-feira',
    2: 'quarta-feira',
    3: 'quinta-feira',
    4: 'sexta-feira',
    5: 'sábado',
    6: 'domingo'
}

# Mapeamento dos meses por extenso
meses_pt = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

from calendar import monthrange

def gerar_folhas_em_lote(request):
    if request.method == 'POST':
        ids_funcionarios = request.POST.getlist('funcionarios')
        mes = int(request.POST.get('mes'))
        ano = int(request.POST.get('ano'))

        folhas_renderizadas = []

        # Obter as informações da escola
        escola = Escola.objects.first()  # Se houver mais de uma escola, ajuste conforme necessário

        for id_func in ids_funcionarios:
            funcionario = get_object_or_404(Funcionario, id=id_func)

            # Obter todos os dias do mês
            total_dias = monthrange(ano, mes)[1]
            datas_do_mes = [date(ano, mes, dia) for dia in range(1, total_dias + 1)]

            # Calcular o último dia do mês
            ultimo_dia_mes = date(ano, mes, total_dias)

            # Feriados cadastrados
            feriados = Feriado.objects.filter(data__month=mes, data__year=ano)
            feriados_dict = {f.data: f.descricao for f in feriados}

            # Sábados Letivos
            sabados_letivos = SabadoLetivo.objects.filter(data__month=mes, data__year=ano)
            sabados_letivos_dict = {sabado.data: sabado.descricao for sabado in sabados_letivos}

            # Horários atribuídos ao funcionário
            horarios = HorarioTrabalho.objects.filter(funcionario=funcionario)
            horario_manha = horarios.filter(turno='Manhã').first()
            horario_tarde = horarios.filter(turno='Tarde').first()

            dias_uteis = []
            for data_atual in datas_do_mes:
                dia_semana = dias_da_semana_pt[data_atual.weekday()]

                # Verifica se o dia é um sábado letivo e trata como dia normal
                if data_atual.weekday() == 5 and data_atual in sabados_letivos_dict:
                    dias_uteis.append({
                        'data': data_atual,
                        'dia_semana': dia_semana,
                        'manha': horario_manha,
                        'tarde': horario_tarde,
                        'feriado': False,
                        'sabado_letivo': True  # Marca como sábado letivo
                    })
                elif data_atual in feriados_dict:
                    dias_uteis.append({
                        'data': data_atual,
                        'dia_semana': dia_semana,
                        'feriado': True,
                        'descricao': feriados_dict[data_atual]
                    })
                else:
                    dias_uteis.append({
                        'data': data_atual,
                        'dia_semana': dia_semana,
                        'manha': horario_manha,
                        'tarde': horario_tarde,
                        'feriado': False
                    })

            # Planejamento (somente para professores com planejamento)
            planejamento = []
            if funcionario.funcao.lower() == "professor(a)" and funcionario.tem_planejamento:
                for d in datas_do_mes:
                    if d.weekday() == 0 and d not in feriados_dict:  # Segunda-feira
                        planejamento.append({
                            'data': d,
                            'dia_semana': dias_da_semana_pt[d.weekday()],
                            'horario': funcionario.horario_planejamento
                        })

            # Preparar contexto para o template
            context = {
                'funcionario': funcionario,
                'dias': dias_uteis,
                'planejamento': planejamento,
                'mes': mes,
                'ano': ano,
                'nome_mes': meses_pt[mes],
                'ultimo_dia_mes': ultimo_dia_mes,  # Passando o último dia do mês
                'escola': escola,  # Adicionando os dados da escola
            }

            # Gerar HTML e salvar no banco
            html_folha = render_to_string('controle/folha_frequencia.html', context)

            FolhaFrequencia.objects.update_or_create(
                funcionario=funcionario,
                mes=mes,
                ano=ano,
                defaults={'html_armazenado': html_folha}
            )

            folhas_renderizadas.append(mark_safe(html_folha))

        return render(request, 'controle/folhas_em_lote.html', {'folhas': folhas_renderizadas})

    return render(request, 'controle/folhas_em_lote.html', {'folhas': []})




from .forms import FuncionarioForm
from django.shortcuts import redirect

def cadastrar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_funcionario')  # ou redirecionar para uma lista
    else:
        form = FuncionarioForm()

    return render(request, 'controle/cadastrar_funcionario.html', {'form': form})

def listar_funcionarios(request):
    funcionarios = Funcionario.objects.select_related('setor').order_by('nome')
    return render(request, 'controle/listar_funcionarios.html', {'funcionarios': funcionarios})

def editar_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)

    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')
    else:
        form = FuncionarioForm(instance=funcionario)

    return render(request, 'controle/editar_funcionario.html', {'form': form, 'funcionario': funcionario})

def cadastrar_horario(request):
    if request.method == 'POST':
        form = HorarioTrabalhoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_horario')
    else:
        form = HorarioTrabalhoForm()

    return render(request, 'controle/cadastrar_horario.html', {'form': form})

def cadastrar_feriado(request):
    feriados = Feriado.objects.order_by('data')

    if request.method == 'POST':
        form = FeriadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_feriado')
    else:
        form = FeriadoForm()

    return render(request, 'controle/cadastrar_feriado.html', {
        'form': form,
        'feriados': feriados
    })

def painel_controle(request):
    return render(request, 'controle/painel_controle.html')

def editar_feriado(request, feriado_id):
    feriado = get_object_or_404(Feriado, id=feriado_id)

    if request.method == 'POST':
        form = FeriadoForm(request.POST, instance=feriado)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_feriado')
    else:
        form = FeriadoForm(instance=feriado)

    return render(request, 'controle/editar_feriado.html', {'form': form, 'feriado': feriado})

def excluir_feriado(request, feriado_id):
    feriado = get_object_or_404(Feriado, id=feriado_id)
    feriado.delete()
    return redirect('cadastrar_feriado')

from django.contrib import messages

def cadastrar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('listar_funcionarios')
        else:
            messages.error(request, 'Erro ao cadastrar. Verifique os campos.')
    else:
        form = FuncionarioForm()

    return render(request, 'controle/cadastrar_funcionario.html', {'form': form})

def excluir_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    funcionario.delete()
    return redirect('listar_funcionarios')

def editar_horario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    
    # Verificar se o funcionário tem um horário de trabalho já registrado
    try:
        horario = HorarioTrabalho.objects.get(funcionario=funcionario)
    except HorarioTrabalho.DoesNotExist:
        horario = None

    if request.method == 'POST':
        form = HorarioTrabalhoForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')  # Ou redirecionar para a página de lista de funcionários
    else:
        form = HorarioTrabalhoForm(instance=horario)
    
    return render(request, 'controle/editar_horario.html', {
        'form': form,
        'funcionario': funcionario
    })

def excluir_folha(request, folha_id):
    folha = get_object_or_404(FolhaFrequencia, id=folha_id)
    folha.delete()
    return redirect('listar_folhas')