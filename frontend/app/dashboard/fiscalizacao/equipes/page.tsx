"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Home, ChevronRight, Users, UserCheck, UserX } from "lucide-react";
import Link from "next/link";
import { fiscalizacaoService, FiscalizacaoResponse } from "@/services/fiscalizacao";
import { toast } from "sonner";

export default function EquipesFiscalizacaoPage() {
  const [fiscalizacoes, setFiscalizacoes] = useState<FiscalizacaoResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    carregarFiscalizacoes();
  }, []);

  const carregarFiscalizacoes = async () => {
    try {
      setIsLoading(true);
      const response = await fiscalizacaoService.getAll({ limit: 1000 });
      setFiscalizacoes(response);
    } catch (error: any) {
      console.error("Erro ao carregar fiscalizações:", error);
      toast.error(error?.response?.data?.detail || "Erro ao carregar fiscalizações");
    } finally {
      setIsLoading(false);
    }
  };

  // Agrupar fiscais
  const fiscaisMap = new Map<number, {
    id: number;
    nome: string;
    email: string;
    fiscalizacoes: Array<{ id: number; status: string; papel: string }>;
  }>();

  fiscalizacoes.forEach((fisc) => {
    if (fisc.fiscais && fisc.fiscais.length > 0) {
      fisc.fiscais.forEach((fiscal) => {
        if (!fiscaisMap.has(fiscal.id)) {
          fiscaisMap.set(fiscal.id, {
            id: fiscal.id,
            nome: fiscal.nome,
            email: fiscal.email || '',
            fiscalizacoes: [],
          });
        }
        
        const fiscalData = fiscaisMap.get(fiscal.id)!;
        fiscalData.fiscalizacoes.push({
          id: fisc.id,
          status: fisc.status_fiscalizacao,
          papel: fiscal.papel || 'auxiliar',
        });
      });
    }
  });

  const fiscaisArray = Array.from(fiscaisMap.values());

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'AGUARDANDO_SOBREVOO': 'bg-yellow-500',
      'AGUARDANDO_INFERENCIA': 'bg-blue-500',
      'GERANDO_RELATORIO': 'bg-purple-500',
      'CONCLUIDA': 'bg-green-500',
      'CANCELADA': 'bg-red-500',
    };
    return colors[status] || 'bg-gray-500';
  };

  const getPapelBadge = (papel: string) => {
    if (papel === 'responsavel') {
      return <Badge variant="default" className="bg-purple-600">Responsável</Badge>;
    }
    return <Badge variant="secondary">Auxiliar</Badge>;
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/dashboard" className="hover:text-foreground transition-colors">
          <Home className="h-4 w-4" />
        </Link>
        <ChevronRight className="h-4 w-4" />
        <Link href="/dashboard/fiscalizacao" className="hover:text-foreground transition-colors">
          Fiscalização
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium">Equipes</span>
      </div>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Users className="h-8 w-8" />
          Equipes de Fiscalização
        </h1>
        <p className="text-muted-foreground">
          Visualize todos os fiscais e suas fiscalizações
        </p>
      </div>

      {/* Estatísticas */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Fiscais</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{fiscaisArray.length}</div>
            <p className="text-xs text-muted-foreground">
              Fiscais ativos no sistema
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fiscalizações Ativas</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {fiscalizacoes.filter((f) => f.status_fiscalizacao === 'AGUARDANDO_INFERENCIA' || f.status_fiscalizacao === 'GERANDO_RELATORIO').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Em andamento
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fiscalizações Pendentes</CardTitle>
            <UserX className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {fiscalizacoes.filter((f) => f.status_fiscalizacao === 'AGUARDANDO_SOBREVOO').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Aguardando início
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Fiscais */}
      <Card>
        <CardHeader>
          <CardTitle>Fiscais e suas Atribuições</CardTitle>
          <CardDescription>
            {isLoading ? "Carregando..." : `${fiscaisArray.length} fiscal(is) encontrado(s)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : fiscaisArray.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-20" />
              <p>Nenhum fiscal encontrado</p>
            </div>
          ) : (
            <div className="space-y-4">
              {fiscaisArray.map((fiscal) => (
                <div
                  key={fiscal.id}
                  className="border rounded-lg p-4 hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-lg">{fiscal.nome}</h3>
                      <p className="text-sm text-muted-foreground">{fiscal.email}</p>
                    </div>
                    <Badge variant="outline">
                      {fiscal.fiscalizacoes.length} fiscalização(ões)
                    </Badge>
                  </div>

                  {/* Fiscalizações do fiscal */}
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Fiscalizações:</p>
                    <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                      {fiscal.fiscalizacoes.map((fisc) => (
                        <Link
                          key={fisc.id}
                          href={`/dashboard/fiscalizacao/${fisc.id}`}
                          className="flex items-center gap-2 p-2 border rounded hover:bg-accent transition-colors"
                        >
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(fisc.status)}`} />
                          <span className="text-sm font-medium">#{fisc.id}</span>
                          {getPapelBadge(fisc.papel)}
                          <span className="text-xs text-muted-foreground ml-auto capitalize">
                            {fisc.status.replace(/_/g, ' ').toLowerCase()}
                          </span>
                        </Link>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
