from django.shortcuts import render, redirect
from .forms import AlunoForm
from .models import Aluno
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import tempfile
from django.template.loader import render_to_string
import io
import pandas as pd
from django.http import JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.http import HttpResponse
from .models import Aluno
import os
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from .models import Aluno
import os
from .utils import avancar_ano_serie
from django.urls import reverse
from reportlab.platypus import Image as RLImage
from datetime import datetime, date
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from .forms import FuncionarioForm
from .models import Funcionario
from .models import Escola
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import date
from collections import Counter
from .models import Turma
from datetime import date
from calendar import monthrange
from django.utils import timezone


@login_required
def pagina_matricula(request):
    return render(request, 'alunos/pagina_matricula.html')


@login_required
def buscar_aluno_rematricula(request):
    if request.method == 'POST':
        termo = request.POST.get('busca')
        alunos = Aluno.objects.filter(nome__icontains=termo)
        return render(request, 'alunos/buscar_rematricula.html', {'alunos': alunos, 'termo': termo})
    return render(request, 'alunos/buscar_rematricula.html')



@login_required
def rematricula_formulario(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    ano_atual = datetime.now().year

    if aluno.ano_rematricula == ano_atual:
        return render(request, "alunos/ja_rematriculado.html", {"aluno": aluno})

    if request.method == "POST":
        resultado = request.POST.get("resultado")
        if resultado == "aprovado":
            aluno.ano_serie = avancar_ano_serie(aluno.ano_serie)
        # Se reprovado, não muda de série
        aluno.status = "veterano"
        aluno.ano_rematricula = ano_atual
        aluno.save()
        return redirect("gerar_pdf_matricula", aluno_id=aluno.id)

    return render(request, "alunos/rematricula_ficha.html", {"aluno": aluno})

@login_required
def aluno_cadastrado(request, aluno_id):
    return render(request, 'alunos/aluno_cadastrado.html', {'aluno_id': aluno_id})

@login_required
def imprimir_matricula(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return render(request, 'alunos/imprimir_matricula.html', {'aluno': aluno})

@login_required
def gerar_pdf_matricula(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    usuario_logado = request.user.username if request.user.is_authenticated else "Desconhecido"
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    escola = Escola.objects.first()
    diretor = Funcionario.objects.filter(funcao='Diretor(a)').first()
    secretario = Funcionario.objects.filter(funcao='Secretario(a)').first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=matricula_{aluno.nome}.pdf'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(name="Normal", fontSize=7, leading=8)
    center = ParagraphStyle(name="Center", fontSize=7, alignment=1, leading=8)
    title_style = ParagraphStyle(name="TitleBlock", parent=normal, fontSize=7, alignment=1,
                                 textColor=colors.white, backColor=colors.grey, spaceAfter=3)
    small_style = ParagraphStyle(name="Small", fontSize=6, leading=8, alignment=0)
    elements = []

    def dado(texto):
        return Paragraph(texto if texto else "Não informado", normal)

    def campo(label, valor):
        return Paragraph(f"<b>{label}:</b> {valor if valor else 'Não informado'}", normal)

    def bloco_titulo(titulo):
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(titulo, title_style))
        elements.append(Spacer(1, 4))

    try:
        if aluno.foto:
            foto_path = os.path.join(settings.MEDIA_ROOT, aluno.foto.name)
            foto = RLImage(foto_path)
            foto.drawHeight = 0.9 * inch
            foto.drawWidth = 0.7 * inch
        else:
            foto = None
    except:
        foto = None

    escola_nome = escola.nome_escola if escola else "ESCOLA MUNICIPAL"
    secretaria_nome = escola.nome_secretaria if escola else "SECRETARIA MUNICIPAL DE EDUCAÇÃO"
    cnpj = escola.cnpj if escola else "00.000.000/0000-00"
    endereco = f"{escola.endereco}, {escola.numero}, {escola.bairro}, {escola.cidade}/{escola.uf}" if escola else "Endereço não cadastrado"
    contato = f"Telefone: {escola.telefone} | E-mail: {escola.email}" if escola else "Contato não cadastrado"

    cabecalho_texto = [
        [Paragraph(f"<b>{secretaria_nome}</b>", center)],
        [Paragraph(f"<b>{escola_nome}</b>", center)],
        [Paragraph(f"CNPJ: {cnpj}", center)],
        [Paragraph(f"Endereço: {endereco}", center)],
        [Paragraph(f"{contato}", center)],
    ]
    tabela_texto = Table(cabecalho_texto, colWidths=[500])
    tabela_texto.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
    ]))

    if foto:
        cabecalho_completo = Table([
            [tabela_texto, foto]
        ], colWidths=[460, 60])
        cabecalho_completo.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(cabecalho_completo)
    else:
        elements.append(tabela_texto)

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>FICHA DE MATRÍCULA – 2025</b>", ParagraphStyle(name="Header", fontSize=9, alignment=1)))
    elements.append(Spacer(1, 4))

    # Blocos 1 a 6 (mantidos do código anterior, exatamente iguais)
    # Bloco 1: Informações Escolares
    bloco_titulo("1. Informações Escolares")
    tabela1 = Table([
        [dado("(X) Aluno Veterano" if aluno.status == "veterano" else "( ) Aluno Veterano"),
         dado("(X) Aluno Novato" if aluno.status == "novato" else "( ) Aluno Novato")],
        [campo("Unidade Escolar", aluno.unidade_escolar), campo("Município", aluno.municipio), campo("DRE", aluno.dre)],
        [Paragraph(
            f"{('(X)' if aluno.modalidade == 'regular' else '( )')} Regular    "
            f"{('(X)' if aluno.modalidade == 'eja' else '( )')} EJA    "
            f"{('(X)' if aluno.modalidade == 'especial' else '( )')} Especial    "
            f"{('(X)' if aluno.modalidade == 'outra' else '( )')} Outra: {aluno.outra_modalidade or ''}", normal)],
        [campo("Etapa", aluno.etapa), campo("Ano/Série", aluno.ano_serie), campo("Ensino Religioso", "Sim" if aluno.ensino_religioso else "Não")],
        [campo("Turno", aluno.turno)],
    ])
    tabela1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela1)

    # Bloco 2: Dados Pessoais
    bloco_titulo("2. Dados Pessoais")
    tabela2 = Table([
        [campo("Nome", aluno.nome), campo("Sexo", aluno.get_sexo_display()), campo("ID", aluno.aluno_id), campo("NIS", aluno.nis)],
        [
        campo("Nascimento", aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else None),
        campo("Profissão", aluno.profissao),
        campo("Raça/Cor", aluno.cor_raca)
        ],
        [campo("Endereço", aluno.endereco), campo("Bairro", aluno.bairro), campo("CEP", aluno.cep)],
        [campo("Cidade", aluno.cidade), campo("UF", aluno.uf), campo("Zona", aluno.get_zona_display())],
        [campo("Transporte Escolar", "Sim" if aluno.transporte_escolar else "Não"), campo("Rota", aluno.rota), campo("Distância", aluno.distancia)],
        [campo("Cidade Nasc.", aluno.cidade_nascimento), campo("UF Nasc.", aluno.uf_nascimento), campo("Nacionalidade", aluno.nacionalidade)],
        [campo("Nº Certidão", aluno.certidao_numero), campo("Folha", aluno.certidao_folha), campo("Livro", aluno.certidao_livro)],
        [campo("Matrícula", aluno.numero_matricula)],
        [campo("Cartório", aluno.cartorio_nome), campo("UF", aluno.cartorio_uf), campo("Cidade Cartório", aluno.cartorio_cidade)],
        [campo("CPF", aluno.cpf), campo("RG", aluno.rg)],
    ])
    tabela2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela2)

    # Bloco 3: Responsáveis
    bloco_titulo("3. Responsáveis")
    tabela3 = Table([
        [campo("Pai", aluno.nome_pai), campo("Nascimento", aluno.nascimento_pai.strftime('%d/%m/%Y') if aluno.nascimento_pai else None), campo("Telefone", aluno.telefone_pai)],
        [campo("Escolaridade Pai", aluno.escolaridade_pai), campo("Profissão Pai", aluno.profissao_pai)],
        [campo("Mãe", aluno.nome_mae), campo("Nascimento", aluno.nascimento_mae.strftime('%d/%m/%Y') if aluno.nascimento_mae else None), campo("Telefone", aluno.telefone_mae)],
        [campo("Escolaridade Mãe", aluno.escolaridade_mae), campo("Profissão Mãe", aluno.profissao_mae)],
    ])
    tabela3.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela3)

    # Bloco 4: Saúde e Necessidades
    bloco_titulo("4. Saúde e Necessidades")
    tabela4 = Table([
        [campo("Reações Alérgicas", "Sim" if aluno.reacoes_alergicas else "Não"), campo("Descrição", aluno.descricao_alergia)],
        [campo("Necessidade Especial", "Sim" if aluno.necessidade_especial else "Não"), campo("Descrição", aluno.descricao_necessidade)],
        [campo("Possui Laudo", "Sim" if aluno.possui_laudo else "Não"), campo("Sala Recursos", "Sim" if aluno.sala_recursos else "Não")],
        [campo("Medicamento Controlado", "Sim" if aluno.medicamento_controlado else "Não"), campo("Qual Medicamento", aluno.nome_medicamento)],
        [campo("UE Atendimento", aluno.ue_atendimento)],
    ])
    tabela4.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela4)

    # Bloco 5: Programas Sociais
    bloco_titulo("5. Programas Sociais")
    tabela5 = Table([
        [campo("Bolsa Família", "Sim" if aluno.bolsa_familia else "Não"), campo("BPC", "Sim" if aluno.bpc else "Não"), campo("Outro Programa", aluno.outro_programa)],
    ])
    tabela5.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela5)

    # Bloco 6: Procedência Escolar
    bloco_titulo("6. Procedência Escolar")
    tabela6 = Table([
        [campo("Escola Anterior", aluno.escola_anterior), campo("Aprovado no", aluno.aprovado_ano), campo("Reprovado no", aluno.reprovado_ano), campo("Em Curso no", aluno.em_curso_ano)],
        [campo("Classificado", "Sim" if aluno.classificado else "Não"), campo("Reclassificado", "Sim" if aluno.reclassificado else "Não")],
    ])
    tabela6.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela6)

    # Assinaturas
    elements.append(Spacer(1, 25))
    assinatura_data = [
        ['________________________________________', '________________________________________', '_________________________________________'],
        [f"{diretor.nome if diretor else 'Não disponível'}", f"{secretario.nome if secretario else 'Não disponível'}", 'Responsável'],
        [f"{diretor.funcao if diretor else ''}", f"{secretario.funcao if secretario else ''}", ""],
        [f"Decreto: {diretor.decreto_nomeacao if diretor else '---'}", f"Decreto: {secretario.decreto_nomeacao if secretario else '---'}", ""],
        [f"Matrícula: {diretor.numero_matricula if diretor else '---'}", f"Matrícula: {secretario.numero_matricula if secretario else '---'}", ""],
    ]
    assinatura_table = Table(assinatura_data, colWidths=[2.2 * inch] * 3)
    assinatura_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -2),
        ('TOPPADDING', (0, 0), (-1, -1), -2),
        ('LEFTPADDING', (0, 0), (-1, -1), -2),
        ('RIGHTPADDING', (0, 0), (-1, -1), -2),
    ]))
    elements.append(assinatura_table)

    # Rodapé
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"Gerado por: {usuario_logado}", small_style))
    elements.append(Paragraph(f"Data e Hora: {data_atual}", small_style))

    doc.build(elements)
    return response
@login_required
def rematricula_sucesso(request):
    return render(request, 'alunos/rematricula_sucesso.html')

@login_required
def editar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            return render(request, 'alunos/editar_sucesso.html', {'aluno': aluno})  # ✅ Novo template
    else:
        form = AlunoForm(instance=aluno)
    return render(request, 'alunos/cadastrar_aluno.html', {
        'form': form,
        'aluno': aluno,
        'modo': 'editar'
    })



from django.urls import reverse
from django.utils.http import urlencode
@login_required
def atualizar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('pagina_matricula')
    else:
        form = AlunoForm(instance=aluno)

    return render(request, 'alunos/cadastrar_aluno.html', {'form': form, 'editar': True})





import matplotlib.pyplot as plt
import base64
from io import BytesIO
@login_required
def painel_alunos(request):
    total_masculino = Aluno.objects.filter(sexo='M').count()
    total_feminino = Aluno.objects.filter(sexo='F').count()
    total_outros = Aluno.objects.exclude(sexo__in=['M', 'F']).count()
    total_geral = total_masculino + total_feminino + total_outros

    hoje = datetime.today().date()
    alunos = Aluno.objects.exclude(data_nascimento__isnull=True)

    idades = []
    distribuicao_idade = {}

    for aluno in alunos:
        nascimento = aluno.data_nascimento
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        if 5 <= idade <= 15:
            idades.append(idade)
        distribuicao_idade[idade] = distribuicao_idade.get(idade, 0) + 1

    contagem_idades = Counter(idades)
    faixa_idades = range(5, 16)

    # Gráfico de Pizza - Sexo
    fig1, ax1 = plt.subplots(figsize=(3, 3))
    ax1.pie(
        [total_masculino, total_feminino, total_outros],
        labels=['Masculino', 'Feminino', 'Outros'],
        autopct='%1.1f%%',
        colors=['#42a5f5', '#ef5350', '#ab47bc'],
        startangle=90
    )
    ax1.axis('equal')
    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png', bbox_inches='tight')
    buffer1.seek(0)
    graphic_sexo = base64.b64encode(buffer1.getvalue()).decode('utf-8')
    buffer1.close()

    # Gráfico de Barras - Total
    fig2, ax2 = plt.subplots(figsize=(4, 2))
    ax2.bar(['Total de Alunos'], [total_geral], color='#4caf50')
    ax2.set_ylim(0, max(10, total_geral + 5))
    ax2.text(0, total_geral + 0.5, str(total_geral), ha='center', fontweight='bold')
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png', bbox_inches='tight')
    buffer2.seek(0)
    graphic_total = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    buffer2.close()

    # Gráfico de Barras - Idades
    fig3, ax3 = plt.subplots(figsize=(5, 2.5))
    faixas = list(faixa_idades)
    valores = [contagem_idades.get(i, 0) for i in faixas]
    ax3.bar(faixas, valores, color='#ff9800')
    ax3.set_title("Distribuição por Idade (5 a 15 anos)")
    ax3.set_xlabel("Idade")
    ax3.set_ylabel("Quantidade")
    buffer3 = BytesIO()
    plt.savefig(buffer3, format='png', bbox_inches='tight')
    buffer3.seek(0)
    graphic_idades = base64.b64encode(buffer3.getvalue()).decode('utf-8')
    buffer3.close()

    return render(request, 'alunos/painel_alunos.html', {
        'graphic_sexo': graphic_sexo,
        'graphic_total': graphic_total,
        'graphic_idades': graphic_idades,
        'total': total_geral,
        'total_m': total_masculino,
        'total_f': total_feminino,
        'total_o': total_outros,
        'alunos': alunos,  # ✅ necessário para mostrar nome + idade
        'contagem_idades': contagem_idades,
        'faixa_idades': faixa_idades,
        'distribuicao_idade': distribuicao_idade,
    })

def login_view(request):
    # Verifica se o método da requisição é POST (submissão do formulário)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        # Verifica se o formulário é válido
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Tenta autenticar o usuário
            user = authenticate(request, username=username, password=password)
            
            # Verifica se a autenticação foi bem-sucedida
            if user is not None:
                login(request, user)  # Realiza o login
                messages.success(request, "Login realizado com sucesso!")
                
                # Redireciona o usuário para o painel de alunos
                return redirect('painel_alunos')
            else:
                # Caso a autenticação falhe
                messages.error(request, "Nome de usuário ou senha inválidos.")
    else:
        form = LoginForm()  # Cria um novo formulário vazio caso a requisição não seja POST

    # Renderiza o template de login com o formulário
    return render(request, 'alunos/login.html', {'form': form})

def home(request):
    # Após o login, redireciona para o painel de alunos
    return redirect('painel_alunos')
@login_required
def pesquisar_aluno_sidebar(request):
    aluno = None
    alunos = []
    termo = request.GET.get('busca', None)

    if 'busca' in request.GET:
        if termo:
            alunos = Aluno.objects.filter(nome__icontains=termo)
        else:
            alunos = Aluno.objects.all()

        if not alunos.exists():
            aluno = 'não_encontrado'

    return render(request, 'alunos/pesquisar_aluno.html', {
        'alunos': alunos,
        'aluno': aluno,
        'busca': termo
    })


@login_required
def visualizar_ficha_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return render(request, 'alunos/ficha_visualizacao.html', {'aluno': aluno})

def parse_data(data_str):
    try:
        return pd.to_datetime(data_str, dayfirst=True, errors='coerce').date()
    except:
        return None
@login_required
def import_alunos(request): 
    if request.method == "POST" and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        erros = []
        atualizados = 0
        nao_encontrados = 0

        try:
            df = pd.read_excel(excel_file)

            for index, row in df.iterrows():
                try:
                    nome = str(row['Nome']).strip()

                    aluno = Aluno.objects.filter(nome__iexact=nome).first()

                    if aluno:
                        aluno.aluno_id = row.get('ID', aluno.aluno_id)
                        aluno.endereco = row.get('Endereço', aluno.endereco)
                        aluno.save()
                        atualizados += 1
                    else:
                        nao_encontrados += 1

                except Exception as erro:
                    erros.append(f"Linha {index + 2}: {erro}")

            if erros:
                messages.warning(request, f'⚠ Atualizados: {atualizados}. Não encontrados: {nao_encontrados}. Alguns erros:\n' + "\n".join(erros))
            else:
                messages.success(request, f'✅ {atualizados} alunos atualizados. {nao_encontrados} não encontrados.')

        except Exception as e:
            messages.error(request, f'❌ Erro ao processar o arquivo: {e}')

    return render(request, 'alunos/importar_alunos.html')


@login_required
def gerar_declaracao_matricula(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=declaracao_matricula_{aluno.nome}.pdf'

    doc = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(name="Normal", fontSize=10, leading=12, alignment=4)
    title_style = ParagraphStyle(name="Title", fontSize=14, alignment=1)
    center_style = ParagraphStyle(name="Center", fontSize=10, leading=12, alignment=1)
    small_style = ParagraphStyle(name="Small", fontSize=6, leading=8, alignment=0)
    elements = []

    # Cabeçalho da escola
    escola = Escola.objects.first()
    if escola:
        try:
            logo_path = os.path.join(settings.MEDIA_ROOT, escola.logo.name)
            logo = Image(logo_path, width=60, height=60)
            logo.hAlign = 'CENTER'
            elements.append(logo)
        except:
            elements.append(Paragraph("Logo não disponível", normal))

        elements.append(Spacer(1, 5))
        elements.append(Paragraph(f"<b>{escola.nome_secretaria}</b>", title_style))
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(f"<b>{escola.nome_escola}</b>", title_style))
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(f"CNPJ: {escola.cnpj}", center_style))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph(
            f"Endereço: {escola.endereco}, {escola.numero}, {escola.bairro}, {escola.cidade}/{escola.uf}",
            center_style))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph(f"Telefone: {escola.telefone} | E-mail: {escola.email}", center_style))
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<b>DECLARAÇÃO DE MATRÍCULA</b>", title_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Declaramos para os devidos fins que o(a) aluno(a) abaixo identificado(a) está regularmente matriculado(a) nesta instituição de ensino:", normal))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Nome do(a) Aluno(a):</b> {aluno.nome}", normal))
    elements.append(Paragraph(f"<b>Data de Nascimento:</b> {aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'Não informado'}", normal))

    responsaveis = []
    if aluno.nome_pai:
        responsaveis.append(f"Pai: {aluno.nome_pai}")
    if aluno.nome_mae:
        responsaveis.append(f"Mãe: {aluno.nome_mae}")
    responsaveis_texto = ", ".join(responsaveis) if responsaveis else "Não informado"
    elements.append(Paragraph(f"<b>Nome(s) do(s) Responsável(is):</b> {responsaveis_texto}", normal))
    elements.append(Paragraph(f"<b>Ano/Série:</b> {aluno.ano_serie}", normal))
    elements.append(Paragraph(f"<b>Turno:</b> {aluno.turno if aluno.turno else 'Não informado'}", normal))
    elements.append(Paragraph(f"<b>Ano Letivo:</b> {aluno.ano_rematricula if aluno.ano_rematricula else 'Não informado'}", normal))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Esta declaração é válida para comprovação de matrícula do(a) referido(a) aluno(a), conforme solicitado.", normal))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Darcinópolis/TO, {data_atual.split(' ')[0]}</b>", normal))
    elements.append(Spacer(1, 30))

    # Buscar o funcionário logado e o diretor
    funcionario = Funcionario.objects.filter(user=request.user).first()
    diretor = Funcionario.objects.filter(funcao='Diretor(a)').first()

    # Assinaturas lado a lado
    assinaturas = [
        [
            Paragraph("____________________________________", center_style),
            Paragraph("____________________________________", center_style)
        ],
        [
            Paragraph(f"{funcionario.nome if funcionario else 'Funcionário'}", center_style),
            Paragraph(f"{diretor.nome if diretor else 'Diretor'}", center_style)
        ],
        [
            Paragraph(f"{funcionario.funcao if funcionario else ''}", center_style),
            Paragraph(f"{diretor.funcao if diretor else ''}", center_style)
        ],
        [
            Paragraph(f"Matrícula: {funcionario.numero_matricula if funcionario else ''}", center_style),
            Paragraph(f"Matrícula: {diretor.numero_matricula if diretor else ''}", center_style)
        ],
        [
            Paragraph(f"Decreto: {funcionario.decreto_nomeacao if funcionario else ''}", center_style),
            Paragraph(f"Decreto: {diretor.decreto_nomeacao if diretor else ''}", center_style)
        ],
    ]

    tabela_assinaturas = Table(assinaturas, colWidths=[260, 260])
    elements.append(tabela_assinaturas)

    tabela_assinaturas.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 0),     # Espaçamento acima do conteúdo
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Espaçamento abaixo do conteúdo
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
]))


    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Gerado por: {request.user.username}", small_style))
    elements.append(Paragraph(f"Data e Hora: {data_atual}", small_style))

    doc.build(elements)
    return response

from django.shortcuts import render, redirect
from .forms import AlunoForm
from .models import Aluno
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import tempfile
from django.template.loader import render_to_string
import io
import pandas as pd
from django.http import JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.http import HttpResponse
from .models import Aluno
import os
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from .models import Aluno
import os
from .utils import avancar_ano_serie
from django.urls import reverse
from reportlab.platypus import Image as RLImage
from datetime import datetime
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from .forms import FuncionarioForm
from .models import Funcionario
from .models import Escola
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import date
from collections import Counter
from .models import Turma
from datetime import date
from calendar import monthrange
from django.utils import timezone
from datetime import date





@login_required
def cadastrar_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save()  # Salva o aluno no banco de dados
            return redirect('gerar_pdf_matricula', aluno_id=aluno.id)  # Redireciona para gerar o PDF com o id do aluno
        else:
            return render(request, 'alunos/cadastrar_aluno.html', {'form': form})  # Recarrega o formulário com erros
    else:
        form = AlunoForm()  # Cria um formulário vazio para o GET
    return render(request, 'alunos/cadastrar_aluno.html', {'form': form})


@login_required
def pagina_matricula(request):
    return render(request, 'alunos/pagina_matricula.html')


@login_required
def buscar_aluno_rematricula(request):
    if request.method == 'POST':
        termo = request.POST.get('busca')
        alunos = Aluno.objects.filter(nome__icontains=termo)
        return render(request, 'alunos/buscar_rematricula.html', {'alunos': alunos, 'termo': termo})
    return render(request, 'alunos/buscar_rematricula.html')



@login_required
def rematricula_formulario(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    ano_atual = datetime.now().year

    if aluno.ano_rematricula == ano_atual:
        return render(request, "alunos/ja_rematriculado.html", {"aluno": aluno})

    if request.method == "POST":
        resultado = request.POST.get("resultado")
        if resultado == "aprovado":
            aluno.ano_serie = avancar_ano_serie(aluno.ano_serie)
        # Se reprovado, não muda de série
        aluno.status = "veterano"
        aluno.ano_rematricula = ano_atual
        aluno.save()
        return redirect("gerar_pdf_matricula", aluno_id=aluno.id)

    return render(request, "alunos/rematricula_ficha.html", {"aluno": aluno})

@login_required
def aluno_cadastrado(request, aluno_id):
    return render(request, 'alunos/aluno_cadastrado.html', {'aluno_id': aluno_id})

@login_required
def imprimir_matricula(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return render(request, 'alunos/imprimir_matricula.html', {'aluno': aluno})

@login_required
def gerar_pdf_matricula(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    usuario_logado = request.user.username if request.user.is_authenticated else "Desconhecido"
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    escola = Escola.objects.first()
    diretor = Funcionario.objects.filter(funcao='Diretor(a)').first()
    secretario = Funcionario.objects.filter(funcao='Secretario(a)').first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=matricula_{aluno.nome}.pdf'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(name="Normal", fontSize=7, leading=8)
    center = ParagraphStyle(name="Center", fontSize=7, alignment=1, leading=8)
    title_style = ParagraphStyle(name="TitleBlock", parent=normal, fontSize=7, alignment=1,
                                 textColor=colors.white, backColor=colors.grey, spaceAfter=3)
    small_style = ParagraphStyle(name="Small", fontSize=6, leading=8, alignment=0)
    elements = []

    def dado(texto):
        return Paragraph(texto if texto else "Não informado", normal)

    def campo(label, valor):
        return Paragraph(f"<b>{label}:</b> {valor if valor else 'Não informado'}", normal)

    def bloco_titulo(titulo):
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(titulo, title_style))
        elements.append(Spacer(1, 4))

    try:
        if aluno.foto:
            foto_path = os.path.join(settings.MEDIA_ROOT, aluno.foto.name)
            foto = RLImage(foto_path)
            foto.drawHeight = 0.9 * inch
            foto.drawWidth = 0.7 * inch
        else:
            foto = None
    except:
        foto = None

    escola_nome = escola.nome_escola if escola else "ESCOLA MUNICIPAL"
    secretaria_nome = escola.nome_secretaria if escola else "SECRETARIA MUNICIPAL DE EDUCAÇÃO"
    cnpj = escola.cnpj if escola else "00.000.000/0000-00"
    endereco = f"{escola.endereco}, {escola.numero}, {escola.bairro}, {escola.cidade}/{escola.uf}" if escola else "Endereço não cadastrado"
    contato = f"Telefone: {escola.telefone} | E-mail: {escola.email}" if escola else "Contato não cadastrado"

    cabecalho_texto = [
        [Paragraph(f"<b>{secretaria_nome}</b>", center)],
        [Paragraph(f"<b>{escola_nome}</b>", center)],
        [Paragraph(f"CNPJ: {cnpj}", center)],
        [Paragraph(f"Endereço: {endereco}", center)],
        [Paragraph(f"{contato}", center)],
    ]
    tabela_texto = Table(cabecalho_texto, colWidths=[500])
    tabela_texto.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
    ]))

    if foto:
        cabecalho_completo = Table([
            [tabela_texto, foto]
        ], colWidths=[460, 60])
        cabecalho_completo.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(cabecalho_completo)
    else:
        elements.append(tabela_texto)

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>FICHA DE MATRÍCULA – 2025</b>", ParagraphStyle(name="Header", fontSize=9, alignment=1)))
    elements.append(Spacer(1, 4))

    # Blocos 1 a 6 (mantidos do código anterior, exatamente iguais)
    # Bloco 1: Informações Escolares
    bloco_titulo("1. Informações Escolares")
    tabela1 = Table([
        [dado("(X) Aluno Veterano" if aluno.status == "veterano" else "( ) Aluno Veterano"),
         dado("(X) Aluno Novato" if aluno.status == "novato" else "( ) Aluno Novato")],
        [campo("Unidade Escolar", aluno.unidade_escolar), campo("Município", aluno.municipio), campo("DRE", aluno.dre)],
        [Paragraph(
            f"{('(X)' if aluno.modalidade == 'regular' else '( )')} Regular    "
            f"{('(X)' if aluno.modalidade == 'eja' else '( )')} EJA    "
            f"{('(X)' if aluno.modalidade == 'especial' else '( )')} Especial    "
            f"{('(X)' if aluno.modalidade == 'outra' else '( )')} Outra: {aluno.outra_modalidade or ''}", normal)],
        [campo("Etapa", aluno.etapa), campo("Ano/Série", aluno.ano_serie), campo("Ensino Religioso", "Sim" if aluno.ensino_religioso else "Não")],
        [campo("Turno", aluno.turno)],
    ])
    tabela1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela1)

    # Bloco 2: Dados Pessoais
    bloco_titulo("2. Dados Pessoais")
    tabela2 = Table([
        [campo("Nome", aluno.nome), campo("Sexo", aluno.get_sexo_display()), campo("ID", aluno.aluno_id), campo("NIS", aluno.nis)],
        [
        campo("Nascimento", aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else None),
        campo("Profissão", aluno.profissao),
        campo("Raça/Cor", aluno.cor_raca)
        ],
        [campo("Endereço", aluno.endereco), campo("Bairro", aluno.bairro), campo("CEP", aluno.cep)],
        [campo("Cidade", aluno.cidade), campo("UF", aluno.uf), campo("Zona", aluno.get_zona_display())],
        [campo("Transporte Escolar", "Sim" if aluno.transporte_escolar else "Não"), campo("Rota", aluno.rota), campo("Distância", aluno.distancia)],
        [campo("Cidade Nasc.", aluno.cidade_nascimento), campo("UF Nasc.", aluno.uf_nascimento), campo("Nacionalidade", aluno.nacionalidade)],
        [campo("Nº Certidão", aluno.certidao_numero), campo("Folha", aluno.certidao_folha), campo("Livro", aluno.certidao_livro)],
        [campo("Matrícula", aluno.numero_matricula)],
        [campo("Cartório", aluno.cartorio_nome), campo("UF", aluno.cartorio_uf), campo("Cidade Cartório", aluno.cartorio_cidade)],
        [campo("CPF", aluno.cpf), campo("RG", aluno.rg)],
    ])
    tabela2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela2)

    # Bloco 3: Responsáveis
    bloco_titulo("3. Responsáveis")
    tabela3 = Table([
        [campo("Pai", aluno.nome_pai), campo("Nascimento", aluno.nascimento_pai.strftime('%d/%m/%Y') if aluno.nascimento_pai else None), campo("Telefone", aluno.telefone_pai)],
        [campo("Escolaridade Pai", aluno.escolaridade_pai), campo("Profissão Pai", aluno.profissao_pai)],
        [campo("Mãe", aluno.nome_mae), campo("Nascimento", aluno.nascimento_mae.strftime('%d/%m/%Y') if aluno.nascimento_mae else None), campo("Telefone", aluno.telefone_mae)],
        [campo("Escolaridade Mãe", aluno.escolaridade_mae), campo("Profissão Mãe", aluno.profissao_mae)],
    ])
    tabela3.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela3)

    # Bloco 4: Saúde e Necessidades
    bloco_titulo("4. Saúde e Necessidades")
    tabela4 = Table([
        [campo("Reações Alérgicas", "Sim" if aluno.reacoes_alergicas else "Não"), campo("Descrição", aluno.descricao_alergia)],
        [campo("Necessidade Especial", "Sim" if aluno.necessidade_especial else "Não"), campo("Descrição", aluno.descricao_necessidade)],
        [campo("Possui Laudo", "Sim" if aluno.possui_laudo else "Não"), campo("Sala Recursos", "Sim" if aluno.sala_recursos else "Não")],
        [campo("Medicamento Controlado", "Sim" if aluno.medicamento_controlado else "Não"), campo("Qual Medicamento", aluno.nome_medicamento)],
        [campo("UE Atendimento", aluno.ue_atendimento)],
    ])
    tabela4.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela4)

    # Bloco 5: Programas Sociais
    bloco_titulo("5. Programas Sociais")
    tabela5 = Table([
        [campo("Bolsa Família", "Sim" if aluno.bolsa_familia else "Não"), campo("BPC", "Sim" if aluno.bpc else "Não"), campo("Outro Programa", aluno.outro_programa)],
    ])
    tabela5.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela5)

    # Bloco 6: Procedência Escolar
    bloco_titulo("6. Procedência Escolar")
    tabela6 = Table([
        [campo("Escola Anterior", aluno.escola_anterior), campo("Aprovado no", aluno.aprovado_ano), campo("Reprovado no", aluno.reprovado_ano), campo("Em Curso no", aluno.em_curso_ano)],
        [campo("Classificado", "Sim" if aluno.classificado else "Não"), campo("Reclassificado", "Sim" if aluno.reclassificado else "Não")],
    ])
    tabela6.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(tabela6)

    # Assinaturas
    elements.append(Spacer(1, 25))
    assinatura_data = [
        ['________________________________________', '________________________________________', '_________________________________________'],
        [f"{diretor.nome if diretor else 'Não disponível'}", f"{secretario.nome if secretario else 'Não disponível'}", 'Responsável'],
        [f"{diretor.funcao if diretor else ''}", f"{secretario.funcao if secretario else ''}", ""],
        [f"Decreto: {diretor.decreto_nomeacao if diretor else '---'}", f"Decreto: {secretario.decreto_nomeacao if secretario else '---'}", ""],
        [f"Matrícula: {diretor.numero_matricula if diretor else '---'}", f"Matrícula: {secretario.numero_matricula if secretario else '---'}", ""],
    ]
    assinatura_table = Table(assinatura_data, colWidths=[2.2 * inch] * 3)
    assinatura_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -2),
        ('TOPPADDING', (0, 0), (-1, -1), -2),
        ('LEFTPADDING', (0, 0), (-1, -1), -2),
        ('RIGHTPADDING', (0, 0), (-1, -1), -2),
    ]))
    elements.append(assinatura_table)

    # Rodapé
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"Gerado por: {usuario_logado}", small_style))
    elements.append(Paragraph(f"Data e Hora: {data_atual}", small_style))

    doc.build(elements)
    return response




@login_required
def rematricula_confirmacao(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    if request.method == 'POST':
        resultado = request.POST.get('resultado')  # 'aprovado' ou 'reprovado'

        if resultado == 'aprovado':
            anos = ["1º ANO", "2º ANO", "3º ANO", "4º ANO", "5º ANO"]
            atual = aluno.ano_serie
            if atual in anos:
                idx = anos.index(atual)
                if idx < len(anos) - 1:
                    aluno.ano_serie = anos[idx + 1]
        # Se reprovado, mantém ano_serie
        aluno.status = 'veterano'
        aluno.save()

        # Redireciona para a página de sucesso
        return redirect('rematricula_sucesso')

    return render(request, 'alunos/rematricula_confirmacao.html', {'aluno': aluno})

def rematricula_sucesso(request):
    return render(request, 'alunos/rematricula_sucesso.html')

@login_required
def editar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            return render(request, 'alunos/editar_sucesso.html', {'aluno': aluno})  # ✅ Novo template
    else:
        form = AlunoForm(instance=aluno)
    return render(request, 'alunos/cadastrar_aluno.html', {
        'form': form,
        'aluno': aluno,
        'modo': 'editar'
    })



from django.urls import reverse
from django.utils.http import urlencode
@login_required
def atualizar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('pagina_matricula')
    else:
        form = AlunoForm(instance=aluno)

    return render(request, 'alunos/cadastrar_aluno.html', {'form': form, 'editar': True})





import matplotlib.pyplot as plt
import base64
from io import BytesIO
@login_required
def painel_alunos(request):
    total_masculino = Aluno.objects.filter(sexo='M').count()
    total_feminino = Aluno.objects.filter(sexo='F').count()
    total_outros = Aluno.objects.exclude(sexo__in=['M', 'F']).count()
    total_geral = total_masculino + total_feminino + total_outros

    hoje = datetime.today().date()
    alunos = Aluno.objects.exclude(data_nascimento__isnull=True)

    idades = []
    distribuicao_idade = {}

    for aluno in alunos:
        nascimento = aluno.data_nascimento
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        if 5 <= idade <= 15:
            idades.append(idade)
        distribuicao_idade[idade] = distribuicao_idade.get(idade, 0) + 1

    contagem_idades = Counter(idades)
    faixa_idades = range(5, 16)

    # Gráfico de Pizza - Sexo
    fig1, ax1 = plt.subplots(figsize=(3, 3))
    ax1.pie(
        [total_masculino, total_feminino, total_outros],
        labels=['Masculino', 'Feminino', 'Outros'],
        autopct='%1.1f%%',
        colors=['#42a5f5', '#ef5350', '#ab47bc'],
        startangle=90
    )
    ax1.axis('equal')
    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png', bbox_inches='tight')
    buffer1.seek(0)
    graphic_sexo = base64.b64encode(buffer1.getvalue()).decode('utf-8')
    buffer1.close()

    # Gráfico de Barras - Total
    fig2, ax2 = plt.subplots(figsize=(4, 2))
    ax2.bar(['Total de Alunos'], [total_geral], color='#4caf50')
    ax2.set_ylim(0, max(10, total_geral + 5))
    ax2.text(0, total_geral + 0.5, str(total_geral), ha='center', fontweight='bold')
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png', bbox_inches='tight')
    buffer2.seek(0)
    graphic_total = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    buffer2.close()

    # Gráfico de Barras - Idades
    fig3, ax3 = plt.subplots(figsize=(5, 2.5))
    faixas = list(faixa_idades)
    valores = [contagem_idades.get(i, 0) for i in faixas]
    ax3.bar(faixas, valores, color='#ff9800')
    ax3.set_title("Distribuição por Idade (5 a 15 anos)")
    ax3.set_xlabel("Idade")
    ax3.set_ylabel("Quantidade")
    buffer3 = BytesIO()
    plt.savefig(buffer3, format='png', bbox_inches='tight')
    buffer3.seek(0)
    graphic_idades = base64.b64encode(buffer3.getvalue()).decode('utf-8')
    buffer3.close()

    return render(request, 'alunos/painel_alunos.html', {
        'graphic_sexo': graphic_sexo,
        'graphic_total': graphic_total,
        'graphic_idades': graphic_idades,
        'total': total_geral,
        'total_m': total_masculino,
        'total_f': total_feminino,
        'total_o': total_outros,
        'alunos': alunos,  # ✅ necessário para mostrar nome + idade
        'contagem_idades': contagem_idades,
        'faixa_idades': faixa_idades,
        'distribuicao_idade': distribuicao_idade,
    })

def login_view(request):
    # Recupera a instância da escola (assumindo que você tem apenas uma escola cadastrada)
    escola = Escola.objects.first()  # Pegue a primeira escola, se existir
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login realizado com sucesso!")
                return redirect('painel_alunos')
            else:
                messages.error(request, "Nome de usuário ou senha inválidos.")
    else:
        form = LoginForm()

    # Passa a escola como contexto para o template
    return render(request, 'alunos/login.html', {'form': form, 'escola': escola})

def home(request):
    return render(request, 'alunos/painel_alunos.html')  # Crie o template 'home.html' conforme sua necessidade
@login_required
def pesquisar_aluno_sidebar(request):
    aluno = None
    alunos = []
    termo = request.GET.get('busca', None)

    if 'busca' in request.GET:
        if termo:
            alunos = Aluno.objects.filter(nome__icontains=termo)
        else:
            alunos = Aluno.objects.all()

        if not alunos.exists():
            aluno = 'não_encontrado'

    return render(request, 'alunos/pesquisar_aluno.html', {
        'alunos': alunos,
        'aluno': aluno,
        'busca': termo
    })


@login_required
def visualizar_ficha_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return render(request, 'alunos/ficha_visualizacao.html', {'aluno': aluno})

def parse_data(data_str):
    try:
        return pd.to_datetime(data_str, dayfirst=True, errors='coerce').date()
    except:
        return None


def formatar_data(valor):
    """Tenta converter datas nos formatos: dd/mm/yyyy, dd.mm.yyyy, yyyy-mm-dd"""
    try:
        if pd.isnull(valor):
            return None
        if isinstance(valor, datetime):
            return valor.date()
        valor_str = str(valor).strip()
        for fmt in ("%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(valor_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f'O valor "{valor}" tem um formato de data inválido.')
    except Exception as e:
        raise e

def parse_boolean(valor):
    """Converte valores como 'Sim', 'Não', '1', '0', True, False para booleano"""
    if isinstance(valor, str):
        valor = valor.strip().lower()
        return valor in ['sim', '1', 'true']
    return bool(valor)
@login_required
def import_alunos(request):
    if request.method == "POST" and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        erros = []
        importados = 0
        ja_existentes = 0

        try:
            df = pd.read_excel(excel_file)

            for index, row in df.iterrows():
                try:
                    nome = str(row.get('Nome', '')).strip()
                    if not nome:
                        continue

                    if Aluno.objects.filter(nome__iexact=nome).exists():
                        ja_existentes += 1
                        continue

                    aluno = Aluno.objects.create(
                        nome=nome,
                        data_nascimento=formatar_data(row.get('Data de Nascimento')),
                        aluno_id=row.get('ID'),
                        sexo=row.get('Sexo'),
                        cpf=row.get('CPF'),
                        rg=row.get('RG'),
                        nome_pai=row.get('Nome do Pai'),
                        nome_mae=row.get('Nome da Mãe'),
                        endereco=row.get('Endereço') or 'Não informado',
                        bairro=row.get('Bairro'),
                        telefone_pai=row.get('Telefone Pai'),
                        telefone_mae=row.get('Telefone Mãe'),
                        cidade=row.get('Cidade'),
                        uf=row.get('UF'),
                        nacionalidade=row.get('Nacionalidade'),
                        ano_serie=row.get('Ano/Série'),
                        turno=row.get('Turno'),
                        transporte_escolar=parse_boolean(row.get('Transporte Escolar')),
                        rota=row.get('Rota') or '',
                        distancia=row.get('Distância') or '',
                    )
                    importados += 1

                except Exception as erro:
                    erros.append(f"Linha {index + 2}: {erro}")

            if erros:
                messages.warning(
                    request,
                    f'⚠️ Importados: {importados}. Ignorados (já existentes): {ja_existentes}. Erros:\n' + "\n".join(erros[:10])
                )
            else:
                messages.success(
                    request,
                    f'✅ {importados} alunos importados com sucesso. {ja_existentes} já existiam e foram ignorados.'
                )

        except Exception as e:
            messages.error(request, f'❌ Erro ao processar o arquivo: {e}')

    return render(request, 'alunos/importar_alunos.html')




@login_required 
def gerar_declaracao_matricula(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=declaracao_matricula_{aluno.nome}.pdf'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(name="Normal", fontSize=10, leading=12, alignment=4)
    title_style = ParagraphStyle(name="Title", fontSize=14, alignment=1)
    center_style = ParagraphStyle(name="Center", fontSize=10, leading=12, alignment=1)
    small_style = ParagraphStyle(name="Small", fontSize=6, leading=8, alignment=0)
    elements = []

    # Cabeçalho da escola
    escola = Escola.objects.first()
    if escola:
        try:
            logo_path = os.path.join(settings.MEDIA_ROOT, escola.logo.name)
            logo = Image(logo_path, width=60, height=60)
            logo.hAlign = 'CENTER'
            elements.append(logo)
        except:
            elements.append(Paragraph("Logo não disponível", normal))

        elements.append(Spacer(1, 5))
        elements.append(Paragraph(f"<b>{escola.nome_secretaria}</b>", title_style))
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(f"<b>{escola.nome_escola}</b>", title_style))
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(f"CNPJ: {escola.cnpj}", center_style))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph(
            f"Endereço: {escola.endereco}, {escola.numero}, {escola.bairro}, {escola.cidade}/{escola.uf}",
            center_style))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph(f"Telefone: {escola.telefone} | E-mail: {escola.email}", center_style))
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<b>DECLARAÇÃO DE MATRÍCULA</b>", title_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Declaramos para os devidos fins que o(a) aluno(a) abaixo identificado(a) está regularmente matriculado(a) nesta instituição de ensino:", normal))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Nome do(a) Aluno(a):</b> {aluno.nome}", normal))
    elements.append(Paragraph(f"<b>Data de Nascimento:</b> {aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'Não informado'}", normal))

    responsaveis = []
    if aluno.nome_pai:
        responsaveis.append(f"Pai: {aluno.nome_pai}")
    if aluno.nome_mae:
        responsaveis.append(f"Mãe: {aluno.nome_mae}")
    responsaveis_texto = ", ".join(responsaveis) if responsaveis else "Não informado"
    elements.append(Paragraph(f"<b>Nome(s) do(s) Responsável(is):</b> {responsaveis_texto}", normal))
    elements.append(Paragraph(f"<b>Ano/Série:</b> {aluno.ano_serie}", normal))
    elements.append(Paragraph(f"<b>Turno:</b> {aluno.turno if aluno.turno else 'Não informado'}", normal))
    elements.append(Paragraph(f"<b>Ano Letivo:</b> {aluno.ano_rematricula if aluno.ano_rematricula else 'Não informado'}", normal))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Esta declaração é válida para comprovação de matrícula do(a) referido(a) aluno(a), conforme solicitado.", normal))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Darcinópolis/TO, {data_atual.split(' ')[0]}</b>", normal))
    elements.append(Spacer(1, 30))

    # Buscar o funcionário logado
    funcionario = Funcionario.objects.filter(user=request.user).first()

    # Buscar o diretor
    diretor = Funcionario.objects.filter(funcao__icontains="diretor").first()

    # Assinatura do usuário logado
    assinatura_usuario = [
        [Paragraph("____________________________________", center_style)],
        [Paragraph(f"{funcionario.nome if funcionario else 'Funcionário'}", center_style)],
        [Paragraph(f"{funcionario.funcao if funcionario else ''}", center_style)],
        [Paragraph(f"Matrícula: {funcionario.numero_matricula if funcionario else ''}", center_style)],
        [Paragraph(f"Decreto: {funcionario.decreto_nomeacao if funcionario else ''}", center_style)],
    ]

    # Assinatura do diretor
    assinatura_diretor = [
        [Paragraph("____________________________________", center_style)],
        [Paragraph(f"{diretor.nome if diretor else 'Diretor(a)'}", center_style)],
        [Paragraph(f"{diretor.funcao if diretor else ''}", center_style)],
        [Paragraph(f"Matrícula: {diretor.numero_matricula if diretor else ''}", center_style)],
        [Paragraph(f"Decreto: {diretor.decreto_nomeacao if diretor else ''}", center_style)],
    ]

    # Exibir as duas assinaturas lado a lado
    tabela_assinaturas = Table(
        [assinatura_usuario, assinatura_diretor],
        colWidths=[260, 260]
    )
    tabela_assinaturas.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    elements.append(tabela_assinaturas)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Gerado por: {request.user.username}", small_style))
    elements.append(Paragraph(f"Data e Hora: {data_atual}", small_style))

    doc.build(elements)
    return response


def distribuir_alunos_turmas():
    # Obtenha todos os alunos, agrupados por série
    series = Aluno.objects.values_list('ano_serie', flat=True).distinct()

    for serie in series:
        alunos_da_serie = Aluno.objects.filter(ano_serie=serie).order_by('sexo')  # Ordena por sexo (para balancear)

        # Crie turmas para cada série
        turma_nome = 'A'  # Inicia com a turma "A"
        turma = Turma.objects.create(nome=turma_nome, serie=serie)

        meninos = alunos_da_serie.filter(sexo='M')
        meninas = alunos_da_serie.filter(sexo='F')

        # Divide os meninos e meninas em duas listas
        turma_alunos = []
        max_alunos = 20
        max_meninos = max_alunos // 2
        max_meninas = max_alunos // 2

        turma_alunos.extend(meninos[:max_meninos])  # Limite de meninos
        turma_alunos.extend(meninas[:max_meninas])  # Limite de meninas

        # Associa esses alunos à turma
        turma.alunos.add(*turma_alunos)
        
        # Atribui a turma para os alunos
        for aluno in turma_alunos:
            aluno.turma = turma
            aluno.save()

        turma.save()

        # Se houver mais alunos para essa série, crie novas turmas
        while len(alunos_da_serie) > len(turma.alunos.all()):
            turma_nome = chr(ord(turma_nome) + 1)  # Vai para a próxima letra: "B", "C", etc.
            turma = Turma.objects.create(nome=turma_nome, serie=serie)

            meninos_restantes = alunos_da_serie.filter(sexo='M')[max_meninos:]
            meninas_restantes = alunos_da_serie.filter(sexo='F')[max_meninas:]

            turma_alunos.extend(meninos_restantes[:max_meninos])  # Limite de meninos
            turma_alunos.extend(meninas_restantes[:max_meninas])  # Limite de meninas

            turma.alunos.add(*turma_alunos)

            # Atribui a turma para os alunos
            for aluno in turma_alunos:
                aluno.turma = turma
                aluno.save()

            turma.save()
@login_required
def cadastrar_funcionario_views(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')  # ou uma página de confirmação
    else:
        form = FuncionarioForm()
    return render(request, 'alunos/cadastrar_funcionario.html', {'form': form})
@login_required
def pesquisar_funcionario(request):
    busca = request.GET.get('busca', '')
    funcionarios = Funcionario.objects.filter(nome__icontains=busca) if busca else []
    
    return render(request, 'alunos/pesquisar_funcionario.html', {
        'funcionarios': funcionarios,
        'busca': busca
    })
@login_required
def listar_funcionarios(request):
    funcionarios = Funcionario.objects.all()
    return render(request, 'alunos/listar_funcionarios.html', {'funcionarios': funcionarios})
@login_required
def editar_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)

    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')  # redireciona para a lista após salvar
    else:
        form = FuncionarioForm(instance=funcionario)

    context = {
        'form': form,
        'funcionario': funcionario
    }
    return render(request, 'alunos/editar_funcionario.html', context)

@login_required
def excluir_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    funcionario.delete()
    return redirect('listar_funcionarios')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def emitir_documentos(request):
    return render(request, 'alunos/emitir_documentos.html')

def calcular_idade(nascimento):
    today = date.today()
    return today.year - nascimento.year - ((today.month, today.day) < (nascimento.month, nascimento.day))
@login_required
def relatorio_por_turma_view(request):
    # Buscar valores únicos de séries e turmas
    series = Turma.objects.values_list('serie', flat=True).distinct()
    turmas = Turma.objects.all()

    # Filtros do formulário
    serie = request.GET.get('serie')
    turma_nome = request.GET.get('turma')
    campos = request.GET.getlist('campos')

    # Consulta base
    alunos = Aluno.objects.all()

    # Aplicar filtros
    if serie:
        alunos = alunos.filter(ano_serie=serie)
    if turma_nome:
        alunos = alunos.filter(turma__nome=turma_nome)

    # Lista de campos possíveis com base no modelo Aluno
    opcoes_campos = [
        'nome', 'data_nascimento', 'sexo', 'cor_raca', 'aluno_id', 'nis',
        'profissao', 'endereco', 'bairro', 'cidade', 'uf', 'zona',
        'cidade_nascimento', 'uf_nascimento', 'nacionalidade',
        'certidao_numero', 'certidao_folha', 'certidao_livro',
        'numero_matricula', 'cartorio_nome', 'cartorio_uf', 'cartorio_cidade',
        'cpf', 'rg',
        'nome_pai', 'telefone_pai', 'profissao_pai', 'escolaridade_pai',
        'nome_mae', 'telefone_mae', 'profissao_mae', 'escolaridade_mae',
        'necessidade_especial', 'descricao_necessidade', 'possui_laudo',
        'transporte_escolar', 'rota', 'distancia',
        'medicamento_controlado', 'nome_medicamento',
        'bolsa_familia', 'bpc', 'outro_programa',
        'ensino_religioso',
        'escola_anterior', 'rede_anterior',
        'aprovado_ano', 'reprovado_ano', 'em_curso_ano',
        'status', 'situacao', 'modalidade', 'etapa', 'ano_serie', 'turno',
    ]

    # Recuperar escola cadastrada
    escola = Escola.objects.first()

    context = {
        'series': sorted(series),
        'turmas': turmas,
        'alunos': alunos,
        'serie': serie,
        'turma': turma_nome,
        'campos': campos,
        'opcoes_campos': opcoes_campos,
        'usuario': request.user,
        'now': timezone.now(),
        'escola': escola,
    }

    return render(request, 'alunos/relatorio_por_turma.html', context)

@login_required
def gerar_relatorio_por_turma(request):
    serie = request.GET.get('serie')
    turma_nome = request.GET.get('turma')

    if not serie or not turma_nome:
        return HttpResponse("Parâmetros inválidos", status=400)

    try:
        turma = Turma.objects.get(serie=serie, nome=turma_nome)
    except Turma.DoesNotExist:
        return HttpResponse("Turma não encontrada", status=404)

    alunos = turma.alunos.all()

    return render(request, 'alunos/relatorio_turma.html', {
        'turma': turma,
        'alunos': alunos,
        'serie': serie,
    })

@login_required
def relatorio_rematricula(request):
    serie_selecionada = request.GET.get('serie')
    turma_selecionada = request.GET.get('turma')

    turmas = Turma.objects.all()
    series = Turma.objects.values_list('serie', flat=True).distinct()

    alunos = Aluno.objects.all()
    if serie_selecionada:
        alunos = alunos.filter(turmas__serie=serie_selecionada)
    if turma_selecionada:
        alunos = alunos.filter(turmas__nome=turma_selecionada)

    return render(request, 'alunos/relatorio_rematricula.html', {
        'alunos': alunos.distinct(),
        'series': series,
        'turmas': turmas,
        'serie_selecionada': serie_selecionada,
        'turma_selecionada': turma_selecionada,
    })

def alocar_alunos_turma(request):
    # Buscando todas as turmas para exibir na seleção
    turmas = Turma.objects.all()
    alunos_info = []

    # Filtrando alunos conforme a pesquisa
    query = request.GET.get('q', '')
    if query:
        alunos = Aluno.objects.filter(nome__icontains=query)  # Filtra os alunos pelo nome
    else:
        alunos = Aluno.objects.all()  # Caso não haja filtro, pega todos os alunos

    # Adicionando o status dos alunos (alocado ou não)
    for aluno in alunos:
        status = f"Alocado na turma {aluno.turma.nome}" if aluno.turma else "Não alocado"
        alunos_info.append({
            'id': aluno.id,
            'nome': aluno.nome,
            'ano_serie': aluno.ano_serie,
            'status': status,
        })

    # Se o formulário for submetido
    if request.method == "POST":
        alunos_ids = request.POST.getlist('alunos')  # Lista de IDs dos alunos selecionados
        turma_id = request.POST.get('turma_id')  # ID da turma selecionada

        # Validar se pelo menos um aluno e uma turma foram selecionados
        if not alunos_ids or not turma_id:
            messages.error(request, "Selecione pelo menos um aluno e uma turma.")
            return redirect('alocar_alunos_turma')

        try:
            turma = Turma.objects.get(id=turma_id)
        except Turma.DoesNotExist:
            messages.error(request, "Turma não encontrada.")
            return redirect('alocar_alunos_turma')

        # Alocar os alunos na turma selecionada
        for aluno_id in alunos_ids:
            try:
                aluno = Aluno.objects.get(id=aluno_id)

                # Remover da turma anterior, se houver
                if aluno.turma and aluno.turma != turma:
                    aluno.turma.alunos.remove(aluno)

                # Atualizar o aluno com a nova turma
                aluno.turma = turma
                aluno.ano_serie = turma.serie
                aluno.turno = turma.turno
                aluno.save()

                # Adicionar o aluno à turma
                turma.alunos.add(aluno)

            except Aluno.DoesNotExist:
                continue

        messages.success(request, "Alunos alocados com sucesso!")
        return redirect('alocar_alunos_turma')

    # Passar as informações para o template
    return render(request, 'alunos/alocar_alunos.html', {
        'alunos_info': alunos_info,
        'turmas': turmas,
        'query': query,
    })


@login_required
def relatorio_alunos_alocados(request):
    turma_id = request.GET.get('turma_id')
    turmas = Turma.objects.all()
    alunos = []
    turma_selecionada = None

    # Dados da escola
    escola = Escola.objects.first()

    # Data atual
    hoje = date.today()
    dias_do_mes = monthrange(hoje.year, hoje.month)[1]  # Ex: 31
    ano_letivo = hoje.year

    # Turma selecionada
    if turma_id:
        turma_selecionada = Turma.objects.filter(id=turma_id).first()
        if turma_selecionada:
            alunos = turma_selecionada.alunos.all()

    return render(request, 'alunos/relatorio_alocados_tela.html', {
        'turmas': turmas,
        'alunos': alunos,
        'turma_id': turma_id,
        'turma_selecionada': turma_selecionada,
        'escola': escola,
        'dias_do_mes': dias_do_mes,
        'ano_letivo': ano_letivo,
        'usuario': request.user,
        'data_hora_impressao': timezone.now(),
    })
@login_required
def pesquisar_alunos(request):
    alunos = Aluno.objects.all()

    # Se o formulário de pesquisa foi submetido
    if 'pesquisa' in request.GET:
        pesquisa = request.GET['pesquisa']
        if pesquisa:
            alunos = alunos.filter(nome__icontains=pesquisa)  # Filtra pelo nome do aluno
        else:
            alunos = Aluno.objects.all()  # Se não houver pesquisa, mostra todos os alunos

    return render(request, 'alunos/pesquisar_alunos.html', {'alunos': alunos})

@login_required
def aniversariantes_view(request):
    hoje = date.today()
    mes = hoje.month
    dia = hoje.day

    # Alunos que fazem aniversário neste mês
    aniversariantes_mes = Aluno.objects.filter(data_nascimento__month=mes)

    # Alunos que fazem aniversário hoje
    aniversariantes_dia = aniversariantes_mes.filter(data_nascimento__day=dia)

    context = {
        'hoje': hoje,
        'aniversariantes_mes': aniversariantes_mes,
        'aniversariantes_dia': aniversariantes_dia,
    }

    return render(request, 'alunos/aniversariantes.html', context)

def relatorios_personalizados(request):
    return render(request, 'alunos/relatorios_personalizados.html')


@login_required
def relatorio_alunos_por_idade(request):
    turma_id = request.GET.get('turma_id')
    hoje = date.today()

    # Dados da escola
    escola = Escola.objects.first()
    ano_letivo = hoje.year
    turmas = Turma.objects.all()
    turma_selecionada = None

    alunos = Aluno.objects.exclude(data_nascimento__isnull=True)
    if turma_id:
        turma_selecionada = get_object_or_404(Turma, id=turma_id)
        alunos = alunos.filter(turma=turma_selecionada)

    relatorio = {}
    totais = {"masculino": 0, "feminino": 0, "total": 0}

    for aluno in alunos:
        idade = hoje.year - aluno.data_nascimento.year - (
            (hoje.month, hoje.day) < (aluno.data_nascimento.month, aluno.data_nascimento.day)
        )
        sexo = aluno.sexo.lower()

        if idade not in relatorio:
            relatorio[idade] = {"masculino": 0, "feminino": 0, "total": 0}

        if sexo == 'm':
            relatorio[idade]["masculino"] += 1
            totais["masculino"] += 1
        elif sexo == 'f':
            relatorio[idade]["feminino"] += 1
            totais["feminino"] += 1

        relatorio[idade]["total"] += 1
        totais["total"] += 1

    relatorio_ordenado = dict(sorted(relatorio.items()))

    context = {
        "turmas": turmas,
        "turma_id": turma_id,
        "turma_selecionada": turma_selecionada,
        "relatorio": relatorio_ordenado,
        "totais": totais,
        "escola": escola,
        "ano_letivo": ano_letivo,
    }

    return render(request, 'alunos/relatorio_por_idade.html', context)




def distribuir_alunos_turmas():
    # Obtenha todos os alunos, agrupados por série
    series = Aluno.objects.values_list('ano_serie', flat=True).distinct()

    for serie in series:
        alunos_da_serie = Aluno.objects.filter(ano_serie=serie).order_by('sexo')  # Ordena por sexo (para balancear)

        # Crie turmas para cada série
        turma_nome = 'A'  # Inicia com a turma "A"
        turma = Turma.objects.create(nome=turma_nome, serie=serie)

        meninos = alunos_da_serie.filter(sexo='M')
        meninas = alunos_da_serie.filter(sexo='F')

        # Divide os meninos e meninas em duas listas
        turma_alunos = []
        max_alunos = 20
        max_meninos = max_alunos // 2
        max_meninas = max_alunos // 2

        turma_alunos.extend(meninos[:max_meninos])  # Limite de meninos
        turma_alunos.extend(meninas[:max_meninas])  # Limite de meninas

        # Associa esses alunos à turma
        turma.alunos.add(*turma_alunos)
        
        # Atribui a turma para os alunos
        for aluno in turma_alunos:
            aluno.turma = turma
            aluno.save()

        turma.save()

        # Se houver mais alunos para essa série, crie novas turmas
        while len(alunos_da_serie) > len(turma.alunos.all()):
            turma_nome = chr(ord(turma_nome) + 1)  # Vai para a próxima letra: "B", "C", etc.
            turma = Turma.objects.create(nome=turma_nome, serie=serie)

            meninos_restantes = alunos_da_serie.filter(sexo='M')[max_meninos:]
            meninas_restantes = alunos_da_serie.filter(sexo='F')[max_meninas:]

            turma_alunos.extend(meninos_restantes[:max_meninos])  # Limite de meninos
            turma_alunos.extend(meninas_restantes[:max_meninas])  # Limite de meninas

            turma.alunos.add(*turma_alunos)

            # Atribui a turma para os alunos
            for aluno in turma_alunos:
                aluno.turma = turma
                aluno.save()

            turma.save()
@login_required
def cadastrar_funcionario_views(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')  # ou uma página de confirmação
    else:
        form = FuncionarioForm()
    return render(request, 'alunos/cadastrar_funcionario.html', {'form': form})
@login_required
def pesquisar_funcionario(request):
    busca = request.GET.get('busca', '')
    funcionarios = Funcionario.objects.filter(nome__icontains=busca) if busca else []
    
    return render(request, 'alunos/pesquisar_funcionario.html', {
        'funcionarios': funcionarios,
        'busca': busca
    })
@login_required
def listar_funcionarios(request):
    funcionarios = Funcionario.objects.all()
    return render(request, 'alunos/listar_funcionarios.html', {'funcionarios': funcionarios})
@login_required
def editar_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)

    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')  # redireciona para a lista após salvar
    else:
        form = FuncionarioForm(instance=funcionario)

    context = {
        'form': form,
        'funcionario': funcionario
    }
    return render(request, 'alunos/editar_funcionario.html', context)

@login_required
def excluir_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    funcionario.delete()
    return redirect('listar_funcionarios')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def emitir_documentos(request):
    return render(request, 'alunos/emitir_documentos.html')

def calcular_idade(nascimento):
    today = date.today()
    return today.year - nascimento.year - ((today.month, today.day) < (nascimento.month, nascimento.day))
@login_required
def relatorio_por_turma_view(request):
    # Buscar valores únicos de séries e turmas
    series = Turma.objects.values_list('serie', flat=True).distinct()
    turmas = Turma.objects.all()

    # Filtros do formulário
    serie = request.GET.get('serie')
    turma_nome = request.GET.get('turma')
    campos = request.GET.getlist('campos')

    # Consulta base
    alunos = Aluno.objects.all()

    # Aplicar filtros
    if serie:
        alunos = alunos.filter(ano_serie=serie)
    if turma_nome:
        alunos = alunos.filter(turma__nome=turma_nome)

    # Lista de campos possíveis com base no modelo Aluno
    opcoes_campos = [
        'nome', 'data_nascimento', 'sexo', 'cor_raca', 'aluno_id', 'nis',
        'profissao', 'endereco', 'bairro', 'cidade', 'uf', 'zona',
        'cidade_nascimento', 'uf_nascimento', 'nacionalidade',
        'certidao_numero', 'certidao_folha', 'certidao_livro',
        'numero_matricula', 'cartorio_nome', 'cartorio_uf', 'cartorio_cidade',
        'cpf', 'rg',
        'nome_pai', 'telefone_pai', 'profissao_pai', 'escolaridade_pai',
        'nome_mae', 'telefone_mae', 'profissao_mae', 'escolaridade_mae',
        'necessidade_especial', 'descricao_necessidade', 'possui_laudo',
        'transporte_escolar', 'rota', 'distancia',
        'medicamento_controlado', 'nome_medicamento',
        'bolsa_familia', 'bpc', 'outro_programa',
        'ensino_religioso',
        'escola_anterior', 'rede_anterior',
        'aprovado_ano', 'reprovado_ano', 'em_curso_ano',
        'status', 'situacao', 'modalidade', 'etapa', 'ano_serie', 'turno',
    ]

    # Recuperar escola cadastrada
    escola = Escola.objects.first()

    context = {
        'series': sorted(series),
        'turmas': turmas,
        'alunos': alunos,
        'serie': serie,
        'turma': turma_nome,
        'campos': campos,
        'opcoes_campos': opcoes_campos,
        'usuario': request.user,
        'now': timezone.now(),
        'escola': escola,
    }

    return render(request, 'alunos/relatorio_por_turma.html', context)

@login_required
def gerar_relatorio_por_turma(request):
    serie = request.GET.get('serie')
    turma_nome = request.GET.get('turma')

    if not serie or not turma_nome:
        return HttpResponse("Parâmetros inválidos", status=400)

    try:
        turma = Turma.objects.get(serie=serie, nome=turma_nome)
    except Turma.DoesNotExist:
        return HttpResponse("Turma não encontrada", status=404)

    alunos = turma.alunos.all()

    return render(request, 'alunos/relatorio_turma.html', {
        'turma': turma,
        'alunos': alunos,
        'serie': serie,
    })

@login_required
def relatorio_rematricula(request):
    serie_selecionada = request.GET.get('serie')
    turma_selecionada = request.GET.get('turma')

    turmas = Turma.objects.all()
    series = Turma.objects.values_list('serie', flat=True).distinct()

    alunos = Aluno.objects.all()
    if serie_selecionada:
        alunos = alunos.filter(turmas__serie=serie_selecionada)
    if turma_selecionada:
        alunos = alunos.filter(turmas__nome=turma_selecionada)

    return render(request, 'alunos/relatorio_rematricula.html', {
        'alunos': alunos.distinct(),
        'series': series,
        'turmas': turmas,
        'serie_selecionada': serie_selecionada,
        'turma_selecionada': turma_selecionada,
    })

def alocar_alunos_turma(request):
    # Buscando todas as turmas para exibir na seleção
    turmas = Turma.objects.all()
    alunos_info = []

    # Filtrando alunos conforme a pesquisa
    query = request.GET.get('q', '')
    if query:
        alunos = Aluno.objects.filter(nome__icontains=query)  # Filtra os alunos pelo nome
    else:
        alunos = Aluno.objects.all()  # Caso não haja filtro, pega todos os alunos

    # Adicionando o status dos alunos (alocado ou não)
    for aluno in alunos:
        status = f"Alocado na turma {aluno.turma.nome}" if aluno.turma else "Não alocado"
        alunos_info.append({
            'id': aluno.id,
            'nome': aluno.nome,
            'ano_serie': aluno.ano_serie,
            'status': status,
        })

    # Se o formulário for submetido
    if request.method == "POST":
        alunos_ids = request.POST.getlist('alunos')  # Lista de IDs dos alunos selecionados
        turma_id = request.POST.get('turma_id')  # ID da turma selecionada

        # Validar se pelo menos um aluno e uma turma foram selecionados
        if not alunos_ids or not turma_id:
            messages.error(request, "Selecione pelo menos um aluno e uma turma.")
            return redirect('alocar_alunos_turma')

        try:
            turma = Turma.objects.get(id=turma_id)
        except Turma.DoesNotExist:
            messages.error(request, "Turma não encontrada.")
            return redirect('alocar_alunos_turma')

        # Alocar os alunos na turma selecionada
        for aluno_id in alunos_ids:
            try:
                aluno = Aluno.objects.get(id=aluno_id)

                # Remover da turma anterior, se houver
                if aluno.turma and aluno.turma != turma:
                    aluno.turma.alunos.remove(aluno)

                # Atualizar o aluno com a nova turma
                aluno.turma = turma
                aluno.ano_serie = turma.serie
                aluno.turno = turma.turno
                aluno.save()

                # Adicionar o aluno à turma
                turma.alunos.add(aluno)

            except Aluno.DoesNotExist:
                continue

        messages.success(request, "Alunos alocados com sucesso!")
        return redirect('alocar_alunos_turma')

    # Passar as informações para o template
    return render(request, 'alunos/alocar_alunos.html', {
        'alunos_info': alunos_info,
        'turmas': turmas,
        'query': query,
    })


@login_required
def relatorio_alunos_alocados(request):
    turma_id = request.GET.get('turma_id')
    turmas = Turma.objects.all()
    alunos = []
    turma_selecionada = None

    # Dados da escola
    escola = Escola.objects.first()

    # Data atual
    hoje = date.today()
    dias_do_mes = monthrange(hoje.year, hoje.month)[1]  # Ex: 31
    ano_letivo = hoje.year

    # Turma selecionada
    if turma_id:
        turma_selecionada = Turma.objects.filter(id=turma_id).first()
        if turma_selecionada:
            alunos = turma_selecionada.alunos.all()

    return render(request, 'alunos/relatorio_alocados_tela.html', {
        'turmas': turmas,
        'alunos': alunos,
        'turma_id': turma_id,
        'turma_selecionada': turma_selecionada,
        'escola': escola,
        'dias_do_mes': dias_do_mes,
        'ano_letivo': ano_letivo,
        'usuario': request.user,
        'data_hora_impressao': timezone.now(),
    })
@login_required
def pesquisar_alunos(request):
    alunos = Aluno.objects.all()

    # Se o formulário de pesquisa foi submetido
    if 'pesquisa' in request.GET:
        pesquisa = request.GET['pesquisa']
        if pesquisa:
            alunos = alunos.filter(nome__icontains=pesquisa)  # Filtra pelo nome do aluno
        else:
            alunos = Aluno.objects.all()  # Se não houver pesquisa, mostra todos os alunos

    return render(request, 'alunos/pesquisar_alunos.html', {'alunos': alunos})

@login_required
def aniversariantes_view(request):
    hoje = date.today()
    mes = hoje.month
    dia = hoje.day

    # Alunos que fazem aniversário neste mês
    aniversariantes_mes = Aluno.objects.filter(data_nascimento__month=mes)

    # Alunos que fazem aniversário hoje
    aniversariantes_dia = aniversariantes_mes.filter(data_nascimento__day=dia)

    context = {
        'hoje': hoje,
        'aniversariantes_mes': aniversariantes_mes,
        'aniversariantes_dia': aniversariantes_dia,
    }

    return render(request, 'alunos/aniversariantes.html', context)

def relatorios_personalizados(request):
    return render(request, 'alunos/relatorios_personalizados.html')


@login_required
def relatorio_alunos_por_idade(request):
    turma_id = request.GET.get('turma_id')
    hoje = date.today()

    # Dados da escola
    escola = Escola.objects.first()
    ano_letivo = hoje.year
    turmas = Turma.objects.all()
    turma_selecionada = None

    alunos = Aluno.objects.exclude(data_nascimento__isnull=True)
    if turma_id:
        turma_selecionada = get_object_or_404(Turma, id=turma_id)
        alunos = alunos.filter(turma=turma_selecionada)

    relatorio = {}
    totais = {"masculino": 0, "feminino": 0, "total": 0}

    for aluno in alunos:
        idade = hoje.year - aluno.data_nascimento.year - (
            (hoje.month, hoje.day) < (aluno.data_nascimento.month, aluno.data_nascimento.day)
        )
        sexo = aluno.sexo.lower()

        if idade not in relatorio:
            relatorio[idade] = {"masculino": 0, "feminino": 0, "total": 0}

        if sexo == 'm':
            relatorio[idade]["masculino"] += 1
            totais["masculino"] += 1
        elif sexo == 'f':
            relatorio[idade]["feminino"] += 1
            totais["feminino"] += 1

        relatorio[idade]["total"] += 1
        totais["total"] += 1

    relatorio_ordenado = dict(sorted(relatorio.items()))

    context = {
        "turmas": turmas,
        "turma_id": turma_id,
        "turma_selecionada": turma_selecionada,
        "relatorio": relatorio_ordenado,
        "totais": totais,
        "escola": escola,
        "ano_letivo": ano_letivo,
    }

    return render(request, 'alunos/relatorio_por_idade.html', context)

