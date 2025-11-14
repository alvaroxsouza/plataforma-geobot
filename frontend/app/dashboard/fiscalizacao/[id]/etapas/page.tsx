"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Home, ChevronRight, Loader2, AlertCircle, CheckCircle2, Clock, Upload, Brain, FileText, Play, ArrowRight, XCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import Link from "next/link";
import { toast } from "sonner";
import { etapasFiscalizacaoService, ProgressoFiscalizacao } from "@/services/etapas-fiscalizacao";

// Mapa de etapas para UI
const ETAPAS_INFO = {
  pendente: {
    label: "Pendente",
    icon: Clock,
    color: "text-gray-500",
    bgColor: "bg-gray-100",
    description: "Fiscalização criada, aguardando início",
  },
  sobrevoo: {
    label: "Sobrevoo",
    icon: Play,
    color: "text-blue-500",
    bgColor: "bg-blue-100",
    description: "Captura aérea em andamento",
  },
  abastecimento: {
    label: "Upload de Imagens",
    icon: Upload,
    color: "text-purple-500",
    bgColor: "bg-purple-100",
    description: "Carregamento de imagens capturadas",
  },
  analise_ia: {
    label: "Análise IA",
    icon: Brain,
    color: "text-orange-500",
    bgColor: "bg-orange-100",
    description: "Processamento com Inteligência Artificial",
  },
  relatorio: {
    label: "Relatório",
    icon: FileText,
    color: "text-green-500",
    bgColor: "bg-green-100",
    description: "Geração de relatório final",
  },
  concluida: {
    label: "Concluída",
    icon: CheckCircle2,
    color: "text-green-600",
    bgColor: "bg-green-200",
    description: "Fiscalização finalizada com sucesso",
  },
  cancelada: {
    label: "Cancelada",
    icon: XCircle,
    color: "text-red-500",
    bgColor: "bg-red-100",
    description: "Fiscalização cancelada",
  },
} as const;

export default function EtapasFiscalizacaoPage() {
  const router = useRouter();
  const params = useParams();
  const fiscalizacaoId = parseInt(params.id as string);

  const [progresso, setProgresso] = useState<ProgressoFiscalizacao | null>(null);
  const [loading, setLoading] = useState(true);
  const [iniciando, setIniciando] = useState(false);
  const [transicionando, setTransicionando] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [relatorioDialogOpen, setRelatorioDialogOpen] = useState(false);
  const [arquivosSelecionados, setArquivosSelecionados] = useState<File[]>([]);
  const [tituloRelatorio, setTituloRelatorio] = useState("");
  const [resumoRelatorio, setResumoRelatorio] = useState("");

  // Carregar progresso
  const carregarProgresso = async () => {
    try {
      setLoading(true);
      const data = await etapasFiscalizacaoService.obterProgresso(fiscalizacaoId);
      setProgresso(data);
    } catch (err) {
      console.error("Erro ao carregar progresso:", err);
      toast.error("Erro ao carregar progresso da fiscalização");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarProgresso();
  }, [fiscalizacaoId]);

  // Iniciar fiscalização
  const handleIniciar = async () => {
    try {
      setIniciando(true);
      await etapasFiscalizacaoService.iniciar(fiscalizacaoId);
      toast.success("Fiscalização iniciada com sucesso!");
      await carregarProgresso();
    } catch (err) {
      console.error("Erro ao iniciar:", err);
      toast.error("Erro ao iniciar fiscalização");
    } finally {
      setIniciando(false);
    }
  };

  // Avançar para próxima etapa
  const handleProximaEtapa = async () => {
    try {
      setTransicionando(true);
      await etapasFiscalizacaoService.proximaEtapa(fiscalizacaoId);
      toast.success("Etapa avançada com sucesso!");
      await carregarProgresso();
    } catch (err) {
      console.error("Erro ao avançar etapa:", err);
      toast.error("Erro ao avançar para próxima etapa");
    } finally {
      setTransicionando(false);
    }
  };

  // Upload de arquivos
  const handleUpload = async () => {
    if (arquivosSelecionados.length === 0 || !progresso?.etapa_em_progresso) {
      toast.error("Selecione ao menos um arquivo");
      return;
    }

    try {
      const etapaId = fiscalizacaoId;

      for (const arquivo of arquivosSelecionados) {
        await etapasFiscalizacaoService.uploadArquivo(etapaId, arquivo);
      }

      toast.success(`${arquivosSelecionados.length} arquivo(s) enviado(s) com sucesso!`);
      setUploadDialogOpen(false);
      setArquivosSelecionados([]);
      await carregarProgresso();
    } catch (err) {
      console.error("Erro no upload:", err);
      toast.error("Erro ao enviar arquivos");
    }
  };

  // Iniciar análise IA
  const handleIniciarIA = async () => {
    try {
      if (!progresso) return;

      toast.info("Iniciando análise de IA...");
      const etapaId = fiscalizacaoId;
      await etapasFiscalizacaoService.iniciarAnaliseIA(etapaId, []);
      toast.success("Análise de IA iniciada!");
      await carregarProgresso();
    } catch (err) {
      console.error("Erro ao iniciar IA:", err);
      toast.error("Erro ao iniciar análise de IA");
    }
  };

  // Gerar relatório
  const handleGerarRelatorio = async () => {
    if (!tituloRelatorio.trim()) {
      toast.error("Digite um título para o relatório");
      return;
    }

    try {
      const etapaId = fiscalizacaoId;
      await etapasFiscalizacaoService.gerarRelatorio(etapaId, tituloRelatorio, {
        resumoExecutivo: resumoRelatorio,
      });

      toast.success("Relatório gerado com sucesso!");
      setRelatorioDialogOpen(false);
      setTituloRelatorio("");
      setResumoRelatorio("");
      await carregarProgresso();
    } catch (err) {
      console.error("Erro ao gerar relatório:", err);
      toast.error("Erro ao gerar relatório");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Carregando progresso...</p>
        </div>
      </div>
    );
  }

  if (!progresso) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center text-red-600">
              <AlertCircle className="mr-2 h-5 w-5" />
              Erro ao Carregar
            </CardTitle>
            <CardDescription>
              Não foi possível carregar o progresso da fiscalização
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.back()} className="w-full">
              Voltar
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const etapaAtual = ETAPAS_INFO[progresso.etapa_atual as keyof typeof ETAPAS_INFO] || ETAPAS_INFO.pendente;
  const IconeAtual = etapaAtual.icon;

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
        <span className="text-foreground font-medium">Pipeline #{fiscalizacaoId}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Pipeline de Fiscalização</h1>
          <p className="text-muted-foreground">
            Gerencie o fluxo de trabalho da fiscalização #{fiscalizacaoId}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={carregarProgresso}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button variant="outline" onClick={() => router.back()}>
            Voltar
          </Button>
        </div>
      </div>

      {/* Status Geral */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <IconeAtual className={`mr-2 h-6 w-6 ${etapaAtual.color}`} />
            {etapaAtual.label}
          </CardTitle>
          <CardDescription>{etapaAtual.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">Progresso Geral</span>
                <span className="text-muted-foreground">{progresso.progresso_geral_percentual}%</span>
              </div>
              <Progress value={progresso.progresso_geral_percentual} className="h-3" />
            </div>

            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 bg-green-50 rounded-lg">
                <CheckCircle2 className="h-6 w-6 text-green-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-green-600">{progresso.etapas_concluidas.length}</p>
                <p className="text-xs text-muted-foreground">Concluídas</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <Clock className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-blue-600">1</p>
                <p className="text-xs text-muted-foreground">Em Progresso</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <AlertCircle className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-600">{progresso.etapas_pendentes.length}</p>
                <p className="text-xs text-muted-foreground">Pendentes</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Timeline de Etapas */}
      <Card>
        <CardHeader>
          <CardTitle>Timeline do Pipeline</CardTitle>
          <CardDescription>Fluxo completo de etapas da fiscalização</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(ETAPAS_INFO).filter(([key]) => key !== "cancelada").map(([key, info], index) => {
              const Icone = info.icon;
              const isConcluida = progresso.etapas_concluidas.includes(key);
              const isAtual = progresso.etapa_atual === key;
              const isPendente = progresso.etapas_pendentes.includes(key);

              return (
                <div key={key}>
                  <div className="flex items-start gap-4">
                    <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
                      isConcluida ? "bg-green-100" : isAtual ? info.bgColor : "bg-gray-100"
                    }`}>
                      <Icone className={`h-6 w-6 ${
                        isConcluida ? "text-green-600" : isAtual ? info.color : "text-gray-400"
                      }`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold">{info.label}</h3>
                        {isConcluida && (
                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Concluída
                          </Badge>
                        )}
                        {isAtual && (
                          <Badge variant="outline" className={`${info.bgColor} ${info.color}`}>
                            <Clock className="h-3 w-3 mr-1" />
                            Em Progresso
                          </Badge>
                        )}
                        {isPendente && (
                          <Badge variant="outline" className="bg-gray-50 text-gray-600">
                            Pendente
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{info.description}</p>
                    </div>
                  </div>
                  {index < Object.keys(ETAPAS_INFO).length - 2 && (
                    <div className="ml-6 h-8 w-0.5 bg-gray-200" />
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Ações Disponíveis */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Disponíveis</CardTitle>
          <CardDescription>Operações para a etapa atual</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            {/* Iniciar */}
            {progresso.etapa_atual === "pendente" && (
              <Button
                onClick={handleIniciar}
                disabled={iniciando}
                className="h-auto flex-col items-start p-4 gap-2"
              >
                <Play className="h-5 w-5" />
                <span className="text-sm font-semibold">Iniciar Fiscalização</span>
              </Button>
            )}

            {/* Próxima Etapa */}
            {progresso.etapa_atual !== "pendente" && progresso.etapa_atual !== "concluida" && (
              <Button
                onClick={handleProximaEtapa}
                disabled={transicionando}
                className="h-auto flex-col items-start p-4 gap-2"
              >
                <ArrowRight className="h-5 w-5" />
                <span className="text-sm font-semibold">Avançar Etapa</span>
              </Button>
            )}

            {/* Upload */}
            {progresso.etapa_atual === "abastecimento" && (
              <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2">
                    <Upload className="h-5 w-5" />
                    <span className="text-sm font-semibold">Upload Imagens</span>
                    <span className="text-xs text-muted-foreground">
                      {progresso.arquivos_carregados} arquivo(s)
                    </span>
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Upload de Imagens</DialogTitle>
                    <DialogDescription>
                      Envie as imagens capturadas durante o sobrevoo
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="arquivos">Selecionar Arquivos</Label>
                      <Input
                        id="arquivos"
                        type="file"
                        multiple
                        accept="image/*"
                        onChange={(e) => setArquivosSelecionados(Array.from(e.target.files || []))}
                      />
                      {arquivosSelecionados.length > 0 && (
                        <p className="text-sm text-muted-foreground">
                          {arquivosSelecionados.length} arquivo(s) selecionado(s)
                        </p>
                      )}
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setUploadDialogOpen(false)}>
                      Cancelar
                    </Button>
                    <Button onClick={handleUpload}>Enviar</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            )}

            {/* Análise IA */}
            {progresso.etapa_atual === "analise_ia" && (
              <Button
                onClick={handleIniciarIA}
                variant="outline"
                className="h-auto flex-col items-start p-4 gap-2"
              >
                <Brain className="h-5 w-5" />
                <span className="text-sm font-semibold">Iniciar Análise IA</span>
              </Button>
            )}

            {/* Relatório */}
            {progresso.etapa_atual === "relatorio" && (
              <Dialog open={relatorioDialogOpen} onOpenChange={setRelatorioDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="h-auto flex-col items-start p-4 gap-2">
                    <FileText className="h-5 w-5" />
                    <span className="text-sm font-semibold">Gerar Relatório</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Gerar Relatório Final</DialogTitle>
                    <DialogDescription>
                      Preencha os dados para gerar o relatório da fiscalização
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="titulo">Título *</Label>
                      <Input
                        id="titulo"
                        placeholder="Ex: Relatório de Fiscalização - Área Central"
                        value={tituloRelatorio}
                        onChange={(e) => setTituloRelatorio(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="resumo">Resumo Executivo</Label>
                      <Textarea
                        id="resumo"
                        placeholder="Breve resumo dos principais achados..."
                        rows={4}
                        value={resumoRelatorio}
                        onChange={(e) => setResumoRelatorio(e.target.value)}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setRelatorioDialogOpen(false)}>
                      Cancelar
                    </Button>
                    <Button onClick={handleGerarRelatorio}>Gerar Relatório</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Resultado IA (se disponível) */}
      {progresso.resultado_ia && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="mr-2 h-5 w-5 text-orange-500" />
              Resultado da Análise IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    {progresso.resultado_ia.deteccoes.length}
                  </p>
                  <p className="text-xs text-muted-foreground">Detecções</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {Math.round(progresso.resultado_ia.confianca_media * 100)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Confiança Média</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-lg font-bold text-purple-600">
                    {progresso.resultado_ia.modelo_utilizado || "N/A"}
                  </p>
                  <p className="text-xs text-muted-foreground">Modelo</p>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">
                    {progresso.resultado_ia.tempo_processamento_segundos || 0}s
                  </p>
                  <p className="text-xs text-muted-foreground">Tempo Proc.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
