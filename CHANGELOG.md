# Histórico de Alterações - AME Control

## [2026-01-23] - Busca Automática de CEP

### Adicionado
- **Busca de CEP via API ViaCEP**: Sistema integrado para buscar endereços automaticamente
- **Campos de endereço separados**: CEP, Logradouro, Número, Complemento, Bairro, Cidade e Estado
- **Preenchimento automático**: Ao digitar o CEP e clicar em "Buscar", os campos são preenchidos automaticamente
- **Validação de CEP**: Formato automático (00000-000) enquanto o usuário digita
- **Feedback visual**: Mensagens de loading, erro e sucesso durante a busca

### Alterado
- **Modelo Empresa**: Campo `endereco` TextField substituído por campos individuais
- **Formulário de Empresa**: Layout reorganizado com seção de endereço dedicada
- **Listagem de Empresas**: Exibe Cidade/Estado ao invés do endereço completo

### Como Usar

1. **Acesse o cadastro de empresa**: Menu Cadastro > Empresas > Nova Empresa
2. **Digite o CEP** no campo apropriado (formato: 00000-000)
3. **Clique no botão "Buscar"** ao lado do campo CEP
4. **Aguarde**: O sistema buscará o endereço na API ViaCEP
5. **Revise e complete**: Os campos serão preenchidos automaticamente, você só precisa adicionar o número e complemento (se houver)

### Como Atualizar

Se você já tem o sistema instalado, execute:

```bash
# 1. Atualize o código
git pull origin main

# 2. Aplique as migrações
python manage.py migrate

# 3. Reinicie o servidor
python manage.py runserver
```

Você verá esta saída ao executar as migrações:
```
Running migrations:
  Applying core.0003_empresa_endereco_campos... OK
```

### Detalhes Técnicos

#### Campos de Endereço
- **CEP**: Máximo 9 caracteres (formato: 00000-000)
- **Logradouro**: Até 255 caracteres (Rua, Avenida, etc.)
- **Número**: Até 10 caracteres
- **Complemento**: Até 100 caracteres (Apto, Sala, Bloco, etc.)
- **Bairro**: Até 100 caracteres
- **Cidade**: Até 100 caracteres
- **Estado**: 2 caracteres maiúsculos (ex: SP, RJ, MG)

#### API ViaCEP
- **Endpoint**: `https://viacep.com.br/ws/{cep}/json/`
- **Método**: GET
- **Formato**: JSON
- **Sem autenticação**: API pública e gratuita

#### JavaScript
- **Busca assíncrona**: Usa Fetch API moderna
- **Formatação automática**: CEP é formatado enquanto digita
- **Validação**: Verifica se o CEP tem 8 dígitos antes de buscar
- **Feedback**: Mensagens visuais de loading, erro e sucesso
- **Foco automático**: Após buscar, o cursor vai para o campo "Número"

---

## [2026-01-23] - Melhorias no Cadastro de Usuários

### Alterado
- **Campo DRT**: Renomeado para "DRT/Matrícula" e agora aceita apenas números
- **Username**: Agora é exibido no formulário de cadastro (campo readonly) e é gerado automaticamente a partir do e-mail
- **Senha Padrão**: Todos os novos usuários são criados com a senha `ame-control`

### Como Atualizar

Se você já tem o sistema instalado, execute:

```bash
# 1. Atualize o código
git pull origin main

# 2. Aplique as migrações
python manage.py migrate

# 3. Reinicie o servidor
python manage.py runserver
```

### Detalhes das Mudanças

#### 1. Campo DRT/Matrícula
- **Antes**: Campo "DRT" que aceitava qualquer texto
- **Agora**: Campo "DRT/Matrícula" que aceita apenas números
- **Validação**: O sistema valida que apenas dígitos sejam inseridos

#### 2. Campo Username
- **Visibilidade**: Agora aparece no formulário de cadastro
- **Comportamento**: É preenchido automaticamente conforme o usuário digita o e-mail
- **Exemplo**: 
  - E-mail: `saulo.bastos@amecaragua.org.br`
  - Username gerado: `saulo.bastos`

#### 3. Senha Padrão
- **Senha**: `ame-control`
- **Primeiro Acesso**: O usuário será obrigado a trocar a senha no primeiro login
- **Segurança**: A senha é armazenada de forma criptografada no banco de dados

### Interface do Formulário

O formulário de cadastro agora inclui:
1. Nome Completo
2. E-mail
3. **Username (gerado automaticamente - readonly)**
4. CPF
5. DRT/Matrícula (apenas números)
6. Nível de Acesso (Tier)

### Card Informativo

Um novo card foi adicionado à lateral direita do formulário exibindo:
- **Senha Padrão**: `ame-control`
- Informação sobre troca obrigatória no primeiro acesso

---

## [2026-01-23] - Versão Inicial

### Adicionado
- Sistema de autenticação com login e logout
- Troca obrigatória de senha no primeiro acesso
- Sistema RBAC com 5 níveis (Tiers)
- Cadastro de usuários (Tier 3+)
- Cadastro de empresas (todos os usuários)
- Cadastro de médicos (todos os usuários)
- Dashboard com estatísticas
- Interface responsiva e corporativa
- CSS único centralizado
