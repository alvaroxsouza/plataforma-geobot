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
import { servicoDenuncias, DenunciaResposta, StatusDenuncia } from "@/services/denuncias";
import { fiscalizacaoService } from "@/services/fiscalizacao";
import { usuarioService, Usuario } from "@/services/usuarios";
import { toast } from "sonner";
import { useMetadata } from "@/hooks/useMetadata";



export default function GerenciarDenunciasPage() {
  const router = useRouter();
  
  // Metadados do sistema
  const {
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    loading: metadataLoading,
  } = useMetadata();
  
  const [denuncias, setDenuncias] = useState<DenunciaResposta[]>([]);
  const [loading, setLoading] = useState(true);
  const [buscaQuery, setBuscaQuery] = useState("");
  
  // Paginação
  const [paginaAtual, setPaginaAtual] = useState(1);
  const [itensPorPagina] = useState(20);
  const [totalItens, setTotalItens] = useState(0);
  
  // Dialog de enviar para fiscalização
  const [fiscalizacaoDialog, setFiscalizacaoDialog] = useState(false);
  const [denunciaSelecionada, setDenunciaSelecionada] = useState<DenunciaResposta | null>(null);
  const [observacoes, setObservacoes] = useState("");
  const [dataConclusao, setDataConclusao] = useState("");
  const [fiscalSelecionado, setFiscalSelecionado] = useState<string>("");
  const [fiscaisDisponiveis, setFiscaisDisponiveis] = useState<Usuario[]>([]);
  const [submitting, setSubmitting] = useState(false);

  // Carregar denúncias
  const carregarDenuncias = async () => {
    try {
      setLoading(true);
      const offset = (paginaAtual - 1) * itensPorPagina;
      const response = await servicoDenuncias.listar({
        todas: true,
        limit: itensPorPagina,
        offset: offset,
      });
      setDenuncias(response.data);
      setTotalItens(response.pagination.total);
    } catch (error) {
      console.error("Erro ao carregar denúncias:", error);
      toast.error("Erro ao carregar denúncias");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDenuncias();
  }, [paginaAtual]);

  // Carregar fiscais disponíveis
  useEffect(() => {
    const carregarFiscais = async () => {
      try {
        const fiscais = await usuarioService.listarFiscais();
        setFiscaisDisponiveis(fiscais);
      } catch (error) {
        console.error("Erro ao carregar fiscais:", error);
      }
    };
    carregarFiscais();
  }, []);

  // Filtrar denúncias pela busca
  const denunciasFiltradas = denuncias.filter(denuncia => 
    denuncia.id.toString().includes(buscaQuery) ||
    denuncia.endereco.logradouro.toLowerCase().includes(buscaQuery.toLowerCase()) ||
    denuncia.observacao.toLowerCase().includes(buscaQuery.toLowerCase()) ||
    denuncia.usuario.nome.toLowerCase().includes(buscaQuery.toLowerCase())
  );

  // Abrir dialog de fiscalização
  const handleEnviarParaFiscalizacao = (denuncia: DenunciaResposta) => {
    setDenunciaSelecionada(denuncia);
    setObservacoes("");
    setDataConclusao("");
    setFiscalizacaoDialog(true);
  };

  // Confirmar envio para fiscalização
  const handleConfirmarFiscalizacao = async () => {
    if (!denunciaSelecionada) return;

    try {
      setSubmitting(true);
      
      // Criar fiscalização
      const fiscalizacao = await fiscalizacaoService.create({
        complaint_id: denunciaSelecionada.id,
        observacoes: observacoes || null,
        data_conclusao_prevista: dataConclusao || null,
      });

      // Se um fiscal foi selecionado, atribuir a fiscalização
      if (fiscalSelecionado) {
        try {
          await fiscalizacaoService.assign(fiscalizacao.id, {
            fiscal_id: parseInt(fiscalSelecionado),
          });
          toast.success("Denúncia enviada e fiscal atribuído com sucesso!");
        } catch (error) {
          console.error("Erro ao atribuir fiscal:", error);
          toast.warning("Fiscalização criada, mas erro ao atribuir fiscal");
        }
      } else {
        toast.success("Denúncia enviada para fiscalização com sucesso!");
      }

      setFiscalizacaoDialog(false);
      setDenunciaSelecionada(null);
      setObservacoes("");
      setDataConclusao("");
      setFiscalSelecionado("");
      
      // Recarregar denúncias
      await carregarDenuncias();
    } catch (error) {
      console.error("Erro ao criar fiscalização:", error);
      toast.error("Erro ao enviar denúncia para fiscalização");
    } finally {
      setSubmitting(false);
    }
  };

  // Cálculos de paginação
  const totalPaginas = Math.ceil(totalItens / itensPorPagina);
  const temPaginaAnterior = paginaAtual > 1;
  const temProximaPagina = paginaAtual < totalPaginas;

  // Estatísticas
  const stats = [
    { 
      label: "Total", 
      value: totalItens,
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
                {denunciasFiltradas.length} denúncia(s) encontrada(s)
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar denúncias..."
                  value={buscaQuery}
                  onChange={(e) => setBuscaQuery(e.target.value)}
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
          {(loading || metadataLoading) ? (
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
                  {denunciasFiltradas.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        Nenhuma denúncia encontrada
                      </TableCell>
                    </TableRow>
                  ) : (
                    denunciasFiltradas.map((denuncia) => (
                      <TableRow key={denuncia.id} className="hover:bg-muted/50">
                        <TableCell className="font-medium">#{denuncia.id}</TableCell>
                        <TableCell>
                          <div className="max-w-[300px]">
                            <div className="font-medium truncate">{denuncia.endereco.logradouro}</div>
                            <div className="text-sm text-muted-foreground truncate">
                              {denuncia.endereco.bairro}, {denuncia.endereco.cidade}/{denuncia.endereco.estado}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="capitalize">{getCategoriaLabel(denuncia.categoria)}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(denuncia.status)}>
                            {getStatusLabel(denuncia.status)}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">{denuncia.usuario.nome}</TableCell>
                        <TableCell className="text-sm">
                          {new Date(denuncia.created_at).toLocaleDateString("pt-BR")}
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
                                onClick={() => router.push(`/dashboard/denuncias/${denuncia.id}`)}
                              >
                                <Eye className="mr-2 h-4 w-4" />
                                Ver Detalhes
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => handleEnviarParaFiscalizacao(denuncia)}
                                disabled={
                                  denuncia.status === "em_fiscalizacao" || 
                                  denuncia.status === "concluida" ||
                                  denuncia.status === "arquivada" ||
                                  denuncia.status === "cancelada"
                                }
                              >
                                <Send className="mr-2 h-4 w-4" />
                                Enviar para Fiscalização
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
          )}
          
          {/* Controles de Paginação */}
          {!loading && totalPaginas > 1 && (
            <div className="flex items-center justify-between px-2 py-4">
              <div className="text-sm text-muted-foreground">
                Mostrando {((paginaAtual - 1) * itensPorPagina) + 1} a {Math.min(paginaAtual * itensPorPagina, totalItens)} de {totalItens} denúncias
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginaAtual(prev => Math.max(1, prev - 1))}
                  disabled={!temPaginaAnterior}
                >
                  Anterior
                </Button>
                <div className="flex items-center gap-2 px-3">
                  <span className="text-sm">
                    Página {paginaAtual} de {totalPaginas}
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginaAtual(prev => Math.min(totalPaginas, prev + 1))}
                  disabled={!temProximaPagina}
                >
                  Próxima
                </Button>
              </div>
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
              Criar uma nova fiscalização para a denúncia #{denunciaSelecionada?.id}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="fiscal">Fiscal Responsável (Opcional)</Label>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="w-full justify-between">
                    {fiscalSelecionado
                      ? fiscaisDisponiveis.find((f) => f.id.toString() === fiscalSelecionado)?.nome
                      : "Selecionar Fiscal"}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-full">
                  <DropdownMenuLabel>Fiscais Disponíveis</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => setFiscalSelecionado("")}>
                    Nenhum (atribuir depois)
                  </DropdownMenuItem>
                  {fiscaisDisponiveis.map((fiscal) => (
                    <DropdownMenuItem
                      key={fiscal.id}
                      onClick={() => setFiscalSelecionado(fiscal.id.toString())}
                    >
                      {fiscal.nome} - {fiscal.email}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

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
