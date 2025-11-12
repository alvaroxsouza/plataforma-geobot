import { Denuncia, EnderecoDenuncia } from "./denuncia";

export type StatusFiscalizacao = 
  | "agendada"
  | "em_andamento" 
  | "concluida"
  | "cancelada";

export type TipoFiscalizacao = 
  | "vistoria"
  | "inspecao"
  | "fiscalizacao_rotina"
  | "atendimento_denuncia"
  | "reincidencia";

export interface EquipeFiscalizacao {
  id: string;
  nome: string;
  cpf: string;
  funcao: string;
}

export interface Fiscalizacao {
  id: string;
  protocolo: string;
  tipo: TipoFiscalizacao;
  status: StatusFiscalizacao;
  denuncia_id?: string;
  denuncia?: Denuncia;
  titulo: string;
  descricao: string;
  localizacao: EnderecoDenuncia;
  equipe: EquipeFiscalizacao[];
  data_agendamento: string;
  data_inicio?: string;
  data_conclusao?: string;
  observacoes?: string;
  resultado?: string;
  imagens_antes?: string[];
  imagens_depois?: string[];
  data_criacao: string;
  data_atualizacao: string;
}

export interface FiltroFiscalizacao {
  status?: StatusFiscalizacao[];
  tipo?: TipoFiscalizacao[];
  data_inicio?: string;
  data_fim?: string;
  fiscalizador_id?: string;
  denuncia_id?: string;
  busca?: string;
}

export interface CreateFiscalizacaoData {
  tipo: TipoFiscalizacao;
  denuncia_id?: string;
  titulo: string;
  descricao: string;
  localizacao: EnderecoDenuncia;
  equipe_ids: string[];
  data_agendamento: string;
}
