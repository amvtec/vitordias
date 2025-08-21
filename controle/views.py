
import calendar
import locale
from calendar import monthrange, day_name
from datetime import date, datetime, timedelta


import pandas as pd


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe


from .forms import (
    HorarioTrabalhoForm,
    FeriadoForm,
    ImportacaoFuncionarioForm,
    GerarFolhasIndividuaisForm,
    FuncionarioForm,
)
from .models import (
    Setor,
    Funcionario,
    Feriado,
    HorarioTrabalho,
    SabadoLetivo,
    FolhaFrequencia,
    Escola,
)



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

# Mapeamento manual dos meses
meses_pt = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

@login_required
def gerar_folha_frequencia(request, funcionario_id, mes, ano):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    escola = Escola.objects.first()

    total_dias = monthrange(ano, mes)[1]
    datas_do_mes = [date(ano, mes, dia) for dia in range(1, total_dias + 1)]

    feriados = Feriado.objects.filter(data__month=mes, data__year=ano)
    feriados_dict = {f.data: f.descricao for f in feriados}

    sabados_letivos = SabadoLetivo.objects.filter(data__month=mes, data__year=ano)
    sabados_letivos_dict = {sabado.data: sabado.descricao for sabado in sabados_letivos}

    horarios = HorarioTrabalho.objects.filter(funcionario=funcionario)
    horario_manha = horarios.filter(turno='Manhã').first()
    horario_tarde = horarios.filter(turno='Tarde').first()

    dias_uteis = []

    for data_atual in datas_do_mes:
        dia_semana = dias_da_semana_pt[data_atual.weekday()]

        if data_atual.weekday() == 5 and data_atual in sabados_letivos_dict:
            # Sábado letivo
            dias_uteis.append({
                'data': data_atual,
                'dia_semana': dia_semana,
                'manha': horario_manha,
                'tarde': horario_tarde,
                'feriado': False,
                'sabado_letivo': True
            })
        elif data_atual in feriados_dict:
            # Feriado COM horários incluídos
            dias_uteis.append({
                'data': data_atual,
                'dia_semana': dia_semana,
                'manha': horario_manha,
                'tarde': horario_tarde,
                'feriado': True,
                'descricao': feriados_dict[data_atual]
            })
        elif data_atual.weekday() < 5:
            # Dias úteis normais
            dias_uteis.append({
                'data': data_atual,
                'dia_semana': dia_semana,
                'manha': horario_manha,
                'tarde': horario_tarde,
                'feriado': False
            })

    # Planejamento para professores
    planejamento = []
    if funcionario.funcao.lower() == "professor(a)" and funcionario.tem_planejamento:
        for d in datas_do_mes:
            if d.weekday() == 0 and d not in feriados_dict:
                planejamento.append({
                    'data': d,
                    'dia_semana': dias_da_semana_pt[d.weekday()],
                    'horario': funcionario.horario_planejamento
                })

    context = {
        'funcionario': funcionario,
        'dias': dias_uteis,
        'planejamento': planejamento,
        'mes': mes,
        'ano': ano,
        'nome_mes': meses_pt[mes],
        'escola': escola,
    }

    html_renderizado = render_to_string('controle/folha_frequencia.html', context)

    FolhaFrequencia.objects.update_or_create(
        funcionario=funcionario,
        mes=mes,
        ano=ano,
        defaults={'html_armazenado': html_renderizado}
    )

    return HttpResponse(html_renderizado)


@login_required
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

@login_required
def listar_folhas(request):
    from django.db.models.functions import Lower  # import local p/ não mexer no topo
    # Obtendo o nome do funcionário da barra de pesquisa (se houver)
    nome_funcionario = request.GET.get('nome', '').strip()

    # Base + join no funcionário e anotação para ordenar por nome (case-insensitive)
    qs = (FolhaFrequencia.objects
          .select_related('funcionario')
          .annotate(nome_i=Lower('funcionario__nome')))

    # Filtrando as folhas de acordo com o nome do funcionário, se o nome for fornecido
    if nome_funcionario:
        qs = qs.filter(funcionario__nome__icontains=nome_funcionario)

    # ✅ Ordenação: nome (A→Z), depois ano e mês
    folhas = qs.order_by('nome_i', 'ano', 'mes')

    return render(request, 'controle/listar_folhas.html', {'folhas': folhas})


@login_required
def visualizar_folha_salva(request, folha_id):
    folha = get_object_or_404(FolhaFrequencia, id=folha_id)
    return HttpResponse(folha.html_armazenado)


# Mapeamento dos dias da semana
dias_da_semana_pt = {
    0: 'segunda-feira',
    1: 'terça-feira',
    2: 'quarta-feira',
    3: 'quinta-feira',
    4: 'sexta-feira',
    5: 'sábado',
    6: 'domingo'
}

# Mapeamento dos meses
meses_pt = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

@login_required
def gerar_folhas_em_lote(request):
    if request.method == 'POST':
        ids_funcionarios = request.POST.getlist('funcionarios')
        mes = int(request.POST.get('mes'))
        ano = int(request.POST.get('ano'))

        folhas_renderizadas = []
        escola = Escola.objects.first()

        # 👉 Ordena os IDs alfabeticamente pelo nome (case-insensitive),
        #    sem remover o get_object_or_404 do loop.
        nomes_qs = Funcionario.objects.filter(id__in=ids_funcionarios).values('id', 'nome')
        mapa_nomes = {str(f['id']): (f['nome'] or '') for f in nomes_qs}
        ids_funcionarios_ordenados = sorted(
            ids_funcionarios,
            key=lambda pk: mapa_nomes.get(str(pk), '').casefold()
        )

        for id_func in ids_funcionarios_ordenados:
            funcionario = get_object_or_404(Funcionario, id=id_func)

            total_dias = monthrange(ano, mes)[1]
            datas_do_mes = [date(ano, mes, dia) for dia in range(1, total_dias + 1)]
            ultimo_dia_mes = date(ano, mes, total_dias)

            feriados = Feriado.objects.filter(data__month=mes, data__year=ano)
            feriados_dict = {f.data: f.descricao for f in feriados}

            sabados_letivos = SabadoLetivo.objects.filter(data__month=mes, data__year=ano)
            sabados_letivos_dict = {sabado.data: sabado.descricao for sabado in sabados_letivos}

            horarios = HorarioTrabalho.objects.filter(funcionario=funcionario)
            horario_manha = horarios.filter(turno='Manhã').first()
            horario_tarde = horarios.filter(turno='Tarde').first()

            dias_uteis = []
            for data_atual in datas_do_mes:
                dia_semana = dias_da_semana_pt[data_atual.weekday()]

                if data_atual.weekday() == 5 and data_atual in sabados_letivos_dict:
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
                        'manha': horario_manha,
                        'tarde': horario_tarde,
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

            planejamento = []
            if funcionario.funcao.lower() == "professor(a)" and funcionario.tem_planejamento:
                for d in datas_do_mes:
                    if d.weekday() == 0 and d not in feriados_dict:
                        planejamento.append({
                            'data': d,
                            'dia_semana': dias_da_semana_pt[d.weekday()],
                            'horario': funcionario.horario_planejamento
                        })

            context = {
                'funcionario': funcionario,
                'dias': dias_uteis,
                'planejamento': planejamento,
                'mes': mes,
                'ano': ano,
                'nome_mes': meses_pt[mes],
                'ultimo_dia_mes': ultimo_dia_mes,
                'escola': escola,
            }

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


@login_required
def cadastrar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)  # <-- Adicionado request.FILES aqui
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')
        else:
            print(form.errors)  # Opcional para depuração
    else:
        form = FuncionarioForm()

    return render(request, 'controle/cadastrar_funcionario.html', {'form': form})

@login_required
def listar_funcionarios(request):
    funcionarios = Funcionario.objects.select_related('setor').order_by('nome')
    return render(request, 'controle/listar_funcionarios.html', {'funcionarios': funcionarios})

@login_required
def editar_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)

    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES, instance=funcionario)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')
        else:
            print(form.errors)
    else:
        form = FuncionarioForm(instance=funcionario)

    return render(request, 'controle/editar_funcionario.html', {
        'form': form,
        'funcionario': funcionario
    })

@login_required
def cadastrar_horario(request):
    if request.method == 'POST':
        form = HorarioTrabalhoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_horario')
    else:
        form = HorarioTrabalhoForm()

    return render(request, 'controle/cadastrar_horario.html', {'form': form})
@login_required
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
@login_required
def painel_controle(request):
    return render(request, 'controle/painel_controle.html')
@login_required
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
@login_required
def excluir_feriado(request, feriado_id):
    feriado = get_object_or_404(Feriado, id=feriado_id)
    feriado.delete()
    return redirect('cadastrar_feriado')

from django.contrib import messages
@login_required
def cadastrar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)  # ⬅️ inclui request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('listar_funcionarios')
        else:
            messages.error(request, 'Erro ao cadastrar. Verifique os campos.')
    else:
        form = FuncionarioForm()

    return render(request, 'controle/cadastrar_funcionario.html', {'form': form})
@login_required
def excluir_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    funcionario.delete()
    return redirect('listar_funcionarios')
@login_required
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
@login_required
def excluir_folha(request, folha_id):
    folha = get_object_or_404(FolhaFrequencia, id=folha_id)
    folha.delete()
    return redirect('listar_folhas')

@login_required
def painel_controle(request):
    # Data “hoje” segura (timezone-aware)
    hoje_date = timezone.localdate()
    agora = timezone.now()

    # Contadores principais
    funcionarios_count = Funcionario.objects.count()
    horarios_count = HorarioTrabalho.objects.count()
    feriados_count = Feriado.objects.count()

    # Folhas geradas nos últimos 30 dias (fallback para TOTAL se não houver campo de data)
    cutoff = agora - timedelta(days=30)
    folhas_qs = FolhaFrequencia.objects.all()

    # Descobre dinamicamente um campo de data (se existir)
    field_names = {f.name for f in FolhaFrequencia._meta.get_fields()}
    if 'created_at' in field_names:
        folhas_qs = folhas_qs.filter(created_at__gte=cutoff)
    elif 'criado_em' in field_names:
        folhas_qs = folhas_qs.filter(criado_em__gte=cutoff)
    elif 'data_criacao' in field_names:
        folhas_qs = folhas_qs.filter(data_criacao__gte=cutoff)
    elif 'updated_at' in field_names:
        folhas_qs = folhas_qs.filter(updated_at__gte=cutoff)
    elif 'atualizado_em' in field_names:
        folhas_qs = folhas_qs.filter(atualizado_em__gte=cutoff)
    # se nenhum campo de data existir, mantém todas (conta total)
    folhas_30d_q = folhas_qs.count()

    # Aniversariantes (listas para o template usar |length)
    aniversariantes_mes = (Funcionario.objects
                           .filter(data_nascimento__month=hoje_date.month)
                           .order_by(Lower('nome')))
    aniversariantes_dia = (Funcionario.objects
                           .filter(data_nascimento__month=hoje_date.month,
                                   data_nascimento__day=hoje_date.day)
                           .order_by(Lower('nome')))

    context = {
        'funcionarios_count': funcionarios_count,
        'horarios_count': horarios_count,
        'feriados_count': feriados_count,
        'folhas_30d_q': folhas_30d_q,
        'aniversariantes_mes': aniversariantes_mes,
        'aniversariantes_dia': aniversariantes_dia,
    }
    return render(request, 'controle/painel_controle.html', context)


@login_required
def importar_funcionarios(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        # Verifica se é um arquivo Excel
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Por favor, envie um arquivo Excel (.xlsx ou .xls).")
            return render(request, 'controle/importar_funcionarios.html')

        try:
            df = pd.read_excel(excel_file)

            # Converte datas
            if 'Data de Admissão' in df.columns:
                df['Data de Admissão'] = pd.to_datetime(df['Data de Admissão'], dayfirst=True, errors='coerce')
            if 'Data de Nascimento' in df.columns:
                df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento'], dayfirst=True, errors='coerce')

            total_importados = 0

            for _, row in df.iterrows():
                setor = Setor.objects.filter(nome=str(row.get('Setor')).strip()).first()
                if not setor:
                    continue  # ignora se o setor não existir

                funcionario_data = {
                    'nome': str(row.get('Nome', '')).strip(),
                    'cargo': str(row.get('Cargo', '')).strip(),
                    'funcao': str(row.get('Função', '')).strip(),
                    'data_admissao': row.get('Data de Admissão'),
                    'setor': setor,
                    'tem_planejamento': str(row.get('Tem Planejamento', '')).strip().lower() in ['sim', 'true', '1'],
                    'horario_planejamento': str(row.get('Horário Planejamento', '')).strip() or None,
                    'sabado_letivo': str(row.get('Sábado Letivo', '')).strip().lower() in ['sim', 'true', '1'],
                    'data_nascimento': row.get('Data de Nascimento')
                }

                matricula = str(row.get('Matrícula', '')).strip()
                if matricula:
                    Funcionario.objects.update_or_create(
                        matricula=matricula,
                        defaults=funcionario_data
                    )
                    total_importados += 1

            messages.success(request, f'{total_importados} funcionários foram importados com sucesso.')

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao importar o arquivo: {e}')

    return render(request, 'controle/importar_funcionarios.html')

@login_required
def importar_horarios_trabalho(request):
    if request.method == 'POST' and request.FILES.get('arquivo_horarios'):
        arquivo = request.FILES['arquivo_horarios']

        if not arquivo.name.endswith(('.xlsx', '.xls', '.csv')):
            messages.error(request, "Envie um arquivo .xlsx, .xls ou .csv válido.")
            return render(request, 'controle/importar_horarios.html')

        try:
            # Lê o arquivo
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)

            total_importados = 0

            for _, row in df.iterrows():
                nome = str(row.get('nome')).strip()
                turno = str(row.get('turno')).strip().capitalize()
                funcionario = Funcionario.objects.filter(nome__iexact=nome).first()

                if funcionario:
                    horario_inicio = datetime.strptime(str(row.get('horario_inicio')), '%H:%M:%S').time()
                    horario_fim = datetime.strptime(str(row.get('horario_fim')), '%H:%M:%S').time()

                    HorarioTrabalho.objects.update_or_create(
                        funcionario=funcionario,
                        turno=turno,
                        defaults={
                            'horario_inicio': horario_inicio,
                            'horario_fim': horario_fim
                        }
                    )
                    total_importados += 1
                else:
                    messages.warning(request, f'Funcionário não encontrado: {nome}')

            messages.success(request, f'{total_importados} horários de trabalho importados com sucesso.')

        except Exception as e:
            messages.error(request, f'Erro ao importar horários: {e}')

    return render(request, 'controle/importar_horarios.html')

def capas_livro_ponto(request):
    setor = request.GET.get('setor')
    ano = int(request.GET.get('ano'))
    mes = int(request.GET.get('mes'))

    escola = Escola.objects.first()

    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR')
        except:
            pass

    nome_mes = date(ano, mes, 1).strftime('%B').capitalize()

    # ⬇️ Calcula primeiro e último dia do mês
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])

    data_abertura = primeiro_dia.strftime('%d de %B de %Y')
    data_encerramento = ultimo_dia.strftime('%d de %B de %Y')

    paginas = FolhaFrequencia.objects.filter(
        funcionario__setor__nome=setor,
        mes=mes,
        ano=ano
    ).count()

    context = {
        'escola': escola,
        'setor': setor.upper(),
        'ano': ano,
        'mes': mes,
        'nome_mes': nome_mes.upper(),
        'paginas': paginas,
        'data_abertura': data_abertura,
        'data_encerramento': data_encerramento,
        'cidade': escola.cidade,
        'uf': escola.uf,
    }
    return render(request, 'controle/capas_livro_ponto.html', context)

def selecionar_setor_capa(request):
    setores = Setor.objects.all()
    hoje = date.today()
    context = {
        'setores': setores,
        'ano': hoje.year,
        'mes': hoje.month
    }
    return render(request, 'controle/selecionar_capa.html', context)

def ficha_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    escola = Escola.objects.first()
    return render(request, 'controle/ficha_funcionario.html', {
        'funcionario': funcionario,
        'dias_semana': dias_semana,
        'escola': escola,
    })

@login_required
def relatorio_personalizado_funcionarios(request):
    funcionarios = Funcionario.objects.all()

    # Filtros aplicados via checkboxes
    filtro_serie = request.POST.getlist('filtro_serie')
    filtro_turma = request.POST.getlist('filtro_turma')
    filtro_turno = request.POST.getlist('filtro_turno')
    filtro_setor = request.POST.getlist('filtro_setor')
    filtro_vinculo = request.POST.getlist('filtro_vinculo')  # NOVO filtro

    if filtro_serie:
        funcionarios = funcionarios.filter(serie__in=filtro_serie)
    if filtro_turma:
        funcionarios = funcionarios.filter(turma__in=filtro_turma)
    if filtro_turno:
        funcionarios = funcionarios.filter(turno__in=filtro_turno)
    if filtro_setor:
        funcionarios = funcionarios.filter(setor__nome__in=filtro_setor)
    if filtro_vinculo:
        funcionarios = funcionarios.filter(tipo_vinculo__in=filtro_vinculo)

    funcionarios = funcionarios.order_by('nome')

    # Campos disponíveis
    campos_disponiveis = [
        ('nome', 'Nome'),
        ('matricula', 'Matrícula'),
        ('cargo', 'Cargo'),
        ('funcao', 'Função'),
        ('setor', 'Setor'),
        ('data_admissao', 'Data de Admissão'),
        ('data_nascimento', 'Data de Nascimento'),
        ('cpf', 'CPF'),
        ('rg', 'RG'),
        ('pis', 'PIS'),
        ('titulo_eleitor', 'Título de Eleitor'),
        ('ctps_numero', 'CTPS Nº'),
        ('ctps_serie', 'CTPS Série'),
        ('telefone', 'Telefone'),
        ('email', 'Email'),
        ('endereco', 'Endereço'),
        ('numero', 'Número'),
        ('bairro', 'Bairro'),
        ('cidade', 'Cidade'),
        ('uf', 'UF'),
        ('cep', 'CEP'),
        ('estado_civil', 'Estado Civil'),
        ('escolaridade', 'Escolaridade'),
        ('tem_planejamento', 'Planejamento'),
        ('horario_planejamento', 'Horário Planejamento'),
        ('sabado_letivo', 'Sábado Letivo'),
        ('turma', 'Turma'),
        ('turno', 'Turno'),
        ('serie', 'Série'),
        ('tipo_vinculo', 'Tipo de Vínculo'),
        ('fonte_pagadora', 'Fonte Pagadora'),
    ]

    # Campos selecionados pelo usuário
    campos_selecionados = request.POST.getlist('campos') if request.method == 'POST' else []

    # Valores únicos para filtros
    series = Funcionario.objects.exclude(serie__isnull=True).exclude(serie__exact='').values_list('serie', flat=True).distinct()
    turmas = Funcionario.objects.exclude(turma__isnull=True).exclude(turma__exact='').values_list('turma', flat=True).distinct()
    turnos = Funcionario.objects.exclude(turno__isnull=True).exclude(turno__exact='').values_list('turno', flat=True).distinct()
    setores = Setor.objects.all()
    vinculos = Funcionario.objects.exclude(tipo_vinculo__isnull=True).exclude(tipo_vinculo__exact='').values_list('tipo_vinculo', flat=True).distinct()

    escola = Escola.objects.first()

    return render(request, 'controle/relatorio_personalizado_funcionarios.html', {
        'funcionarios': funcionarios,
        'campos_disponiveis': campos_disponiveis,
        'campos_selecionados': campos_selecionados,
        'escola': escola,
        'series': series,
        'turmas': turmas,
        'turnos': turnos,
        'setores': setores,
        'vinculos': vinculos,
        'filtro_serie': filtro_serie,
        'filtro_turma': filtro_turma,
        'filtro_turno': filtro_turno,
        'filtro_setor': filtro_setor,
        'filtro_vinculo': filtro_vinculo,  # Enviado para o template
    })

def relatorio_professores(request):
    series = sorted([s for s in set(Funcionario.objects.values_list('serie', flat=True)) if s is not None])
    turmas = sorted([t for t in set(Funcionario.objects.values_list('turma', flat=True)) if t is not None])
    turnos = sorted([t for t in set(Funcionario.objects.values_list('turno', flat=True)) if t is not None])

    setores = Setor.objects.all()

    filtro_serie = request.POST.getlist('filtro_serie')
    filtro_turma = request.POST.getlist('filtro_turma')
    filtro_turno = request.POST.getlist('filtro_turno')
    filtro_setor = request.POST.getlist('filtro_setor')
    campos_selecionados = request.POST.getlist('campos')

    funcionarios = Funcionario.objects.filter(funcao__iexact="PROFESSOR(A)")

    if filtro_serie:
        funcionarios = funcionarios.filter(serie__in=filtro_serie)
    if filtro_turma:
        funcionarios = funcionarios.filter(turma__in=filtro_turma)
    if filtro_turno:
        funcionarios = funcionarios.filter(turno__in=filtro_turno)
    if filtro_setor:
        funcionarios = funcionarios.filter(setor__nome__in=filtro_setor)

    # Ordena com segurança, tratando None como string
    funcionarios = sorted(
        funcionarios, 
        key=lambda f: (str(f.serie or ""), str(f.turma or ""))
    )

    campos_disponiveis = [
        ('nome', 'Nome'),
        ('matricula', 'Matrícula'),
        ('serie', 'Série'),
        ('turma', 'Turma'),
        ('turno', 'Turno'),
        ('setor', 'Setor'),
        ('telefone', 'Telefone'),
        ('email', 'Email'),
        ('vinculo', 'Tipo de Vínculo'),
    ]

    escola = Escola.objects.first() if Escola.objects.exists() else None

    contexto = {
        'escola': escola,
        'series': series,
        'turmas': turmas,
        'turnos': turnos,
        'setores': setores,
        'filtro_serie': filtro_serie,
        'filtro_turma': filtro_turma,
        'filtro_turno': filtro_turno,
        'filtro_setor': filtro_setor,
        'campos_disponiveis': campos_disponiveis,
        'campos_selecionados': campos_selecionados,
        'funcionarios': funcionarios,
    }
    return render(request, 'controle/relatorio_professores.html', contexto)


def relatorios_funcionarios(request):
    return render(request, 'controle/relatorios_funcionarios.html')


@login_required
def gerar_folhas_multimes_funcionario(request):
    folhas_geradas = []
    anos = list(range(2025, 2031))  # ⬅️ de 2025 até 2030

    if request.method == 'POST':
        form = GerarFolhasIndividuaisForm(request.POST)
        if form.is_valid():
            funcionario = form.cleaned_data['funcionario']
            ano = form.cleaned_data['ano']
            meses = list(map(int, form.cleaned_data['meses']))

            for mes in meses:
                response = gerar_folha_frequencia(request, funcionario.id, mes, ano)
                folhas_geradas.append(response.content.decode())
    else:
        form = GerarFolhasIndividuaisForm()

    return render(request, 'controle/gerar_folhas_individuais.html', {
        'form': form,
        'folhas_geradas': folhas_geradas,
        'anos': anos,
    })

from django.db.models import Prefetch
from django.utils import timezone
import io
import pandas as pd

@login_required
def relatorio_horarios(request):
    """
    Lista horários (Manhã/Tarde) por servidor, com filtros e exportação para Excel.
    """
    funcionarios_qs = (
        Funcionario.objects
        .select_related('setor')
        .prefetch_related(
            Prefetch(
                'horariotrabalho_set',            # nome reverso padrão correto
                queryset=HorarioTrabalho.objects.order_by('turno')
            )
        )
        .order_by(Lower('nome'))
    )

    # ---- Filtros via GET ----
    setor_id   = request.GET.get('setor') or ''
    turno_func = request.GET.get('turno') or ''
    serie      = request.GET.get('serie') or ''
    turma      = request.GET.get('turma') or ''
    vinculo    = request.GET.get('vinculo') or ''

    if setor_id:
        funcionarios_qs = funcionarios_qs.filter(setor_id=setor_id)
    if turno_func:
        funcionarios_qs = funcionarios_qs.filter(turno=turno_func)
    if serie:
        funcionarios_qs = funcionarios_qs.filter(serie=serie)
    if turma:
        funcionarios_qs = funcionarios_qs.filter(turma=turma)
    if vinculo:
        funcionarios_qs = funcionarios_qs.filter(tipo_vinculo=vinculo)

    def fmt_hora(t):
        return t.strftime('%H:%M') if t else ''

    def fmt_data(d):
        return d.strftime('%d/%m/%Y') if d else ''

    linhas = []
    for f in funcionarios_qs:
        horarios = list(f.horariotrabalho_set.all())
        manha = next((h for h in horarios if h.turno == 'Manhã'), None)
        tarde = next((h for h in horarios if h.turno == 'Tarde'), None)

        linhas.append({
            'Nome': f.nome,
            'Matrícula': f.matricula,
            'Setor': f.setor.nome if f.setor else '',

            # >>> NOVOS CAMPOS <<<
            'Cargo': f.cargo or '',
            'Função': f.funcao or '',
            'Data de Admissão': fmt_data(f.data_admissao),

            'Série': f.serie or '',
            'Turma': f.turma or '',
            'Turno (cadastro)': f.turno or '',
            'Vínculo': f.tipo_vinculo or '',
            'Manhã - Início': fmt_hora(manha.horario_inicio) if manha else '',
            'Manhã - Fim': fmt_hora(manha.horario_fim) if manha else '',
            'Tarde - Início': fmt_hora(tarde.horario_inicio) if tarde else '',
            'Tarde - Fim': fmt_hora(tarde.horario_fim) if tarde else '',
        })

    # ---- Exportação Excel (ou CSV fallback) ----
    if request.GET.get('export') == '1':
        df = pd.DataFrame(linhas)
        filename = f"relatorio_horarios_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"

        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Horários')
            output.seek(0)
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception:
            csv_bytes = df.to_csv(index=False, sep=';').encode('utf-8-sig')
            response = HttpResponse(csv_bytes, content_type='text/csv; charset=utf-8')
            # fix de aspas no replace
            response['Content-Disposition'] = f'attachment; filename="{filename.replace(".xlsx", ".csv")}"'
            return response

    setores = Setor.objects.all().order_by('nome')
    series = (Funcionario.objects
              .exclude(serie__isnull=True).exclude(serie__exact='')
              .values_list('serie', flat=True).distinct().order_by('serie'))
    turmas = (Funcionario.objects
              .exclude(turma__isnull=True).exclude(turma__exact='')
              .values_list('turma', flat=True).distinct().order_by('turma'))
    turnos_func = (Funcionario.objects
                   .exclude(turno__isnull=True).exclude(turno__exact='')
                   .values_list('turno', flat=True).distinct().order_by('turno'))
    vinculos = (Funcionario.objects
                .exclude(tipo_vinculo__isnull=True).exclude(tipo_vinculo__exact='')
                .values_list('tipo_vinculo', flat=True).distinct().order_by('tipo_vinculo'))

    escola = Escola.objects.first()

    context = {
        'escola': escola,
        'linhas': linhas,
        'setores': setores,
        'series': series,
        'turmas': turmas,
        'turnos_func': turnos_func,
        'vinculos': vinculos,
        'filtros': {
            'setor': setor_id,
            'turno': turno_func,
            'serie': serie,
            'turma': turma,
            'vinculo': vinculo
        }
    }
    return render(request, 'controle/relatorio_horarios.html', context)