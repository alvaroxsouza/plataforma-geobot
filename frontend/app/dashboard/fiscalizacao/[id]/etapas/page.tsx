"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Image,
  Zap,
  FileText,
  ChevronRight,
  Upload,
  Play,
  Loader2,
  Download,
  Eye,
  MoreVertical,
} from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface Etapa {
  id: number;
  nome: string;
  descricao: string;
  status: "pendente" | "em_progresso" | "concluida" | "erro";
  progresso: number;
  icone: React.ReactNode;
  duracao?: string;
}

const etapas: Etapa[] = [
  {
    id: 1,
    nome: "Sobrevôo",
    descricao: "Captura aérea com drone",
    status: "concluida",
    progresso: 100,
    icone: <Image className="h-5 w-5" />,
    duracao: "45min",
  },
  {
    id: 2,
    nome: "Abastecimento",
    descricao: "Upload de imagens do sobrevôo",
    status: "em_progresso",
    progresso: 65,
    icone: <Upload className="h-5 w-5" />,
  },
  {
    id: 3,
    nome: "Análise IA",
    descricao: "Processamento com modelo de IA",
    status: "pendente",
    progresso: 0,
    icone: <Zap className="h-5 w-5" />,
  },
  {
    id: 4,
    nome: "Relatório",
    descricao: "Geração do relatório final",
    status: "pendente",
    progresso: 0,
    icone: <FileText className="h-5 w-5" />,
  },
];

const getStatusColor = (status: Etapa["status"]) => {
  switch (status) {
    case "concluida":
      return "bg-green-100 text-green-800";
    case "em_progresso":
      return "bg-blue-100 text-blue-800";
    case "erro":
      return "bg-red-100 text-red-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
};

const getStatusIcon = (status: Etapa["status"]) => {
  switch (status) {
    case "concluida":
      return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    case "em_progresso":
      return <Clock className="h-5 w-5 text-blue-600 animate-spin" />;
    case "erro":
      return <AlertCircle className="h-5 w-5 text-red-600" />;
    default:
      return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />;
  }
};

const statusTexto = {
  concluida: "Concluída",
  em_progresso: "Em Progresso",
  pendente: "Pendente",
  erro: "Erro",
};

export default function FiscalizacaoEtapasPipelinePage() {
  const [etapaSelecionada, setEtapaSelecionada] = useState(2);
  const [detalhesAbertos, setDetalhesAbertos] = useState(false);
  const [imagens, setImagens] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [resultadoIA, setResultadoIA] = useState<any>(null);
  const [relatorio, setRelatorio] = useState<any>(null);

  useEffect(() => {
    // Simular carregamento de dados
    const timer = setTimeout(() => {
      setResultadoIA({
        deteccoes: 3,
        confianca: 0.87,
        tempo: "12m 34s",
      });
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setImagens([...imagens, ...files]);
  };

  const handleUpload = async () => {
    setUploading(true);
    // Simular upload
    await new Promise(resolve => setTimeout(resolve, 2000));
    setUploading(false);
    setImagens([]);
  };

  const handleIniciarAnalise = async () => {
    console.log("Iniciando análise de IA...");
    // Trigger Skypilot job
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold tracking-tight">
                Pipeline de Fiscalização
              </h1>
              <p className="text-muted-foreground mt-2">
                Denúncia #12345 - Fiscalização em andamento
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">65%</div>
              <p className="text-sm text-muted-foreground">Progresso Geral</p>
            </div>
          </div>
        </div>

        {/* Progresso Geral */}
        <Card className="bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20">
          <CardContent className="pt-6">
            <Progress value={65} className="h-3" />
            <div className="flex justify-between mt-3 text-sm text-muted-foreground">
              <span>2 etapas concluídas</span>
              <span>2 etapas pendentes</span>
            </div>
          </CardContent>
        </Card>

        {/* Timeline de Etapas */}
        <div className="grid gap-4">
          {etapas.map((etapa, index) => (
            <div key={etapa.id}>
              <Card
                className={`cursor-pointer transition-all hover:shadow-lg ${
                  etapaSelecionada === index ? "ring-2 ring-primary" : ""
                }`}
                onClick={() => {
                  setEtapaSelecionada(index);
                  setDetalhesAbertos(true);
                }}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                        {getStatusIcon(etapa.status)}
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-lg">{etapa.nome}</h3>
                          <Badge className={getStatusColor(etapa.status)}>
                            {statusTexto[etapa.status]}
                          </Badge>
                          {etapa.duracao && (
                            <span className="text-xs text-muted-foreground">
                              {etapa.duracao}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {etapa.descricao}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="w-32">
                        <Progress value={etapa.progresso} className="h-2" />
                        <p className="text-xs text-muted-foreground text-right mt-1">
                          {etapa.progresso}%
                        </p>
                      </div>
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Linhas conectoras */}
              {index < etapas.length - 1 && (
                <div className="flex justify-center py-2">
                  <div className={`w-1 h-8 ${etapas[index].status === "concluida" ? "bg-green-400" : "bg-gray-300"}`} />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Detalhes da Etapa Selecionada */}
        {detalhesAbertos && (
          <Card className="border-primary/50 bg-primary/5">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Detalhes - {etapas[etapaSelecionada].nome}</CardTitle>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setDetalhesAbertos(false)}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Etapa 2: Abastecimento */}
              {etapaSelecionada === 1 && (
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-3">Upload de Imagens</h4>
                    <div className="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center hover:border-primary/60 transition-colors">
                      <Upload className="h-8 w-8 mx-auto mb-3 text-muted-foreground" />
                      <p className="text-sm font-medium">Arraste imagens ou clique para selecionar</p>
                      <p className="text-xs text-muted-foreground mt-1">Formatos suportados: JPG, PNG</p>
                      <input
                        type="file"
                        multiple
                        accept="image/*"
                        className="hidden"
                        id="file-input"
                        onChange={handleFileSelect}
                      />
                      <label htmlFor="file-input" className="mt-4 inline-block">
                        <Button type="button" variant="outline">
                          Selecionar Arquivos
                        </Button>
                      </label>
                    </div>
                  </div>

                  {imagens.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3">Imagens Selecionadas ({imagens.length})</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {imagens.map((img, idx) => (
                          <div key={idx} className="relative group">
                            <img
                              src={URL.createObjectURL(img)}
                              alt={`Preview ${idx}`}
                              className="w-full h-24 object-cover rounded-lg"
                            />
                            <button
                              className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded opacity-0 group-hover:opacity-100"
                              onClick={() => setImagens(imagens.filter((_, i) => i !== idx))}
                            >
                              ✕
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={handleUpload}
                    disabled={imagens.length === 0 || uploading}
                    className="w-full"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Fazendo upload...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Enviar {imagens.length > 0 ? `${imagens.length} Imagens` : "Imagens"}
                      </>
                    )}
                  </Button>
                </div>
              )}

              {/* Etapa 3: Análise IA */}
              {etapaSelecionada === 2 && (
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-3">Status da Análise</h4>
                    <div className="bg-muted p-4 rounded-lg space-y-2">
                      <p className="text-sm">
                        <span className="font-medium">Imagens para processar:</span> 12
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Modelo:</span> YOLOv8 (Detecção de Anomalias)
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Estimativa de tempo:</span> 15-25 minutos
                      </p>
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex gap-3">
                      <Zap className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-blue-900">Processamento no Skypilot</p>
                        <p className="text-blue-700 text-xs mt-1">
                          Uma máquina Azure será provisionada para executar a análise
                        </p>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={handleIniciarAnalise}
                    className="w-full"
                    size="lg"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Iniciar Análise com IA
                  </Button>

                  {resultadoIA && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
                      <p className="font-semibold text-green-900">✓ Análise Concluída</p>
                      <p className="text-sm text-green-700">
                        <span className="font-medium">{resultadoIA.deteccoes}</span> anomalias detectadas
                      </p>
                      <p className="text-sm text-green-700">
                        Confiança média: <span className="font-medium">{(resultadoIA.confianca * 100).toFixed(1)}%</span>
                      </p>
                      <p className="text-xs text-green-600">
                        Tempo de processamento: {resultadoIA.tempo}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Etapa 4: Relatório */}
              {etapaSelecionada === 3 && (
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-3">Gerar Relatório</h4>
                    <p className="text-sm text-muted-foreground mb-4">
                      Crie um relatório consolidado com os resultados da análise
                    </p>
                  </div>

                  <Button className="w-full" size="lg">
                    <FileText className="h-4 w-4 mr-2" />
                    Gerar Relatório Final
                  </Button>

                  {relatorio && (
                    <div className="bg-muted p-4 rounded-lg space-y-3">
                      <p className="font-semibold">Relatório Gerado</p>
                      <p className="text-sm">Ref: RF-2025-001234</p>
                      <Button variant="outline" className="w-full">
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Painel de Resumo */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Etapas Concluídas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">2 / 4</div>
              <p className="text-xs text-muted-foreground mt-1">
                Sobrevôo, Abastecimento
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Imagens Processadas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12 / 12</div>
              <p className="text-xs text-muted-foreground mt-1">
                100% dos arquivos carregados
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Anomalias Detectadas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground mt-1">
                Confiança: 87%
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
