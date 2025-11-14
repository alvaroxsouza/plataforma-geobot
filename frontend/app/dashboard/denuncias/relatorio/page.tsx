"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Home, ChevronRight, Download, FileText, Loader2, AlertCircle, Calendar, Filter } from "lucide-react";
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
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function RelatorioDenunciasPage() {
  const router = useRouter();
  const {
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    loading: metadataLoading,
  } = useMetadata();

  const [denuncias, setDenuncias] = useState<DenunciaResposta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtroStatus, setFiltroStatus] = useState<StatusDenuncia | "todas">("todas");
  const [filtroCategoria, setFiltroCategoria] = useState<string>("todas");
  const [dataInicio, setDataInicio] = useState<string>("");
  const [dataFim, setDataFim] = useState<string>("");

  // Carregar denúncias
  const carregarDenuncias = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await servicoDenuncias.listar({ todas: true });
      setDenuncias(response.data);
    } catch (err) {
      console.error("Erro ao carregar denúncias:", err);
      setError("Erro ao carregar dados para o relatório");
      toast.error("Erro ao carregar denúncias");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDenuncias();
  }, []);

  // Aplicar filtros
  const denunciasFiltradas = denuncias.filter((d) => {
    if (filtroStatus !== "todas" && d.status !== filtroStatus) return false;
    if (filtroCategoria !== "todas" && d.categoria !== filtroCategoria) return false;
    
    if (dataInicio) {
      const dataCriacao = new Date(d.created_at);
      const dataInicioFiltro = new Date(dataInicio);
      if (dataCriacao < dataInicioFiltro) return false;
    }
    
    if (dataFim) {
      const dataCriacao = new Date(d.created_at);
      const dataFimFiltro = new Date(dataFim);
      dataFimFiltro.setHours(23, 59, 59, 999);
      if (dataCriacao > dataFimFiltro) return false;
    }
    
    return true;
  });

  // Estatísticas
  const stats = {
    total: denunciasFiltradas.length,
    pendentes: denunciasFiltradas.filter(d => d.status === "pendente").length,
    em_analise: denunciasFiltradas.filter(d => d.status === "em_analise").length,
    em_fiscalizacao: denunciasFiltradas.filter(d => d.status === "em_fiscalizacao").length,
    concluidas: denunciasFiltradas.filter(d => d.status === "concluida").length,
    arquivadas: denunciasFiltradas.filter(d => d.status === "arquivada").length,
  };

  // Categorias únicas
  const categorias = Array.from(new Set(denuncias.map(d => d.categoria)));

  const exportarCSV = () => {
    const headers = ["ID", "UUID", "Categoria", "Status", "Prioridade", "Data Criação", "Endereço", "Cidade"];
    const rows = denunciasFiltradas.map(d => [
      d.id,
      d.uuid,
      d.categoria,
      d.status,
      d.prioridade,
      format(new Date(d.created_at), "dd/MM/yyyy HH:mm", { locale: ptBR }),
      `${d.endereco.logradouro}${d.endereco.numero ? `, ${d.endereco.numero}` : ""}`,
      `${d.endereco.cidade}/${d.endereco.estado}`
    ]);

    const csv = [headers, ...rows].map(row => row.join(";")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `relatorio_denuncias_${format(new Date(), "yyyy-MM-dd")}.csv`;
    link.click();
    toast.success("Relatório exportado com sucesso!");
  };

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
        <span className="text-foreground font-medium">Relatórios</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Relatórios de Denúncias</h1>
          <p className="text-muted-foreground">
            Gere e exporte relatórios personalizados
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={carregarDenuncias} disabled={loading}>
            <FileText className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button onClick={exportarCSV} disabled={denunciasFiltradas.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Exportar CSV
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="mr-2 h-5 w-5" />
            Filtros do Relatório
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <Select value={filtroStatus} onValueChange={(value) => setFiltroStatus(value as StatusDenuncia | "todas")}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todas">Todos os status</SelectItem>
                  <SelectItem value="pendente">Pendente</SelectItem>
                  <SelectItem value="em_analise">Em Análise</SelectItem>
                  <SelectItem value="em_fiscalizacao">Em Fiscalização</SelectItem>
                  <SelectItem value="concluida">Concluída</SelectItem>
                  <SelectItem value="arquivada">Arquivada</SelectItem>
                  <SelectItem value="cancelada">Cancelada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Categoria</label>
              <Select value={filtroCategoria} onValueChange={setFiltroCategoria}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas as categorias" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todas">Todas as categorias</SelectItem>
                  {categorias.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {getCategoriaLabel(cat)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Data Início</label>
              <input
                type="date"
                value={dataInicio}
                onChange={(e) => setDataInicio(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Data Fim</label>
              <input
                type="date"
                value={dataFim}
                onChange={(e) => setDataFim(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Denúncias
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pendentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-600">{stats.pendentes}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Em Análise
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">{stats.em_analise}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Em Fiscalização
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">{stats.em_fiscalizacao}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Concluídas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{stats.concluidas}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Arquivadas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-600">{stats.arquivadas}</div>
          </CardContent>
        </Card>
      </div>

      {/* Conteúdo */}
      <Card>
        <CardHeader>
          <CardTitle>Dados do Relatório</CardTitle>
          <CardDescription>
            {denunciasFiltradas.length} registro(s) no relatório
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading || metadataLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                <p className="text-sm text-muted-foreground">Carregando dados...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Erro ao carregar dados</h3>
              <p className="text-sm text-muted-foreground mb-4">{error}</p>
              <Button onClick={carregarDenuncias}>Tentar Novamente</Button>
            </div>
          ) : denunciasFiltradas.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Nenhuma denúncia encontrada com os filtros aplicados</p>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Use o botão "Exportar CSV" no topo da página para gerar o arquivo de dados.
              </p>
              <div className="text-sm">
                <strong>Resumo:</strong> O relatório contém {denunciasFiltradas.length} denúncia(s) 
                {dataInicio && ` desde ${format(new Date(dataInicio), "dd/MM/yyyy", { locale: ptBR })}`}
                {dataFim && ` até ${format(new Date(dataFim), "dd/MM/yyyy", { locale: ptBR })}`}.
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
