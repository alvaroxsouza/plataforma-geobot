"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Home, ChevronRight, Search, Filter, Eye, Send } from "lucide-react";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { complaintsService, ComplaintResponse, ComplaintStatus } from "@/services/complaints";
import { fiscalizacaoService } from "@/services/fiscalizacao";
import { toast } from "sonner";

// Badge de status
const StatusBadge = ({ status }: { status: ComplaintStatus }) => {
  const variants: Record<ComplaintStatus, { variant: "default" | "secondary" | "destructive" | "outline", label: string, color?: string }> = {
    PENDING: { variant: "secondary", label: "Pendente" },
    IN_ANALYSIS: { variant: "default", label: "Em Análise" },
    COMPLETED: { variant: "default", label: "Concluída", color: "bg-green-100 text-green-800 hover:bg-green-200" },
    REJECTED: { variant: "destructive", label: "Rejeitada" },
    CANCELLED: { variant: "outline", label: "Cancelada" }
  };

  const config = variants[status];

  return (
    <Badge variant={config.variant} className={config.color}>
      {config.label}
    </Badge>
  );
};

export default function GerenciarDenunciasPage() {
  const router = useRouter();
  const [complaints, setComplaints] = useState<ComplaintResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  
  // Dialog de enviar para fiscalização
  const [fiscalizacaoDialog, setFiscalizacaoDialog] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState<ComplaintResponse | null>(null);
  const [observacoes, setObservacoes] = useState("");
  const [dataConclusao, setDataConclusao] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Carregar denúncias
  const loadComplaints = async () => {
    try {
      setLoading(true);
      const data = await complaintsService.getAll({
        limit: 100,
      });
      setComplaints(data);
    } catch (error) {
      console.error("Erro ao carregar denúncias:", error);
      toast.error("Erro ao carregar denúncias");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComplaints();
  }, []);

  // Filtrar denúncias pela busca
  const complaintsFiltradas = complaints.filter(complaint => 
    complaint.id.toString().includes(searchQuery) ||
    complaint.street_address.toLowerCase().includes(searchQuery.toLowerCase()) ||
    complaint.subject.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Abrir dialog de fiscalização
  const handleEnviarParaFiscalizacao = (complaint: ComplaintResponse) => {
    setSelectedComplaint(complaint);
    setObservacoes("");
    setDataConclusao("");
    setFiscalizacaoDialog(true);
  };

  // Confirmar envio para fiscalização
  const handleConfirmarFiscalizacao = async () => {
    if (!selectedComplaint) return;

    try {
      setSubmitting(true);
      
      // Criar fiscalização
      await fiscalizacaoService.create({
        complaint_id: selectedComplaint.id,
        observacoes: observacoes || null,
        data_conclusao_prevista: dataConclusao || null,
      });

      toast.success("Denúncia enviada para fiscalização com sucesso!");
      setFiscalizacaoDialog(false);
      setSelectedComplaint(null);
      
      // Recarregar denúncias
      await loadComplaints();
    } catch (error) {
      console.error("Erro ao criar fiscalização:", error);
      toast.error("Erro ao enviar denúncia para fiscalização");
    } finally {
      setSubmitting(false);
    }
  };

  // Estatísticas
  const stats = [
    { 
      label: "Total", 
      value: complaints.length,
      color: "text-blue-600"
    },
    { 
      label: "Pendentes", 
      value: complaints.filter(c => c.status === "PENDING").length,
      color: "text-yellow-600"
    },
    { 
      label: "Em Análise", 
      value: complaints.filter(c => c.status === "IN_ANALYSIS").length,
      color: "text-purple-600"
    },
    { 
      label: "Concluídas", 
      value: complaints.filter(c => c.status === "COMPLETED").length,
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
        <span className="text-foreground font-medium">Gerenciar Denúncias</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Gerenciar Denúncias
          </h1>
          <p className="text-muted-foreground">
            Visualize e gerencie todas as denúncias do sistema
          </p>
        </div>
        <Link href="/dashboard">
          <Button variant="outline">
            Voltar ao Dashboard
          </Button>
        </Link>
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
                {complaintsFiltradas.length} denúncia(s) encontrada(s)
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
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Carregando denúncias...
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Endereço</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Denunciante</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {complaintsFiltradas.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        Nenhuma denúncia encontrada
                      </TableCell>
                    </TableRow>
                  ) : (
                    complaintsFiltradas.map((complaint) => (
                      <TableRow key={complaint.id} className="hover:bg-muted/50">
                        <TableCell className="font-medium">#{complaint.id}</TableCell>
                        <TableCell>
                          <div className="max-w-[300px]">
                            <div className="font-medium truncate">{complaint.street_address}</div>
                            {complaint.observacoes && (
                              <div className="text-sm text-muted-foreground truncate">
                                {complaint.observacoes}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="capitalize">{complaint.subject}</TableCell>
                        <TableCell>
                          <StatusBadge status={complaint.status} />
                        </TableCell>
                        <TableCell className="text-sm">{complaint.complainant.nome}</TableCell>
                        <TableCell className="text-sm">
                          {new Date(complaint.created_at).toLocaleDateString("pt-BR")}
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                Ações
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Ações</DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                onClick={() => router.push(`/dashboard/denuncias/${complaint.id}`)}
                              >
                                <Eye className="mr-2 h-4 w-4" />
                                Ver Detalhes
                              </DropdownMenuItem>
                              {complaint.status === "PENDING" && (
                                <DropdownMenuItem
                                  onClick={() => handleEnviarParaFiscalizacao(complaint)}
                                >
                                  <Send className="mr-2 h-4 w-4" />
                                  Enviar para Fiscalização
                                </DropdownMenuItem>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de Fiscalização */}
      <Dialog open={fiscalizacaoDialog} onOpenChange={setFiscalizacaoDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Enviar para Fiscalização</DialogTitle>
            <DialogDescription>
              Criar uma nova fiscalização para a denúncia #{selectedComplaint?.id}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="data-conclusao">Data de Conclusão Prevista (Opcional)</Label>
              <Input
                id="data-conclusao"
                type="date"
                value={dataConclusao}
                onChange={(e) => setDataConclusao(e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações (Opcional)</Label>
              <Textarea
                id="observacoes"
                placeholder="Adicione observações sobre a fiscalização..."
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                rows={4}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setFiscalizacaoDialog(false)}
              disabled={submitting}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleConfirmarFiscalizacao}
              disabled={submitting}
            >
              {submitting ? "Enviando..." : "Confirmar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
