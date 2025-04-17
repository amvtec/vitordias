from django import forms
from .models import FolhaMensal
from .models import Funcionario

from django import forms
from .models import FolhaMensal

class FolhaMensalForm(forms.ModelForm):
    class Meta:
        model = FolhaMensal
        exclude = ['funcionario', 'mes']  # <- mes está sendo tratado à parte

from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'
