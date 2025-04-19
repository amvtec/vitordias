from django.db import models
from cloudinary.models import CloudinaryField

class Setor(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Funcionario(models.Model):
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20)
    cargo = models.CharField(max_length=50)
    funcao = models.CharField(max_length=50)
    data_admissao = models.DateField()
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    
    # Campos adicionais
    tem_planejamento = models.BooleanField(default=False)
    horario_planejamento = models.CharField(max_length=50, blank=True, null=True)
    sabado_letivo = models.BooleanField(default=False)
    data_nascimento = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome

class HorarioTrabalho(models.Model):
    TURNOS = [
        ('Manhã', 'Manhã'),
        ('Tarde', 'Tarde'),
    ]
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    turno = models.CharField(max_length=10, choices=TURNOS)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):
        return f"{self.funcionario.nome} - {self.turno}: {self.horario_inicio} às {self.horario_fim}"

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

    def __str__(self):
        return f"{self.nome_escola} - {self.nome_secretaria}"

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
