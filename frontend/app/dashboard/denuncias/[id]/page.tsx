"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { 
  Home, 
  ChevronRight, 
  MapPin, 
  User, 
  AlertCircle,
  ArrowLeft,
  Edit,
  Trash2,
  Send,
  CheckCircle,
  Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { toast } from "sonner";

import { 
  servicoDenuncias, 
  DenunciaResposta, 
  StatusDenuncia, 
  Prioridade 
} from "@/services/denuncias";
import { fiscalizacaoService } from "@/services/fiscalizacao";
import { useMetadata } from "@/hooks/useMetadata";

export default function DenunciaDetalhePage() {
  const router = useRouter();
  const params = useParams();
  const denunciaId = Number(params.id);

  // Metadados do sistema
  const {
    status: statusOptions,
    prioridades: prioridadeOptions,
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    getPrioridadeLabel,
    getPrioridadeColor,
    loading: metadataLoading,
  } = useMetadata();

  // Estado da denúncia
  const [denuncia, setDenuncia] = useState<DenunciaResposta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Dialogs
  const [editDialog, setEditDialog] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [statusDialog, setStatusDialog] = useState(false);
  const [fiscalizacaoDialog, setFiscalizacaoDialog] = useState(false);

  // Formulários
  const [observacaoEdit, setObservacaoEdit] = useState("");
  const [prioridadeEdit, setPrioridadeEdit] = useState<Prioridade>("media");
  const [novoStatus, setNovoStatus] = useState<StatusDenuncia>("pendente");
  const [observacoesFiscalizacao, setObservacoesFiscalizacao] = useState("");
  const [dataConclusaoFiscalizacao, setDataConclusaoFiscalizacao] = useState("");

  // Estado de submissão
  const [submitting, setSubmitting] = useState(false);

  // Verificar se é admin/fiscal (será validado no backend)
  const [isAdminOuFiscal, setIsAdminOuFiscal] = useState(false);

  // Carregar denúncia
  const carregarDenuncia = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await servicoDenuncias.obterPorId(denunciaId);
      setDenuncia(data);
      setObservacaoEdit(data.observacao);
      setPrioridadeEdit(data.prioridade);
      setNovoStatus(data.status);

      // Tentar verificar se é admin/fiscal
      try {
        await servicoDenuncias.listar({ todas: true });
        setIsAdminOuFiscal(true);
      } catch {
        setIsAdminOuFiscal(false);
      }
    } catch (err) {
      console.error("Erro ao carregar denúncia:", err);
      setError(err instanceof Error ? err.message : "Erro ao carregar denúncia");
      toast.error("Erro ao carregar denúncia");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (denunciaId) {
      carregarDenuncia();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [denunciaId]);

  // Editar denúncia
  const handleEditar = async () => {
    if (!denuncia) return;

    try {
      setSubmitting(true);
      await servicoDenuncias.atualizar(denuncia.id, {
        observacao: observacaoEdit,
        prioridade: prioridadeEdit,
      });
      toast.success("Denúncia atualizada com sucesso!");
      setEditDialog(false);
      await carregarDenuncia();
    } catch (err) {
      console.error("Erro ao atualizar denúncia:", err);
      toast.error(err instanceof Error ? err.message : "Erro ao atualizar denúncia");
    } finally {
      setSubmitting(false);
    }
  };

  // Deletar denúncia
  const handleDeletar = async () => {
    if (!denuncia) return;

    try {
      setSubmitting(true);
      await servicoDenuncias.deletar(denuncia.id);
      toast.success("Denúncia deletada com sucesso!");
      router.push("/dashboard/denuncias");
    } catch (err) {
      console.error("Erro ao deletar denúncia:", err);
      toast.error(err instanceof Error ? err.message : "Erro ao deletar denúncia");
      setSubmitting(false);
    }
  };

  // Atualizar status (admin/fiscal)
  const handleAtualizarStatus = async () => {
    if (!denuncia) return;

    try {
      setSubmitting(true);
      await servicoDenuncias.atualizarStatus(denuncia.id, { status: novoStatus });
      toast.success("Status atualizado com sucesso!");
      setStatusDialog(false);
      await carregarDenuncia();
    } catch (err) {
      console.error("Erro ao atualizar status:", err);
      toast.error(err instanceof Error ? err.message : "Erro ao atualizar status");
    } finally {
      setSubmitting(false);
    }
  };

  // Enviar para fiscalização
  const handleEnviarParaFiscalizacao = async () => {
    if (!denuncia) return;

    try {
      setSubmitting(true);
      await fiscalizacaoService.create({
        complaint_id: denuncia.id,
        observacoes: observacoesFiscalizacao || null,
        data_conclusao_prevista: dataConclusaoFiscalizacao || null,
      });
      toast.success("Denúncia enviada para fiscalização com sucesso!");
      setFiscalizacaoDialog(false);
      await carregarDenuncia();
    } catch (err) {
      console.error("Erro ao criar fiscalização:", err);
      toast.error(err instanceof Error ? err.message : "Erro ao enviar para fiscalização");
    } finally {
      setSubmitting(false);
    }
  };

  // Loading
  if (loading || metadataLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] p-6">
        <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">
          {metadataLoading ? "Carregando configurações..." : "Carregando denúncia..."}
        </p>
      </div>
    );
  }

  // Error
  if (error || !denuncia) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] p-6">
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold mb-2">Erro ao carregar denúncia</h2>
        <p className="text-muted-foreground mb-4">{error || "Denúncia não encontrada"}</p>
        <Button onClick={() => router.push("/dashboard/denuncias")}>
          Voltar para Denúncias
        </Button>
      </div>
    );
  }

  // Verificar se pode editar (apenas criador e status pendente)
  const podeEditar = denuncia.status === "pendente";
  const podeDeletar = denuncia.status === "pendente";

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
        <span className="text-foreground font-medium">Denúncia #{denuncia.id}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Denúncia #{denuncia.id}
          </h1>
          <p className="text-muted-foreground">
            Criada em {format(new Date(denuncia.created_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
          </p>
        </div>
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>
      </div>

      {/* Badges de Status e Categoria */}
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline" className={`${getStatusColor(denuncia.status)} text-base px-4 py-2`}>
          {getStatusLabel(denuncia.status)}
        </Badge>
        <Badge variant="outline" className={`${getPrioridadeColor(denuncia.prioridade)} text-base px-4 py-2`}>
          Prioridade: {getPrioridadeLabel(denuncia.prioridade)}
        </Badge>
        <Badge variant="secondary" className="text-base px-4 py-2">
          {getCategoriaLabel(denuncia.categoria)}
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Coluna Principal - Detalhes */}
        <div className="md:col-span-2 space-y-6">
          {/* Descrição */}
          <Card>
            <CardHeader>
              <CardTitle>Descrição da Denúncia</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {denuncia.observacao}
              </p>
            </CardContent>
          </Card>

          {/* Localização */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Localização
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-muted-foreground text-xs">Endereço</Label>
                <p className="font-medium">
                  {denuncia.endereco.logradouro}
                  {denuncia.endereco.numero && `, ${denuncia.endereco.numero}`}
                </p>
                {denuncia.endereco.complemento && (
                  <p className="text-sm text-muted-foreground">{denuncia.endereco.complemento}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground text-xs">Bairro</Label>
                  <p className="font-medium">{denuncia.endereco.bairro}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground text-xs">Cidade/UF</Label>
                  <p className="font-medium">
                    {denuncia.endereco.cidade}/{denuncia.endereco.estado}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground text-xs">CEP</Label>
                  <p className="font-medium">{denuncia.endereco.cep}</p>
                </div>
                {(denuncia.endereco.latitude && denuncia.endereco.longitude) && (
                  <div>
                    <Label className="text-muted-foreground text-xs">Coordenadas</Label>
                    <p className="font-medium text-sm">
                      {denuncia.endereco.latitude.toFixed(6)}, {denuncia.endereco.longitude.toFixed(6)}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Informações do Denunciante (para admin/fiscal) */}
          {isAdminOuFiscal && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Denunciante
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label className="text-muted-foreground text-xs">Nome</Label>
                  <p className="font-medium">{denuncia.usuario.nome}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground text-xs">Email</Label>
                  <p className="font-medium">{denuncia.usuario.email}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Coluna Lateral - Ações */}
        <div className="space-y-6">
          {/* Card de Informações */}
          <Card>
            <CardHeader>
              <CardTitle>Informações</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-muted-foreground text-xs">ID</Label>
                <p className="font-medium">#{denuncia.id}</p>
              </div>
              <div>
                <Label className="text-muted-foreground text-xs">UUID</Label>
                <p className="font-mono text-xs">{denuncia.uuid}</p>
              </div>
              <div>
                <Label className="text-muted-foreground text-xs">Criado em</Label>
                <p className="font-medium">
                  {format(new Date(denuncia.created_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground text-xs">Atualizado em</Label>
                <p className="font-medium">
                  {format(new Date(denuncia.updated_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Card de Ações */}
          <Card>
            <CardHeader>
              <CardTitle>Ações</CardTitle>
              <CardDescription>Gerencie esta denúncia</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {/* Ações para o criador */}
              {podeEditar && (
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => setEditDialog(true)}
                >
                  <Edit className="mr-2 h-4 w-4" />
                  Editar Denúncia
                </Button>
              )}

              {podeDeletar && (
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => setDeleteDialog(true)}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Deletar Denúncia
                </Button>
              )}

              {/* Ações para admin/fiscal */}
              {isAdminOuFiscal && (
                <>
                  <Button 
                    className="w-full justify-start" 
                    variant="outline"
                    onClick={() => setStatusDialog(true)}
                  >
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Alterar Status
                  </Button>

                  {denuncia.status === "pendente" && (
                    <Button 
                      className="w-full justify-start" 
                      variant="default"
                      onClick={() => setFiscalizacaoDialog(true)}
                    >
                      <Send className="mr-2 h-4 w-4" />
                      Enviar para Fiscalização
                    </Button>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Dialog - Editar Denúncia */}
      <Dialog open={editDialog} onOpenChange={setEditDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Editar Denúncia</DialogTitle>
            <DialogDescription>
              Atualize as informações da denúncia
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="prioridade">Prioridade</Label>
              <Select value={prioridadeEdit} onValueChange={(value) => setPrioridadeEdit(value as Prioridade)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {prioridadeOptions.map((prioridade) => (
                    <SelectItem key={prioridade.value} value={prioridade.value}>
                      {prioridade.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="observacao">Descrição</Label>
              <Textarea
                id="observacao"
                value={observacaoEdit}
                onChange={(e) => setObservacaoEdit(e.target.value)}
                rows={6}
                placeholder="Descreva o problema..."
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialog(false)} disabled={submitting}>
              Cancelar
            </Button>
            <Button onClick={handleEditar} disabled={submitting}>
              {submitting ? "Salvando..." : "Salvar Alterações"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog - Deletar Denúncia */}
      <Dialog open={deleteDialog} onOpenChange={setDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Exclusão</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja deletar esta denúncia? Esta ação não pode ser desfeita.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialog(false)} disabled={submitting}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeletar} disabled={submitting}>
              {submitting ? "Deletando..." : "Deletar Denúncia"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog - Alterar Status (Admin/Fiscal) */}
      <Dialog open={statusDialog} onOpenChange={setStatusDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Alterar Status</DialogTitle>
            <DialogDescription>
              Atualize o status desta denúncia
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="status">Novo Status</Label>
              <Select value={novoStatus} onValueChange={(value) => setNovoStatus(value as StatusDenuncia)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((status) => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setStatusDialog(false)} disabled={submitting}>
              Cancelar
            </Button>
            <Button onClick={handleAtualizarStatus} disabled={submitting}>
              {submitting ? "Atualizando..." : "Atualizar Status"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog - Enviar para Fiscalização */}
      <Dialog open={fiscalizacaoDialog} onOpenChange={setFiscalizacaoDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Enviar para Fiscalização</DialogTitle>
            <DialogDescription>
              Criar uma nova fiscalização para esta denúncia
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="data-conclusao-fisc">Data de Conclusão Prevista (Opcional)</Label>
              <Input
                id="data-conclusao-fisc"
                type="date"
                value={dataConclusaoFiscalizacao}
                onChange={(e) => setDataConclusaoFiscalizacao(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="observacoes-fisc">Observações (Opcional)</Label>
              <Textarea
                id="observacoes-fisc"
                placeholder="Adicione observações sobre a fiscalização..."
                value={observacoesFiscalizacao}
                onChange={(e) => setObservacoesFiscalizacao(e.target.value)}
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
            <Button onClick={handleEnviarParaFiscalizacao} disabled={submitting}>
              {submitting ? "Enviando..." : "Confirmar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
