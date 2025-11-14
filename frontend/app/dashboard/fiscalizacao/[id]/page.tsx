"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Home, ChevronRight, Loader2, AlertCircle, Calendar, MapPin, User, FileText, Clock, Eye, CheckCircle2, ArrowRight, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import Link from "next/link";
import { fiscalizacaoService, FiscalizacaoResponse } from "@/services/fiscalizacao";
import { toast } from "sonner";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function VisualizarFiscalizacaoPage() {
  const router = useRouter();
  const params = useParams();
  const fiscalizacaoId = parseInt(params.id as string);

  const [fiscalizacao, setFiscalizacao] = useState<FiscalizacaoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Carregar fiscalização
  useEffect(() => {
    const carregarFiscalizacao = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fiscalizacaoService.getById(fiscalizacaoId);
        setFiscalizacao(data);
      } catch (err) {
        console.error("Erro ao carregar fiscalização:", err);
        setError("Erro ao carregar dados da fiscalização");
        toast.error("Erro ao carregar fiscalização");
      } finally {
        setLoading(false);
      }
    };

    carregarFiscalizacao();
  }, [fiscalizacaoId]);

  const getStatusColor = (status: string): string => {
    const colors = {
      AGUARDANDO_SOBREVOO: "bg-yellow-100 text-yellow-800 border-yellow-300",
      AGUARDANDO_INFERENCIA: "bg-blue-100 text-blue-800 border-blue-300",
      GERANDO_RELATORIO: "bg-purple-100 text-purple-800 border-purple-300",
      CONCLUIDA: "bg-green-100 text-green-800 border-green-300",
      CANCELADA: "bg-red-100 text-red-800 border-red-300",
    } as const;
    return colors[status as keyof typeof colors] || "bg-gray-100 text-gray-800 border-gray-300";
  };

  const getStatusLabel = (status: string): string => {
    const labels = {
      AGUARDANDO_SOBREVOO: "Aguardando Sobrevoo",
      AGUARDANDO_INFERENCIA: "Aguardando Inferência",
      GERANDO_RELATORIO: "Gerando Relatório",
      CONCLUIDA: "Concluída",
      CANCELADA: "Cancelada",
    } as const;
    return labels[status as keyof typeof labels] || status;
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return "Não definida";
    try {
      return format(new Date(dateString), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR });
    } catch {
      return "Data inválida";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-sm text-muted-foreground">Carregando fiscalização...</p>
        </div>
      </div>
    );
  }

  if (error || !fiscalizacao) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-semibold mb-2">Erro ao carregar fiscalização</h3>
        <p className="text-sm text-muted-foreground mb-4">{error}</p>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.back()}>
            Voltar
          </Button>
          <Button onClick={() => window.location.reload()}>
            Tentar Novamente
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/dashboard" className="hover:text-foreground transition-colors">
          <Home className="h-4 w-4" />
        </Link>
        <ChevronRight className="h-4 w-4" />
        <Link href="/dashboard/fiscalizacao" className="hover:text-foreground transition-colors">
          Fiscalizações
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium">Fiscalização #{fiscalizacao.id}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold tracking-tight">
              Fiscalização #{fiscalizacao.id}
            </h1>
            <Badge className={`${getStatusColor(fiscalizacao.status_fiscalizacao)} border`}>
              {getStatusLabel(fiscalizacao.status_fiscalizacao)}
            </Badge>
          </div>
          <p className="text-muted-foreground">
            {fiscalizacao.codigo || `Código: FISC-${fiscalizacao.id}`}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.back()}>
            Voltar
          </Button>
          <Link href={`/dashboard/fiscalizacao/${fiscalizacao.id}/etapas`}>
            <Button>
              <ArrowRight className="h-4 w-4 mr-2" />
              Ver Pipeline
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Informações Principais */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Informações da Fiscalização
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-muted-foreground">ID da Denúncia</label>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-lg font-semibold">#{fiscalizacao.complaint_id}</p>
                  <Link href={`/dashboard/denuncias/${fiscalizacao.complaint_id}`}>
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-muted-foreground">UUID</label>
                <p className="text-sm font-mono mt-1 break-all">{fiscalizacao.uuid}</p>
              </div>
            </div>

            <Separator />

            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Data de Início</label>
                  <p className="text-sm mt-1">{formatDate(fiscalizacao.data_inicio)}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Conclusão Prevista</label>
                  <p className="text-sm mt-1">{formatDate(fiscalizacao.data_conclusao_prevista)}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Conclusão Efetiva</label>
                  <p className="text-sm mt-1">{formatDate(fiscalizacao.data_conclusao_efetiva)}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Data de Criação</label>
                  <p className="text-sm mt-1">{formatDate(fiscalizacao.data_criacao)}</p>
                </div>
              </div>
            </div>

            {fiscalizacao.observacoes && (
              <>
                <Separator />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Observações</label>
                  <p className="text-sm mt-2 p-3 bg-muted rounded-md">{fiscalizacao.observacoes}</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Fiscais Atribuídos */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Fiscais Atribuídos
            </CardTitle>
            <CardDescription>
              {fiscalizacao.fiscais?.length || 0} fiscal(is) trabalhando nesta fiscalização
            </CardDescription>
          </CardHeader>
          <CardContent>
            {fiscalizacao.fiscais && fiscalizacao.fiscais.length > 0 ? (
              <div className="space-y-3">
                {fiscalizacao.fiscais.map((fiscal, index) => (
                  <div
                    key={fiscal.id}
                    className={`p-3 rounded-lg border ${
                      fiscal.papel === "responsavel" ? "bg-primary/5 border-primary" : "bg-muted"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <p className="font-medium text-sm">{fiscal.nome || "Nome não disponível"}</p>
                      </div>
                      {fiscal.papel === "responsavel" && (
                        <Badge variant="default" className="text-xs">
                          Responsável
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground ml-6">{fiscal.email || "Email não disponível"}</p>
                    {fiscal.data_atribuicao && (
                      <p className="text-xs text-muted-foreground ml-6 mt-1">
                        Desde: {formatDate(fiscal.data_atribuicao)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <User className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Nenhum fiscal atribuído</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Ações Rápidas */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Disponíveis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            <Link href={`/dashboard/fiscalizacao/${fiscalizacao.id}/etapas`} className="block">
              <Button variant="outline" className="w-full">
                <ArrowRight className="h-4 w-4 mr-2" />
                Gerenciar Pipeline
              </Button>
            </Link>

            <Link href={`/dashboard/denuncias/${fiscalizacao.complaint_id}`} className="block">
              <Button variant="outline" className="w-full">
                <Eye className="h-4 w-4 mr-2" />
                Ver Denúncia Original
              </Button>
            </Link>

            <Button variant="outline" className="w-full" disabled>
              <FileText className="h-4 w-4 mr-2" />
              Gerar Relatório
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
