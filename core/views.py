from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from functools import wraps
import csv
import io
from decimal import Decimal

from .forms import (
    LoginForm, TrocaSenhaForm, UsuarioForm, EmpresaForm, MedicoForm,
    CirurgiaForm, CirurgiaUploadForm, ExameForm, ServicoMedicoForm
)
from .models import Usuario, Empresa, Medico, Cirurgia, Exame, ServicoMedico


# DECORATOR PARA TIER 5
def tier5_required(view_func):
    """Decorator que restringe acesso apenas para usuários Tier 5."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.primeiro_acesso:
            return redirect('trocar_senha')
        if not request.user.is_admin():
            messages.error(request, 'Acesso negado. Esta área é restrita a administradores (Tier 5).')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
    """View de login."""
    if request.user.is_authenticated:
        if request.user.primeiro_acesso:
            return redirect('trocar_senha')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                if user.primeiro_acesso:
                    messages.warning(request, 'Você precisa trocar sua senha antes de continuar.')
                    return redirect('trocar_senha')
                messages.success(request, f'Bem-vindo(a), {user.nome_completo}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    """View de logout."""
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')


@login_required
def trocar_senha_view(request):
    """View para troca de senha no primeiro acesso."""
    if request.method == 'POST':
        form = TrocaSenhaForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.primeiro_acesso = False
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('dashboard')
    else:
        form = TrocaSenhaForm(request.user)
    
    return render(request, 'core/trocar_senha.html', {'form': form})


@login_required
def dashboard_view(request):
    """Landing page após login."""
    if request.user.primeiro_acesso:
        return redirect('trocar_senha')
    
    context = {
        'total_usuarios': Usuario.objects.count(),
        'total_empresas': Empresa.objects.filter(ativa=True).count(),
        'total_medicos': Medico.objects.filter(ativo=True).count(),
        'total_cirurgias': Cirurgia.objects.filter(ativa=True).count(),
        'total_exames': Exame.objects.filter(ativo=True).count(),
        'total_servicos': ServicoMedico.objects.filter(ativo=True).count(),
    }
    return render(request, 'core/dashboard.html', context)


# CADASTROS

@login_required
def cadastro_menu_view(request):
    """Menu de cadastros."""
    if request.user.primeiro_acesso:
        return redirect('trocar_senha')
    return render(request, 'core/cadastro_menu.html')


# USUARIOS

@login_required
def usuario_lista_view(request):
    """Lista todos os usuários."""
    if not request.user.pode_cadastrar_usuarios():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    usuarios = Usuario.objects.all().order_by('-data_cadastro')
    return render(request, 'core/usuario_lista.html', {'usuarios': usuarios})


@login_required
def usuario_criar_view(request):
    """Cria novo usuário."""
    if not request.user.pode_cadastrar_usuarios():
        messages.error(request, 'Você não tem permissão para cadastrar usuários.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('usuario_lista')
    else:
        form = UsuarioForm()
    
    return render(request, 'core/usuario_form.html', {'form': form, 'acao': 'Cadastrar'})


# EMPRESAS

@login_required
def empresa_lista_view(request):
    """Lista todas as empresas."""
    empresas = Empresa.objects.all().order_by('razao_social')
    return render(request, 'core/empresa_lista.html', {'empresas': empresas})


@login_required
def empresa_criar_view(request):
    """Cria nova empresa."""
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.cadastrado_por = request.user
            empresa.save()
            messages.success(request, 'Empresa cadastrada com sucesso!')
            return redirect('empresa_lista')
    else:
        form = EmpresaForm()
    
    return render(request, 'core/empresa_form.html', {'form': form, 'acao': 'Cadastrar'})


@login_required
def empresa_editar_view(request, pk):
    """Edita uma empresa existente."""
    empresa = get_object_or_404(Empresa, pk=pk)
    
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa atualizada com sucesso!')
            return redirect('empresa_lista')
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'core/empresa_form.html', {'form': form, 'acao': 'Editar'})


# MEDICOS

@login_required
def medico_lista_view(request):
    """Lista todos os médicos."""
    medicos = Medico.objects.all().order_by('nome_completo')
    return render(request, 'core/medico_lista.html', {'medicos': medicos})


@login_required
def medico_criar_view(request):
    """Cria novo médico."""
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            medico = form.save(commit=False)
            medico.cadastrado_por = request.user
            medico.save()
            messages.success(request, 'Médico cadastrado com sucesso!')
            return redirect('medico_lista')
    else:
        form = MedicoForm()
    
    return render(request, 'core/medico_form.html', {'form': form, 'acao': 'Cadastrar'})


@login_required
def medico_editar_view(request, pk):
    """Edita um médico existente."""
    medico = get_object_or_404(Medico, pk=pk)
    
    if request.method == 'POST':
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico atualizado com sucesso!')
            return redirect('medico_lista')
    else:
        form = MedicoForm(instance=medico)
    
    return render(request, 'core/medico_form.html', {'form': form, 'acao': 'Editar'})


# ===== ÁREA ADMINISTRATIVA (TIER 5) =====

@tier5_required
def admin_menu_view(request):
    """Menu da área administrativa."""
    context = {
        'total_cirurgias': Cirurgia.objects.count(),
        'total_exames': Exame.objects.count(),
        'total_servicos': ServicoMedico.objects.count(),
    }
    return render(request, 'core/admin/menu.html', context)


# CIRURGIAS

@tier5_required
def cirurgia_lista_view(request):
    """Lista todas as cirurgias."""
    cirurgias = Cirurgia.objects.all().order_by('especialidade', 'descricao')
    return render(request, 'core/admin/cirurgia_lista.html', {'cirurgias': cirurgias})


@tier5_required
def cirurgia_criar_view(request):
    """Cria nova cirurgia."""
    if request.method == 'POST':
        form = CirurgiaForm(request.POST)
        if form.is_valid():
            cirurgia = form.save(commit=False)
            cirurgia.cadastrado_por = request.user
            cirurgia.save()
            messages.success(request, 'Cirurgia cadastrada com sucesso!')
            return redirect('cirurgia_lista')
    else:
        form = CirurgiaForm()
    
    return render(request, 'core/admin/cirurgia_form.html', {'form': form, 'acao': 'Cadastrar'})


@tier5_required
def cirurgia_editar_view(request, pk):
    """Edita uma cirurgia existente."""
    cirurgia = get_object_or_404(Cirurgia, pk=pk)
    
    if request.method == 'POST':
        form = CirurgiaForm(request.POST, instance=cirurgia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cirurgia atualizada com sucesso!')
            return redirect('cirurgia_lista')
    else:
        form = CirurgiaForm(instance=cirurgia)
    
    return render(request, 'core/admin/cirurgia_form.html', {'form': form, 'acao': 'Editar'})


@tier5_required
def cirurgia_upload_view(request):
    """Upload de CSV de cirurgias."""
    if request.method == 'POST':
        form = CirurgiaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo_csv']
            
            # Lê o arquivo CSV
            arquivo.seek(0)
            decoded_file = arquivo.read().decode('utf-8')
            csv_file = io.StringIO(decoded_file)
            reader = csv.DictReader(csv_file)
            
            # Mapeia variações de nomes de colunas
            def get_column(row, variations):
                for var in variations:
                    if var in row:
                        return row[var]
                    # Tenta com espaços substituídos por underscore
                    var_underscore = var.replace(' ', '_')
                    if var_underscore in row:
                        return row[var_underscore]
                return None
            
            sucesso = 0
            erro = 0
            erros_detalhados = []
            
            for i, row in enumerate(reader, start=2):  # Começa do 2 (header é linha 1)
                try:
                    codigo = get_column(row, ['Codigo SIGTAP', 'codigo_sigtap', 'codigo'])
                    descricao = get_column(row, ['Descricao', 'descricao'])
                    valor_str = get_column(row, ['Valor', 'valor'])
                    tipo = get_column(row, ['Tipo Cirurgia', 'tipo_cirurgia', 'tipo'])
                    especialidade = get_column(row, ['Especialidade', 'especialidade'])
                    
                    if not all([codigo, descricao, valor_str, tipo, especialidade]):
                        erros_detalhados.append(f"Linha {i}: Dados incompletos")
                        erro += 1
                        continue
                    
                    # Converte valor
                    try:
                        valor = Decimal(valor_str.replace(',', '.'))
                    except:
                        erros_detalhados.append(f"Linha {i}: Valor inválido '{valor_str}'")
                        erro += 1
                        continue
                    
                    # Mapeia tipo de cirurgia - NOVOS TIPOS
                    tipo_stripped = tipo.strip()
                    if tipo_stripped.upper() == 'CMA':
                        tipo_cirurgia = 'CMA'
                    elif tipo_stripped.lower() == 'cma':
                        tipo_cirurgia = 'cma'
                    else:
                        # Aceita qualquer variação mas padroniza
                        tipo_upper = tipo_stripped.upper()
                        if 'MAIOR' in tipo_upper or tipo_upper == 'CMA':
                            tipo_cirurgia = 'CMA'
                        elif 'MENOR' in tipo_upper:
                            tipo_cirurgia = 'cma'
                        else:
                            erros_detalhados.append(f"Linha {i}: Tipo inválido '{tipo}'. Use 'CMA' ou 'cma'")
                            erro += 1
                            continue
                    
                    # Cria ou atualiza cirurgia
                    cirurgia, created = Cirurgia.objects.update_or_create(
                        codigo_sigtap=codigo.strip(),
                        defaults={
                            'descricao': descricao.strip(),
                            'valor': valor,
                            'tipo_cirurgia': tipo_cirurgia,
                            'especialidade': especialidade.strip(),
                            'cadastrado_por': request.user,
                        }
                    )
                    sucesso += 1
                    
                except Exception as e:
                    erros_detalhados.append(f"Linha {i}: {str(e)}")
                    erro += 1
            
            # Mensagens de resultado
            if sucesso > 0:
                messages.success(request, f'{sucesso} cirurgia(s) importada(s) com sucesso!')
            if erro > 0:
                messages.warning(request, f'{erro} linha(s) com erro. Detalhes: {"; ".join(erros_detalhados[:5])}')
            
            return redirect('cirurgia_lista')
    else:
        form = CirurgiaUploadForm()
    
    return render(request, 'core/admin/cirurgia_upload.html', {'form': form})


# EXAMES

@tier5_required
def exame_lista_view(request):
    """Lista todos os exames."""
    exames = Exame.objects.all().order_by('tipo_exame', 'descricao')
    return render(request, 'core/admin/exame_lista.html', {'exames': exames})


@tier5_required
def exame_criar_view(request):
    """Cria novo exame."""
    if request.method == 'POST':
        form = ExameForm(request.POST)
        if form.is_valid():
            exame = form.save(commit=False)
            exame.cadastrado_por = request.user
            exame.save()
            messages.success(request, 'Exame cadastrado com sucesso!')
            return redirect('exame_lista')
    else:
        form = ExameForm()
    
    return render(request, 'core/admin/exame_form.html', {'form': form, 'acao': 'Cadastrar'})


@tier5_required
def exame_editar_view(request, pk):
    """Edita um exame existente."""
    exame = get_object_or_404(Exame, pk=pk)
    
    if request.method == 'POST':
        form = ExameForm(request.POST, instance=exame)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exame atualizado com sucesso!')
            return redirect('exame_lista')
    else:
        form = ExameForm(instance=exame)
    
    return render(request, 'core/admin/exame_form.html', {'form': form, 'acao': 'Editar'})


# SERVIÇOS MÉDICOS

@tier5_required
def servico_lista_view(request):
    """Lista todos os serviços médicos."""
    servicos = ServicoMedico.objects.all().order_by('especialidade', 'descricao')
    return render(request, 'core/admin/servico_lista.html', {'servicos': servicos})


@tier5_required
def servico_criar_view(request):
    """Cria novo serviço médico."""
    if request.method == 'POST':
        form = ServicoMedicoForm(request.POST)
        if form.is_valid():
            servico = form.save(commit=False)
            servico.cadastrado_por = request.user
            servico.save()
            messages.success(request, 'Serviço médico cadastrado com sucesso!')
            return redirect('servico_lista')
    else:
        form = ServicoMedicoForm()
    
    return render(request, 'core/admin/servico_form.html', {'form': form, 'acao': 'Cadastrar'})


@tier5_required
def servico_editar_view(request, pk):
    """Edita um serviço médico existente."""
    servico = get_object_or_404(ServicoMedico, pk=pk)
    
    if request.method == 'POST':
        form = ServicoMedicoForm(request.POST, instance=servico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço médico atualizado com sucesso!')
            return redirect('servico_lista')
    else:
        form = ServicoMedicoForm(instance=servico)
    
    return render(request, 'core/admin/servico_form.html', {'form': form, 'acao': 'Editar'})
