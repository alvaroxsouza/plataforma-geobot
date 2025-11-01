import { api } from "./api";

// Types baseados na API OpenAPI
export type TipoNotificacao = 
  | "DENUNCIA_CRIADA"
  | "DENUNCIA_ACEITA"
  | "DENUNCIA_REJEITADA"
  | "DENUNCIA_CONCLUIDA"
  | "DENUNCIA_CANCELADA"
  | "FISCALIZACAO_ATRIBUIDA"
  | "FISCALIZACAO_CONCLUIDA"
  | "RELATORIO_DISPONIVEL"
  | "SOBREVOO_CONCLUIDO"
  | "INFERENCIA_CONCLUIDA";

export interface NotificacaoResponse {
  id: number;
  usuario_id: number;
  tipo: TipoNotificacao;
  titulo: string;
  mensagem: string;
  link_relacionado?: string | null;
  lida: boolean;
  data_leitura?: string | null;
  data_criacao: string;
}

// Serviços de notificações
export const notificacoesService = {
  // Listar minhas notificações
  getAll: (params?: {
    apenas_nao_lidas?: boolean;
    limit?: number;
    offset?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.apenas_nao_lidas !== undefined) {
      queryParams.append("apenas_nao_lidas", params.apenas_nao_lidas.toString());
    }
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.offset) queryParams.append("offset", params.offset.toString());
    
    const query = queryParams.toString();
    return api.get<NotificacaoResponse[]>(`/notificacoes/${query ? `?${query}` : ""}`);
  },

  // Contar notificações não lidas
  countUnread: () => 
    api.get<{ count: number }>("/notificacoes/nao-lidas/count"),

  // Obter detalhes de uma notificação
  getById: (id: number) => 
    api.get<NotificacaoResponse>(`/notificacoes/${id}`),

  // Marcar notificação como lida
  markAsRead: (id: number) => 
    api.patch<NotificacaoResponse>(`/notificacoes/${id}/marcar-lida`),

  // Marcar todas como lidas
  markAllAsRead: () => 
    api.post<{ message: string; count: number }>("/notificacoes/marcar-todas-lidas"),

  // Deletar notificação
  delete: (id: number) => 
    api.delete(`/notificacoes/${id}`),
};
