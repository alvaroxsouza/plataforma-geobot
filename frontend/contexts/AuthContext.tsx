"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { authService, ApiError } from "@/lib/services/api";
import { UserLogin, UserCreate, AuthState } from "@/lib/types/auth";
import { sessionStorage } from "@/lib/sessionStorage";

interface AuthContextType extends AuthState {
  login: (credentials: UserLogin) => Promise<void>;
  register: (userData: UserCreate) => Promise<void>;
  logout: () => Promise<void>;
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
    // Verificar se há token salvo ao montar o componente
    const checkAuth = async () => {
      try {
        // Garantir que estamos no cliente
        if (typeof window === 'undefined') {
          setState(prev => ({ ...prev, isLoading: false }));
          return;
        }

        // Usar o serviço de sessão para verificar
        if (sessionStorage.hasValidSession()) {
          const token = sessionStorage.getToken();
          const savedUser = sessionStorage.getUser();
          
          if (token) {
            try {
              console.log('[AuthContext] Verificando token salvo...');
              // Validar com o servidor
              const user = await authService.getCurrentUser(token);
              console.log('[AuthContext] Token válido, usuário autenticado:', user.nome);
              
              // Atualizar sessão com dados frescos
              sessionStorage.saveSession(token, user);
              
              setState({
                user,
                token,
                isAuthenticated: true,
                isLoading: false,
              });
            } catch (error) {
              console.warn('[AuthContext] Token inválido ou expirado, limpando sessão:', error);
              sessionStorage.clearSession();
              setState({
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
              });
              // Redirecionar para login se estiver em rota protegida
              if (window.location.pathname.startsWith('/dashboard')) {
                router.push('/auth');
              }
            }
          } else {
            console.log('[AuthContext] Sessão inválida');
            sessionStorage.clearSession();
            setState({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        } else {
          console.log('[AuthContext] Nenhuma sessão válida encontrada');
          sessionStorage.clearSession();
          setState({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } catch (error) {
        console.error('[AuthContext] Erro ao verificar autenticação:', error);
        sessionStorage.clearSession();
        setState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    checkAuth();
  }, [router]);

  const login = async (credentials: UserLogin) => {
    try {
      const response = await authService.login(credentials);
      const token = response.access_token;
      const user = response.usuario;

      console.log('[AuthContext] Login bem-sucedido:', user.nome);
      
      // Salvar sessão usando o serviço
      sessionStorage.saveSession(token, user, response.expires_in || 60 * 60 * 24 * 7);
      
      setState({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });

      console.log('[AuthContext] Estado de autenticação atualizado');
      
      router.push("/dashboard");
    } catch (error) {
      console.error('[AuthContext] Erro ao fazer login:', error);
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Erro ao fazer login. Verifique suas credenciais e tente novamente.");
    }
  };

  const register = async (userData: UserCreate) => {
    try {
      await authService.register(userData);
      // Após cadastro, fazer login automaticamente
      await login({ email: userData.email, senha: userData.senha });
    } catch (error) {
      console.error('Erro ao criar conta:', error);
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Erro ao criar conta. Verifique os dados e tente novamente.");
    }
  };

  const logout = async () => {
    try {
      if (state.token) {
        await authService.logout(state.token);
      }
    } catch (error) {
      console.error('[AuthContext] Erro ao fazer logout no servidor:', error);
    } finally {
      console.log('[AuthContext] Fazendo logout, limpando sessão');
      sessionStorage.clearSession();
      setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
      router.push("/auth");
    }
  };

  const updateUser = async (_data: { full_name?: string; password?: string }) => {
    if (!state.token) throw new Error("Não autenticado");
    
    try {
      // Validar token antes de atualizar
      await authService.validateToken(state.token);
      // TODO: Implementar endpoint de atualização quando disponível na API
      throw new Error("Funcionalidade de atualização ainda não implementada na API");
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
