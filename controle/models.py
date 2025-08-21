from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


# =======================
# Novos modelos
# =======================

class Prefeitura(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True, unique=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = CloudinaryField('Logo da prefeitura', blank=True, null=True)

    class Meta:
        verbose_name = "Prefeitura"
        verbose_name_plural = "Prefeituras"

    def __str__(self):
        return self.nome


class Secretaria(models.Model):
    prefeitura = models.ForeignKey(
        Prefeitura,
        on_delete=models.PROTECT,
        related_name='secretarias'
    )
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = CloudinaryField('Logo da secretaria', blank=True, null=True)

    class Meta:
        unique_together = ('prefeitura', 'nome')
        verbose_name = "Secretaria"
        verbose_name_plural = "Secretarias"

    def __str__(self):
        return f"{self.nome} ({self.prefeitura})"


# =======================
# Modelos existentes (mantidos)
# =======================

class Setor(models.Model):
    nome = models.CharField(max_length=100)
    # Vínculo novo: Setor -> Secretaria (mantido opcional para migrar sem dor)
    secretaria = models.ForeignKey(
        Secretaria,
        on_delete=models.PROTECT,
        related_name='setores',
        null=True,
        blank=True
    )

    def __str__(self):
        if self.secretaria:
            return f"{self.nome} — {self.secretaria.nome}"
        return self.nome


class Funcionario(models.Model):
    TURNO_CHOICES = [
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno'),
        ('Integral', 'Integral'),
    ]

    SERIE_CHOICES = [
        ('1º ANO', '1º ANO'),
        ('2º ANO', '2º ANO'),
        ('3º ANO', '3º ANO'),
        ('4º ANO', '4º ANO'),
        ('5º ANO', '5º ANO'),
        ('6º ANO', '6º ANO'),
        ('7º ANO', '7º ANO'),
        ('8º ANO', '8º ANO'),
        ('9º ANO', '9º ANO'),
    ]

    TURMA_CHOICES = [
        ('A', 'Turma A'),
        ('B', 'Turma B'),
        ('C', 'Turma C'),
        ('D', 'Turma D'),
        ('E', 'Turma E'),
        ('F', 'Turma F'),
        ('G', 'Turma G'),
    ]

    TIPO_VINCULO_CHOICES = [
        ('Efetivo', 'Efetivo'),
        ('Contratado', 'Contratado'),
    ]

    # Vínculo OPCIONAL com usuário para permissões (não quebra cadastro existente)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='horarios',
        null=True,
        blank=True,
        help_text="Vínculo opcional com usuário do sistema."
    )

    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=50)
    funcao = models.CharField(max_length=50)
    setor = models.ForeignKey('Setor', on_delete=models.CASCADE)
    data_admissao = models.DateField()
    data_nascimento = models.DateField(null=True, blank=True)

    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    pis = models.CharField(max_length=20, blank=True, null=True)
    titulo_eleitor = models.CharField(max_length=20, blank=True, null=True)
    ctps_numero = models.CharField(max_length=20, blank=True, null=True)
    ctps_serie = models.CharField(max_length=10, blank=True, null=True)

    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)

    estado_civil = models.CharField(max_length=20, blank=True, null=True)
    escolaridade = models.CharField(max_length=100, blank=True, null=True)
    tem_planejamento = models.BooleanField(default=False)
    horario_planejamento = models.CharField(max_length=50, blank=True, null=True)
    sabado_letivo = models.BooleanField(default=False)

    foto = models.ImageField(upload_to='fotos_funcionarios/', blank=True, null=True)

    turma = models.CharField(max_length=10, choices=TURMA_CHOICES, blank=True, null=True)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, blank=True, null=True)
    serie = models.CharField(max_length=20, choices=SERIE_CHOICES, blank=True, null=True)

    tipo_vinculo = models.CharField(
        max_length=20,
        choices=TIPO_VINCULO_CHOICES,
        blank=True,
        null=True
    )

    fonte_pagadora = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    inicio_ferias = models.DateField(blank=True, null=True)
    fim_ferias = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nome


class HorarioTrabalho(models.Model):
    TURNOS = [
        ('Manhã', 'Manhã'),
        ('Tarde', 'Tarde'),
    ]
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    turno = models.CharField(max_length=10, choices=TURNOS)
    horario_inicio = models.TimeField(blank=True, null=True)
    horario_fim = models.TimeField(blank=True, null=True)

    def __str__(self):
        hi = self.horario_inicio.strftime('%H:%M') if self.horario_inicio else '__:__'
        hf = self.horario_fim.strftime('%H:%M') if self.horario_fim else '__:__'
        return f"{self.funcionario.nome} - {self.turno}: {hi} às {hf}"


class Feriado(models.Model):
    data = models.DateField(unique=True)
    descricao = models.CharField(max_length=100)
    sabado_letivo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.data.strftime('%d/%m/%Y')} - {self.descricao}"


class FolhaFrequencia(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    mes = models.IntegerField()
    ano = models.IntegerField()
    data_geracao = models.DateTimeField(auto_now_add=True)
    html_armazenado = models.TextField()

    class Meta:
        unique_together = ('funcionario', 'mes', 'ano')

    def __str__(self):
        return f"{self.funcionario.nome} - {self.mes:02d}/{self.ano}"


class SabadoLetivo(models.Model):
    data = models.DateField(unique=True)
    descricao = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Sábado Letivo - {self.data.strftime('%d/%m/%Y')}"


class Escola(models.Model):
    nome_secretaria = models.CharField(max_length=255)
    nome_escola = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    logo = CloudinaryField('Imagem de fundo', blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

    # Opcional: vincular Escola a uma Secretaria (sem quebrar o que já existe)
    secretaria = models.ForeignKey(
        Secretaria,
        on_delete=models.PROTECT,
        related_name='escolas',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nome_escola} - {self.nome_secretaria}"

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"


# =======================
# Permissões por Secretaria
# =======================

class AcessoSecretaria(models.Model):
    class Nivel(models.TextChoices):
        LEITURA = 'LEITURA', 'Leitura'
        GERENCIA = 'GERENCIA', 'Gerenciar (CRUD)'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='acessos_secretaria'
    )
    secretaria = models.ForeignKey(
        Secretaria,
        on_delete=models.CASCADE,
        related_name='acessos'
    )
    nivel = models.CharField(
        max_length=16,
        choices=Nivel.choices,
        default=Nivel.LEITURA
    )

    class Meta:
        unique_together = ('user', 'secretaria')
        verbose_name = "Acesso à Secretaria"
        verbose_name_plural = "Acessos às Secretarias"

    def __str__(self):
        return f"{self.user} -> {self.secretaria} ({self.get_nivel_display()})"
