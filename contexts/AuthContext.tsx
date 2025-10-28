"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { authService, ApiError } from "@/lib/services/api";
import { UserLogin, UserCreate, AuthState } from "@/lib/types/auth";

interface AuthContextType extends AuthState {
  login: (credentials: UserLogin) => Promise<void>;
  register: (userData: UserCreate) => Promise<void>;
  logout: () => void;
  updateUser: (data: { full_name?: string; password?: string }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });
  const router = useRouter();

  useEffect(() => {
    // Verificar se há token salvo no localStorage ao montar o componente
    const checkAuth = async () => {
      try {
        // Garantir que estamos no cliente
        if (typeof window === 'undefined') {
          setState(prev => ({ ...prev, isLoading: false }));
          return;
        }

        const token = localStorage.getItem("token");
        
        if (token) {
          try {
            const user = await authService.getCurrentUser(token);
            // Sincronizar cookie também
            document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24 * 7}`;
            setState({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch {
            localStorage.removeItem("token");
            document.cookie = 'token=; path=/; max-age=0';
            setState({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        } else {
          setState({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        setState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: UserLogin) => {
    try {
      const response = await authService.login(credentials);
      const token = response.access_token;
      
      // Buscar dados do usuário
      const user = await authService.getCurrentUser(token);

      console.log('Login bem-sucedido:', user);
      
      if (typeof window !== 'undefined') {
        localStorage.setItem("token", token);
        // Também salvar nos cookies para o proxy funcionar
        document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 dias
      }

      console.log('Token salvo com sucesso:', token);
      
      setState({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });

      console.log('Estado de autenticação atualizado:', { user, token });
      
      router.push("/dashboard");
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      throw new Error("Erro ao fazer login. Tente novamente.");
    }
  };

  const register = async (userData: UserCreate) => {
    try {
      await authService.register(userData);
      // Após cadastro, fazer login automaticamente
      await login({ email: userData.email, password: userData.password });
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      throw new Error("Erro ao criar conta. Tente novamente.");
    }
  };

  const logout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem("token");
      // Remover cookie também
      document.cookie = 'token=; path=/; max-age=0';
    }
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
    router.push("/auth");
  };

  const updateUser = async (data: { full_name?: string; password?: string }) => {
    if (!state.token) throw new Error("Não autenticado");
    
    try {
      const updatedUser = await authService.updateUser(state.token, data);
      setState((prev) => ({ ...prev, user: updatedUser }));
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      throw new Error("Erro ao atualizar usuário.");
    }
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
}
