import { api } from "./api";

// Tipos baseados na API OpenAPI (Swagger)
export type StatusDenuncia = 
  | "pendente" 
  | "em_analise" 
  | "em_fiscalizacao" 
  | "concluida" 
  | "arquivada" 
  | "cancelada";

export type CategoriaDenuncia = 
  | "calcada"
  | "rua"
  | "ciclovia"
  | "semaforo"
  | "sinalizacao"
  | "iluminacao"
  | "lixo_entulho"
  | "poluicao"
  | "barulho"
  | "outros";

export type Prioridade = "baixa" | "media" | "alta" | "urgente";

/**
 * Interface para criação de denúncia
 * Campos obrigatórios conforme Swagger:
 * - categoria, prioridade, observacao, logradouro, bairro, cidade, estado, cep
 */
export interface DenunciaCriar {
  categoria: CategoriaDenuncia;
  prioridade: Prioridade;
  observacao: string;
  logradouro: string;
  numero?: string | null;
  complemento?: string | null;
  bairro: string;
  cidade: string;
  estado: string;
  cep: string;
  latitude?: number | null;
  longitude?: number | null;
}

/**
 * Interface para resposta da API com dados da denúncia
 */
export interface DenunciaResposta {
  id: number;
  uuid: string;
  status: StatusDenuncia;
  categoria: CategoriaDenuncia;
  prioridade: Prioridade;
  observacao: string;
  usuario: {
    nome: string;
    email: string;
  };
  endereco: {
    logradouro: string;
    numero?: string | null;
    complemento?: string | null;
    bairro: string;
    cidade: string;
    estado: string;
    cep: string;
    latitude?: number | null;
    longitude?: number | null;
  };
  created_at: string;
  updated_at: string;
}

/**
 * Interface para metadados de paginação
 */
export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
}

/**
 * Interface para resposta paginada de denúncias
 */
export interface DenunciaRespostaPaginada {
  data: DenunciaResposta[];
  pagination: PaginationMeta;
}

/**
 * Interface para atualização de denúncia
 * Apenas campos editáveis: observacao e prioridade
 */
export interface DenunciaAtualizar {
  observacao?: string | null;
  prioridade?: Prioridade | null;
}

/**
 * Interface para atualização de status (admin/fiscal)
 */
export interface DenunciaAtualizarStatus {
  status: StatusDenuncia;
}

/**
 * Serviços de denúncias
 * Endpoints conforme documentação Swagger OpenAPI 3.1.0
 */
export const servicoDenuncias = {
  /**
   * Lista denúncias do usuário ou todas (para admin/fiscal) com paginação
   * GET /api/denuncias/
   * 
   * @param parametros - Filtros de busca
   * @param parametros.status - Filtrar por status
   * @param parametros.categoria - Filtrar por categoria (rua, calcada, ciclovia, etc)
   * @param parametros.todas - Se true, lista todas as denúncias (apenas admin/fiscal)
   * @param parametros.limit - Quantidade de registros por página (padrão: 50)
   * @param parametros.offset - Posição inicial para paginação (padrão: 0)
   */
  listar: (parametros?: {
    status?: StatusDenuncia;
    categoria?: CategoriaDenuncia;
    todas?: boolean;
    limit?: number;
    offset?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (parametros?.status) queryParams.append("status", parametros.status);
    if (parametros?.categoria) queryParams.append("categoria", parametros.categoria);
    if (parametros?.todas !== undefined) queryParams.append("todas", parametros.todas.toString());
    if (parametros?.limit !== undefined) queryParams.append("limit", parametros.limit.toString());
    if (parametros?.offset !== undefined) queryParams.append("offset", parametros.offset.toString());
    
    const query = queryParams.toString();
    return api.get<DenunciaRespostaPaginada>(`/api/denuncias/${query ? `?${query}` : ""}`);
  },

  /**
   * Cria uma nova denúncia
   * POST /api/denuncias/
   * 
   * @param dados - Dados da denúncia a ser criada
   */
  criar: (dados: DenunciaCriar) => 
    api.post<DenunciaResposta>("/api/denuncias/", dados),

  /**
   * Busca uma denúncia por ID
   * GET /api/denuncias/{denuncia_id}
   * 
   * @param id - ID da denúncia
   */
  obterPorId: (id: number) => 
    api.get<DenunciaResposta>(`/api/denuncias/${id}`),

  /**
   * Atualiza uma denúncia (apenas criador e status pendente)
   * PATCH /api/denuncias/{denuncia_id}
   * 
   * @param id - ID da denúncia
   * @param dados - Dados a serem atualizados (observacao e/ou prioridade)
   */
  atualizar: (id: number, dados: DenunciaAtualizar) => 
    api.patch<DenunciaResposta>(`/api/denuncias/${id}`, dados),

  /**
   * Deleta uma denúncia (apenas criador e status pendente)
   * DELETE /api/denuncias/{denuncia_id}
   * 
   * @param id - ID da denúncia
   */
  deletar: (id: number) => 
    api.delete<{ mensagem: string }>(`/api/denuncias/${id}`),

  /**
   * Atualiza o status de uma denúncia (apenas admin/fiscal)
   * PATCH /api/denuncias/{denuncia_id}/status
   * 
   * @param id - ID da denúncia
   * @param dados - Novo status da denúncia
   */
  atualizarStatus: (id: number, dados: DenunciaAtualizarStatus) => 
    api.patch<DenunciaResposta>(`/api/denuncias/${id}/status`, dados),
};
