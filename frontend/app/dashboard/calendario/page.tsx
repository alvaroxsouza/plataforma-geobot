"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Home, ChevronRight, Calendar as CalendarIcon, Users, Clock, RefreshCw, Filter, ChevronLeft, ChevronRight as ChevronRightIcon } from "lucide-react";
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
import { toast } from "sonner";
import { fiscalizacaoService, FiscalizacaoResponse } from "@/services/fiscalizacao";
import { usuarioService, Usuario } from "@/services/usuarios";
import CalendarioFiscalizacoes from "@/components/dashboard/CalendarioFiscalizacoes";

export default function CalendarioPage() {
  const router = useRouter();

  const [fiscalizacoes, setFiscalizacoes] = useState<FiscalizacaoResponse[]>([]);
  const [fiscais, setFiscais] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroFiscal, setFiltroFiscal] = useState<string>("todos");
  const [filtroStatus, setFiltroStatus] = useState<string>("todos");

  // Carregar dados
  const carregarDados = useCallback(async () => {
    try {
      setLoading(true);

      // Carregar fiscalizações
      const fiscalizacoesData = await fiscalizacaoService.getAll({
        limit: 1000,
      });

      // Carregar lista de fiscais
      const fiscaisData = await usuarioService.listarFiscais();

      setFiscalizacoes(fiscalizacoesData);
      setFiscais(fiscaisData);
      toast.success(`${fiscalizacoesData.length} fiscalização(ões) carregada(s)`);
    } catch (err) {
      console.error("Erro ao carregar dados:", err);
      toast.error("Erro ao carregar dados do calendário");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  // Aplicar filtros
  const fiscalizacoesFiltradas = fiscalizacoes.filter((f) => {
    // Filtro por fiscal: verificar se o fiscal está na lista de fiscais atribuídos
    if (filtroFiscal !== "todos") {
      const fiscalIdNumber = parseInt(filtroFiscal);
      const temFiscal = f.fiscais?.some(fiscal => fiscal.id === fiscalIdNumber);
      if (!temFiscal) {
        return false;
      }
    }
    if (filtroStatus !== "todos" && f.status_fiscalizacao !== filtroStatus) {
      return false;
    }
    return true;
  });

  // Estatísticas
  const stats = [
    {
      label: "Total",
      value: fiscalizacoesFiltradas.length,
      icon: CalendarIcon,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      label: "Aguardando Sobrevoo",
      value: fiscalizacoesFiltradas.filter((f) => f.status_fiscalizacao === "AGUARDANDO_SOBREVOO").length,
      icon: Clock,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
    },
    {
      label: "Em Andamento",
      value: fiscalizacoesFiltradas.filter(
        (f) => f.status_fiscalizacao === "AGUARDANDO_INFERENCIA" || f.status_fiscalizacao === "GERANDO_RELATORIO"
      ).length,
      icon: Clock,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      label: "Concluídas",
      value: fiscalizacoesFiltradas.filter((f) => f.status_fiscalizacao === "CONCLUIDA").length,
      icon: CalendarIcon,
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
        <span className="text-foreground font-medium">Calendário de Fiscalizações</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Calendário de Fiscalizações</h1>
          <p className="text-muted-foreground">
            Visualize e gerencie os prazos de fiscalização
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={carregarDados} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Link href="/dashboard/fiscalizacao">
            <Button variant="outline">Ver Lista</Button>
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
            Filtros do Calendário
          </CardTitle>
          <CardDescription>Filtre as fiscalizações exibidas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">Fiscal Responsável</label>
              <Select value={filtroFiscal} onValueChange={setFiltroFiscal}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os fiscais" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os Fiscais</SelectItem>
                  {fiscais.map((fiscal) => (
                    <SelectItem key={fiscal.id} value={fiscal.id.toString()}>
                      {fiscal.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <Select value={filtroStatus} onValueChange={setFiltroStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os Status</SelectItem>
                  <SelectItem value="AGUARDANDO_SOBREVOO">Aguardando Sobrevoo</SelectItem>
                  <SelectItem value="AGUARDANDO_INFERENCIA">Aguardando Inferência</SelectItem>
                  <SelectItem value="GERANDO_RELATORIO">Gerando Relatório</SelectItem>
                  <SelectItem value="CONCLUIDA">Concluída</SelectItem>
                  <SelectItem value="CANCELADA">Cancelada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Legenda</label>
              <div className="flex flex-wrap gap-2">
                <Badge className="bg-yellow-500 hover:bg-yellow-600">Sobrevoo</Badge>
                <Badge className="bg-purple-500 hover:bg-purple-600">Processando</Badge>
                <Badge className="bg-green-500 hover:bg-green-600">Concluída</Badge>
                <Badge className="bg-red-500 hover:bg-red-600">Atrasada</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calendário */}
      <Card>
        <CardHeader>
          <CardTitle>Calendário Interativo</CardTitle>
          <CardDescription>
            Clique nos eventos para ver detalhes e gerenciar fiscalizações
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-[600px] bg-muted/20 rounded-lg">
              <div className="text-center">
                <Clock className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                <p className="text-sm text-muted-foreground">Carregando fiscalizações...</p>
              </div>
            </div>
          ) : (
            <CalendarioFiscalizacoes
              fiscalizacoes={fiscalizacoesFiltradas}
              onEventClick={(fiscalizacao: FiscalizacaoResponse) => {
                router.push(`/dashboard/fiscalizacao/${fiscalizacao.id}/etapas`);
              }}
            />
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
        <CardContent className="pt-6">
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-primary/20 rounded-lg">
              <Users className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Gestão de Equipes</h3>
              <p className="text-sm text-muted-foreground">
                Este calendário mostra todas as fiscalizações e seus prazos de conclusão previstos.
                As cores indicam o status atual. Fiscalizações atrasadas aparecem em vermelho.
                Clique em um evento para acessar os detalhes e gerenciar o pipeline de trabalho.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
