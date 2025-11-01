# GeoBot Platform - Frontend

Plataforma moderna e elegante de autenticação e gerenciamento, construída com Next.js 16, TypeScript e shadcn/ui.

## 🚀 Funcionalidades

- ✅ **Autenticação Completa**
  - Login de usuários
  - Cadastro de novos usuários
  - Recuperação de senha (interface pronta)
  - Gerenciamento de sessão com JWT

- 🎨 **Interface Moderna**
  - Design responsivo e elegante
  - Componentes shadcn/ui
  - Tailwind CSS
  - Animações suaves

- 🔒 **Segurança**
  - Integração completa com backend FastAPI
  - Proteção de rotas
  - Validação de formulários
  - Tratamento de erros

## 🛠️ Tecnologias

- **Next.js 16** - Framework React
- **TypeScript** - Tipagem estática
- **shadcn/ui** - Biblioteca de componentes
- **Tailwind CSS** - Estilização
- **Lucide React** - Ícones
- **Context API** - Gerenciamento de estado

## 📦 Instalação

1. Clone o repositório e instale as dependências:

```bash
npm install
```

2. Configure as variáveis de ambiente:

```bash
cp .env.example .env.local
```

Edite o arquivo `.env.local` e configure a URL da API:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Inicie o servidor de desenvolvimento:

```bash
npm run dev
```

4. Acesse `http://localhost:3000`

## 📁 Estrutura do Projeto

```
├── app/
│   ├── auth/              # Página de autenticação
│   ├── dashboard/         # Página do dashboard (após login)
│   ├── layout.tsx         # Layout principal com AuthProvider
│   └── page.tsx           # Página inicial (redirecionamento)
├── components/
│   ├── auth/              # Componentes de autenticação
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ForgotPasswordForm.tsx
│   └── ui/                # Componentes shadcn/ui
├── contexts/
│   └── AuthContext.tsx    # Context de autenticação
├── lib/
│   ├── services/
│   │   └── api.ts         # Serviço de API
│   ├── types/
│   │   └── auth.ts        # Tipos TypeScript
│   └── utils.ts           # Utilitários
└── middleware.ts          # Middleware de proteção de rotas
```

## 🔌 Integração com Backend

A aplicação está totalmente integrada com a API FastAPI. Os endpoints utilizados:

- `POST /auth/login` - Login
- `POST /auth/register` - Cadastro
- `GET /auth/me` - Dados do usuário autenticado
- `PATCH /auth/me` - Atualizar dados do usuário
- `DELETE /auth/me` - Deletar conta

### Exemplo de uso da API:

```typescript
import { authService } from "@/lib/services/api";

// Login
const response = await authService.login({
  email: "user@example.com",
  password: "senha123"
});

// Cadastro
const user = await authService.register({
  cpf: "12345678900",
  full_name: "João Silva",
  email: "joao@example.com",
  password: "senha123"
});
```

## 🎨 Componentes Principais

### LoginForm
Formulário de login com validação e feedback de erros.

### RegisterForm
Formulário de cadastro com:
- Validação de CPF (formatação automática)
- Confirmação de senha
- Validação de e-mail

### ForgotPasswordForm
Interface para recuperação de senha (backend a ser implementado).

### AuthContext
Gerenciamento global de autenticação:
```typescript
const { user, login, logout, isAuthenticated } = useAuth();
```

## 🚀 Próximos Passos

- [ ] Implementar endpoint de recuperação de senha no backend
- [ ] Adicionar validação de força de senha
- [ ] Implementar refresh token
- [ ] Adicionar testes unitários
- [ ] Melhorar feedback de erros
- [ ] Adicionar funcionalidades do dashboard

## 📝 Scripts Disponíveis

```bash
npm run dev      # Inicia servidor de desenvolvimento
npm run build    # Cria build de produção
npm start        # Inicia servidor de produção
npm run lint     # Executa linter
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

---

Desenvolvido com ❤️ usando Next.js e shadcn/ui
