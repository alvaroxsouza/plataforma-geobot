import { api } from "./api";

export interface Usuario {
  id: number;
  nome: string;
  email: string;
  grupos: string[];
}

export interface UsuarioListaResponse {
  usuarios: Usuario[];
  total: number;
}

/**
 * Serviços de usuários
 */
export const usuarioService = {
  /**
   * Lista usuários com filtros (ADMIN)
   * GET /api/usuarios/
   */
  listar: (params?: {
    grupo?: string;
    limit?: number;
    offset?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.grupo) queryParams.append("grupo", params.grupo);
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.offset) queryParams.append("offset", params.offset.toString());
    
    const query = queryParams.toString();
    return api.get<Usuario[]>(`/api/usuarios/${query ? `?${query}` : ""}`);
  },

  /**
   * Busca fiscais disponíveis
   */
  listarFiscais: () => {
    return api.get<Usuario[]>("/api/usuarios/?grupo=fiscal");
  },

  /**
   * Obter dados do usuário atual
   * GET /api/me
   */
  me: () => api.get<Usuario>("/api/me"),
};
