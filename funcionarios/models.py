from django.db import models

class Funcionario(models.Model):
    SETOR_CHOICES = [
        ('Administrativo', 'Administrativo'),
        ('Pedagógico', 'Pedagógico'),
    ]

    nome = models.CharField(max_length=100)  # Obrigatório
    funcao = models.CharField(max_length=50, blank=True, null=True)
    carga_horaria_semanal = models.IntegerField(blank=True, null=True)
    carga_horaria_mensal = models.IntegerField(blank=True, null=True)
    planejamento = models.BooleanField(default=False)
    aluno_especial = models.BooleanField(default=False)
    data_nascimento = models.DateField(null=True, blank=True)
    setor = models.CharField(max_length=20, choices=SETOR_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.nome



class FolhaMensal(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='folhas')
    mes = models.CharField(max_length=20)
    ano = models.IntegerField()
    faltas = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    diarias_qtd = models.PositiveIntegerField(blank=True, null=True)
    diarias_horas = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)

    servidor_substituto = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='substituicoes',
        verbose_name='Servidor Substituto'
    )

    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.funcionario.nome} - {self.mes}/{self.ano}'

