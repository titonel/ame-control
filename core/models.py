from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator, RegexValidator


class UsuarioManager(BaseUserManager):
    """Manager customizado para o modelo Usuario."""
    
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('tier', 5)
        extra_fields.setdefault('primeiro_acesso', False)

        return self.create_user(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    """Modelo customizado de usuário com níveis de acesso (RBAC)."""
    
    TIER_CHOICES = [
        (1, 'Tier 1 - Operacional'),
        (2, 'Tier 2 - Analista/Líder'),
        (3, 'Tier 3 - Supervisor'),
        (4, 'Tier 4 - Coordenador'),
        (5, 'Tier 5 - Gerente/Administrador'),
    ]
    
    # O username será gerado automaticamente do email
    email = models.EmailField(
        'E-mail',
        unique=True,
        validators=[EmailValidator()]
    )
    nome_completo = models.CharField('Nome Completo', max_length=255)
    
    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message='CPF deve estar no formato: 000.000.000-00'
        )]
    )
    
    drt = models.CharField(
        'DRT/Matrícula',
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\d+$',
            message='DRT/Matrícula deve conter apenas números'
        )],
        help_text='Apenas números'
    )
    
    tier = models.IntegerField(
        'Nível de Acesso',
        choices=TIER_CHOICES,
        default=1
    )
    
    primeiro_acesso = models.BooleanField(
        'Primeiro Acesso',
        default=True,
        help_text='Indica se o usuário precisa trocar a senha no próximo login'
    )
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nome_completo']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.get_tier_display()})"
    
    def save(self, *args, **kwargs):
        # Gera o username a partir do email se não foi definido
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
    
    def pode_cadastrar_usuarios(self):
        """Verifica se o usuário tem permissão para cadastrar outros usuários."""
        return self.tier >= 3


class Empresa(models.Model):
    """Modelo para cadastro de empresas."""
    
    razao_social = models.CharField('Razão Social', max_length=255)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=255, blank=True)
    
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
            message='CNPJ deve estar no formato: 00.000.000/0000-00'
        )]
    )
    
    endereco = models.TextField('Endereço', blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    
    ativa = models.BooleanField('Ativa', default=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    cadastrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='empresas_cadastradas',
        verbose_name='Cadastrado por'
    )
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['razao_social']
    
    def __str__(self):
        return self.nome_fantasia or self.razao_social


class Medico(models.Model):
    """Modelo para cadastro de médicos."""
    
    nome_completo = models.CharField('Nome Completo', max_length=255)
    
    crm = models.CharField(
        'CRM',
        max_length=20,
        unique=True,
        help_text='Ex: CRM/SP 123456'
    )
    
    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message='CPF deve estar no formato: 000.000.000-00'
        )]
    )
    
    especialidade = models.CharField('Especialidade', max_length=100, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    
    ativo = models.BooleanField('Ativo', default=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    cadastrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='medicos_cadastrados',
        verbose_name='Cadastrado por'
    )
    
    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"Dr(a). {self.nome_completo} - {self.crm}"
