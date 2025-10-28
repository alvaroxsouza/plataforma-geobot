export type StatusDenuncia = 
  | "pendente" 
  | "em_analise" 
  | "em_fiscalizacao" 
  | "resolvida" 
  | "rejeitada"
  | "arquivada";

export type PrioridadeDenuncia = "baixa" | "media" | "alta" | "urgente";

export type CategoriaDenuncia = 
  | "calcada"
  | "rua"
  | "ciclovia"
  | "semaforo"
  | "sinalizacao"
  | "iluminacao"
  | "lixo"
  | "poluicao"
  | "barulho"
  | "outro";

export interface LocalizacaoDenuncia {
  latitude: number;
  longitude: number;
  endereco: string;
  bairro?: string;
  cidade: string;
  estado: string;
  cep?: string;
}

export interface ImagemDenuncia {
  id: string;
  url: string;
  thumbnail?: string;
  descricao?: string;
  data_upload: string;
}

export interface Denuncia {
  id: string;
  titulo: string;
  descricao: string;
  categoria: CategoriaDenuncia;
  status: StatusDenuncia;
  prioridade: PrioridadeDenuncia;
  localizacao: LocalizacaoDenuncia;
  imagens: ImagemDenuncia[];
  denunciante_id: string;
  denunciante_nome: string;
  denunciante_cpf?: string;
  fiscalizador_id?: string;
  fiscalizador_nome?: string;
  data_criacao: string;
  data_atualizacao: string;
  data_resolucao?: string;
  observacoes?: string;
  protocolo: string;
}

export interface FiltroDenuncia {
  status?: StatusDenuncia[];
  prioridade?: PrioridadeDenuncia[];
  categoria?: CategoriaDenuncia[];
  data_inicio?: string;
  data_fim?: string;
  denunciante_id?: string;
  fiscalizador_id?: string;
  busca?: string;
}

export interface CreateDenunciaData {
  titulo: string;
  descricao: string;
  categoria: CategoriaDenuncia;
  localizacao: LocalizacaoDenuncia;
  imagens?: File[];
}
