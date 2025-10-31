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

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.mensagem || errorData.detail || `Erro ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
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
