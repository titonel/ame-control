from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import LoginForm, TrocaSenhaForm, UsuarioForm, EmpresaForm, MedicoForm
from .models import Usuario, Empresa, Medico


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
