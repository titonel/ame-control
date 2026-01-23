"""Views para área administrativa (Tier 5)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal, InvalidOperation
import csv
import io

from .models import Cirurgia, Exame, ServicoMedico
from .forms import CirurgiaForm, CirurgiaCSVUploadForm, ExameForm, ServicoMedicoForm


def admin_required(view_func):
    """Decorator para verificar se o usuário é Tier 5."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin():
            messages.error(request, 'Acesso negado. Esta área é exclusiva para administradores (Tier 5).')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def admin_menu_view(request):
    """Menu principal da área administrativa."""
    context = {
        'total_cirurgias': Cirurgia.objects.filter(ativa=True).count(),
        'total_exames': Exame.objects.filter(ativo=True).count(),
        'total_servicos': ServicoMedico.objects.filter(ativo=True).count(),
    }
    return render(request, 'core/admin/menu.html', context)


# ==================== CIRURGIAS ====================

@login_required
@admin_required
def cirurgia_lista_view(request):
    """Lista todas as cirurgias."""
    cirurgias = Cirurgia.objects.all().order_by('descricao')
    
    # Filtros
    tipo = request.GET.get('tipo')
    especialidade = request.GET.get('especialidade')
    busca = request.GET.get('busca')
    
    if tipo:
        cirurgias = cirurgias.filter(tipo_cirurgia=tipo)
    if especialidade:
        cirurgias = cirurgias.filter(especialidade__icontains=especialidade)
    if busca:
        cirurgias = cirurgias.filter(
            Q(codigo_sigtap__icontains=busca) |
            Q(descricao__icontains=busca)
        )
    
    # Especialidades para filtro
    especialidades = Cirurgia.objects.values_list('especialidade', flat=True).distinct().order_by('especialidade')
    
    context = {
        'cirurgias': cirurgias,
        'especialidades': especialidades,
        'tipo_choices': Cirurgia.TIPO_CHOICES,
    }
    return render(request, 'core/admin/cirurgia_lista.html', context)


@login_required
@admin_required
def cirurgia_criar_view(request):
    """Cria nova cirurgia manualmente."""
    if request.method == 'POST':
        form = CirurgiaForm(request.POST)
        if form.is_valid():
            cirurgia = form.save(commit=False)
            cirurgia.cadastrado_por = request.user
            cirurgia.save()
            messages.success(request, f'Cirurgia "{cirurgia.descricao[:50]}" cadastrada com sucesso!')
            return redirect('cirurgia_lista')
    else:
        form = CirurgiaForm()
    
    return render(request, 'core/admin/cirurgia_form.html', {'form': form, 'acao': 'Cadastrar'})


@login_required
@admin_required
def cirurgia_editar_view(request, pk):
    """Edita uma cirurgia existente."""
    cirurgia = get_object_or_404(Cirurgia, pk=pk)
    
    if request.method == 'POST':
        form = CirurgiaForm(request.POST, instance=cirurgia)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cirurgia "{cirurgia.descricao[:50]}" atualizada com sucesso!')
            return redirect('cirurgia_lista')
    else:
        form = CirurgiaForm(instance=cirurgia)
    
    return render(request, 'core/admin/cirurgia_form.html', {'form': form, 'acao': 'Editar', 'cirurgia': cirurgia})


@login_required
@admin_required
def cirurgia_upload_csv_view(request):
    """Upload de arquivo CSV com cirurgias."""
    if request.method == 'POST':
        form = CirurgiaCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.cleaned_data['arquivo_csv']
            sobrescrever = form.cleaned_data['sobrescrever']
            
            try:
                resultado = processar_csv_cirurgias(arquivo, request.user, sobrescrever)
                
                if resultado['sucesso'] > 0:
                    messages.success(
                        request,
                        f'{resultado["sucesso"]} cirurgia(s) importada(s) com sucesso!'
                    )
                
                if resultado['atualizados'] > 0:
                    messages.info(
                        request,
                        f'{resultado["atualizados"]} cirurgia(s) atualizada(s).'
                    )
                
                if resultado['erros']:
                    messages.warning(
                        request,
                        f'{len(resultado["erros"])} erro(s) encontrado(s). '
                        f'Linhas com erro: {", ".join(map(str, resultado["erros"]))}'
                    )
                
                return redirect('cirurgia_lista')
                
            except Exception as e:
                messages.error(request, f'Erro ao processar arquivo: {str(e)}')
    else:
        form = CirurgiaCSVUploadForm()
    
    return render(request, 'core/admin/cirurgia_upload_csv.html', {'form': form})


def processar_csv_cirurgias(arquivo, usuario, sobrescrever=False):
    """Processa arquivo CSV e importa cirurgias."""
    from django.db import Q
    
    resultado = {
        'sucesso': 0,
        'atualizados': 0,
        'erros': [],
    }
    
    # Lê o arquivo
    arquivo.seek(0)
    conteudo = arquivo.read().decode('utf-8')
    leitor = csv.DictReader(io.StringIO(conteudo))
    
    # Mapeia nomes de colunas (normaliza)
    mapa_colunas = {}
    for col in leitor.fieldnames:
        col_lower = col.strip().lower()
        if 'codigo' in col_lower or 'sigtap' in col_lower:
            mapa_colunas['codigo_sigtap'] = col
        elif 'descri' in col_lower:
            mapa_colunas['descricao'] = col
        elif 'valor' in col_lower or 'preco' in col_lower or 'pre' in col_lower:
            mapa_colunas['valor'] = col
        elif 'tipo' in col_lower:
            mapa_colunas['tipo_cirurgia'] = col
        elif 'especialidade' in col_lower:
            mapa_colunas['especialidade'] = col
    
    linha_numero = 1
    
    with transaction.atomic():
        for linha in leitor:
            linha_numero += 1
            
            try:
                # Extrai dados
                codigo_sigtap = linha[mapa_colunas['codigo_sigtap']].strip()
                descricao = linha[mapa_colunas['descricao']].strip()
                valor_str = linha[mapa_colunas['valor']].strip().replace(',', '.')
                tipo_cirurgia = linha[mapa_colunas['tipo_cirurgia']].strip().upper()
                especialidade = linha[mapa_colunas['especialidade']].strip()
                
                # Valida dados obrigatórios
                if not codigo_sigtap or not descricao:
                    resultado['erros'].append(linha_numero)
                    continue
                
                # Converte valor
                try:
                    valor = Decimal(valor_str)
                except (InvalidOperation, ValueError):
                    resultado['erros'].append(linha_numero)
                    continue
                
                # Normaliza tipo de cirurgia
                tipo_map = {
                    'ELETIVA': 'ELETIVA',
                    'URGENCIA': 'URGENCIA',
                    'URGÊNCIA': 'URGENCIA',
                    'EMERGENCIA': 'EMERGENCIA',
                    'EMERGÊNCIA': 'EMERGENCIA',
                    'AMBULATORIAL': 'AMBULATORIAL',
                }
                tipo_cirurgia = tipo_map.get(tipo_cirurgia, 'ELETIVA')
                
                # Verifica se já existe
                cirurgia_existente = Cirurgia.objects.filter(codigo_sigtap=codigo_sigtap).first()
                
                if cirurgia_existente:
                    if sobrescrever:
                        cirurgia_existente.descricao = descricao
                        cirurgia_existente.valor = valor
                        cirurgia_existente.tipo_cirurgia = tipo_cirurgia
                        cirurgia_existente.especialidade = especialidade
                        cirurgia_existente.save()
                        resultado['atualizados'] += 1
                    else:
                        # Pula se já existe e não deve sobrescrever
                        continue
                else:
                    # Cria nova cirurgia
                    Cirurgia.objects.create(
                        codigo_sigtap=codigo_sigtap,
                        descricao=descricao,
                        valor=valor,
                        tipo_cirurgia=tipo_cirurgia,
                        especialidade=especialidade,
                        cadastrado_por=usuario,
                        ativa=True
                    )
                    resultado['sucesso'] += 1
                    
            except Exception as e:
                print(f"Erro na linha {linha_numero}: {str(e)}")
                resultado['erros'].append(linha_numero)
                continue
    
    return resultado


@login_required
@admin_required
def buscar_sigtap_view(request):
    """Busca informações de um código SIGTAP."""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({'erro': 'Código não fornecido'}, status=400)
    
    # TODO: Integrar com API SIGTAP quando disponível
    # Por enquanto, verifica se já existe no banco
    cirurgia = Cirurgia.objects.filter(codigo_sigtap=codigo).first()
    
    if cirurgia:
        return JsonResponse({
            'encontrado': True,
            'descricao': cirurgia.descricao,
            'valor': str(cirurgia.valor),
            'tipo_cirurgia': cirurgia.tipo_cirurgia,
            'especialidade': cirurgia.especialidade,
            'fonte': 'banco_dados'
        })
    else:
        return JsonResponse({
            'encontrado': False,
            'mensagem': 'Código SIGTAP não encontrado no banco de dados. '
                       'Integração com API oficial em desenvolvimento.'
        })


# ==================== EXAMES ====================

@login_required
@admin_required
def exame_lista_view(request):
    """Lista todos os exames."""
    exames = Exame.objects.all().order_by('descricao')
    return render(request, 'core/admin/exame_lista.html', {'exames': exames})


# ==================== SERVIÇOS MÉDICOS ====================

@login_required
@admin_required
def servico_lista_view(request):
    """Lista todos os serviços médicos."""
    servicos = ServicoMedico.objects.all().order_by('descricao')
    return render(request, 'core/admin/servico_lista.html', {'servicos': servicos})
