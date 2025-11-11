"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Home, ChevronRight, Search, Filter, Eye, MessageSquare, MoreVertical, MapPin, Calendar, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { servicoDenuncias, DenunciaResposta, StatusDenuncia } from "@/services/denuncias";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { toast } from "sonner";

// Mapeamento de categorias (slug para nome)
const categoriasMap: Record<string, string> = {
  "calcada": "Calçada",
  "rua": "Rua",
  "ciclovia": "Ciclovia",
  "semaforo": "Semáforo",
  "sinalizacao": "Sinalização",
  "iluminacao": "Iluminação",
  "lixo_entulho": "Lixo e Entulho",
  "poluicao": "Poluição",
  "barulho": "Barulho",
  "outros": "Outros"
};

// Mapeamento inverso (slug para valor da API)
const categoriaAPIMap: Record<string, string> = {
  "calcada": "calcada",
  "rua": "rua",
  "ciclovia": "ciclovia",
  "semaforo": "semaforo",
  "sinalizacao": "sinalizacao",
  "iluminacao": "iluminacao",
  "lixo_entulho": "lixo_entulho",
  "poluicao": "poluicao",
  "barulho": "barulho",
  "outros": "outros"
};

// Badge de status
const StatusBadge = ({ status }: { status: StatusDenuncia }) => {
  const statusColors: Record<StatusDenuncia, string> = {
    pendente: "bg-yellow-100 text-yellow-800 border-yellow-200",
    em_analise: "bg-blue-100 text-blue-800 border-blue-200",
    em_fiscalizacao: "bg-purple-100 text-purple-800 border-purple-200",
    concluida: "bg-green-100 text-green-800 border-green-200",
    arquivada: "bg-gray-100 text-gray-800 border-gray-200",
    cancelada: "bg-red-100 text-red-800 border-red-200",
  };

  const statusLabels: Record<StatusDenuncia, string> = {
    pendente: "Pendente",
    em_analise: "Em Análise",
    em_fiscalizacao: "Em Fiscalização",
    concluida: "Concluída",
    arquivada: "Arquivada",
    cancelada: "Cancelada",
  };

  return (
    <Badge variant="outline" className={statusColors[status]}>
      {statusLabels[status]}
    </Badge>
  );
};

// Badge de prioridade
const PrioridadeBadge = ({ prioridade }: { prioridade: string }) => {
  const variants: Record<string, { color: string, label: string }> = {
    baixa: { color: "bg-blue-100 text-blue-800", label: "Baixa" },
    media: { color: "bg-yellow-100 text-yellow-800", label: "Média" },
    alta: { color: "bg-orange-100 text-orange-800", label: "Alta" },
    urgente: { color: "bg-red-100 text-red-800", label: "Urgente" }
  };

  const config = variants[prioridade] || { color: "bg-gray-100 text-gray-800", label: prioridade };

  return (
    <Badge className={config.color}>
      {config.label}
    </Badge>
  );
};

export default function EquipamentoDenunciasPage() {
  const params = useParams();
  const router = useRouter();
  const categoriaSlug = params.categoria as string;
  const [searchQuery, setSearchQuery] = useState("");
  const [denuncias, setDenuncias] = useState<DenunciaResposta[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");

  // Nome da categoria formatado
  const nomeCategoria = categoriasMap[categoriaSlug] || "Equipamento";
  const categoriaAPI = categoriaAPIMap[categoriaSlug];

  // Carregar denúncias da API
  const carregarDenuncias = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Tentar carregar todas as denúncias
      let denunciasData: DenunciaResposta[];
      try {
        denunciasData = await servicoDenuncias.listar({ todas: true });
      } catch {
        // Se falhar, carregar apenas as do usuário
        denunciasData = await servicoDenuncias.listar({ todas: false });
      }

      // Filtrar por categoria
      const denunciasFiltradas = denunciasData.filter(
        (d) => d.categoria === categoriaAPI
      );
      
      setDenuncias(denunciasFiltradas);
    } catch (err) {
      console.error("Erro ao carregar denúncias:", err);
      setError("Não foi possível carregar as denúncias. Tente novamente.");
      toast.error("Erro ao carregar denúncias");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (categoriaAPI) {
      carregarDenuncias();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoriaAPI]);

  // Filtrar denúncias pela busca
  const denunciasFiltradas = denuncias.filter(denuncia => 
    denuncia.observacao.toLowerCase().includes(searchQuery.toLowerCase()) ||
    denuncia.id.toString().includes(searchQuery) ||
    denuncia.endereco.logradouro.toLowerCase().includes(searchQuery.toLowerCase()) ||
    denuncia.endereco.bairro.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Estatísticas
  const stats = [
    { 
      label: "Total", 
      value: denuncias.length,
      color: "text-blue-600"
    },
    { 
      label: "Pendentes", 
      value: denuncias.filter(d => d.status === "pendente").length,
      color: "text-yellow-600"
    },
    { 
      label: "Em Análise", 
      value: denuncias.filter(d => d.status === "em_analise").length,
      color: "text-purple-600"
    },
    { 
      label: "Concluídas", 
      value: denuncias.filter(d => d.status === "concluida").length,
      color: "text-green-600"
    }
  ];

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
        <span className="text-foreground font-medium">{nomeCategoria}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Denúncias: {nomeCategoria}
          </h1>
          <p className="text-muted-foreground">
            Visualize todas as denúncias relacionadas a {nomeCategoria.toLowerCase()}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/dashboard/denuncias">
            <Button variant="outline">
              Voltar para Denúncias
            </Button>
          </Link>
          <Link href="/dashboard/denuncias/nova">
            <Button>
              Nova Denúncia
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${stat.color}`}>
                {stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tabela de Denúncias */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Lista de Denúncias</CardTitle>
              <CardDescription>
                {denunciasFiltradas.length} denúncia(s) encontrada(s)
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar denúncias..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
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
          {isLoading ? (
            <div className="text-center py-12">
              <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary mb-4" />
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
            <div className="text-center py-12">
              <AlertCircle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                Nenhuma denúncia encontrada
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {searchQuery 
                  ? "Tente ajustar os filtros de busca" 
                  : `Não há denúncias de ${nomeCategoria} no momento`}
              </p>
              {!searchQuery && (
                <Link href="/dashboard/denuncias/nova">
                  <Button>
                    Criar Nova Denúncia
                  </Button>
                </Link>
              )}
            </div>
          ) : viewMode === "cards" ? (
            <div className="space-y-4">
              {denunciasFiltradas.map((denuncia) => (
                <Card key={denuncia.id} className="hover:shadow-lg transition-all hover:border-primary/50">
                  <CardContent className="p-6">
                    <div className="flex flex-col gap-4">
                      {/* Header com Badges */}
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge variant="secondary" className="font-medium">
                          #{denuncia.id}
                        </Badge>
                        <StatusBadge status={denuncia.status} />
                        <PrioridadeBadge prioridade={denuncia.prioridade} />
                      </div>

                      {/* Descrição */}
                      <div>
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
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Prioridade</TableHead>
                    <TableHead>Localização</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {denunciasFiltradas.map((denuncia) => (
                      <TableRow key={denuncia.id} className="hover:bg-muted/50">
                        <TableCell className="font-medium">#{denuncia.id}</TableCell>
                        <TableCell>
                          <div className="max-w-[300px]">
                            <p className="text-sm truncate">{denuncia.observacao}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={denuncia.status} />
                        </TableCell>
                        <TableCell>
                          <PrioridadeBadge prioridade={denuncia.prioridade} />
                        </TableCell>
                        <TableCell>
                          <div className="text-sm max-w-[200px]">
                            <div className="truncate">{denuncia.endereco.logradouro}</div>
                            <div className="text-muted-foreground truncate">
                              {denuncia.endereco.bairro}, {denuncia.endereco.cidade}/{denuncia.endereco.estado}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-sm">
                          {format(new Date(denuncia.created_at), "dd/MM/yyyy", { locale: ptBR })}
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Ações</DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                onClick={() => router.push(`/dashboard/denuncias/${denuncia.id}`)}
                              >
                                <Eye className="mr-2 h-4 w-4" />
                                Ver Detalhes
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
