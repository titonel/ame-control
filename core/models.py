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
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
    
    def pode_cadastrar_usuarios(self):
        """Verifica se o usuário tem permissão para cadastrar outros usuários."""
        return self.tier >= 3
    
    def is_admin(self):
        """Verifica se o usuário é administrador (Tier 5)."""
        return self.tier == 5


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
    
    cep = models.CharField(
        'CEP',
        max_length=9,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\d{5}-\d{3}$',
            message='CEP deve estar no formato: 00000-000'
        )]
    )
    logradouro = models.CharField('Logradouro', max_length=255, blank=True, help_text='Rua, Avenida, etc.')
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True, help_text='Apto, Sala, Bloco, etc.')
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField(
        'Estado',
        max_length=2,
        blank=True,
        validators=[RegexValidator(
            regex=r'^[A-Z]{2}$',
            message='Estado deve ser a sigla com 2 letras maiúsculas (ex: SP)'
        )]
    )
    
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
    
    @property
    def endereco_completo(self):
        """Retorna o endereço completo formatado."""
        partes = []
        if self.logradouro:
            partes.append(self.logradouro)
        if self.numero:
            partes.append(f"nº {self.numero}")
        if self.complemento:
            partes.append(self.complemento)
        if self.bairro:
            partes.append(f"- {self.bairro}")
        if self.cidade and self.estado:
            partes.append(f"- {self.cidade}/{self.estado}")
        if self.cep:
            partes.append(f"- CEP: {self.cep}")
        return ' '.join(partes) if partes else 'Endereço não informado'


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


# ===== MODELOS DA ÁREA ADMINISTRATIVA =====

class Cirurgia(models.Model):
    """Modelo para cadastro de cirurgias."""
    
    TIPO_CHOICES = [
        ('ELETIVA', 'Eletiva'),
        ('URGENCIA', 'Urgência'),
        ('EMERGENCIA', 'Emergência'),
        ('AMBULATORIAL', 'Ambulatorial'),
    ]
    
    codigo_sigtap = models.CharField(
        'Código SIGTAP',
        max_length=20,
        unique=True,
        help_text='Ex: 04.07.01.012-0'
    )
    
    descricao = models.CharField('Descrição', max_length=500)
    
    valor = models.DecimalField(
        'Valor (R$)',
        max_digits=10,
        decimal_places=2,
        help_text='Valor do procedimento em reais'
    )
    
    tipo_cirurgia = models.CharField(
        'Tipo de Cirurgia',
        max_length=20,
        choices=TIPO_CHOICES,
        default='ELETIVA'
    )
    
    especialidade = models.CharField(
        'Especialidade',
        max_length=100,
        help_text='Ex: Ortopedia, Cardiologia, etc.'
    )
    
    ativa = models.BooleanField('Ativa', default=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    cadastrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cirurgias_cadastradas',
        verbose_name='Cadastrado por'
    )
    
    class Meta:
        verbose_name = 'Cirurgia'
        verbose_name_plural = 'Cirurgias'
        ordering = ['especialidade', 'descricao']
    
    def __str__(self):
        return f"{self.codigo_sigtap} - {self.descricao}"


class Exame(models.Model):
    """Modelo para cadastro de exames."""
    
    TIPO_CHOICES = [
        ('LABORATORIAL', 'Laboratorial'),
        ('IMAGEM', 'Imagem'),
        ('FUNCIONAL', 'Funcional'),
        ('PATOLOGIA', 'Patologia'),
    ]
    
    codigo_sigtap = models.CharField(
        'Código SIGTAP',
        max_length=20,
        unique=True,
        help_text='Ex: 02.02.03.004-0'
    )
    
    descricao = models.CharField('Descrição', max_length=500)
    
    valor = models.DecimalField(
        'Valor (R$)',
        max_digits=10,
        decimal_places=2,
        help_text='Valor do exame em reais'
    )
    
    tipo_exame = models.CharField(
        'Tipo de Exame',
        max_length=20,
        choices=TIPO_CHOICES,
        default='LABORATORIAL'
    )
    
    preparo = models.TextField(
        'Preparo',
        blank=True,
        help_text='Orientações de preparo para o exame'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    cadastrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='exames_cadastrados',
        verbose_name='Cadastrado por'
    )
    
    class Meta:
        verbose_name = 'Exame'
        verbose_name_plural = 'Exames'
        ordering = ['tipo_exame', 'descricao']
    
    def __str__(self):
        return f"{self.codigo_sigtap} - {self.descricao}"


class ServicoMedico(models.Model):
    """Modelo para cadastro de serviços médicos."""
    
    codigo_sigtap = models.CharField(
        'Código SIGTAP',
        max_length=20,
        unique=True,
        help_text='Ex: 03.01.01.007-5'
    )
    
    descricao = models.CharField('Descrição', max_length=500)
    
    valor = models.DecimalField(
        'Valor (R$)',
        max_digits=10,
        decimal_places=2,
        help_text='Valor do serviço em reais'
    )
    
    especialidade = models.CharField(
        'Especialidade',
        max_length=100,
        blank=True,
        help_text='Especialidade responsável pelo serviço'
    )
    
    duracao_estimada = models.IntegerField(
        'Duração Estimada (minutos)',
        blank=True,
        null=True,
        help_text='Tempo estimado do atendimento em minutos'
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    cadastrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='servicos_cadastrados',
        verbose_name='Cadastrado por'
    )
    
    class Meta:
        verbose_name = 'Serviço Médico'
        verbose_name_plural = 'Serviços Médicos'
        ordering = ['especialidade', 'descricao']
    
    def __str__(self):
        return f"{self.codigo_sigtap} - {self.descricao}"
