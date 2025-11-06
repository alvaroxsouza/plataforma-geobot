"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, MapPin, Calendar, AlertCircle, Home, ChevronRight, Loader2, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

import { servicoDenuncias, DenunciaResposta, StatusDenuncia } from "@/services/denuncias";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface DenunciaStats {
  total: number;
  pendentes: number;
  em_analise: number;
  em_fiscalizacao: number;
  concluidas: number;
  arquivadas: number;
  canceladas: number;
}

const categoriasLabels: Record<string, string> = {
  calcada: "Calçada",
  rua: "Rua",
  ciclovia: "Ciclovia",
  semaforo: "Semáforo",
  sinalizacao: "Sinalização",
  iluminacao: "Iluminação",
  lixo_entulho: "Lixo e Entulho",
  poluicao: "Poluição",
  barulho: "Barulho",
  outros: "Outros",
};

const statusLabels: Record<StatusDenuncia, string> = {
  pendente: "Pendente",
  em_analise: "Em Análise",
  em_fiscalizacao: "Em Fiscalização",
  concluida: "Concluída",
  arquivada: "Arquivada",
  cancelada: "Cancelada",
};

const statusColors: Record<StatusDenuncia, string> = {
  pendente: "bg-yellow-100 text-yellow-800 border-yellow-200",
  em_analise: "bg-blue-100 text-blue-800 border-blue-200",
  em_fiscalizacao: "bg-purple-100 text-purple-800 border-purple-200",
  concluida: "bg-green-100 text-green-800 border-green-200",
  arquivada: "bg-gray-100 text-gray-800 border-gray-200",
  cancelada: "bg-red-100 text-red-800 border-red-200",
};

const prioridadeColors: Record<string, string> = {
  baixa: "bg-blue-100 text-blue-800",
  media: "bg-yellow-100 text-yellow-800",
  alta: "bg-orange-100 text-orange-800",
  urgente: "bg-red-100 text-red-800",
};

export default function DenunciasPage() {

  const [searchQuery, setSearchQuery] = useState("");
  const [denuncias, setDenuncias] = useState<DenunciaResposta[]>([]);
  const [denunciasFiltradas, setDenunciasFiltradas] = useState<DenunciaResposta[]>([]);
  const [stats, setStats] = useState<DenunciaStats>({
    total: 0,
    pendentes: 0,
    em_analise: 0,
    em_fiscalizacao: 0,
    concluidas: 0,
    arquivadas: 0,
    canceladas: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusAtivo, setStatusAtivo] = useState<"todas" | StatusDenuncia>("todas");

  // Verificar se usuário é admin ou fiscal - será validado no backend
  // Por ora, assumimos que todos podem tentar carregar, mas o backend restringirá
  const [isAdminOuFiscal, setIsAdminOuFiscal] = useState(false);

  const carregarDenuncias = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Tentar carregar todas as denúncias primeiro (admin/fiscal)
      try {
        const responseAll = await servicoDenuncias.listar({ todas: true });
        setDenuncias(responseAll);
        calcularEstatisticas(responseAll);
        setIsAdminOuFiscal(true);
      } catch {
        // Se falhar, carregar apenas as do usuário (cidadão)
        const responseMy = await servicoDenuncias.listar({ todas: false });
        setDenuncias(responseMy);
        calcularEstatisticas(responseMy);
        setIsAdminOuFiscal(false);
      }
    } catch (err) {
      console.error("Erro ao carregar denúncias:", err);
      setError("Não foi possível carregar as denúncias. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  const calcularEstatisticas = (denunciasData: DenunciaResposta[]) => {
    const stats: DenunciaStats = {
      total: denunciasData.length,
      pendentes: denunciasData.filter(d => d.status === "pendente").length,
      em_analise: denunciasData.filter(d => d.status === "em_analise").length,
      em_fiscalizacao: denunciasData.filter(d => d.status === "em_fiscalizacao").length,
      concluidas: denunciasData.filter(d => d.status === "concluida").length,
      arquivadas: denunciasData.filter(d => d.status === "arquivada").length,
      canceladas: denunciasData.filter(d => d.status === "cancelada").length,
    };
    setStats(stats);
  };

  useEffect(() => {
    carregarDenuncias();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let filtered = denuncias;

    // Filtrar por status
    if (statusAtivo !== "todas") {
      filtered = filtered.filter(d => d.status === statusAtivo);
    }

    // Filtrar por busca
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(d => 
        d.observacao.toLowerCase().includes(query) ||
        d.endereco.logradouro.toLowerCase().includes(query) ||
        d.endereco.bairro.toLowerCase().includes(query) ||
        d.endereco.cidade.toLowerCase().includes(query) ||
        categoriasLabels[d.categoria].toLowerCase().includes(query)
      );
    }

    setDenunciasFiltradas(filtered);
  }, [denuncias, statusAtivo, searchQuery]);

  const statsCards = [
    { 
      label: "Total de Denúncias", 
      value: stats.total,
      icon: AlertCircle,
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    { 
      label: "Pendentes", 
      value: stats.pendentes,
      icon: AlertCircle,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50"
    },
    { 
      label: "Em Análise", 
      value: stats.em_analise,
      icon: AlertCircle,
      color: "text-orange-600",
      bgColor: "bg-orange-50"
    },
    { 
      label: "Concluídas", 
      value: stats.concluidas,
      icon: AlertCircle,
      color: "text-green-600",
      bgColor: "bg-green-50"
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
        <span className="text-foreground font-medium">Denúncias</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Denúncias</h1>
          <p className="text-muted-foreground">
            {isAdminOuFiscal 
              ? "Gerencie e acompanhe todas as denúncias da plataforma" 
              : "Acompanhe suas denúncias"}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/dashboard">
            <Button variant="outline">
              Voltar ao Dashboard
            </Button>
          </Link>
          <Link href="/dashboard/denuncias/nova">
            <Button size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              Nova Denúncia
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.label}
                </CardTitle>
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

      <Card>
        <CardHeader>
          <CardTitle>Denúncias por Tipo de Equipamento</CardTitle>
          <CardDescription>
            Acesse rapidamente as denúncias específicas de cada equipamento público
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {[
              { slug: "calcada", nome: "Calçada", icon: "🚶" },
              { slug: "rua", nome: "Rua", icon: "🛣️" },
              { slug: "ciclovia", nome: "Ciclovia", icon: "🚴" },
              { slug: "semaforo", nome: "Semáforo", icon: "🚦" },
              { slug: "sinalizacao", nome: "Sinalização", icon: "🚧" },
              { slug: "iluminacao", nome: "Iluminação", icon: "💡" },
              { slug: "lixo", nome: "Lixo e Entulho", icon: "🗑️" },
              { slug: "poluicao", nome: "Poluição", icon: "🏭" },
              { slug: "barulho", nome: "Barulho", icon: "🔊" },
              { slug: "outros", nome: "Outros", icon: "📋" }
            ].map((equipamento) => (
              <Link 
                key={equipamento.slug}
                href={`/dashboard/denuncias/equipamentos/${equipamento.slug}`}
              >
                <Card className="hover:shadow-md hover:scale-105 transition-all cursor-pointer border-2 hover:border-primary/50">
                  <CardContent className="p-4 text-center">
                    <div className="text-3xl mb-2">{equipamento.icon}</div>
                    <div className="font-medium text-sm">{equipamento.nome}</div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Search and Filter */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Lista de Denúncias</CardTitle>
              <CardDescription>
                {isAdminOuFiscal 
                  ? "Visualize e gerencie todas as denúncias registradas" 
                  : "Visualize e gerencie suas denúncias"}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar denúncias..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline" size="icon" onClick={carregarDenuncias}>
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="todas" className="w-full" onValueChange={(value) => setStatusAtivo(value as "todas" | StatusDenuncia)}>
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="todas">
                Todas ({stats.total})
              </TabsTrigger>
              <TabsTrigger value="pendente">
                Pendentes ({stats.pendentes})
              </TabsTrigger>
              <TabsTrigger value="em_analise">
                Em Análise ({stats.em_analise})
              </TabsTrigger>
              <TabsTrigger value="em_fiscalizacao">
                Fiscalização ({stats.em_fiscalizacao})
              </TabsTrigger>
              <TabsTrigger value="concluida">
                Concluídas ({stats.concluidas})
              </TabsTrigger>
              <TabsTrigger value="arquivada">
                Arquivadas ({stats.arquivadas})
              </TabsTrigger>
            </TabsList>

            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin mx-auto h-12 w-12 border-4 border-primary border-t-transparent rounded-full mb-4" />
                <p className="text-sm text-muted-foreground">Carregando denúncias...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Erro ao carregar denúncias</h3>
                <p className="text-sm text-muted-foreground mb-4">{error}</p>
                <Button onClick={carregarDenuncias}>Tentar Novamente</Button>
              </div>
            ) : denunciasFiltradas.length === 0 ? (
              <div className="text-center py-12 mt-6">
                <AlertCircle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Nenhuma denúncia encontrada</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {searchQuery 
                    ? "Tente ajustar os filtros de busca" 
                    : "Comece criando sua primeira denúncia"}
                </p>
                {!searchQuery && (
                  <Link href="/dashboard/denuncias/nova">
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Criar Denúncia
                    </Button>
                  </Link>
                )}
              </div>
            ) : (
              <div className="mt-6 space-y-4">
                {denunciasFiltradas.map((denuncia) => (
                  <Card key={denuncia.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                        <div className="flex-1 space-y-3">
                          <div className="flex items-start gap-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline" className={statusColors[denuncia.status]}>
                                  {statusLabels[denuncia.status]}
                                </Badge>
                                <Badge variant="outline" className={prioridadeColors[denuncia.prioridade]}>
                                  {denuncia.prioridade.charAt(0).toUpperCase() + denuncia.prioridade.slice(1)}
                                </Badge>
                                <span className="text-sm text-muted-foreground">
                                  {categoriasLabels[denuncia.categoria]}
                                </span>
                              </div>
                              <p className="text-sm text-foreground mb-2">
                                {denuncia.observacao}
                              </p>
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <MapPin className="h-4 w-4" />
                                <span>
                                  {denuncia.endereco.logradouro}
                                  {denuncia.endereco.numero && `, ${denuncia.endereco.numero}`}
                                  {" - "}
                                  {denuncia.endereco.bairro}, {denuncia.endereco.cidade}/{denuncia.endereco.estado}
                                </span>
                              </div>
                              <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                                <Calendar className="h-4 w-4" />
                                <span>
                                  Criada em {format(new Date(denuncia.created_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                                </span>
                              </div>
                              {isAdminOuFiscal && (
                                <div className="text-sm text-muted-foreground mt-1">
                                  Denunciante: {denuncia.usuario.nome} ({denuncia.usuario.email})
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Link href={`/dashboard/denuncias/${denuncia.id}`}>
                            <Button variant="outline" size="sm">
                              Ver Detalhes
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </Tabs>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/dashboard/denuncias/mapa">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-blue-50 group-hover:bg-blue-100 transition-colors">
                  <MapPin className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Mapa de Denúncias</CardTitle>
                  <CardDescription>
                    Visualize todas as denúncias no mapa
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/denuncias/relatorio">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-purple-50 group-hover:bg-purple-100 transition-colors">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Relatórios</CardTitle>
                  <CardDescription>
                    Gere relatórios e análises
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/denuncias/estatisticas">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-green-50 group-hover:bg-green-100 transition-colors">
                  <AlertCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Estatísticas</CardTitle>
                  <CardDescription>
                    Análise detalhada de dados
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>
      </div>
      
    </div>
  );
}
