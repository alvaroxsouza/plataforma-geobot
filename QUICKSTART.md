# 🚀 Quick Start - GeoBot Platform

## Setup em 5 Minutos

### 1️⃣ Configurar Variáveis de Ambiente (30 segundos)

```bash
cp .env.example .env.local
```

Edite `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2️⃣ Instalar Dependências (2 minutos)

```bash
npm install
```

### 3️⃣ Iniciar Servidor (10 segundos)

```bash
npm run dev
```

### 4️⃣ Acessar Aplicação

Abra seu navegador em: **http://localhost:3000**

---

## 🎯 Testar Rapidamente

### Criar uma Conta

1. Acesse http://localhost:3000/auth
2. Clique em "Cadastrar"
3. Preencha:
   - Nome: Seu Nome
   - CPF: 123.456.789-00
   - Email: seu@email.com
   - Senha: senha123
4. Clique em "Criar Conta"
5. Você será redirecionado para o Dashboard!

### Fazer Login

1. Acesse http://localhost:3000/auth
2. Aba "Entrar"
3. Digite email e senha
4. Clique em "Entrar"

---

## 📁 Estrutura Rápida

```
app/
  ├── auth/          → Tela de login/cadastro
  └── dashboard/     → Página após login

components/
  ├── auth/          → Formulários de autenticação
  └── ui/            → Componentes do shadcn/ui

lib/
  ├── services/      → Integração com API
  └── types/         → Tipos TypeScript

contexts/
  └── AuthContext    → Estado global de autenticação
```

---

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Iniciar produção
npm start

# Linting
npm run lint

# Adicionar componente shadcn
npx shadcn@latest add [nome]
```

---

## 📚 Documentação

- **README.md** - Visão geral completa
- **docs/API_INTEGRATION.md** - Como usar a API
- **docs/COMPONENTS_GUIDE.md** - Guia de componentes
- **docs/TESTING_GUIDE.md** - Como testar
- **IMPLEMENTATION_SUMMARY.md** - Resumo executivo
- **CHECKLIST.md** - Checklist de funcionalidades

---

## 🐛 Problemas Comuns

### Backend não conecta?

Verifique se:
1. Backend está rodando em `http://localhost:8000`
2. CORS está configurado corretamente
3. URL da API está correta em `.env.local`

### Token não persiste?

Limpe o localStorage:
```javascript
localStorage.clear();
window.location.reload();
```

---

## ✅ Pronto!

Sua aplicação está funcionando! 🎉

Próximos passos:
- [ ] Testar cadastro e login
- [ ] Explorar o dashboard
- [ ] Ler a documentação completa
- [ ] Customizar conforme necessário

---

**Desenvolvido com Next.js 16 + TypeScript + shadcn/ui** 🚀
