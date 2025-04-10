from django.db import models

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
    
    # Adicionando novos campos
    tem_planejamento = models.BooleanField(default=False)  # Se o funcionário tem planejamento
    horario_planejamento = models.CharField(max_length=50, blank=True, null=True)  # Horário do planejamento
    sabado_letivo = models.BooleanField(default=False)  # Se o sábado é letivo para esse funcionário

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
    sabado_letivo = models.BooleanField(default=False)  # Marca o sábado como letivo

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

from django.db import models

class SabadoLetivo(models.Model):
    data = models.DateField(unique=True)  # Data do sábado letivo
    descricao = models.CharField(max_length=100, blank=True, null=True)  # Descrição opcional

    def __str__(self):
        return f"Sábado Letivo - {self.data.strftime('%d/%m/%Y')}"

# controle/models.py

from django.db import models

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
    telefone = models.CharField(max_length=15, blank=True, null=True)  # Telefone da escola
    email = models.EmailField(max_length=254, blank=True, null=True)  # E-mail da escola

    def __str__(self):
        return f"{self.nome_escola} - {self.nome_secretaria}"

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
