"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { MapPin, Upload, X, Loader2, Home, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Link from "next/link";
import { servicoDenuncias } from "@/services/denuncias";
import { CategoriaDenuncia, Prioridade } from "@/lib/types/denuncia";

export default function NovaDenunciaPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [images, setImages] = useState<File[]>([]);
  
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

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newImages = Array.from(e.target.files);
      setImages([...images, ...newImages]);
    }
  };

  const removeImage = (index: number) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validar campos obrigatórios
      if (!formData.categoria || !formData.observacao || !formData.logradouro || 
          !formData.bairro || !formData.cidade || !formData.estado || !formData.cep) {
        alert("Por favor, preencha todos os campos obrigatórios.");
        setIsLoading(false);
        return;
      }

      // Criar denúncia
      const novaDenuncia = await servicoDenuncias.criar(formData);
      
      console.log("Denúncia criada com sucesso:", novaDenuncia);
      alert("Denúncia criada com sucesso!");
      
      // Redirecionar para a página de denúncias
      router.push("/dashboard/denuncias");
    } catch (error) {
      console.error("Erro ao criar denúncia:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro desconhecido";
      alert(`Erro ao criar denúncia: ${errorMessage}`);
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
                  <Input
                    id="estado"
                    placeholder="UF"
                    maxLength={2}
                    value={formData.estado}
                    onChange={(e) => setFormData({...formData, estado: e.target.value.toUpperCase()})}
                    required
                  />
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

              <Button type="button" variant="outline" className="w-full gap-2">
                <MapPin className="h-4 w-4" />
                Usar Minha Localização Atual
              </Button>
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
