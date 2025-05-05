from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'matricula', 'cargo', 'funcao', 'data_admissao', 'data_nascimento', 'setor', 'tem_planejamento', 'horario_planejamento']
        widgets = {
            'data_admissao': forms.TextInput(attrs={
                'placeholder': '00/00/0000',
                'class': 'data-input',
                'autocomplete': 'off'
            }),
            'data_nascimento': forms.TextInput(attrs={
                'placeholder': '00/00/0000',
                'class': 'data-input',
                'autocomplete': 'off'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(FuncionarioForm, self).__init__(*args, **kwargs)

        # Permitir formato dd/mm/yyyy para os campos data_admissao e data_nascimento
        self.fields['data_admissao'].input_formats = ['%d/%m/%Y']
        self.fields['data_nascimento'].input_formats = ['%d/%m/%Y']

        # Controlar se o campo de horário é obrigatório
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
