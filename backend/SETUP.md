# Backend — Guia de Setup e Deploy

API Flask responsável por receber o formulário "Planeje uma experiência" do site do Accenture Innovation Center Recife e enviar e-mail automático via SMTP Office 365.

---

## Estrutura dos arquivos

```
backend/
  app.py              ← servidor Flask, endpoint POST /api/contato
  email_service.py    ← função de envio de e-mail (smtplib, Office 365)
  requirements.txt    ← dependências Python
  Dockerfile          ← imagem Python 3.11-slim + gunicorn
  docker-compose.yml  ← usado pelo Dokploy
  .env.example        ← template de variáveis de ambiente
  .dockerignore       ← exclui .env e caches do build Docker
  SETUP.md            ← este arquivo
```

---

## O que o backend faz

1. Recebe um `POST /api/contato` com JSON:
   ```json
   {
     "nome": "...",
     "empresa": "...",
     "email": "email.do.visitante@empresa.com",
     "mensagem": "..."
   }
   ```
2. Valida que todos os campos estão preenchidos
3. Envia e-mail via SMTP Office 365 com:
   - **From:** conta remetente fixa (variável de ambiente)
   - **To:** `philippe.fontes@accenture.com`
   - **CC:** `carla.b.nascimento@accenture.com`
   - **Reply-To:** e-mail do visitante (para resposta direta)
   - **Subject:** `Innovation Center Recife — [Empresa]`
4. Retorna `{"ok": true}` em sucesso ou `{"erro": "..."}` em falha

---

## Variáveis de ambiente obrigatórias

Copie `.env.example` para `.env` e preencha:

```env
EMAIL_REMETENTE=noreply@suaempresa.com
EMAIL_SENHA=sua_senha_aqui
```

> **Atenção:** nunca commite o `.env` — ele está no `.dockerignore` e não deve ir para o repositório.

Se a conta usar **MFA/autenticação moderna** (comum em Office 365 corporativo), a senha deve ser um **App Password** gerado pelo administrador do tenant, não a senha normal da conta.

---

## Rodar localmente (para testar)

```bash
# 1. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# edite o .env com as credenciais reais

export EMAIL_REMETENTE=noreply@suaempresa.com
export EMAIL_SENHA=sua_senha

# 4. Subir o servidor
python app.py
# servidor sobe em http://localhost:5000
```

Testar com curl:
```bash
curl -X POST http://localhost:5000/api/contato \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste","empresa":"Acme","email":"teste@acme.com","mensagem":"Quero explorar IA"}'
```

Resposta esperada: `{"ok": true}`

---

## Deploy no Dokploy

### 1. Criar o serviço no Dokploy

- Tipo: **Docker Compose**
- Apontar para a pasta `backend/` do repositório (ou subir os arquivos manualmente)
- O Dokploy vai usar o `docker-compose.yml` automaticamente

### 2. Configurar variáveis de ambiente no Dokploy

Na interface do Dokploy, vá em **Environment Variables** do serviço e adicione:

| Chave | Valor |
|---|---|
| `EMAIL_REMETENTE` | endereço do remetente fixo |
| `EMAIL_SENHA` | senha ou App Password |

> Isso substitui o `.env` físico — não é necessário criar o arquivo no servidor.

### 3. Fazer o deploy

Dokploy irá:
1. Fazer o build da imagem via `Dockerfile`
2. Subir o container na porta `5000`
3. Expor via proxy reverso (configurar domínio/SSL na aba de domínios do Dokploy)

### 4. Atualizar o frontend

Após o Dokploy gerar a URL pública do backend (ex: `https://api.seudominio.com`), abrir `Site/index.html` e localizar a linha:

```html
<form id="contact-form" ... data-api-url="http://localhost:5000/api/contato">
```

Substituir pelo endereço real:

```html
<form id="contact-form" ... data-api-url="https://api.seudominio.com/api/contato">
```

---

## CORS

O backend está configurado com `CORS(app, origins="*")` — aceita requisições de qualquer origem.

Em produção, restringir para o domínio real do frontend editando `app.py`:

```python
CORS(app, origins=["https://www.seudominio.com"])
```

---

## Dependências

| Pacote | Versão | Motivo |
|---|---|---|
| flask | 3.1.0 | Framework web |
| flask-cors | 5.0.0 | Habilita CORS para o frontend |
| gunicorn | 23.0.0 | Servidor WSGI para produção |

`smtplib` e `email.mime` são bibliotecas nativas do Python — sem instalação extra.
