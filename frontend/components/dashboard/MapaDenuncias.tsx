"use client";

import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { Icon, LatLngBounds } from "leaflet";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, MapPin, User, ExternalLink } from "lucide-react";
import { DenunciaResposta } from "@/services/denuncias";
import "leaflet/dist/leaflet.css";

// Fix para ícones do Leaflet no Next.js
delete (Icon.Default.prototype as any)._getIconUrl;
Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

interface MapaDenunciasProps {
  denuncias: DenunciaResposta[];
  getStatusColor: (status: string) => string;
  getStatusLabel: (status: string) => string;
  getCategoriaLabel: (categoria: string) => string;
  getPrioridadeColor: (prioridade: string) => string;
}

// Componente auxiliar para ajustar o mapa aos marcadores
function FitBounds({ denuncias }: { denuncias: DenunciaResposta[] }) {
  const map = useMap();

  useEffect(() => {
    if (denuncias.length === 0) {
      // Centrar no Brasil se não houver denúncias
      map.setView([-15.7975, -47.8919], 4);
      return;
    }

    if (denuncias.length === 1) {
      // Se houver apenas uma denúncia, centralizar nela
      const denuncia = denuncias[0];
      map.setView([denuncia.endereco.latitude!, denuncia.endereco.longitude!], 14);
      return;
    }

    // Se houver múltiplas denúncias, ajustar para mostrar todas
    const bounds = new LatLngBounds(
      denuncias.map((d) => [d.endereco.latitude!, d.endereco.longitude!])
    );
    map.fitBounds(bounds, { padding: [50, 50] });
  }, [denuncias, map]);

  return null;
}

// Criar ícones customizados por status
const createCustomIcon = (status: string): Icon => {
  let color = "#6b7280"; // gray (padrão)
  
  switch (status) {
    case "pendente":
      color = "#eab308"; // yellow
      break;
    case "em_analise":
      color = "#3b82f6"; // blue
      break;
    case "em_fiscalizacao":
      color = "#a855f7"; // purple
      break;
    case "concluida":
      color = "#22c55e"; // green
      break;
    case "arquivada":
      color = "#9ca3af"; // gray
      break;
    case "cancelada":
      color = "#ef4444"; // red
      break;
  }

  // SVG customizado para o marcador
  const svgIcon = `
    <svg width="32" height="42" viewBox="0 0 32 42" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 0C7.163 0 0 7.163 0 16c0 8.837 16 26 16 26s16-17.163 16-26C32 7.163 24.837 0 16 0z" 
            fill="${color}" stroke="#fff" stroke-width="2"/>
      <circle cx="16" cy="16" r="6" fill="#fff"/>
    </svg>
  `;

  return new Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(svgIcon)}`,
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -42],
  });
};

export default function MapaDenuncias({
  denuncias,
  getStatusColor,
  getStatusLabel,
  getCategoriaLabel,
  getPrioridadeColor,
}: MapaDenunciasProps) {
  const router = useRouter();

  // Coordenadas padrão (centro do Brasil)
  const defaultCenter: [number, number] = [-15.7975, -47.8919];
  const defaultZoom = 4;

  const formatData = (dataString: string) => {
    return new Date(dataString).toLocaleDateString("pt-BR");
  };

  return (
    <div className="h-[600px] w-full rounded-lg overflow-hidden border">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <FitBounds denuncias={denuncias} />

        {denuncias.map((denuncia) => {
          if (!denuncia.endereco.latitude || !denuncia.endereco.longitude) {
            return null;
          }

          return (
            <Marker
              key={denuncia.id}
              position={[denuncia.endereco.latitude, denuncia.endereco.longitude]}
              icon={createCustomIcon(denuncia.status)}
            >
              <Popup maxWidth={300} minWidth={250}>
                <div className="p-2 space-y-3">
                  {/* Header */}
                  <div className="border-b pb-2">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h3 className="font-semibold text-sm line-clamp-2">
                        {getCategoriaLabel(denuncia.categoria)} - ID #{denuncia.id}
                      </h3>
                      <Badge
                        variant="outline"
                        className={`text-xs whitespace-nowrap ${getStatusColor(denuncia.status)}`}
                      >
                        {getStatusLabel(denuncia.status)}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-600">
                      UUID: <span className="font-mono font-semibold text-[10px]">{denuncia.uuid.slice(0, 18)}...</span>
                    </p>
                  </div>

                  {/* Detalhes */}
                  <div className="space-y-2 text-xs">
                    <div className="flex items-start gap-2">
                      <MapPin className="h-3.5 w-3.5 text-gray-500 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-700">Categoria</p>
                        <p className="text-gray-600">{getCategoriaLabel(denuncia.categoria)}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <Badge
                        variant="outline"
                        className={`text-xs ${getPrioridadeColor(denuncia.prioridade)}`}
                      >
                        Prioridade: {denuncia.prioridade.toUpperCase()}
                      </Badge>
                    </div>

                    <div className="flex items-start gap-2">
                      <Calendar className="h-3.5 w-3.5 text-gray-500 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-700">Data de Criação</p>
                        <p className="text-gray-600">{formatData(denuncia.created_at)}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <MapPin className="h-3.5 w-3.5 text-gray-500 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-700">Endereço</p>
                        <p className="text-gray-600 text-[11px] leading-tight">
                          {denuncia.endereco.logradouro}
                          {denuncia.endereco.numero && `, ${denuncia.endereco.numero}`}
                          {denuncia.endereco.bairro && ` - ${denuncia.endereco.bairro}`}
                        </p>
                        <p className="text-gray-600 text-[11px]">
                          {denuncia.endereco.cidade}/{denuncia.endereco.estado}
                        </p>
                      </div>
                    </div>

                    {denuncia.usuario && (
                      <div className="flex items-start gap-2">
                        <User className="h-3.5 w-3.5 text-gray-500 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-gray-700">Usuário</p>
                          <p className="text-gray-600">{denuncia.usuario.nome}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Ações */}
                  <div className="pt-2 border-t">
                    <Button
                      size="sm"
                      variant="default"
                      className="w-full text-xs h-8"
                      onClick={() => router.push(`/dashboard/denuncias/${denuncia.id}`)}
                    >
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Ver Detalhes Completos
                    </Button>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
