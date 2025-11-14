"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import dynamic from "next/dynamic";
import { MapPin, Upload, X, Loader2, Home, ChevronRight, Navigation } from "lucide-react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Link from "next/link";
import { servicoDenuncias } from "@/services/denuncias";
import { CategoriaDenuncia, Prioridade } from "@/lib/types/denuncia";
import { toast } from "sonner";

// Importar o mapa dinamicamente para evitar SSR
const MapContainer = dynamic(() => import("react-leaflet").then((mod) => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((mod) => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import("react-leaflet").then((mod) => mod.Marker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), { ssr: false });
const useMapEvents = dynamic(() => import("react-leaflet").then((mod) => mod.useMapEvents), { ssr: false });

// Ícone customizado para o marcador
const customIcon = typeof window !== 'undefined' ? L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
}) : null;

// Componente para capturar cliques no mapa
function MapClickHandler({ onLocationSelect }: { onLocationSelect: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function NovaDenunciaPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isGeocodingLoading, setIsGeocodingLoading] = useState(false);
  const [images, setImages] = useState<File[]>([]);
  const [isMounted, setIsMounted] = useState(false);
  
  const [formData, setFormData] = useState({
    categoria: "" as CategoriaDenuncia,
    prioridade: "media" as Prioridade,
    observacao: "",
    logradouro: "",
    numero: "",
    complemento: "",
    bairro: "",
    cidade: "",
    estado: "",
    cep: "",
    latitude: undefined as number | undefined,
    longitude: undefined as number | undefined,
  });

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const categorias = [
    { value: "calcada", label: "Calçada" },
    { value: "rua", label: "Rua" },
    { value: "ciclovia", label: "Ciclovia" },
    { value: "semaforo", label: "Semáforo" },
    { value: "sinalizacao", label: "Sinalização" },
    { value: "iluminacao", label: "Iluminação" },
    { value: "lixo_entulho", label: "Lixo e Entulho" },
    { value: "poluicao", label: "Poluição" },
    { value: "barulho", label: "Barulho" },
    { value: "outros", label: "Outros" },
  ];

  const prioridades = [
    { value: "baixa", label: "Baixa" },
    { value: "media", label: "Média" },
    { value: "alta", label: "Alta" },
    { value: "urgente", label: "Urgente" },
  ];

  const estados = [
    { value: "AC", label: "Acre" },
    { value: "AL", label: "Alagoas" },
    { value: "AP", label: "Amapá" },
    { value: "AM", label: "Amazonas" },
    { value: "BA", label: "Bahia" },
    { value: "CE", label: "Ceará" },
    { value: "DF", label: "Distrito Federal" },
    { value: "ES", label: "Espírito Santo" },
    { value: "GO", label: "Goiás" },
    { value: "MA", label: "Maranhão" },
    { value: "MT", label: "Mato Grosso" },
    { value: "MS", label: "Mato Grosso do Sul" },
    { value: "MG", label: "Minas Gerais" },
    { value: "PA", label: "Pará" },
    { value: "PB", label: "Paraíba" },
    { value: "PR", label: "Paraná" },
    { value: "PE", label: "Pernambuco" },
    { value: "PI", label: "Piauí" },
    { value: "RJ", label: "Rio de Janeiro" },
    { value: "RN", label: "Rio Grande do Norte" },
    { value: "RS", label: "Rio Grande do Sul" },
    { value: "RO", label: "Rondônia" },
    { value: "RR", label: "Roraima" },
    { value: "SC", label: "Santa Catarina" },
    { value: "SP", label: "São Paulo" },
    { value: "SE", label: "Sergipe" },
    { value: "TO", label: "Tocantins" },
  ];

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newImages = Array.from(e.target.files);
      setImages([...images, ...newImages]);
    }
  };

  const removeImage = (index: number) => {
    setImages(images.filter((_, i) => i !== index));
  };

  // Função para geocodificar endereço usando Nominatim (OpenStreetMap)
  const geocodeAddress = async () => {
    if (!formData.logradouro || !formData.cidade || !formData.estado) {
      toast.error("Preencha pelo menos logradouro, cidade e estado para buscar a localização");
      return;
    }

    setIsGeocodingLoading(true);
    try {
      // Construir query de endereço
      const addressParts = [
        formData.numero && `${formData.numero}`,
        formData.logradouro,
        formData.bairro,
        formData.cidade,
        formData.estado,
        "Brasil"
      ].filter(Boolean);
      
      const address = addressParts.join(", ");
      
      // Fazer requisição para Nominatim
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`
      );
      
      const data = await response.json();
      
      if (data && data.length > 0) {
        const lat = parseFloat(data[0].lat);
        const lon = parseFloat(data[0].lon);
        
        setFormData({
          ...formData,
          latitude: lat,
          longitude: lon,
        });
        
        toast.success("Localização encontrada no mapa!");
      } else {
        toast.error("Não foi possível encontrar a localização deste endereço. Tente clicar no mapa.");
      }
    } catch (error) {
      console.error("Erro ao geocodificar endereço:", error);
      toast.error("Erro ao buscar localização. Tente clicar no mapa.");
    } finally {
      setIsGeocodingLoading(false);
    }
  };

  // Função para fazer reverse geocoding (coordenadas -> endereço)
  const reverseGeocode = async (lat: number, lng: number) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`
      );
      
      const data = await response.json();
      
      if (data && data.address) {
        const addr = data.address;
        
        // Atualizar campos do formulário com os dados do endereço
        setFormData(prev => ({
          ...prev,
          latitude: lat,
          longitude: lng,
          logradouro: addr.road || prev.logradouro,
          numero: addr.house_number || prev.numero,
          bairro: addr.suburb || addr.neighbourhood || prev.bairro,
          cidade: addr.city || addr.town || addr.municipality || prev.cidade,
          estado: addr.state_code?.toUpperCase() || prev.estado,
          cep: addr.postcode || prev.cep,
        }));
        
        return true;
      }
      return false;
    } catch (error) {
      console.error("Erro ao fazer reverse geocoding:", error);
      return false;
    }
  };

  // Função para usar geolocalização do navegador
  const useCurrentLocation = async () => {
    if (!navigator.geolocation) {
      toast.error("Geolocalização não é suportada pelo seu navegador");
      return;
    }

    toast.info("Obtendo sua localização...");
    
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        
        // Fazer reverse geocoding para preencher o endereço
        const success = await reverseGeocode(lat, lng);
        
        if (success) {
          toast.success("Localização e endereço obtidos com sucesso!");
        } else {
          // Se falhar o reverse geocoding, apenas definir as coordenadas
          setFormData(prev => ({
            ...prev,
            latitude: lat,
            longitude: lng,
          }));
          toast.success("Localização atual definida no mapa!");
        }
      },
      (error) => {
        console.error("Erro ao obter localização:", error);
        toast.error("Não foi possível obter sua localização. Verifique as permissões do navegador.");
      }
    );
  };

  // Função para lidar com clique no mapa
  const handleMapClick = async (lat: number, lng: number) => {
    // Fazer reverse geocoding para preencher o endereço
    const success = await reverseGeocode(lat, lng);
    
    if (success) {
      toast.success("Localização marcada e endereço preenchido!");
    } else {
      // Se falhar o reverse geocoding, apenas definir as coordenadas
      setFormData(prev => ({
        ...prev,
        latitude: lat,
        longitude: lng,
      }));
      toast.success("Localização marcada no mapa!");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validar campos obrigatórios
      if (!formData.categoria || !formData.observacao || !formData.logradouro || 
          !formData.bairro || !formData.cidade || !formData.estado || !formData.cep) {
        toast.error("Por favor, preencha todos os campos obrigatórios.");
        setIsLoading(false);
        return;
      }

      // Avisar se localização não foi definida
      if (!formData.latitude || !formData.longitude) {
        toast.warning("Localização não definida. Use os botões 'Buscar no Mapa' ou 'Minha Localização', ou clique no mapa.");
      }

      // Criar denúncia
      const novaDenuncia = await servicoDenuncias.criar(formData);
      
      console.log("Denúncia criada com sucesso:", novaDenuncia);
      toast.success("Denúncia criada com sucesso!");
      
      // Redirecionar para a página de denúncias
      setTimeout(() => {
        router.push("/dashboard/denuncias");
      }, 1000);
    } catch (error) {
      console.error("Erro ao criar denúncia:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro desconhecido";
      toast.error(`Erro ao criar denúncia: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

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
        <span className="text-foreground font-medium">Nova Denúncia</span>
      </div>

      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Nova Denúncia</h1>
          <p className="text-muted-foreground">
            Preencha o formulário abaixo para registrar uma nova denúncia
          </p>
        </div>
        <Link href="/dashboard/denuncias">
          <Button variant="outline">Voltar para Denúncias</Button>
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-3">
        {/* Informações Básicas */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações da Denúncia</CardTitle>
              <CardDescription>
                Descreva o problema identificado
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="categoria">Categoria *</Label>
                <Select
                  value={formData.categoria}
                  onValueChange={(value) => setFormData({...formData, categoria: value as CategoriaDenuncia})}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione uma categoria" />
                  </SelectTrigger>
                  <SelectContent>
                    {categorias.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="prioridade">Prioridade *</Label>
                <Select
                  value={formData.prioridade}
                  onValueChange={(value) => setFormData({...formData, prioridade: value as Prioridade})}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a prioridade" />
                  </SelectTrigger>
                  <SelectContent>
                    {prioridades.map((prior) => (
                      <SelectItem key={prior.value} value={prior.value}>
                        {prior.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="observacao">Descrição/Observação *</Label>
                <Textarea
                  id="observacao"
                  placeholder="Descreva o problema em detalhes..."
                  value={formData.observacao}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({...formData, observacao: e.target.value})}
                  rows={6}
                  required
                />
              </div>
            </CardContent>
          </Card>

          {/* Localização */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Localização
              </CardTitle>
              <CardDescription>
                Informe onde o problema está localizado
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="logradouro">Logradouro (Rua/Avenida) *</Label>
                <Input
                  id="logradouro"
                  placeholder="Ex: Rua das Flores"
                  value={formData.logradouro}
                  onChange={(e) => setFormData({...formData, logradouro: e.target.value})}
                  required
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="numero">Número</Label>
                  <Input
                    id="numero"
                    placeholder="123"
                    value={formData.numero}
                    onChange={(e) => setFormData({...formData, numero: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="complemento">Complemento</Label>
                  <Input
                    id="complemento"
                    placeholder="Apto 101"
                    value={formData.complemento}
                    onChange={(e) => setFormData({...formData, complemento: e.target.value})}
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="bairro">Bairro *</Label>
                  <Input
                    id="bairro"
                    placeholder="Nome do bairro"
                    value={formData.bairro}
                    onChange={(e) => setFormData({...formData, bairro: e.target.value})}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cidade">Cidade *</Label>
                  <Input
                    id="cidade"
                    placeholder="Nome da cidade"
                    value={formData.cidade}
                    onChange={(e) => setFormData({...formData, cidade: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="estado">Estado *</Label>
                  <Select
                    value={formData.estado}
                    onValueChange={(value) => setFormData({...formData, estado: value})}
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o estado" />
                    </SelectTrigger>
                    <SelectContent className="max-h-[300px] z-[9999]">
                      {estados.map((estado) => (
                        <SelectItem key={estado.value} value={estado.value}>
                          {estado.label} ({estado.value})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cep">CEP *</Label>
                  <Input
                    id="cep"
                    placeholder="00000-000"
                    value={formData.cep}
                    onChange={(e) => setFormData({...formData, cep: e.target.value})}
                    required
                  />
                </div>
              </div>

              {/* Mapa Interativo */}
              {isMounted && (
                <div className="mt-6 pt-6 border-t">
                  <Label className="mb-2 block text-base font-semibold">
                    📍 Localização no Mapa {formData.latitude && formData.longitude && "✓"}
                  </Label>
                  <p className="text-sm text-muted-foreground mb-4">
                    Clique no mapa para marcar a localização exata ou use os botões abaixo
                  </p>
                  
                  <div className="grid gap-2 md:grid-cols-2 mb-4">
                    <Button 
                      type="button" 
                      variant="outline" 
                      className="gap-2"
                      onClick={geocodeAddress}
                      disabled={isGeocodingLoading}
                    >
                      {isGeocodingLoading ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Buscando...
                        </>
                      ) : (
                        <>
                          <MapPin className="h-4 w-4" />
                          Buscar no Mapa
                        </>
                      )}
                    </Button>
                    
                    <Button 
                      type="button" 
                      variant="outline" 
                      className="gap-2"
                      onClick={useCurrentLocation}
                    >
                      <Navigation className="h-4 w-4" />
                      Minha Localização
                    </Button>
                  </div>

                  <div className="h-[350px] rounded-lg overflow-hidden border shadow-sm relative z-0">
                    <MapContainer
                      center={[
                        formData.latitude || -9.6498, 
                        formData.longitude || -35.7089
                      ]}
                      zoom={formData.latitude && formData.longitude ? 16 : 13}
                      style={{ height: "100%", width: "100%" }}
                      key={`${formData.latitude}-${formData.longitude}`}
                    >
                      <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      />
                      {formData.latitude && formData.longitude && customIcon && (
                        <Marker 
                          position={[formData.latitude, formData.longitude]}
                          icon={customIcon}
                        >
                          <Popup>
                            📍 Localização da Denúncia<br />
                            <strong>Lat:</strong> {formData.latitude.toFixed(6)}<br />
                            <strong>Lng:</strong> {formData.longitude.toFixed(6)}
                          </Popup>
                        </Marker>
                      )}
                      <MapClickHandler onLocationSelect={handleMapClick} />
                    </MapContainer>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Imagens */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Imagens
              </CardTitle>
              <CardDescription>
                Adicione fotos que evidenciem o problema (opcional)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                  id="image-upload"
                />
                <label htmlFor="image-upload" className="cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-sm font-medium mb-1">
                    Clique para fazer upload ou arraste as imagens
                  </p>
                  <p className="text-xs text-muted-foreground">
                    PNG, JPG ou WEBP até 10MB cada
                  </p>
                </label>
              </div>

              {images.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {images.map((image, index) => (
                    <div key={index} className="relative group">
                      <div className="relative w-full h-32">
                        <Image
                          src={URL.createObjectURL(image)}
                          alt={`Preview ${index + 1}`}
                          fill
                          className="object-cover rounded-lg"
                        />
                      </div>
                      <Button
                        type="button"
                        variant="destructive"
                        size="icon"
                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeImage(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar - Resumo e Ações */}
        <div className="space-y-6">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle>Resumo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="font-medium">Nova</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Imagens:</span>
                  <span className="font-medium">{images.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Localização:</span>
                  <span className={`font-medium ${formData.latitude && formData.longitude ? 'text-green-600' : 'text-amber-600'}`}>
                    {formData.latitude && formData.longitude ? '✓ Definida' : '⚠ Não definida'}
                  </span>
                </div>
              </div>

              <div className="pt-4 space-y-2">
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Criando...
                    </>
                  ) : (
                    "Criar Denúncia"
                  )}
                </Button>
                <Link href="/dashboard/denuncias" className="block">
                  <Button type="button" variant="outline" className="w-full">
                    Cancelar
                  </Button>
                </Link>
              </div>

              <div className="pt-4 border-t text-xs text-muted-foreground">
                <p>* Campos obrigatórios</p>
                <p className="mt-1">
                  Após criar, a denúncia será analisada pela equipe responsável.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>
    </div>
  );
}
