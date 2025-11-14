import { api } from "./api";

// Types baseados na API OpenAPI
export type FiscalizacaoStatus = 
  | "AGUARDANDO_SOBREVOO" 
  | "AGUARDANDO_INFERENCIA" 
  | "GERANDO_RELATORIO" 
  | "CONCLUIDA" 
  | "CANCELADA";

export interface FiscalizacaoCreate {
  complaint_id: number;
  data_conclusao_prevista?: string | null;
  observacoes?: string | null;
  fiscais_ids?: number[] | null; // NOVO: Lista de IDs de fiscais
}

export interface FiscalAtribuido {
  id: number;
  nome: string | null;
  email: string | null;
  papel: "responsavel" | "auxiliar";
  data_atribuicao: string | null;
}

export interface FiscalizacaoResponse {
  id: number;
  complaint_id: number;
  fiscal_responsavel_id?: number | null; // DEPRECATED: Mantido para compatibilidade
  fiscais: FiscalAtribuido[]; // NOVO: Array com todos os fiscais
  status_fiscalizacao: FiscalizacaoStatus;
  data_inicio: string;
  data_conclusao_prevista?: string | null;
  data_conclusao_efetiva?: string | null;
  data_criacao: string;
  data_atualizacao: string;
}

export interface FiscalizacaoAdicionarFiscal {
  fiscal_id: number;
  papel?: "responsavel" | "auxiliar"; // Padrão: "auxiliar"
}

export interface FiscalizacaoHistoricoResponse {
  id: number;
  fiscalizacao_id: number;
  status_anterior?: string | null;
  status_novo: string;
  usuario_id?: number | null;
  observacoes?: string | null;
  timestamp: string;
}

// Mapeamento de status para o front-end
export const STATUS_LABELS: Record<FiscalizacaoStatus, string> = {
  AGUARDANDO_SOBREVOO: "Aguardando Sobrevoo",
  AGUARDANDO_INFERENCIA: "Aguardando Inferência",
  GERANDO_RELATORIO: "Gerando Relatório",
  CONCLUIDA: "Concluída",
  CANCELADA: "Cancelada",
};

// Serviços de fiscalização
export const fiscalizacaoService = {
  // Criar nova fiscalização (FISCAL/ADMIN)
  create: (data: FiscalizacaoCreate) => 
    api.post<FiscalizacaoResponse>("/api/fiscalizacao/", data),

  // Listar fiscalizações com filtros (FISCAL/ADMIN)
  getAll: (params?: {
    status_filter?: FiscalizacaoStatus;
    fiscal_id?: number;
    limit?: number;
    offset?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.status_filter) queryParams.append("status_filter", params.status_filter);
    if (params?.fiscal_id) queryParams.append("fiscal_id", params.fiscal_id.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.offset) queryParams.append("offset", params.offset.toString());
    
    const query = queryParams.toString();
    return api.get<FiscalizacaoResponse[]>(`/api/fiscalizacao/${query ? `?${query}` : ""}`);
  },

  // Listar minhas fiscalizações (FISCAL)
  getMy: () => 
    api.get<FiscalizacaoResponse[]>("/api/fiscalizacao/minhas"),

  // Obter detalhes de uma fiscalização
  getById: (id: number) => 
    api.get<FiscalizacaoResponse>(`/api/fiscalizacao/${id}`),

  // Adicionar fiscal a uma fiscalização (ADMIN)
  addFiscal: (id: number, data: FiscalizacaoAdicionarFiscal) => 
    api.post<FiscalizacaoResponse>(`/api/fiscalizacao/${id}/fiscais`, data),

  // Remover fiscal de uma fiscalização (ADMIN)
  removeFiscal: (id: number, fiscalId: number) => 
    api.delete<FiscalizacaoResponse>(`/api/fiscalizacao/${id}/fiscais/${fiscalId}`),

  // Obter histórico de uma fiscalização (FISCAL/ADMIN)
  getHistory: (id: number) => 
    api.get<FiscalizacaoHistoricoResponse[]>(`/api/fiscalizacao/${id}/historico`),
};
