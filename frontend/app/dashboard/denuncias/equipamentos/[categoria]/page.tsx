"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Home, ChevronRight, Search, Filter, Eye, MessageSquare, MoreVertical } from "lucide-react";
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

// Mapeamento de categorias
const categoriasMap: Record<string, string> = {
  "calcada": "Calçada",
  "rua": "Rua",
  "ciclovia": "Ciclovia",
  "semaforo": "Semáforo",
  "sinalizacao": "Sinalização",
  "iluminacao": "Iluminação Pública",
  "lixo": "Lixo e Entulho",
  "poluicao": "Poluição",
  "barulho": "Barulho",
  "outros": "Outros"
};

// Badge de status
const StatusBadge = ({ status }: { status: string }) => {
  const variants: Record<string, { variant: "default" | "secondary" | "destructive" | "outline", label: string }> = {
    pendente: { variant: "secondary", label: "Pendente" },
    em_analise: { variant: "default", label: "Em Análise" },
    em_fiscalizacao: { variant: "outline", label: "Em Fiscalização" },
    resolvida: { variant: "default", label: "Resolvida" },
    rejeitada: { variant: "destructive", label: "Rejeitada" }
  };

  const config = variants[status] || { variant: "secondary", label: status };

  return (
    <Badge variant={config.variant} className={status === "resolvida" ? "bg-green-100 text-green-800 hover:bg-green-200" : ""}>
      {config.label}
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
  const categoria = params.categoria as string;
  const [searchQuery, setSearchQuery] = useState("");

  // Nome da categoria formatado
  const nomeCategoria = categoriasMap[categoria] || "Equipamento";

  // Dados mockados para demonstração
  const denuncias = [
    {
      id: "D-2024-001",
      titulo: `Problema em ${nomeCategoria}`,
      descricao: "Necessita de reparo urgente",
      status: "pendente",
      prioridade: "alta",
      endereco: "Rua das Flores, 123",
      bairro: "Centro",
      cidade: "São Paulo",
      data: "15/01/2024",
      denunciante: "João Silva",
      comentarios: 3
    },
    {
      id: "D-2024-002",
      titulo: `${nomeCategoria} danificada`,
      descricao: "Situação crítica que requer atenção",
      status: "em_analise",
      prioridade: "media",
      endereco: "Av. Principal, 456",
      bairro: "Jardins",
      cidade: "São Paulo",
      data: "14/01/2024",
      denunciante: "Maria Santos",
      comentarios: 1
    },
    {
      id: "D-2024-003",
      titulo: `Manutenção em ${nomeCategoria}`,
      descricao: "Necessita de manutenção preventiva",
      status: "em_fiscalizacao",
      prioridade: "baixa",
      endereco: "Rua do Comércio, 789",
      bairro: "Vila Nova",
      cidade: "São Paulo",
      data: "13/01/2024",
      denunciante: "Carlos Oliveira",
      comentarios: 5
    },
    {
      id: "D-2024-004",
      titulo: `${nomeCategoria} em bom estado`,
      descricao: "Verificação concluída, problema resolvido",
      status: "resolvida",
      prioridade: "media",
      endereco: "Rua da Paz, 321",
      bairro: "Centro",
      cidade: "São Paulo",
      data: "12/01/2024",
      denunciante: "Ana Costa",
      comentarios: 2
    },
    {
      id: "D-2024-005",
      titulo: `Falso problema em ${nomeCategoria}`,
      descricao: "Denúncia improcedente após verificação",
      status: "rejeitada",
      prioridade: "baixa",
      endereco: "Av. Brasil, 654",
      bairro: "Jardins",
      cidade: "São Paulo",
      data: "11/01/2024",
      denunciante: "Pedro Almeida",
      comentarios: 0
    }
  ];

  // Filtrar denúncias pela busca
  const denunciasFiltradas = denuncias.filter(denuncia => 
    denuncia.titulo.toLowerCase().includes(searchQuery.toLowerCase()) ||
    denuncia.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    denuncia.endereco.toLowerCase().includes(searchQuery.toLowerCase())
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
      label: "Resolvidas", 
      value: denuncias.filter(d => d.status === "resolvida").length,
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
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Protocolo</TableHead>
                  <TableHead>Título</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Prioridade</TableHead>
                  <TableHead>Localização</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead className="text-center">Comentários</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {denunciasFiltradas.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                      Nenhuma denúncia encontrada
                    </TableCell>
                  </TableRow>
                ) : (
                  denunciasFiltradas.map((denuncia) => (
                    <TableRow key={denuncia.id} className="hover:bg-muted/50">
                      <TableCell className="font-medium">{denuncia.id}</TableCell>
                      <TableCell>
                        <div className="max-w-[300px]">
                          <div className="font-medium">{denuncia.titulo}</div>
                          <div className="text-sm text-muted-foreground truncate">
                            {denuncia.descricao}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={denuncia.status} />
                      </TableCell>
                      <TableCell>
                        <PrioridadeBadge prioridade={denuncia.prioridade} />
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{denuncia.endereco}</div>
                          <div className="text-muted-foreground">
                            {denuncia.bairro}, {denuncia.cidade}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm">{denuncia.data}</TableCell>
                      <TableCell className="text-center">
                        <div className="flex items-center justify-center gap-1">
                          <MessageSquare className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{denuncia.comentarios}</span>
                        </div>
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
                            <DropdownMenuItem>
                              <MessageSquare className="mr-2 h-4 w-4" />
                              Adicionar Comentário
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
