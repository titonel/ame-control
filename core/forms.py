from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import Usuario, Empresa, Medico


class LoginForm(forms.Form):
    """Formulário de login."""
    username = forms.CharField(
        label='Usuário',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )


class TrocaSenhaForm(PasswordChangeForm):
    """Formulário para troca de senha no primeiro acesso."""
    old_password = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha atual'
        })
    )
    new_password1 = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        })
    )
    new_password2 = forms.CharField(
        label='Confirme a Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )


class UsuarioForm(forms.ModelForm):
    """Formulário para cadastro de usuários."""
    username_display = forms.CharField(
        label='Username (gerado automaticamente)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'username_display',
            'placeholder': 'Será gerado após digitar o e-mail'
        }),
        help_text='O username será a parte do e-mail antes do @'
    )
    
    class Meta:
        model = Usuario
        fields = ['nome_completo', 'email', 'cpf', 'drt', 'tier']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'email_field'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'drt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apenas números'
            }),
            'tier': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Já existe um usuário com este e-mail.')
        return email
    
    def clean_drt(self):
        drt = self.cleaned_data.get('drt')
        if drt and not drt.isdigit():
            raise ValidationError('DRT/Matrícula deve conter apenas números.')
        return drt
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        # Gera o username a partir do email
        usuario.username = self.cleaned_data['email'].split('@')[0]
        # Define a senha padrão
        usuario.set_password('ame-control')
        usuario.primeiro_acesso = True
        if commit:
            usuario.save()
        return usuario


class EmpresaForm(forms.ModelForm):
    """Formulário para cadastro de empresas."""
    
    class Meta:
        model = Empresa
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'telefone', 'email', 'ativa'
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'cep_field'
            }),
            'logradouro': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'logradouro_field',
                'placeholder': 'Rua, Avenida, etc.'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'numero_field',
                'placeholder': 'Número'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'complemento_field',
                'placeholder': 'Apto, Sala, Bloco, etc.'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'bairro_field',
                'placeholder': 'Bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'cidade_field',
                'placeholder': 'Cidade'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'estado_field',
                'placeholder': 'UF (ex: SP)',
                'maxlength': '2',
                'style': 'text-transform: uppercase;'
            }),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MedicoForm(forms.ModelForm):
    """Formulário para cadastro de médicos."""
    
    class Meta:
        model = Medico
        fields = ['nome_completo', 'crm', 'cpf', 'especialidade', 'telefone', 'email', 'ativo']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'crm': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CRM/SP 123456'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'especialidade': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
