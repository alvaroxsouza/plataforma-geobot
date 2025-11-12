import { api } from "./api";

// ============================================================================
// TIPOS DE METADADOS
// ============================================================================

export interface MetadataItem {
  value: string;
  label: string;
  descricao: string;
}

export interface StatusDenunciaMetadata extends MetadataItem {
  cor: string;
}

export interface CategoriaDenunciaMetadata extends MetadataItem {
  icone: string;
}

export interface PrioridadeMetadata extends MetadataItem {
  cor: string;
}

export interface MetadataResponse {
  status_denuncia: {
    status: StatusDenunciaMetadata[];
  };
  categorias_denuncia: {
    categorias: CategoriaDenunciaMetadata[];
  };
  prioridades: {
    prioridades: PrioridadeMetadata[];
  };
}

// ============================================================================
// SERVIÇO DE METADADOS
// ============================================================================

/**
 * Serviço para buscar metadados do sistema (enums, opções, etc.)
 * Estes dados vêm diretamente do backend e garantem sincronização
 */
export const metadataService = {
  /**
   * Busca todos os metadados do sistema
   * Inclui: status de denúncia, categorias, prioridades
   */
  obterTodos: () => 
    api.get<MetadataResponse>("/api/metadata/"),

  /**
   * Busca apenas os status de denúncia
   */
  obterStatusDenuncia: () => 
    api.get<{ status: StatusDenunciaMetadata[] }>("/api/metadata/status-denuncia"),

  /**
   * Busca apenas as categorias de denúncia
   */
  obterCategorias: () => 
    api.get<{ categorias: CategoriaDenunciaMetadata[] }>("/api/metadata/categorias-denuncia"),

  /**
   * Busca apenas as prioridades
   */
  obterPrioridades: () => 
    api.get<{ prioridades: PrioridadeMetadata[] }>("/api/metadata/prioridades"),
};

// ============================================================================
// HELPERS PARA CONVERSÃO DE CORES
// ============================================================================

/**
 * Converte a cor retornada do backend para classes Tailwind
 */
export const getStatusColorClasses = (cor: string): string => {
  const colorMap: Record<string, string> = {
    yellow: "bg-yellow-100 text-yellow-800 border-yellow-200",
    blue: "bg-blue-100 text-blue-800 border-blue-200",
    purple: "bg-purple-100 text-purple-800 border-purple-200",
    green: "bg-green-100 text-green-800 border-green-200",
    gray: "bg-gray-100 text-gray-800 border-gray-200",
    red: "bg-red-100 text-red-800 border-red-200",
  };
  return colorMap[cor] || "bg-gray-100 text-gray-800 border-gray-200";
};

/**
 * Converte a cor da prioridade para classes Tailwind
 */
export const getPrioridadeColorClasses = (cor: string): string => {
  const colorMap: Record<string, string> = {
    blue: "bg-blue-100 text-blue-800",
    yellow: "bg-yellow-100 text-yellow-800",
    orange: "bg-orange-100 text-orange-800",
    red: "bg-red-100 text-red-800",
  };
  return colorMap[cor] || "bg-gray-100 text-gray-800";
};
