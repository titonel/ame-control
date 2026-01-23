#!/usr/bin/env python
"""
Script de setup automático para o AME Control
Execute este script após clonar o repositório
"""

import os
import sys
import subprocess

def print_step(message):
    """Imprime mensagem de passo."""
    print("\n" + "="*60)
    print(f"  {message}")
    print("="*60 + "\n")

def run_command(command, description):
    """Executa um comando e trata erros."""
    print(f"Executando: {description}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"\u2713 {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\u2717 Erro ao executar: {description}")
        print(f"Erro: {e}")
        return False

def main():
    """Função principal do setup."""
    print_step("BEM-VINDO AO SETUP DO AME CONTROL")
    
    # Verifica se está no diretório correto
    if not os.path.exists('manage.py'):
        print("\u2717 Erro: Este script deve ser executado na raiz do projeto.")
        sys.exit(1)
    
    # Passo 1: Instalar dependências
    print_step("PASSO 1: Instalando dependências")
    if not run_command("pip install -r requirements.txt", "Instalação de dependências"):
        print("\nErro na instalação. Verifique se o pip está instalado e tente novamente.")
        sys.exit(1)
    
    # Passo 2: Executar migrações
    print_step("PASSO 2: Criando banco de dados")
    if not run_command("python manage.py migrate", "Migrações do banco de dados"):
        print("\nErro nas migrações. Verifique o arquivo de erro acima.")
        sys.exit(1)
    
    # Passo 3: Criar superusuário
    print_step("PASSO 3: Criar superusuário")
    print("Agora você precisa criar um superusuário para acessar o sistema.")
    print("Por favor, responda as perguntas abaixo:\n")
    
    os.system("python manage.py createsuperuser")
    
    # Finalização
    print_step("SETUP CONCLUÍDO COM SUCESSO!")
    print("O AME Control foi instalado e configurado.\n")
    print("Para iniciar o servidor, execute:")
    print("  python manage.py runserver\n")
    print("Em seguida, acesse: http://127.0.0.1:8000\n")
    print("Bom trabalho!")

if __name__ == "__main__":
    main()
