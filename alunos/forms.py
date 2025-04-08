from django import forms
from .models import Aluno
from .models import Funcionario

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'nascimento_pai': forms.DateInput(attrs={'type': 'date'}),
            'nascimento_mae': forms.DateInput(attrs={'type': 'date'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Nome de Usuário', widget=forms.TextInput(attrs={'placeholder': 'Digite seu nome de usuário'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'}), label='Senha')

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['user', 'nome', 'funcao', 'numero_matricula', 'decreto_nomeacao']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'funcao': forms.Select(attrs={'class': 'form-control'}),
            'numero_matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'decreto_nomeacao': forms.TextInput(attrs={'class': 'form-control'}),
        }