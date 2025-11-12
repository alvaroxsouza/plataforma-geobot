"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
}

export function useAuthenticatedFetch() {
  const { token, logout } = useAuth();

  const authenticatedFetch = useCallback(
    async <T = any>(url: string, options: FetchOptions = {}): Promise<T> => {
      const { skipAuth, headers, ...restOptions } = options;

      const fetchHeaders: Record<string, string> = {
        "Content-Type": "application/json",
        ...(headers as Record<string, string>),
      };

      // Adicionar token se disponível e não skipAuth
      if (token && !skipAuth) {
        fetchHeaders["Authorization"] = `Bearer ${token}`;
      }

      const fullUrl = url.startsWith("http") ? url : `${API_URL}${url}`;

      console.log('[AuthFetch] Requisição:', { url: fullUrl, hasToken: !!token });

      try {
        const response = await fetch(fullUrl, {
          ...restOptions,
          headers: fetchHeaders,
        });

        // Se 401, fazer logout automático
        if (response.status === 401 && !skipAuth) {
          console.warn('[AuthFetch] Token inválido (401), fazendo logout...');
          await logout();
          throw new Error("Sessão expirada. Por favor, faça login novamente.");
        }

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const errorMessage =
            errorData.mensagem ||
            errorData.detail?.mensagem ||
            errorData.detail ||
            errorData.message ||
            `Erro ${response.status}: ${response.statusText}`;
          throw new Error(errorMessage);
        }

        return response.json();
      } catch (error) {
        console.error('[AuthFetch] Erro na requisição:', error);
        throw error;
      }
    },
    [token, logout]
  );

  return authenticatedFetch;
}
