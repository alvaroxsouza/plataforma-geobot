/**
 * Status de uma denúncia conforme Swagger
 * 
 * - pendente: Denúncia criada, aguardando análise
 * - em_analise: Denúncia sendo analisada pela equipe
 * - em_fiscalizacao: Denúncia em processo de fiscalização
 * - concluida: Denúncia resolvida com sucesso
 * - arquivada: Denúncia arquivada
 * - cancelada: Denúncia cancelada pelo usuário
 */
export type StatusDenuncia = 
  | "pendente" 
  | "em_analise" 
  | "em_fiscalizacao" 
  | "concluida" 
  | "arquivada"
  | "cancelada";

/**
 * Prioridade de uma denúncia conforme Swagger
 */
export type Prioridade = "baixa" | "media" | "alta" | "urgente";

/**
 * Categoria de uma denúncia conforme Swagger
 * 
 * - ambiental: Problemas ambientais (poluição, desmatamento, etc.)
 * - sanitaria: Problemas sanitários (esgoto, lixo, etc.)
 * - construcao_irregular: Construções irregulares ou sem autorização
 * - poluicao_sonora: Poluição sonora e barulho excessivo
 * - outros: Outras categorias não especificadas
 */
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

/**
 * Interface para endereço da denúncia
 */
export interface EnderecoDenuncia {
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
 * Interface para dados do usuário denunciante
 */
export interface UsuarioDenuncia {
  nome: string;
  email: string;
}

/**
 * Interface para denúncia completa conforme API
 */
export interface Denuncia {
  id: number;
  uuid: string;
  categoria: CategoriaDenuncia;
  status: StatusDenuncia;
  prioridade: Prioridade;
  observacao: string;
  usuario: UsuarioDenuncia;
  endereco: EnderecoDenuncia;
  created_at: string;
  updated_at: string;
}

/**
 * Interface para filtros de busca de denúncias
 */
export interface FiltroDenuncia {
  status?: StatusDenuncia;
  todas?: boolean;
}

/**
 * Interface para criação de denúncia conforme Swagger
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
 * Interface para atualização de denúncia
 */
export interface DenunciaAtualizar {
  observacao?: string | null;
  prioridade?: Prioridade | null;
}
