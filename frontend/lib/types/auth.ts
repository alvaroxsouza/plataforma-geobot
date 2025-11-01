export type UserRole = "cidadao" | "fiscalizador" | "admin";

export interface UserLogin {
  email: string;
  senha: string;
}

export interface UserCreate {
  cpf: string;
  nome: string;
  email: string;
  senha: string;
}

export interface UserResponse {
  id: number;
  uuid: string;
  cpf: string;
  nome: string;
  email: string;
  ativo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface LoginResponse {
  mensagem: string;
  access_token: string;
  token_type: string;
  expires_in: number;
  usuario: UserResponse;
}

export interface CadastroResponse {
  mensagem: string;
  usuario: UserResponse;
}

export interface LogoutResponse {
  mensagem: string;
  usuario: string;
}

export interface TokenValidation {
  valido: boolean;
  mensagem: string;
  usuario: UserResponse;
}

export interface AuthState {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
