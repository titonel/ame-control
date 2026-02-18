from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import Usuario, Empresa, Medico, Cirurgia, Exame, ServicoMedico
import csv
import io


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
        usuario.username = self.cleaned_data['email'].split('@')[0]
        usuario.set_password('farol')
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


# ===== FORMULÁRIOS DA ÁREA ADMINISTRATIVA =====

class CirurgiaForm(forms.ModelForm):
    """Formulário para cadastro de cirurgias."""
    
    class Meta:
        model = Cirurgia
        fields = ['codigo_sigtap', 'descricao', 'valor', 'tipo_cirurgia', 'especialidade', 'ativa']
        widgets = {
            'codigo_sigtap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 04.07.01.012-0',
                'id': 'codigo_sigtap_field'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'id': 'descricao_field'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'id': 'valor_field'
            }),
            'tipo_cirurgia': forms.Select(attrs={
                'class': 'form-select',
                'id': 'tipo_cirurgia_field'
            }),
            'especialidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ortopedia',
                'id': 'especialidade_field'
            }),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CirurgiaUploadForm(forms.Form):
    """Formulário para upload de CSV de cirurgias."""
    arquivo_csv = forms.FileField(
        label='Arquivo CSV',
        help_text='Upload de arquivo CSV com as colunas: Código SIGTAP, Descrição, Valor, Tipo Cirurgia, Especialidade',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )
    
    def clean_arquivo_csv(self):
        arquivo = self.cleaned_data.get('arquivo_csv')
        
        if not arquivo.name.endswith('.csv'):
            raise ValidationError('O arquivo deve estar no formato CSV.')
        
        # Verifica se o arquivo é UTF-8 (aceita BOM)
        try:
            arquivo.seek(0)
            content = arquivo.read().decode('utf-8-sig')  # utf-8-sig remove BOM
            arquivo.seek(0)
        except UnicodeDecodeError:
            raise ValidationError('O arquivo deve estar codificado em UTF-8.')
        
        # Valida as colunas
        arquivo.seek(0)
        content_str = arquivo.read().decode('utf-8-sig')
        csv_file = io.StringIO(content_str)
        
        # Detecta delimitador
        sample = csv_file.read(1024)
        csv_file.seek(0)
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(sample).delimiter
        except:
            delimiter = ';'  # Default para ponto e vírgula
        
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        
        required_columns = ['Codigo SIGTAP', 'Descricao', 'Valor', 'Tipo Cirurgia', 'Especialidade']
        
        if not reader.fieldnames:
            raise ValidationError('O arquivo CSV está vazio ou mal formatado.')
        
        # Normaliza fieldnames (remove espaços extras)
        fieldnames_normalized = [f.strip() for f in reader.fieldnames]
        fieldnames_lower = [f.lower() for f in fieldnames_normalized]
        
        # Aceita variações nos nomes das colunas
        for col in required_columns:
            col_variations = [col.lower(), col.lower().replace(' ', '_')]
            if not any(variation in fieldnames_lower for variation in col_variations):
                raise ValidationError(f'Coluna obrigatória ausente: {col}. Colunas encontradas: {", ".join(fieldnames_normalized)}')
        
        arquivo.seek(0)
        return arquivo


class ExameForm(forms.ModelForm):
    """Formulário para cadastro de exames."""
    
    class Meta:
        model = Exame
        fields = ['codigo_sigtap', 'descricao', 'valor', 'tipo_exame', 'preparo', 'ativo']
        widgets = {
            'codigo_sigtap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 02.02.03.004-0'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'tipo_exame': forms.Select(attrs={'class': 'form-select'}),
            'preparo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Orientações de preparo...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ServicoMedicoForm(forms.ModelForm):
    """Formulário para cadastro de serviços médicos."""

    class Meta:
        model = ServicoMedico
        fields = ['valor', 'especialidade', 'duracao_estimada', 'ativo']
        widgets = {
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'especialidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Clínica Médica'
            }),
            'duracao_estimada': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minutos'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProducaoUploadForm(forms.Form):
    """Formulário para upload de planilha de produção mensal."""
    arquivo = forms.FileField(
        label='Arquivo de Produção',
        help_text='Formatos aceitos: .xlsx, .xls ou .csv (UTF-8)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        })
    )

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            nome = arquivo.name.lower()
            if not (nome.endswith('.xlsx') or nome.endswith('.xls') or nome.endswith('.csv')):
                raise ValidationError('O arquivo deve ser no formato .xlsx, .xls ou .csv.')
        return arquivo
        return arquivo
