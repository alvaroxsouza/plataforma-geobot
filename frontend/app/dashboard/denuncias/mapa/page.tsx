"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { Home, ChevronRight, MapPin, Loader2, AlertCircle, Filter, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Link from "next/link";
import { servicoDenuncias, DenunciaResposta, StatusDenuncia } from "@/services/denuncias";
import { useMetadata } from "@/hooks/useMetadata";
import { toast } from "sonner";

// Importação dinâmica do mapa para evitar problemas de SSR
const MapaInterativo = dynamic(() => import("@/components/dashboard/MapaDenuncias"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-[600px] bg-muted/20 rounded-lg">
      <div className="text-center">
        <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
        <p className="text-sm text-muted-foreground">Carregando mapa...</p>
      </div>
    </div>
  ),
});

export default function MapaDenunciasPage() {
  const router = useRouter();
  const {
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    getPrioridadeColor,
    loading: metadataLoading,
  } = useMetadata();

  const [denuncias, setDenuncias] = useState<DenunciaResposta[]>([]);
  const [denunciasFiltradas, setDenunciasFiltradas] = useState<DenunciaResposta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtroStatus, setFiltroStatus] = useState<StatusDenuncia | "todas">("todas");
  const [filtroPrioridade, setFiltroPrioridade] = useState<string>("todas");

  // Carregar denúncias
  const carregarDenuncias = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Tentar carregar todas as denúncias (admin/fiscal)
      let denunciasData: DenunciaResposta[];
      try {
        const response = await servicoDenuncias.listar({ todas: true, limit: 1000, offset: 0 });
        denunciasData = response.data;
      } catch {
        // Se falhar, carregar apenas as do usuário
        const response = await servicoDenuncias.listar({ todas: false, limit: 1000, offset: 0 });
        denunciasData = response.data;
      }

      // Filtrar apenas denúncias com coordenadas válidas
      const denunciasComCoordenadas = denunciasData.filter(
        (d) => d.endereco.latitude && d.endereco.longitude
      );
      
      setDenuncias(denunciasComCoordenadas);
      setDenunciasFiltradas(denunciasComCoordenadas);
      
      if (denunciasComCoordenadas.length === 0) {
        toast.warning("Nenhuma denúncia com coordenadas encontrada");
      } else {
        toast.success(`${denunciasComCoordenadas.length} denúncia(s) carregada(s) no mapa`);
      }
    } catch (err: any) {
      console.error("Erro ao carregar denúncias:", err);
      const errorMessage = err?.response?.data?.detail || err?.message || "Erro desconhecido";
      setError(`Não foi possível carregar as denúncias: ${errorMessage}`);
      toast.error(`Erro: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDenuncias();
  }, []);

  // Aplicar filtros
  useEffect(() => {
    let filtered = denuncias;

    if (filtroStatus !== "todas") {
      filtered = filtered.filter(d => d.status === filtroStatus);
    }

    if (filtroPrioridade !== "todas") {
      filtered = filtered.filter(d => d.prioridade === filtroPrioridade);
    }

    setDenunciasFiltradas(filtered);
  }, [denuncias, filtroStatus, filtroPrioridade]);

  // Estatísticas
  const stats = [
    {
      label: "Total no Mapa",
      value: denunciasFiltradas.length,
      icon: MapPin,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      label: "Pendentes",
      value: denunciasFiltradas.filter(d => d.status === "pendente").length,
      icon: AlertCircle,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
    },
    {
      label: "Em Fiscalização",
      value: denunciasFiltradas.filter(d => d.status === "em_fiscalizacao").length,
      icon: AlertCircle,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      label: "Concluídas",
      value: denunciasFiltradas.filter(d => d.status === "concluida").length,
      icon: AlertCircle,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
  ];

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/dashboard" className="hover:text-foreground transition-colors">
          <Home className="h-4 w-4" />
        </Link>
        <ChevronRight className="h-4 w-4" />
        <Link href="/dashboard/denuncias" className="hover:text-foreground transition-colors">
          Denúncias
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium">Mapa</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Mapa de Denúncias</h1>
          <p className="text-muted-foreground">
            Visualização geográfica de todas as denúncias registradas
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={carregarDenuncias} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Link href="/dashboard/denuncias">
            <Button variant="outline">Voltar para Lista</Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="mr-2 h-5 w-5" />
            Filtros do Mapa
          </CardTitle>
          <CardDescription>Filtre as denúncias exibidas no mapa</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <Select value={filtroStatus} onValueChange={(value) => setFiltroStatus(value as StatusDenuncia | "todas")}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todas">Todos os Status</SelectItem>
                  <SelectItem value="pendente">Pendente</SelectItem>
                  <SelectItem value="em_analise">Em Análise</SelectItem>
                  <SelectItem value="em_fiscalizacao">Em Fiscalização</SelectItem>
                  <SelectItem value="concluida">Concluída</SelectItem>
                  <SelectItem value="arquivada">Arquivada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Prioridade</label>
              <Select value={filtroPrioridade} onValueChange={setFiltroPrioridade}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas as prioridades" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todas">Todas as Prioridades</SelectItem>
                  <SelectItem value="baixa">Baixa</SelectItem>
                  <SelectItem value="media">Média</SelectItem>
                  <SelectItem value="alta">Alta</SelectItem>
                  <SelectItem value="urgente">Urgente</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Legenda</label>
              <div className="flex flex-wrap gap-2">
                <Badge className="bg-yellow-500 hover:bg-yellow-600">Pendente</Badge>
                <Badge className="bg-blue-500 hover:bg-blue-600">Em Análise</Badge>
                <Badge className="bg-purple-500 hover:bg-purple-600">Fiscalização</Badge>
                <Badge className="bg-green-500 hover:bg-green-600">Concluída</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mapa */}
      <Card>
        <CardHeader>
          <CardTitle>Mapa Interativo</CardTitle>
          <CardDescription>
            Clique nos marcadores para ver detalhes das denúncias
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="flex flex-col items-center justify-center h-[600px] bg-muted/20 rounded-lg">
              <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Erro ao carregar mapa</h3>
              <p className="text-sm text-muted-foreground mb-4">{error}</p>
              <Button onClick={carregarDenuncias}>Tentar Novamente</Button>
            </div>
          ) : loading || metadataLoading ? (
            <div className="flex items-center justify-center h-[600px] bg-muted/20 rounded-lg">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                <p className="text-sm text-muted-foreground">Carregando denúncias...</p>
              </div>
            </div>
          ) : (
            <MapaInterativo
              denuncias={denunciasFiltradas}
              getStatusColor={getStatusColor}
              getStatusLabel={getStatusLabel}
              getCategoriaLabel={getCategoriaLabel}
              getPrioridadeColor={getPrioridadeColor}
            />
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
        <CardContent className="pt-6">
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-primary/20 rounded-lg">
              <MapPin className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Sobre o Mapa</h3>
              <p className="text-sm text-muted-foreground">
                Este mapa exibe todas as denúncias que possuem coordenadas geográficas registradas.
                As cores dos marcadores indicam o status da denúncia. Clique em um marcador para ver
                mais detalhes e acessar a denúncia completa.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
