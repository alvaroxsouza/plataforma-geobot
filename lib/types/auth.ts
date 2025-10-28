export type UserRole = "cidadao" | "fiscalizador" | "admin";

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserCreate {
  cpf: string;
  full_name: string;
  email: string;
  password: string;
  role?: UserRole;
}

export interface UserResponse {
  id: number;
  uuid: string;
  cpf: string;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AuthState {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
