# Guia de Instalação do AME Control

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## Passos de Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/titonel/ame-control.git
cd ame-control
```

### 2. Crie e Ative o Ambiente Virtual

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

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Execute as Migrações do Banco de Dados

**IMPORTANTE:** Execute este comando para criar as tabelas no banco de dados:

```bash
python manage.py migrate
```

Você deve ver uma saída similar a:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  ...
  Applying core.0001_initial... OK
```

### 5. Crie um Superusuário (Administrador)

```bash
python manage.py createsuperuser
```

O sistema irá solicitar:
- **Username**: Digite o nome de usuário desejado
- **E-mail**: Digite um e-mail válido (ex: admin@amecaragua.org.br)
- **Nome completo**: Digite seu nome completo
- **Password**: Digite uma senha (não será exibida ao digitar)
- **Password (again)**: Confirme a senha

### 6. Execute o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

O sistema estará disponível em: **http://127.0.0.1:8000**

### 7. Acesse o Sistema

Abra seu navegador e acesse:
- **Sistema Principal**: http://127.0.0.1:8000
- **Painel Administrativo**: http://127.0.0.1:8000/admin

Use as credenciais do superusuário criado no passo 5.

## Resolvendo Problemas Comuns

### Erro: "no such table: core_usuario"

**Causa:** As migrações não foram executadas.

**Solução:**
```bash
python manage.py migrate
```

### Erro: "ModuleNotFoundError: No module named 'decouple'"

**Causa:** Dependências não foram instaladas.

**Solução:**
```bash
pip install -r requirements.txt
```

### Erro ao criar superusuário com CPF

**Causa:** O modelo Usuario customizado requer CPF no formato correto.

**Solução:** Use o painel admin após criar um superusuário básico, ou edite manualmente via Django shell.

### Resetar o Banco de Dados

Se precisar começar do zero:

**No Windows:**
```bash
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

**No Linux/Mac:**
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Configurações Avançadas

### Usando PostgreSQL

1. Instale o psycopg2:
```bash
pip install psycopg2-binary
```

2. Edite o arquivo `.env` ou `ame_control/settings.py` para configurar o PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ame_control_db',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Próximos Passos

Após a instalação:

1. Acesse o sistema com o superusuário criado
2. Cadastre novos usuários através do menu "Cadastro > Usuários"
3. Cadastre empresas e médicos conforme necessário
4. Explore as funcionalidades do sistema

## Suporte

Para dúvidas ou problemas:
- Verifique este guia novamente
- Consulte a documentação do Django: https://docs.djangoproject.com/
- Verifique os logs de erro no terminal
