import { api } from "./api";

// Types baseados na API OpenAPI
export type ComplaintStatus = "PENDING" | "IN_ANALYSIS" | "COMPLETED" | "REJECTED" | "CANCELLED";

export type MotivoRejeicao = "DUPLICADA" | "INFORMACAO_INSUFICIENTE" | "FORA_ESCOPO" | "OUTRO";

export interface ComplaintCreate {
  street_address: string;
  subject: string;
  latitude?: number | null;
  longitude?: number | null;
  observacoes?: string | null;
}

export interface ComplaintResponse {
  id: number;
  street_address: string;
  subject: string;
  status: ComplaintStatus;
  created_at: string;
  updated_at?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  observacoes?: string | null;
  motivo_rejeicao?: MotivoRejeicao | null;
  justificativa_rejeicao?: string | null;
  denuncia_duplicada_id?: number | null;
  complainant: {
    id: number;
    uuid: string;
    cpf: string;
    nome: string;
    email: string;
    ativo: boolean;
  };
}

export interface ComplaintUpdate {
  street_address?: string | null;
  observacoes?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface ComplaintReject {
  motivo_rejeicao: MotivoRejeicao;
  justificativa: string;
  denuncia_duplicada_id?: number | null;
}

export interface ComplaintCancel {
  motivo: string;
}

// Serviços de denúncias
export const complaintsService = {
  // Criar nova denúncia
  create: (data: ComplaintCreate) => 
    api.post<ComplaintResponse>("/complaints/", data),

  // Listar todas as denúncias (FISCAL/ADMIN)
  getAll: (params?: {
    status?: ComplaintStatus;
    subject?: string;
    limit?: number;
    offset?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append("status", params.status);
    if (params?.subject) queryParams.append("subject", params.subject);
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.offset) queryParams.append("offset", params.offset.toString());
    
    const query = queryParams.toString();
    return api.get<ComplaintResponse[]>(`/complaints/${query ? `?${query}` : ""}`);
  },

  // Listar denúncias pendentes
  getPending: () => 
    api.get<ComplaintResponse[]>("/complaints/pending"),

  // Listar minhas denúncias (CIDADAO)
  getMy: () => 
    api.get<ComplaintResponse[]>("/complaints/minhas"),

  // Obter denúncia por ID
  getById: (id: number) => 
    api.get<ComplaintResponse>(`/complaints/${id}`),

  // Atualizar denúncia (apenas PENDING)
  update: (id: number, data: ComplaintUpdate) => 
    api.patch<ComplaintResponse>(`/complaints/${id}`, data),

  // Rejeitar denúncia (FISCAL)
  reject: (id: number, data: ComplaintReject) => 
    api.post<ComplaintResponse>(`/complaints/${id}/rejeitar`, data),

  // Cancelar denúncia (CIDADAO)
  cancel: (id: number, data: ComplaintCancel) => 
    api.post<ComplaintResponse>(`/complaints/${id}/cancelar`, data),

  // Analisar imagem da denúncia (FISCALIZADOR)
  analyzeImage: (id: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.postFormData<ComplaintResponse>(`/complaints/${id}/analyze`, formData);
  },

  // Download do relatório PDF
  downloadReport: async (id: number): Promise<Blob> => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/complaints/${id}/report/download`, {
      method: "GET",
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });
    
    if (!response.ok) {
      throw new Error("Erro ao baixar relatório");
    }
    
    return response.blob();
  },
};
