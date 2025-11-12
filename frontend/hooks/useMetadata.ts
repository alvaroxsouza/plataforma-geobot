"use client";

import { useState, useEffect } from "react";
import { 
  metadataService, 
  StatusDenunciaMetadata, 
  CategoriaDenunciaMetadata,
  PrioridadeMetadata,
  getStatusColorClasses,
  getPrioridadeColorClasses,
} from "@/services/metadata";

// Cache global para evitar múltiplas requisições
const metadataCache: {
  status: StatusDenunciaMetadata[] | null;
  categorias: CategoriaDenunciaMetadata[] | null;
  prioridades: PrioridadeMetadata[] | null;
  loading: boolean;
} = {
  status: null,
  categorias: null,
  prioridades: null,
  loading: false,
};

/**
 * Hook para buscar e cachear metadados do sistema
 * Os dados são compartilhados entre todos os componentes que usam este hook
 */
export function useMetadata() {
  const [status, setStatus] = useState<StatusDenunciaMetadata[]>(metadataCache.status || []);
  const [categorias, setCategorias] = useState<CategoriaDenunciaMetadata[]>(metadataCache.categorias || []);
  const [prioridades, setPrioridades] = useState<PrioridadeMetadata[]>(metadataCache.prioridades || []);
  const [loading, setLoading] = useState(metadataCache.loading);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Se já temos dados em cache, não precisamos buscar novamente
    if (metadataCache.status && metadataCache.categorias && metadataCache.prioridades) {
      return;
    }

    // Se já está carregando, não fazer nova requisição
    if (metadataCache.loading) {
      return;
    }

    const carregarMetadados = async () => {
      try {
        metadataCache.loading = true;
        setLoading(true);
        setError(null);

        const data = await metadataService.obterTodos();

        // Atualizar cache global
        metadataCache.status = data.status_denuncia.status;
        metadataCache.categorias = data.categorias_denuncia.categorias;
        metadataCache.prioridades = data.prioridades.prioridades;
        metadataCache.loading = false;

        // Atualizar estado local
        setStatus(data.status_denuncia.status);
        setCategorias(data.categorias_denuncia.categorias);
        setPrioridades(data.prioridades.prioridades);
      } catch (err) {
        console.error("Erro ao carregar metadados:", err);
        setError(err instanceof Error ? err.message : "Erro ao carregar metadados");
        metadataCache.loading = false;
      } finally {
        setLoading(false);
      }
    };

    carregarMetadados();
  }, []);

  // Funções auxiliares para buscar labels e cores
  const getStatusLabel = (value: string): string => {
    return status.find(s => s.value === value)?.label || value;
  };

  const getStatusColor = (value: string): string => {
    const item = status.find(s => s.value === value);
    return item ? getStatusColorClasses(item.cor) : "";
  };

  const getCategoriaLabel = (value: string): string => {
    return categorias.find(c => c.value === value)?.label || value;
  };

  const getCategoriaIcone = (value: string): string => {
    return categorias.find(c => c.value === value)?.icone || "📋";
  };

  const getPrioridadeLabel = (value: string): string => {
    return prioridades.find(p => p.value === value)?.label || value;
  };

  const getPrioridadeColor = (value: string): string => {
    const item = prioridades.find(p => p.value === value);
    return item ? getPrioridadeColorClasses(item.cor) : "";
  };

  return {
    // Dados
    status,
    categorias,
    prioridades,
    
    // Estado
    loading,
    error,
    
    // Funções auxiliares
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    getCategoriaIcone,
    getPrioridadeLabel,
    getPrioridadeColor,
  };
}
