/**
 * Serviço para gerenciar etapas de fiscalização via API
 */
import { useAuthenticatedFetch } from "@/hooks/useAuthenticatedFetch";

export interface Etapa {
  id: number;
  uuid: string;
  fiscalizacao_id: number;
  etapa: string;
  iniciada_em: string;
  concluida_em?: string;
  progresso_percentual: number;
  dados?: Record<string, any>;
  resultado?: Record<string, any>;
  erro?: string;
  created_at: string;
  updated_at: string;
}

export interface Deteccao {
  tipo: string;
  confianca: number;
  localizacao?: Record<string, any>;
  descricao?: string;
  severidade?: string;
}

export interface ResultadoAnaliseIA {
  id: number;
  uuid: string;
  etapa_id: number;
  job_id?: string;
  deteccoes: Deteccao[];
  confianca_media: number;
  classificacao_geral?: string;
  modelo_utilizado?: string;
  tempo_processamento_segundos?: number;
  status_processamento: string;
  created_at: string;
}

export interface ProgressoFiscalizacao {
  fiscalizacao_id: number;
  etapa_atual: string;
  etapas_concluidas: string[];
  etapa_em_progresso?: string;
  etapas_pendentes: string[];
  progresso_geral_percentual: number;
  arquivos_carregados: number;
  resultado_ia?: ResultadoAnaliseIA;
  relatorio?: any;
}

export const etapasFiscalizacaoService = {
  /**
   * Obtém o progresso completo de uma fiscalização
   */
  async obterProgresso(fiscalizacaoId: number): Promise<ProgressoFiscalizacao> {
    const response = await fetch(
      `/api/fiscalizacoes/${fiscalizacaoId}/progresso`
    );
    return response.json();
  },

  /**
   * Inicia uma fiscalização
   */
  async iniciar(
    fiscalizacaoId: number,
    dadosIniciais?: Record<string, any>
  ): Promise<Etapa> {
    const response = await fetch(
      `/api/fiscalizacoes/${fiscalizacaoId}/iniciar`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ dados_iniciais: dadosIniciais }),
      }
    );
    return response.json();
  },

  /**
   * Transiciona para a próxima etapa
   */
  async proximaEtapa(
    fiscalizacaoId: number,
    dados?: Record<string, any>
  ): Promise<Etapa> {
    const response = await fetch(
      `/api/fiscalizacoes/${fiscalizacaoId}/proxima-etapa`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ dados }),
      }
    );
    return response.json();
  },

  /**
   * Atualiza o progresso de uma etapa
   */
  async atualizarProgresso(
    etapaId: number,
    progresso: number,
    resultado?: Record<string, any>
  ): Promise<Etapa> {
    const response = await fetch(`/api/etapas/${etapaId}/progresso`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        progresso_percentual: progresso,
        resultado,
      }),
    });
    return response.json();
  },

  /**
   * Faz upload de arquivo para uma etapa
   */
  async uploadArquivo(
    etapaId: number,
    arquivo: File,
    metadados?: Record<string, any>
  ): Promise<any> {
    const formData = new FormData();
    formData.append("arquivo", arquivo);
    if (metadados) {
      formData.append("metadados", JSON.stringify(metadados));
    }

    const response = await fetch(`/api/etapas/${etapaId}/upload`, {
      method: "POST",
      body: formData,
      // Não incluir Content-Type, deixar o browser definir
    });
    return response.json();
  },

  /**
   * Inicia análise de IA
   */
  async iniciarAnaliseIA(
    etapaId: number,
    imagensIds: number[],
    parametrosModelo?: Record<string, any>
  ): Promise<ResultadoAnaliseIA> {
    const response = await fetch(`/api/etapas/${etapaId}/analise-ia`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        imagens_ids: imagensIds,
        parametros_modelo: parametrosModelo,
      }),
    });
    return response.json();
  },

  /**
   * Obtém resultado da análise de IA
   */
  async obterResultadoIA(etapaId: number): Promise<ResultadoAnaliseIA> {
    const response = await fetch(`/api/etapas/${etapaId}/resultado-ia`);
    return response.json();
  },

  /**
   * Gera relatório
   */
  async gerarRelatorio(
    etapaId: number,
    titulo: string,
    opcoes?: {
      resumoExecutivo?: string;
      conclusoes?: string;
      recomendacoes?: string;
      resultadoAnaliseIAId?: number;
    }
  ): Promise<any> {
    const response = await fetch(`/api/etapas/${etapaId}/relatorio`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        titulo,
        ...opcoes,
      }),
    });
    return response.json();
  },

  /**
   * Obtém relatório
   */
  async obterRelatorio(fiscalizacaoId: number): Promise<any> {
    const response = await fetch(
      `/api/fiscalizacoes/${fiscalizacaoId}/relatorio`
    );
    return response.json();
  },

  /**
   * Cancela uma fiscalização
   */
  async cancelar(fiscalizacaoId: number): Promise<Etapa> {
    const response = await fetch(
      `/api/fiscalizacoes/${fiscalizacaoId}/cancelar`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    return response.json();
  },
};
