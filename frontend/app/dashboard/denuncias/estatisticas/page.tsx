"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Home, ChevronRight, BarChart3, Loader2, AlertCircle, TrendingUp, TrendingDown, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { servicoDenuncias, DenunciaResposta } from "@/services/denuncias";
import { useMetadata } from "@/hooks/useMetadata";
import { toast } from "sonner";

export default function EstatisticasDenunciasPage() {
  const router = useRouter();
  const {
    getStatusLabel,
    getCategoriaLabel,
    loading: metadataLoading,
  } = useMetadata();

  const [denuncias, setDenuncias] = useState<DenunciaResposta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Carregar denúncias
  const carregarDenuncias = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await servicoDenuncias.listar({ todas: true });
      setDenuncias(response.data);
    } catch (err) {
      console.error("Erro ao carregar denúncias:", err);
      setError("Erro ao carregar estatísticas");
      toast.error("Erro ao carregar denúncias");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDenuncias();
  }, []);

  // Cálculos de estatísticas
  const porCategoria: Record<string, number> = {};
  const porCidade: Record<string, number> = {};

  const estatisticas = {
    total: denuncias.length,
    por_status: {
      pendente: denuncias.filter(d => d.status === "pendente").length,
      em_analise: denuncias.filter(d => d.status === "em_analise").length,
      em_fiscalizacao: denuncias.filter(d => d.status === "em_fiscalizacao").length,
      concluida: denuncias.filter(d => d.status === "concluida").length,
      arquivada: denuncias.filter(d => d.status === "arquivada").length,
      cancelada: denuncias.filter(d => d.status === "cancelada").length,
    },
    por_prioridade: {
      baixa: denuncias.filter(d => d.prioridade === "baixa").length,
      media: denuncias.filter(d => d.prioridade === "media").length,
      alta: denuncias.filter(d => d.prioridade === "alta").length,
      urgente: denuncias.filter(d => d.prioridade === "urgente").length,
    },
    por_categoria: porCategoria,
    por_cidade: porCidade,
  };

  // Agrupar por categoria
  denuncias.forEach((d) => {
    const cat = getCategoriaLabel(d.categoria);
    estatisticas.por_categoria[cat] = (estatisticas.por_categoria[cat] || 0) + 1;
  });

  // Agrupar por cidade
  denuncias.forEach((d) => {
    const cidade = d.endereco.cidade;
    estatisticas.por_cidade[cidade] = (estatisticas.por_cidade[cidade] || 0) + 1;
  });

  // Top 5 categorias
  const topCategorias = Object.entries(estatisticas.por_categoria)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  // Top 5 cidades
  const topCidades = Object.entries(estatisticas.por_cidade)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  // Taxa de conclusão
  const taxaConclusao = estatisticas.total > 0
    ? ((estatisticas.por_status.concluida / estatisticas.total) * 100).toFixed(1)
    : "0.0";

  // Taxa de resolução (concluídas + arquivadas)
  const taxaResolucao = estatisticas.total > 0
    ? (((estatisticas.por_status.concluida + estatisticas.por_status.arquivada) / estatisticas.total) * 100).toFixed(1)
    : "0.0";

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
        <span className="text-foreground font-medium">Estatísticas</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Estatísticas de Denúncias</h1>
          <p className="text-muted-foreground">
            Análise detalhada e indicadores de desempenho
          </p>
        </div>
        <Button variant="outline" onClick={carregarDenuncias} disabled={loading}>
          <BarChart3 className="h-4 w-4 mr-2" />
          Atualizar
        </Button>
      </div>

      {loading || metadataLoading ? (
        <div className="flex items-center justify-center py-24">
          <div className="text-center">
            <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-sm text-muted-foreground">Carregando estatísticas...</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-24">
          <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Erro ao carregar estatísticas</h3>
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <Button onClick={carregarDenuncias}>Tentar Novamente</Button>
        </div>
      ) : (
        <>
          {/* KPIs Principais */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center justify-between">
                  Total de Denúncias
                  <Activity className="h-4 w-4" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">{estatisticas.total}</div>
                <p className="text-xs text-muted-foreground mt-1">Registradas no sistema</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center justify-between">
                  Taxa de Conclusão
                  <TrendingUp className="h-4 w-4 text-green-600" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">{taxaConclusao}%</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {estatisticas.por_status.concluida} denúncias concluídas
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center justify-between">
                  Taxa de Resolução
                  <TrendingUp className="h-4 w-4 text-blue-600" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">{taxaResolucao}%</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Concluídas + Arquivadas
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center justify-between">
                  Em Aberto
                  <TrendingDown className="h-4 w-4 text-orange-600" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">
                  {estatisticas.por_status.pendente + estatisticas.por_status.em_analise + estatisticas.por_status.em_fiscalizacao}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Aguardando resolução</p>
              </CardContent>
            </Card>
          </div>

          {/* Distribuição por Status */}
          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Status</CardTitle>
              <CardDescription>Quantidade de denúncias em cada status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {Object.entries(estatisticas.por_status).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium capitalize">{getStatusLabel(status)}</p>
                      <p className="text-2xl font-bold">{count}</p>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {estatisticas.total > 0 ? ((count / estatisticas.total) * 100).toFixed(1) : "0.0"}%
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Distribuição por Prioridade */}
          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Prioridade</CardTitle>
              <CardDescription>Classificação de urgência das denúncias</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {Object.entries(estatisticas.por_prioridade).map(([prioridade, count]) => {
                  const colors = {
                    baixa: "text-green-600 border-green-200",
                    media: "text-yellow-600 border-yellow-200",
                    alta: "text-orange-600 border-orange-200",
                    urgente: "text-red-600 border-red-200",
                  };
                  const color = colors[prioridade as keyof typeof colors] || "text-gray-600 border-gray-200";

                  return (
                    <div key={prioridade} className={`flex flex-col p-4 border-2 rounded-lg ${color}`}>
                      <p className="font-medium capitalize text-sm">{prioridade}</p>
                      <p className="text-3xl font-bold mt-2">{count}</p>
                      <p className="text-xs mt-1">
                        {estatisticas.total > 0 ? ((count / estatisticas.total) * 100).toFixed(1) : "0.0"}% do total
                      </p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Top Categorias */}
            <Card>
              <CardHeader>
                <CardTitle>Top 5 Categorias</CardTitle>
                <CardDescription>Categorias com mais denúncias</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {topCategorias.length > 0 ? (
                    topCategorias.map(([categoria, count], index) => (
                      <div key={categoria} className="flex items-center gap-4">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-medium">{categoria}</p>
                            <Badge variant="secondary">{count}</Badge>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary rounded-full"
                              style={{ width: `${(count / estatisticas.total) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      Nenhuma categoria encontrada
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Top Cidades */}
            <Card>
              <CardHeader>
                <CardTitle>Top 5 Cidades</CardTitle>
                <CardDescription>Cidades com mais denúncias</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {topCidades.length > 0 ? (
                    topCidades.map(([cidade, count], index) => (
                      <div key={cidade} className="flex items-center gap-4">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-secondary/10 text-secondary-foreground font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-medium">{cidade}</p>
                            <Badge variant="secondary">{count}</Badge>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-secondary rounded-full"
                              style={{ width: `${(count / estatisticas.total) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      Nenhuma cidade encontrada
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
