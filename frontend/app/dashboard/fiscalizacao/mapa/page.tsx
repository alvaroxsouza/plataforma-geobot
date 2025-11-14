"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Home, ChevronRight, MapPin } from "lucide-react";
import Link from "next/link";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { fiscalizacaoService, FiscalizacaoResponse } from "@/services/fiscalizacao";
import { servicoDenuncias, DenunciaResposta } from "@/services/denuncias";
import { toast } from "sonner";

interface FiscalizacaoComDenuncia extends FiscalizacaoResponse {
  denuncia?: DenunciaResposta;
}

// Importar componentes do mapa dinamicamente
const MapContainer = dynamic(() => import("react-leaflet").then((mod) => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((mod) => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import("react-leaflet").then((mod) => mod.Marker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), { ssr: false });

// Ícone customizado para o marcador
const fiscalizacaoIcon = typeof window !== 'undefined' ? L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
}) : null;

export default function MapaFiscalizacaoPage() {
  const [fiscalizacoes, setFiscalizacoes] = useState<FiscalizacaoComDenuncia[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    carregarFiscalizacoes();
  }, []);

  const carregarFiscalizacoes = async () => {
    try {
      setIsLoading(true);
      
      // Buscar todas as fiscalizações
      const fiscalizacoesResponse = await fiscalizacaoService.getAll({ limit: 1000 });
      
      // Buscar todas as denúncias
      const denunciasResponse = await servicoDenuncias.listar({ todas: true, limit: 10000 });
      
      // Criar mapa de denúncias por ID
      const denunciasMap = new Map<number, DenunciaResposta>();
      denunciasResponse.data.forEach((denuncia) => {
        denunciasMap.set(denuncia.id, denuncia);
      });
      
      // Associar denúncias às fiscalizações
      const fiscalizacoesComDenuncia: FiscalizacaoComDenuncia[] = fiscalizacoesResponse.map((fisc) => ({
        ...fisc,
        denuncia: denunciasMap.get(fisc.complaint_id),
      }));
      
      // Filtrar apenas fiscalizações com denúncias que tenham coordenadas
      const fiscalizacoesComLocalizacao = fiscalizacoesComDenuncia.filter(
        (fisc) => fisc.denuncia?.endereco?.latitude && fisc.denuncia?.endereco?.longitude
      );
      
      setFiscalizacoes(fiscalizacoesComLocalizacao);
      
      if (fiscalizacoesComLocalizacao.length === 0) {
        toast.info("Nenhuma fiscalização com localização encontrada");
      }
    } catch (error: any) {
      console.error("Erro ao carregar fiscalizações:", error);
      toast.error(error?.response?.data?.detail || "Erro ao carregar fiscalizações");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'AGUARDANDO_SOBREVOO': 'bg-yellow-100 text-yellow-800',
      'AGUARDANDO_INFERENCIA': 'bg-blue-100 text-blue-800',
      'GERANDO_RELATORIO': 'bg-purple-100 text-purple-800',
      'CONCLUIDA': 'bg-green-100 text-green-800',
      'CANCELADA': 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'AGUARDANDO_SOBREVOO': 'Aguardando Sobrevoo',
      'AGUARDANDO_INFERENCIA': 'Aguardando Inferência',
      'GERANDO_RELATORIO': 'Gerando Relatório',
      'CONCLUIDA': 'Concluída',
      'CANCELADA': 'Cancelada',
    };
    return labels[status] || status;
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
        <span className="text-foreground font-medium">Mapa</span>
      </div>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <MapPin className="h-8 w-8" />
          Mapa de Fiscalizações
        </h1>
        <p className="text-muted-foreground">
          Visualize todas as fiscalizações no mapa
        </p>
      </div>

      {/* Mapa */}
      <Card>
        <CardHeader>
          <CardTitle>Localização das Fiscalizações</CardTitle>
          <CardDescription>
            {isLoading ? (
              "Carregando fiscalizações..."
            ) : (
              `${fiscalizacoes.length} fiscalização(ões) com localização definida`
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center h-[600px]">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            isMounted && (
              <div className="h-[600px] rounded-lg overflow-hidden border">
                <MapContainer
                  center={[-9.6498, -35.7089]} // Maceió-AL
                  zoom={13}
                  style={{ height: "100%", width: "100%" }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {fiscalizacoes.map((fiscalizacao) => {
                    if (!fiscalizacao.denuncia?.endereco?.latitude || !fiscalizacao.denuncia?.endereco?.longitude) {
                      return null;
                    }
                    
                    return (
                      <Marker
                        key={fiscalizacao.id}
                        position={[fiscalizacao.denuncia.endereco.latitude, fiscalizacao.denuncia.endereco.longitude]}
                        icon={fiscalizacaoIcon || undefined}
                      >
                        <Popup>
                          <div className="p-2">
                            <h3 className="font-semibold mb-2">
                              Fiscalização #{fiscalizacao.id}
                            </h3>
                            <div className="space-y-1 text-sm">
                              <p>
                                <strong>Denúncia:</strong> #{fiscalizacao.complaint_id}
                              </p>
                              <p>
                                <strong>Status:</strong>{" "}
                                <span className={`px-2 py-0.5 rounded text-xs ${getStatusColor(fiscalizacao.status_fiscalizacao)}`}>
                                  {getStatusLabel(fiscalizacao.status_fiscalizacao)}
                                </span>
                              </p>
                              {fiscalizacao.denuncia.endereco.logradouro && (
                                <p>
                                  <strong>Local:</strong>{" "}
                                  {fiscalizacao.denuncia.endereco.logradouro}
                                  {fiscalizacao.denuncia.endereco.numero && `, ${fiscalizacao.denuncia.endereco.numero}`}
                                </p>
                              )}
                              {fiscalizacao.denuncia.endereco.bairro && (
                                <p>
                                  <strong>Bairro:</strong> {fiscalizacao.denuncia.endereco.bairro}
                                </p>
                              )}
                              {fiscalizacao.fiscais && fiscalizacao.fiscais.length > 0 && (
                                <p>
                                  <strong>Fiscal:</strong> {fiscalizacao.fiscais[0].nome}
                                </p>
                              )}
                              <Link
                                href={`/dashboard/fiscalizacao/${fiscalizacao.id}`}
                                className="text-blue-600 hover:underline inline-block mt-2"
                              >
                                Ver detalhes →
                              </Link>
                            </div>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  })}
                </MapContainer>
              </div>
            )
          )}
        </CardContent>
      </Card>
    </div>
  );
}
