from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('trocar-senha/', views.trocar_senha_view, name='trocar_senha'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Menu de Cadastros
    path('cadastro/', views.cadastro_menu_view, name='cadastro_menu'),
    
    # Usuários
    path('usuarios/', views.usuario_lista_view, name='usuario_lista'),
    path('usuarios/novo/', views.usuario_criar_view, name='usuario_criar'),
    
    # Empresas
    path('empresas/', views.empresa_lista_view, name='empresa_lista'),
    path('empresas/nova/', views.empresa_criar_view, name='empresa_criar'),
    path('empresas/<int:pk>/editar/', views.empresa_editar_view, name='empresa_editar'),
    
    # Médicos
    path('medicos/', views.medico_lista_view, name='medico_lista'),
    path('medicos/novo/', views.medico_criar_view, name='medico_criar'),
    path('medicos/<int:pk>/editar/', views.medico_editar_view, name='medico_editar'),
]
