# AME Control

Sistema de controle corporativo com autenticação e controle de acesso baseado em funções (RBAC).

## Características

- Sistema de login com troca obrigatória de senha no primeiro acesso
- Controle de acesso baseado em 5 níveis (Tiers)
- Cadastro de usuários, empresas e médicos
- Interface responsiva e corporativa
- Desenvolvido em Django/Python

## Instalação Rápida

### Opção 1: Setup Automático (Recomendado)

```bash
git clone https://github.com/titonel/ame-control.git
cd ame-control
python -m venv .venv

# No Windows:
.venv\Scripts\activate

# No Linux/Mac:
source .venv/bin/activate

# Execute o setup automático:
python setup.py
```

### Opção 2: Instalação Manual

1. **Clone o repositório:**
```bash
git clone https://github.com/titonel/ame-control.git
cd ame-control
```

2. **Crie e ative o ambiente virtual:**

**No Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**No Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **⚠️ IMPORTANTE: Execute as migrações do banco de dados:**
```bash
python manage.py migrate
```

> **Nota:** Este passo é essencial! Se você pular esta etapa, receberá o erro: `django.db.utils.OperationalError: no such table: core_usuario`

5. **Crie um superusuário (administrador):**
```bash
python manage.py createsuperuser
```

O sistema irá solicitar:
- Username
- E-mail
- Nome completo
- Password (2x)

6. **Inicie o servidor:**
```bash
python manage.py runserver
```

7. **Acesse o sistema:**
- Sistema: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

## Resolução de Problemas

### Erro: "no such table: core_usuario"

**Este erro ocorre quando as migrações não foram executadas.**

**Solução:**
```bash
python manage.py migrate
```

Você deve ver uma saída como:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying core.0001_initial... OK
  ...
```

Após isso, execute novamente:
```bash
python manage.py createsuperuser
```

### Erro: "ModuleNotFoundError: No module named 'decouple'"

**Solução:**
```bash
pip install -r requirements.txt
```

### Resetar o Banco de Dados

Se precisar recomeçar do zero:

**Windows:**
```bash
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

**Linux/Mac:**
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Estrutura do Projeto

```
ame-control/
├── ame_control/          # Configurações do projeto
├── core/                  # Aplicação principal
│   ├── models.py         # Modelos (Usuario, Empresa, Medico)
│   ├── views.py          # Lógica das views
│   ├── forms.py          # Formulários
│   ├── urls.py           # Rotas
│   └── migrations/       # Migrações do banco
├── templates/            # Templates HTML
├── static/               # Arquivos estáticos
│   └── estilo.css        # CSS único do sistema
├── manage.py             # Script de gerenciamento
├── requirements.txt      # Dependências
└── setup.py              # Script de setup automático
```

## Níveis de Acesso (RBAC)

- **Tier 1**: Usuários operacionais (inserção de dados)
- **Tier 2**: Analistas e líderes de setor
- **Tier 3**: Supervisores (podem cadastrar usuários)
- **Tier 4**: Coordenadores
- **Tier 5**: Gerentes e administradores do sistema

## Funcionalidades

### Autenticação
- Login com username e senha
- Troca obrigatória de senha no primeiro acesso
- Senhas criptografadas com segurança
- Logout seguro

### Cadastros

**Usuários** (Tier 3+):
- Nome completo, e-mail, CPF, DRT
- Nível de acesso (Tier)
- Username gerado automaticamente do e-mail

**Empresas** (Todos):
- Razão social, nome fantasia, CNPJ
- Endereço, telefone, e-mail
- Status ativo/inativo

**Médicos** (Todos):
- Nome completo, CRM, CPF
- Especialidade, telefone, e-mail
- Status ativo/inativo

## Documentação Adicional

Para mais detalhes, consulte:
- [INSTALACAO.md](INSTALACAO.md) - Guia completo de instalação

## Tecnologias Utilizadas

- **Backend**: Python 3.8+, Django 4.2
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Banco de Dados**: SQLite (padrão) / PostgreSQL (opcional)
- **Autenticação**: Sistema Django Auth customizado

## Licença

Todos os direitos reservados.
