from django.db import models
from django.contrib.auth.models import User

# Lista de UFs para escolha
UF_CHOICES = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MG', 'Minas Gerais'), ('MS', 'Mato Grosso do Sul'),
    ('MT', 'Mato Grosso'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PE', 'Pernambuco'),
    ('PI', 'Piauí'), ('PR', 'Paraná'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RO', 'Rondônia'), ('RR', 'Roraima'), ('RS', 'Rio Grande do Sul'), ('SC', 'Santa Catarina'),
    ('SE', 'Sergipe'), ('SP', 'São Paulo'), ('TO', 'Tocantins'),
]

# Lista de cor/raça
COR_RACA = [
    ('branca', 'Branca'),
    ('preta', 'Preta'),
    ('parda', 'Parda'),
    ('amarela', 'Amarela'),
    ('indigena', 'Indígena'),
]

# Lista de anos/séries
ANOS_SERIE = [
    ('1º ANO', '1º ANO'),
    ('2º ANO', '2º ANO'),
    ('3º ANO', '3º ANO'),
    ('4º ANO', '4º ANO'),
    ('5º ANO', '5º ANO'),
]

# Lista de turnos
TURNOS = [
    ('matutino', 'Matutino'),
    ('vespertino', 'Vespertino')
]

class Professor(models.Model):
    nome = models.CharField(max_length=200)
    especializacao = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome


class Turma(models.Model):
    nome = models.CharField(max_length=2)  # A, B, C, etc.
    serie = models.CharField(max_length=50, choices=ANOS_SERIE)
    turno = models.CharField(max_length=10, choices=TURNOS)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    alunos = models.ManyToManyField('Aluno', blank=True, related_name="turmas")
    max_alunos = models.IntegerField(default=20)

    def __str__(self):
        return f"{self.serie} - Turma {self.nome} - {self.turno}"


class Aluno(models.Model):
    ALUNO_STATUS = [
        ('veterano', 'Veterano'),
        ('novato', 'Novato'),
    ]
    status = models.CharField(max_length=10, choices=ALUNO_STATUS)

    SITUACAO_STATUS = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('transferido', 'Transferido'),
    ]
    situacao = models.CharField(max_length=15, choices=SITUACAO_STATUS, default='ativo')

    unidade_escolar = models.CharField(max_length=100, default='Escola Municipal Vitor Dias')
    municipio = models.CharField(max_length=50, default='Darcinópolis-TO')
    dre = models.CharField(max_length=50, default='Tocantinópolis-TO')

    MODALIDADE = [
        ('regular', 'Regular'),
        ('eja', 'EJA'),
        ('especial', 'Educação Especial'),
        ('outra', 'Outra'),
    ]
    modalidade = models.CharField(max_length=20, choices=MODALIDADE)
    outra_modalidade = models.CharField(max_length=50, blank=True, null=True)

    etapa = models.CharField(max_length=50, default='Ensino Fundamental')
    ano_serie = models.CharField(max_length=30, choices=ANOS_SERIE)
    turno = models.CharField(max_length=10, choices=TURNOS, blank=True, null=True)

    nome = models.CharField(max_length=200)
    sexo = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Feminino')])
    cor_raca = models.CharField(max_length=20, choices=COR_RACA, blank=True, null=True)
    aluno_id = models.CharField(max_length=30, blank=True, null=True)
    nis = models.CharField(max_length=30, blank=True, null=True)
    data_nascimento = models.DateField()
    profissao = models.CharField(max_length=50, default='Estudante')
    foto = models.ImageField(upload_to='fotos_alunos/', blank=True, null=True)

    endereco = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    cep = models.CharField(max_length=20, default='77910-000')
    cidade = models.CharField(max_length=50, default='Darcinópolis-TO')
    uf = models.CharField(max_length=2, choices=UF_CHOICES, default='TO')
    zona = models.CharField(max_length=10, choices=[('rural', 'Rural'), ('urbana', 'Urbana')])

    transporte_escolar = models.BooleanField()
    rota = models.CharField(max_length=100, blank=True, null=True)
    distancia = models.CharField(max_length=100, blank=True, null=True)

    cidade_nascimento = models.CharField(max_length=50)
    uf_nascimento = models.CharField(max_length=2, choices=UF_CHOICES)
    nacionalidade = models.CharField(max_length=30)

    certidao_numero = models.CharField(max_length=50)
    certidao_folha = models.CharField(max_length=10)
    certidao_livro = models.CharField(max_length=20)
    numero_matricula = models.CharField(max_length=100)
    cartorio_nome = models.CharField(max_length=100)
    cartorio_uf = models.CharField(max_length=2, choices=UF_CHOICES)
    cartorio_cidade = models.CharField(max_length=50)

    cpf = models.CharField(max_length=20, blank=True, null=True)
    rg = models.CharField(max_length=20, blank=True, null=True)

    nome_pai = models.CharField(max_length=100, blank=True, null=True)
    nascimento_pai = models.DateField(blank=True, null=True)
    escolaridade_pai = models.CharField(max_length=100, blank=True, null=True)
    profissao_pai = models.CharField(max_length=100, blank=True, null=True)
    telefone_pai = models.CharField(max_length=20, blank=True, null=True)

    nome_mae = models.CharField(max_length=100, blank=True, null=True)
    nascimento_mae = models.DateField(blank=True, null=True)
    escolaridade_mae = models.CharField(max_length=100, blank=True, null=True)
    profissao_mae = models.CharField(max_length=100, blank=True, null=True)
    telefone_mae = models.CharField(max_length=20, blank=True, null=True)

    reacoes_alergicas = models.BooleanField(default=False)
    descricao_alergia = models.CharField(max_length=200, blank=True, null=True)

    necessidade_especial = models.BooleanField(default=False)
    descricao_necessidade = models.CharField(max_length=200, blank=True, null=True)
    possui_laudo = models.BooleanField(default=False)

    sala_recursos = models.BooleanField(default=False)
    ue_atendimento = models.CharField(max_length=100, blank=True, null=True)

    bolsa_familia = models.BooleanField(default=False)
    bpc = models.BooleanField(default=False)
    outro_programa = models.CharField(max_length=100, blank=True, null=True)

    medicamento_controlado = models.BooleanField(default=False)
    nome_medicamento = models.CharField(max_length=100, blank=True, null=True)

    ensino_religioso = models.BooleanField(default=False)

    escola_anterior = models.CharField(max_length=200, blank=True, null=True)
    rede_anterior = models.CharField(max_length=30, choices=[
        ('estadual', 'Rede Estadual'),
        ('municipal', 'Rede Municipal'),
        ('privada', 'Rede Privada'),
        ('conveniada', 'Rede Conveniada'),
    ], blank=True, null=True)

    aprovado_ano = models.CharField(max_length=50, blank=True, null=True)
    reprovado_ano = models.CharField(max_length=50, blank=True, null=True)
    em_curso_ano = models.CharField(max_length=50, blank=True, null=True)

    classificado = models.BooleanField(default=False)
    reclassificado = models.BooleanField(default=False)

    ano_rematricula = models.IntegerField(blank=True, null=True, default=None)

    turma = models.ForeignKey('Turma', on_delete=models.SET_NULL, null=True, blank=True)
    professor = models.ForeignKey('Professor', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # Só tenta alocar automaticamente se a turma estiver vazia
        if not self.turma and self.ano_serie and self.turno:
            turma_disponivel = Turma.objects.filter(
                serie=self.ano_serie,
                turno=self.turno
            ).annotate(num_alunos=models.Count('alunos')).filter(num_alunos__lt=models.F('max_alunos')).first()

            if turma_disponivel:
                self.turma = turma_disponivel

        super().save(*args, **kwargs)

        # Adiciona o aluno à lista ManyToMany da turma
        if self.turma and not self.turma.alunos.filter(id=self.id).exists():
            self.turma.alunos.add(self)



class Funcionario(models.Model):
    FUNCOES = [
        ('Administrador', 'Administrador(a)'),  # ✅ Nova função com acesso total
        ('Diretor(a)', 'Diretor(a)'),
        ('Secretario(a)', 'Secretário(a)'),
        ('Coordenador(a)', 'Coordenador(a)'),
        ('Agente Administrativo', 'Agente Administrativo'),
        ('Auxiliar Administrativo', 'Auxiliar Administrativo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    funcao = models.CharField(max_length=30, choices=FUNCOES)
    numero_matricula = models.CharField(max_length=20)
    decreto_nomeacao = models.CharField(max_length=100)
    assinatura = models.ImageField(upload_to='assinaturas/', null=True, blank=True)  # ✅ Campo para imagem da assinatura

    def __str__(self):
        return f"{self.nome} - {self.funcao}"

    
class Escola(models.Model):
    nome_secretaria = models.CharField(max_length=255)
    nome_escola = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)  # Formato: 00.000.000/0000-00
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)  # UF do Brasil (exemplo: 'MG', 'SP', etc.)
    logo = models.ImageField(upload_to='escolas/logos/', blank=True, null=True)
    imagem_fundo = models.ImageField(upload_to='escolas/fundos/', blank=True, null=True)  # Novo campo para imagem de fundo
    telefone = models.CharField(max_length=15, blank=True, null=True)  # Telefone da escola
    email = models.EmailField(max_length=254, blank=True, null=True)  # E-mail da escola

    def __str__(self):
        return f"{self.nome_escola} - {self.nome_secretaria}"

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"

class DocumentoAluno(models.Model):
    TIPO_CHOICES = [
        ('matricula', 'Ficha de Matrícula'),
        ('declaracao', 'Declaração de Matrícula'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_geracao = models.DateTimeField(auto_now_add=True)

    html_gerado = models.TextField()  # Conteúdo da versão renderizada

    assinada_diretor = models.BooleanField(default=False)
    data_assinatura_diretor = models.DateTimeField(blank=True, null=True)

    assinada_secretario = models.BooleanField(default=False)
    data_assinatura_secretario = models.DateTimeField(blank=True, null=True)

    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.aluno.nome} ({self.data_geracao.date()})"

    class Meta:
        ordering = ['-data_geracao']
