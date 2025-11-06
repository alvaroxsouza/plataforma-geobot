"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, ClipboardCheck, Calendar, Users, MapPin, Home, ChevronRight, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

import { fiscalizacaoService, FiscalizacaoResponse, FiscalizacaoStatus, STATUS_LABELS } from "@/services/fiscalizacao";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface FiscalizacaoStats {
  total: number;
  aguardando_sobrevoo: number;
  aguardando_inferencia: number;
  gerando_relatorio: number;
  concluida: number;
  cancelada: number;
}

const statusColors: Record<FiscalizacaoStatus, string> = {
  AGUARDANDO_SOBREVOO: "bg-yellow-100 text-yellow-800 border-yellow-200",
  AGUARDANDO_INFERENCIA: "bg-blue-100 text-blue-800 border-blue-200",
  GERANDO_RELATORIO: "bg-purple-100 text-purple-800 border-purple-200",
  CONCLUIDA: "bg-green-100 text-green-800 border-green-200",
  CANCELADA: "bg-red-100 text-red-800 border-red-200",
};

export default function FiscalizacaoPage() {

  const [searchQuery, setSearchQuery] = useState("");
  const [fiscalizacoes, setFiscalizacoes] = useState<FiscalizacaoResponse[]>([]);
  const [fiscalizacoesFiltradas, setFiscalizacoesFiltradas] = useState<FiscalizacaoResponse[]>([]);
  const [stats, setStats] = useState<FiscalizacaoStats>({
    total: 0,
    aguardando_sobrevoo: 0,
    aguardando_inferencia: 0,
    gerando_relatorio: 0,
    concluida: 0,
    cancelada: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusAtivo, setStatusAtivo] = useState<"todas" | FiscalizacaoStatus>("todas");

  // Verificar se usuário é admin ou fiscal - será validado no backend
  const [isAdminOuFiscal, setIsAdminOuFiscal] = useState(true);

  const carregarFiscalizacoes = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fiscalizacaoService.getAll();
      setFiscalizacoes(response);
      calcularEstatisticas(response);
      setIsAdminOuFiscal(true);
    } catch (err) {
      console.error("Erro ao carregar fiscalizações:", err);
      // Se for erro 403, é porque não tem permissão
      const error = err as { response?: { status?: number }; message?: string };
      if (error?.response?.status === 403 || error?.message?.includes("403")) {
        setError("Você não tem permissão para acessar fiscalizações.");
        setIsAdminOuFiscal(false);
      } else {
        setError("Não foi possível carregar as fiscalizações. Tente novamente.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const calcularEstatisticas = (fiscalizacoesData: FiscalizacaoResponse[]) => {
    const stats: FiscalizacaoStats = {
      total: fiscalizacoesData.length,
      aguardando_sobrevoo: fiscalizacoesData.filter(f => f.status_fiscalizacao === "AGUARDANDO_SOBREVOO").length,
      aguardando_inferencia: fiscalizacoesData.filter(f => f.status_fiscalizacao === "AGUARDANDO_INFERENCIA").length,
      gerando_relatorio: fiscalizacoesData.filter(f => f.status_fiscalizacao === "GERANDO_RELATORIO").length,
      concluida: fiscalizacoesData.filter(f => f.status_fiscalizacao === "CONCLUIDA").length,
      cancelada: fiscalizacoesData.filter(f => f.status_fiscalizacao === "CANCELADA").length,
    };
    setStats(stats);
  };

  useEffect(() => {
    carregarFiscalizacoes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let filtered = fiscalizacoes;

    // Filtrar por status
    if (statusAtivo !== "todas") {
      filtered = filtered.filter(f => f.status_fiscalizacao === statusAtivo);
    }

    // Filtrar por busca
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(f => 
        f.id.toString().includes(query) ||
        f.complaint_id.toString().includes(query)
      );
    }

    setFiscalizacoesFiltradas(filtered);
  }, [fiscalizacoes, statusAtivo, searchQuery]);

  const statsCards = [
    { 
      label: "Total de Fiscalizações", 
      value: stats.total,
      icon: ClipboardCheck,
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    { 
      label: "Aguardando Sobrevoo", 
      value: stats.aguardando_sobrevoo,
      icon: Calendar,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50"
    },
    { 
      label: "Em Processamento", 
      value: stats.aguardando_inferencia + stats.gerando_relatorio,
      icon: Users,
      color: "text-orange-600",
      bgColor: "bg-orange-50"
    },
    { 
      label: "Concluídas", 
      value: stats.concluida,
      icon: ClipboardCheck,
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
        <span className="text-foreground font-medium">Fiscalização</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Fiscalização</h1>
          <p className="text-muted-foreground">
            Gerencie vistorias, inspeções e fiscalizações de campo
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/dashboard">
            <Button variant="outline">
              Voltar ao Dashboard
            </Button>
          </Link>
          <Link href="/dashboard/fiscalizacao/nova">
            <Button size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              Nova Fiscalização
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

      {/* Search and Filter */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Lista de Fiscalizações</CardTitle>
              <CardDescription>
                {isAdminOuFiscal 
                  ? "Acompanhe todas as fiscalizações e vistorias" 
                  : "Acesso restrito a administradores e fiscais"}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar fiscalizações..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                  disabled={!isAdminOuFiscal}
                />
              </div>
              <Button variant="outline" size="icon" onClick={carregarFiscalizacoes} disabled={!isAdminOuFiscal}>
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="todas" className="w-full" onValueChange={(value) => setStatusAtivo(value as "todas" | FiscalizacaoStatus)}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="todas">
                Todas ({stats.total})
              </TabsTrigger>
              <TabsTrigger value="AGUARDANDO_SOBREVOO">
                Sobrevoo ({stats.aguardando_sobrevoo})
              </TabsTrigger>
              <TabsTrigger value="AGUARDANDO_INFERENCIA">
                Inferência ({stats.aguardando_inferencia})
              </TabsTrigger>
              <TabsTrigger value="GERANDO_RELATORIO">
                Relatório ({stats.gerando_relatorio})
              </TabsTrigger>
              <TabsTrigger value="CONCLUIDA">
                Concluídas ({stats.concluida})
              </TabsTrigger>
            </TabsList>

            {!isAdminOuFiscal ? (
              <div className="text-center py-12 mt-6">
                <ClipboardCheck className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Acesso Restrito</h3>
                <p className="text-sm text-muted-foreground">
                  Apenas administradores e fiscais podem acessar as fiscalizações.
                </p>
              </div>
            ) : isLoading ? (
              <div className="text-center py-12 mt-6">
                <div className="animate-spin mx-auto h-12 w-12 border-4 border-primary border-t-transparent rounded-full mb-4" />
                <p className="text-sm text-muted-foreground">Carregando fiscalizações...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12 mt-6">
                <ClipboardCheck className="mx-auto h-12 w-12 text-red-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Erro ao carregar fiscalizações</h3>
                <p className="text-sm text-muted-foreground mb-4">{error}</p>
                <Button onClick={carregarFiscalizacoes}>Tentar Novamente</Button>
              </div>
            ) : fiscalizacoesFiltradas.length === 0 ? (
              <div className="text-center py-12 mt-6">
                <ClipboardCheck className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Nenhuma fiscalização encontrada</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {searchQuery 
                    ? "Tente ajustar os filtros de busca" 
                    : "Comece criando uma nova fiscalização"}
                </p>
                {!searchQuery && (
                  <Link href="/dashboard/gerenciar-denuncias">
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Ir para Denúncias
                    </Button>
                  </Link>
                )}
              </div>
            ) : (
              <div className="mt-6 space-y-4">
                {fiscalizacoesFiltradas.map((fiscalizacao) => (
                  <Card key={fiscalizacao.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                        <div className="flex-1 space-y-3">
                          <div className="flex items-start gap-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline" className={statusColors[fiscalizacao.status_fiscalizacao]}>
                                  {STATUS_LABELS[fiscalizacao.status_fiscalizacao]}
                                </Badge>
                                <span className="text-sm text-muted-foreground">
                                  Fiscalização #{fiscalizacao.id}
                                </span>
                              </div>
                              <p className="text-sm text-foreground mb-2">
                                Denúncia: #{fiscalizacao.complaint_id}
                              </p>
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <Calendar className="h-4 w-4" />
                                <span>
                                  Criada em {format(new Date(fiscalizacao.data_criacao), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                                </span>
                              </div>
                              {fiscalizacao.data_conclusao_prevista && (
                                <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                                  <Calendar className="h-4 w-4" />
                                  <span>
                                    Previsão de conclusão: {format(new Date(fiscalizacao.data_conclusao_prevista), "dd/MM/yyyy", { locale: ptBR })}
                                  </span>
                                </div>
                              )}
                              {fiscalizacao.data_conclusao_efetiva && (
                                <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                                  <Calendar className="h-4 w-4" />
                                  <span>
                                    Concluída em: {format(new Date(fiscalizacao.data_conclusao_efetiva), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Link href={`/dashboard/fiscalizacao/${fiscalizacao.id}`}>
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
        <Link href="/dashboard/fiscalizacao/calendario">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-purple-50 group-hover:bg-purple-100 transition-colors">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Calendário</CardTitle>
                  <CardDescription>
                    Visualize as fiscalizações agendadas
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/fiscalizacao/equipes">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-blue-50 group-hover:bg-blue-100 transition-colors">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Equipes</CardTitle>
                  <CardDescription>
                    Gerencie as equipes de fiscalização
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/fiscalizacao/mapa">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-green-50 group-hover:bg-green-100 transition-colors">
                  <MapPin className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Mapa de Ações</CardTitle>
                  <CardDescription>
                    Visualize as fiscalizações no mapa
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>
      </div>

      {/* Types of Fiscalização */}
      <Card>
        <CardHeader>
          <CardTitle>Tipos de Fiscalização</CardTitle>
          <CardDescription>
            Selecione o tipo de fiscalização que deseja realizar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {[
              { title: "Vistoria", icon: ClipboardCheck, color: "blue" },
              { title: "Inspeção", icon: Search, color: "purple" },
              { title: "Rotina", icon: Calendar, color: "green" },
              { title: "Atend. Denúncia", icon: MapPin, color: "orange" },
              { title: "Reincidência", icon: Users, color: "red" },
            ].map((type, index) => {
              const Icon = type.icon;
              return (
                <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader className="text-center">
                    <div className={`mx-auto p-3 rounded-lg bg-${type.color}-50 mb-2`}>
                      <Icon className={`h-6 w-6 text-${type.color}-600`} />
                    </div>
                    <CardTitle className="text-sm">{type.title}</CardTitle>
                  </CardHeader>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
