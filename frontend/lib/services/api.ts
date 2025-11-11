import { UserLogin, UserCreate, LoginResponse, CadastroResponse, UserResponse, LogoutResponse, TokenValidation } from "@/lib/types/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// Mapeamento de mensagens de erro comuns
const ERROR_MESSAGES: Record<number, string> = {
  400: 'Dados inválidos. Verifique as informações e tente novamente.',
  401: 'Credenciais inválidas. Verifique seu e-mail e senha.',
  403: 'Acesso negado. Você não tem permissão para esta ação.',
  404: 'Recurso não encontrado. Verifique se os dados estão corretos.',
  409: 'Já existe um cadastro com estes dados.',
  422: 'Dados inválidos. Verifique os campos obrigatórios.',
  500: 'Erro no servidor. Tente novamente mais tarde.',
  502: 'Servidor temporariamente indisponível. Tente novamente.',
  503: 'Serviço temporariamente indisponível. Tente novamente.',
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = ERROR_MESSAGES[response.status] || `Erro ${response.status}: ${response.statusText}`;
    let errorData: any = {};
    
    try {
      errorData = await response.json();
      
      // Tentar extrair a mensagem de erro de diferentes formatos
      // Prioridade para mensagens customizadas do backend
      if (errorData.mensagem) {
        errorMessage = errorData.mensagem;
      } else if (errorData.detail) {
        // Se detail for um objeto com mensagem (nosso formato customizado)
        if (typeof errorData.detail === 'object' && !Array.isArray(errorData.detail)) {
          if (errorData.detail.mensagem) {
            errorMessage = errorData.detail.mensagem;
          } else if (errorData.detail.erro) {
            errorMessage = errorData.detail.erro;
          } else {
            errorMessage = JSON.stringify(errorData.detail);
          }
        }
        // Se detail for uma string, usar diretamente
        else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } 
        // Se detail for um array (validação do FastAPI)
        else if (Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map((err: any) => {
            if (typeof err === 'string') return err;
            if (err.msg) {
              // Traduzir mensagens comuns de validação
              const msg = err.msg.toLowerCase();
              if (msg.includes('field required')) return `Campo obrigatório: ${err.loc?.[1] || 'desconhecido'}`;
              if (msg.includes('value is not a valid')) return `Valor inválido para: ${err.loc?.[1] || 'campo'}`;
              return err.msg;
            }
            return JSON.stringify(err);
          });
          errorMessage = errors.join('; ');
        }
      } else if (errorData.message) {
        errorMessage = errorData.message;
      } else if (errorData.error) {
        errorMessage = errorData.error;
      }
    } catch (e) {
      // Se não conseguir parsear o JSON, manter a mensagem padrão
      console.error('Erro ao parsear resposta de erro:', e);
    }
    
    throw new ApiError(errorMessage, response.status, errorData);
  }
  return response.json();
}

export const authService = {
  async login(credentials: UserLogin): Promise<LoginResponse> {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });
    return handleResponse<LoginResponse>(response);
  },

  async register(userData: UserCreate): Promise<CadastroResponse> {
    const response = await fetch(`${API_URL}/api/auth/cadastro`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });
    return handleResponse<CadastroResponse>(response);
  },

  async getCurrentUser(token: string): Promise<UserResponse> {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    return handleResponse<UserResponse>(response);
  },

  async logout(token: string): Promise<LogoutResponse> {
    const response = await fetch(`${API_URL}/api/auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    return handleResponse<LogoutResponse>(response);
  },

  async validateToken(token: string): Promise<TokenValidation> {
    const response = await fetch(`${API_URL}/api/auth/validar-token`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    return handleResponse<TokenValidation>(response);
  },
};

export { ApiError };
