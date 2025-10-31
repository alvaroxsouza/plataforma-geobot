// Configuração base da API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Helper para obter o token
const getToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
};

// Helper para headers com autenticação
const getAuthHeaders = (): HeadersInit => {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

// Helper para tratar erros da API
const handleApiError = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(error.detail || `Erro ${response.status}`);
  }
  return response;
};

export const api = {
  // GET request
  get: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    await handleApiError(response);
    return response.json();
  },

  // POST request
  post: async <T>(endpoint: string, data?: unknown): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    await handleApiError(response);
    return response.json();
  },

  // PATCH request
  patch: async <T>(endpoint: string, data?: unknown): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    await handleApiError(response);
    return response.json();
  },

  // DELETE request
  delete: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    await handleApiError(response);
    return response.json();
  },

  // POST com FormData (para upload de arquivos)
  postFormData: async <T>(endpoint: string, formData: FormData): Promise<T> => {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });
    await handleApiError(response);
    return response.json();
  },
};
