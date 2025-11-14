"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, MapPin, Calendar, AlertCircle, Home, ChevronRight, Loader2, Eye, Map } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import Link from "next/link";

import { servicoDenuncias, DenunciaResposta, StatusDenuncia } from "@/services/denuncias";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { useMetadata } from "@/hooks/useMetadata";

interface DenunciaStats {
  total: number;
  pendentes: number;
  em_analise: number;
  em_fiscalizacao: number;
  concluidas: number;
  arquivadas: number;
  canceladas: number;
}

export default function DenunciasPage() {
  // Metadados do sistema
  const {
    status: statusOptions,
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    getCategoriaIcone,
    getPrioridadeLabel,
    getPrioridadeColor,
    loading: metadataLoading,
  } = useMetadata();

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
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");
  
  // Paginação
  const [paginaAtual, setPaginaAtual] = useState(1);
  const [itensPorPagina] = useState(20);
  const [totalItens, setTotalItens] = useState(0);

  // Verificar se usuário é admin ou fiscal - será validado no backend
  // Por ora, assumimos que todos podem tentar carregar, mas o backend restringirá
  const [isAdminOuFiscal, setIsAdminOuFiscal] = useState(false);

  const carregarDenuncias = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const offset = (paginaAtual - 1) * itensPorPagina;
      
      // Tentar carregar todas as denúncias primeiro (admin/fiscal)
      try {
        const responseAll = await servicoDenuncias.listar({ 
          todas: true,
          limit: itensPorPagina,
          offset: offset
        });
        setDenuncias(responseAll.data);
        setTotalItens(responseAll.pagination.total);
        calcularEstatisticas(responseAll.data);
        setIsAdminOuFiscal(true);
      } catch {
        // Se falhar, carregar apenas as do usuário (cidadão)
        const responseMy = await servicoDenuncias.listar({ 
          todas: false,
          limit: itensPorPagina,
          offset: offset
        });
        setDenuncias(responseMy.data);
        setTotalItens(responseMy.pagination.total);
        calcularEstatisticas(responseMy.data);
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
  }, [paginaAtual]);

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
        getCategoriaLabel(d.categoria).toLowerCase().includes(query)
      );
    }

    setDenunciasFiltradas(filtered);
  }, [denuncias, statusAtivo, searchQuery, getCategoriaLabel]);

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
          <Link href="/dashboard/denuncias/mapa">
            <Button variant="outline" className="gap-2">
              <Map className="h-4 w-4" />
              Ver Mapa
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
        <CardHeader className="pb-3">
          <CardTitle>Denúncias por Tipo de Equipamento</CardTitle>
          <CardDescription>
            Acesse rapidamente as denúncias específicas de cada equipamento público
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {[
              { slug: "calcada", nome: "Calçada", icon: "🚶" },
              { slug: "rua", nome: "Rua", icon: "🛣️" },
              { slug: "ciclovia", nome: "Ciclovia", icon: "🚴" },
              { slug: "semaforo", nome: "Semáforo", icon: "🚦" },
              { slug: "sinalizacao", nome: "Sinalização", icon: "🚧" }
            ].map((equipamento) => (
              <Link 
                key={equipamento.slug}
                href={`/dashboard/denuncias/equipamentos/${equipamento.slug}`}
                className="block"
              >
                <Card className="h-full hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer border-2 hover:border-primary/50 group">
                  <CardContent className="p-6 flex flex-col items-center justify-center text-center h-full min-h-[120px]">
                    <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">
                      {equipamento.icon}
                    </div>
                    <div className="font-semibold text-sm">{equipamento.nome}</div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
          
          <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 mt-4">
            {[
              { slug: "iluminacao", nome: "Iluminação", icon: "💡" },
              { slug: "lixo_entulho", nome: "Lixo e Entulho", icon: "🗑️" },
              { slug: "poluicao", nome: "Poluição", icon: "🏭" },
              { slug: "barulho", nome: "Barulho", icon: "🔊" },
              { slug: "outros", nome: "Outros", icon: "📋" }
            ].map((equipamento) => (
              <Link 
                key={equipamento.slug}
                href={`/dashboard/denuncias/equipamentos/${equipamento.slug}`}
                className="block"
              >
                <Card className="h-full hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer border-2 hover:border-primary/50 group">
                  <CardContent className="p-6 flex flex-col items-center justify-center text-center h-full min-h-[120px]">
                    <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">
                      {equipamento.icon}
                    </div>
                    <div className="font-semibold text-sm">{equipamento.nome}</div>
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
              <div className="flex gap-1 border rounded-md p-1">
                <Button 
                  variant={viewMode === "cards" ? "default" : "ghost"} 
                  size="sm"
                  onClick={() => setViewMode("cards")}
                  className="h-8"
                >
                  Cards
                </Button>
                <Button 
                  variant={viewMode === "table" ? "default" : "ghost"} 
                  size="sm"
                  onClick={() => setViewMode("table")}
                  className="h-8"
                >
                  Tabela
                </Button>
              </div>
              <Button variant="outline" size="icon" onClick={carregarDenuncias}>
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="todas" className="w-full" onValueChange={(value) => setStatusAtivo(value as "todas" | StatusDenuncia)}>
            <div className="overflow-x-auto pb-2">
              <TabsList className="inline-flex w-full min-w-max md:grid md:w-full md:grid-cols-6 h-auto gap-1">
                <TabsTrigger value="todas" className="whitespace-nowrap px-4 py-2">
                  Todas <span className="ml-1 font-bold">({stats.total})</span>
                </TabsTrigger>
                <TabsTrigger value="pendente" className="whitespace-nowrap px-4 py-2">
                  Pendentes <span className="ml-1 font-bold">({stats.pendentes})</span>
                </TabsTrigger>
                <TabsTrigger value="em_analise" className="whitespace-nowrap px-4 py-2">
                  Em Análise <span className="ml-1 font-bold">({stats.em_analise})</span>
                </TabsTrigger>
                <TabsTrigger value="em_fiscalizacao" className="whitespace-nowrap px-4 py-2">
                  Fiscalização <span className="ml-1 font-bold">({stats.em_fiscalizacao})</span>
                </TabsTrigger>
                <TabsTrigger value="concluida" className="whitespace-nowrap px-4 py-2">
                  Concluídas <span className="ml-1 font-bold">({stats.concluidas})</span>
                </TabsTrigger>
                <TabsTrigger value="arquivada" className="whitespace-nowrap px-4 py-2">
                  Arquivadas <span className="ml-1 font-bold">({stats.arquivadas})</span>
                </TabsTrigger>
              </TabsList>
            </div>

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
            ) : viewMode === "cards" ? (
              <div className="mt-6 space-y-4">
                {denunciasFiltradas.map((denuncia) => (
                  <Card key={denuncia.id} className="hover:shadow-lg transition-all hover:border-primary/50 group">
                    <CardContent className="p-6">
                      <div className="flex flex-col gap-4">
                        {/* Header com Badges e Categoria */}
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant="outline" className={`${getStatusColor(denuncia.status)} font-medium`}>
                            {getStatusLabel(denuncia.status)}
                          </Badge>
                          <Badge variant="outline" className={`${getPrioridadeColor(denuncia.prioridade)} font-medium`}>
                            Prioridade: {getPrioridadeLabel(denuncia.prioridade)}
                          </Badge>
                          <Badge variant="secondary" className="font-medium">
                            {getCategoriaLabel(denuncia.categoria)}
                          </Badge>
                        </div>

                        {/* Descrição */}
                        <div>
                          <h3 className="font-semibold text-base mb-2 text-foreground">
                            Descrição
                          </h3>
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {denuncia.observacao}
                          </p>
                        </div>

                        {/* Informações */}
                        <div className="grid gap-3 sm:grid-cols-2">
                          <div className="flex items-start gap-2">
                            <MapPin className="h-4 w-4 mt-0.5 text-primary flex-shrink-0" />
                            <div className="text-sm">
                              <p className="font-medium text-foreground">
                                {denuncia.endereco.logradouro}
                                {denuncia.endereco.numero && `, ${denuncia.endereco.numero}`}
                              </p>
                              <p className="text-muted-foreground">
                                {denuncia.endereco.bairro}, {denuncia.endereco.cidade}/{denuncia.endereco.estado}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-start gap-2">
                            <Calendar className="h-4 w-4 mt-0.5 text-primary flex-shrink-0" />
                            <div className="text-sm">
                              <p className="font-medium text-foreground">
                                {format(new Date(denuncia.created_at), "dd/MM/yyyy", { locale: ptBR })}
                              </p>
                              <p className="text-muted-foreground">
                                às {format(new Date(denuncia.created_at), "HH:mm", { locale: ptBR })}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Denunciante (Admin/Fiscal) */}
                        {isAdminOuFiscal && (
                          <div className="pt-3 border-t">
                            <p className="text-sm text-muted-foreground">
                              <span className="font-medium text-foreground">Denunciante:</span> {denuncia.usuario.nome} · {denuncia.usuario.email}
                            </p>
                          </div>
                        )}

                        {/* Botão de Ação */}
                        <div className="flex justify-end pt-2">
                          <Link href={`/dashboard/denuncias/${denuncia.id}`}>
                            <Button variant="default" size="sm" className="gap-2">
                              <Eye className="h-4 w-4" />
                              Ver Detalhes
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="mt-6">
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Categoria</TableHead>
                        <TableHead>Prioridade</TableHead>
                        <TableHead>Endereço</TableHead>
                        <TableHead>Data</TableHead>
                        {isAdminOuFiscal && <TableHead>Denunciante</TableHead>}
                        <TableHead className="text-right">Ações</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {denunciasFiltradas.map((denuncia) => (
                        <TableRow key={denuncia.id} className="hover:bg-muted/50">
                          <TableCell className="font-medium">#{denuncia.id}</TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(denuncia.status)}>
                              {getStatusLabel(denuncia.status)}
                            </Badge>
                          </TableCell>
                          <TableCell>{getCategoriaLabel(denuncia.categoria)}</TableCell>
                          <TableCell>
                            <Badge className={getPrioridadeColor(denuncia.prioridade)}>
                              {getPrioridadeLabel(denuncia.prioridade)}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="max-w-[200px]">
                              <div className="font-medium truncate">{denuncia.endereco.logradouro}</div>
                              <div className="text-sm text-muted-foreground truncate">
                                {denuncia.endereco.bairro}, {denuncia.endereco.cidade}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="text-sm">
                            {format(new Date(denuncia.created_at), "dd/MM/yyyy", { locale: ptBR })}
                          </TableCell>
                          {isAdminOuFiscal && (
                            <TableCell className="text-sm">{denuncia.usuario.nome}</TableCell>
                          )}
                          <TableCell className="text-right">
                            <Link href={`/dashboard/denuncias/${denuncia.id}`}>
                              <Button variant="ghost" size="sm">
                                <Eye className="h-4 w-4 mr-2" />
                                Ver
                              </Button>
                            </Link>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}
          </Tabs>
        </CardContent>
        
        {/* Controles de Paginação */}
        {!isLoading && Math.ceil(totalItens / itensPorPagina) > 1 && (
          <CardContent className="pt-0">
            <div className="flex items-center justify-between px-2 py-4 border-t">
              <div className="text-sm text-muted-foreground">
                Mostrando {((paginaAtual - 1) * itensPorPagina) + 1} a {Math.min(paginaAtual * itensPorPagina, totalItens)} de {totalItens} denúncias
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginaAtual(prev => Math.max(1, prev - 1))}
                  disabled={paginaAtual === 1}
                >
                  Anterior
                </Button>
                <div className="flex items-center gap-2 px-3">
                  <span className="text-sm">
                    Página {paginaAtual} de {Math.ceil(totalItens / itensPorPagina)}
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginaAtual(prev => Math.min(Math.ceil(totalItens / itensPorPagina), prev + 1))}
                  disabled={paginaAtual >= Math.ceil(totalItens / itensPorPagina)}
                >
                  Próxima
                </Button>
              </div>
            </div>
          </CardContent>
        )}
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
