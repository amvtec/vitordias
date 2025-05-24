from django import forms
from .models import Funcionario
from datetime import date


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            'nome',
            'matricula',
            'cargo',
            'funcao',
            'setor',
            'turno',
            'turma',
            'data_admissao',
            'data_nascimento',
            'cpf',
            'rg',
            'pis',
            'titulo_eleitor',
            'ctps_numero',
            'ctps_serie',
            'telefone',
            'email',
            'endereco',
            'numero',
            'bairro',
            'cidade',
            'uf',
            'cep',
            'estado_civil',
            'escolaridade',
            'tem_planejamento',
            'horario_planejamento',
            'sabado_letivo',
            'foto',
        ]

        widgets = {
            'data_admissao': forms.TextInput(attrs={
                'placeholder': 'dd/mm/aaaa',
                'class': 'data-input',
                'autocomplete': 'off',
                'data-mask': 'date',
            }),
            'data_nascimento': forms.TextInput(attrs={
                'placeholder': 'dd/mm/aaaa',
                'class': 'data-input',
                'autocomplete': 'off',
                'data-mask': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(FuncionarioForm, self).__init__(*args, **kwargs)

        # Aceitar entrada no formato brasileiro
        self.fields['data_admissao'].input_formats = ['%d/%m/%Y']
        self.fields['data_nascimento'].input_formats = ['%d/%m/%Y']

        # Mostrar valores já salvos no formato correto ao editar
        if self.instance and self.instance.pk:
            if self.instance.data_admissao:
                self.initial['data_admissao'] = self.instance.data_admissao.strftime('%d/%m/%Y')
            if self.instance.data_nascimento:
                self.initial['data_nascimento'] = self.instance.data_nascimento.strftime('%d/%m/%Y')

        # Campo opcional inicialmente
        self.fields['horario_planejamento'].required = False
        if self.instance and self.instance.tem_planejamento:
            self.fields['horario_planejamento'].required = True

from .models import HorarioTrabalho

class HorarioTrabalhoForm(forms.ModelForm):
    class Meta:
        model = HorarioTrabalho
        fields = ['funcionario', 'turno', 'horario_inicio', 'horario_fim']
        widgets = {
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

from .models import Feriado

class FeriadoForm(forms.ModelForm):
    class Meta:
        model = Feriado
        fields = ['data', 'descricao', 'sabado_letivo']  # Incluindo o campo sabado_letivo
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'sabado_letivo': forms.CheckboxInput(attrs={'class': 'checkbox-input'}),  # Checkbox para sábado letivo
        }


class ImportacaoFuncionarioForm(forms.Form):
    excel_file = forms.FileField(label='Arquivo Excel', required=True)

MESES_CHOICES = [
    (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
    (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
    (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
]

class GerarFolhasIndividuaisForm(forms.Form):
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all(), label="Funcionário")
    ano = forms.IntegerField(label="Ano", initial=date.today().year)
    meses = forms.MultipleChoiceField(choices=MESES_CHOICES, widget=forms.CheckboxSelectMultiple, label="Meses")
