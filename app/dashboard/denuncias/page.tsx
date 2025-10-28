"use client";

import { useState } from "react";
import { Plus, Search, Filter, MapPin, Calendar, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Link from "next/link";

export default function DenunciasPage() {
  const [searchQuery, setSearchQuery] = useState("");

  // Dados mockados para demonstração
  const stats = [
    { 
      label: "Total de Denúncias", 
      value: "248", 
      change: "+12%", 
      changeType: "positive",
      icon: AlertCircle,
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    { 
      label: "Pendentes", 
      value: "42", 
      change: "-8%", 
      changeType: "negative",
      icon: AlertCircle,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50"
    },
    { 
      label: "Em Análise", 
      value: "18", 
      change: "+3", 
      changeType: "neutral",
      icon: AlertCircle,
      color: "text-orange-600",
      bgColor: "bg-orange-50"
    },
    { 
      label: "Resolvidas", 
      value: "188", 
      change: "+15%", 
      changeType: "positive",
      icon: AlertCircle,
      color: "text-green-600",
      bgColor: "bg-green-50"
    },
  ];

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Denúncias</h1>
          <p className="text-muted-foreground">
            Gerencie e acompanhe todas as denúncias da plataforma
          </p>
        </div>
        <Link href="/dashboard/denuncias/nova">
          <Button size="lg" className="gap-2">
            <Plus className="h-5 w-5" />
            Nova Denúncia
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.label}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className={`text-xs ${
                  stat.changeType === 'positive' 
                    ? 'text-green-600' 
                    : stat.changeType === 'negative' 
                    ? 'text-red-600' 
                    : 'text-muted-foreground'
                }`}>
                  {stat.change} em relação ao mês anterior
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Search and Filter */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Lista de Denúncias</CardTitle>
              <CardDescription>
                Visualize e gerencie todas as denúncias registradas
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar denúncias..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="todas" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="todas">Todas</TabsTrigger>
              <TabsTrigger value="pendentes">Pendentes</TabsTrigger>
              <TabsTrigger value="em_analise">Em Análise</TabsTrigger>
              <TabsTrigger value="fiscalizacao">Fiscalização</TabsTrigger>
              <TabsTrigger value="resolvidas">Resolvidas</TabsTrigger>
            </TabsList>

            <TabsContent value="todas" className="mt-6">
              <div className="text-center py-12">
                <AlertCircle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Nenhuma denúncia encontrada</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Comece criando sua primeira denúncia ou ajuste os filtros de busca
                </p>
                <Link href="/dashboard/denuncias/nova">
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Criar Denúncia
                  </Button>
                </Link>
              </div>
            </TabsContent>

            <TabsContent value="pendentes" className="mt-6">
              <div className="text-center py-12">
                <AlertCircle className="mx-auto h-12 w-12 text-yellow-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">42 Denúncias Pendentes</h3>
                <p className="text-sm text-muted-foreground">
                  Aguardando análise inicial
                </p>
              </div>
            </TabsContent>

            <TabsContent value="em_analise" className="mt-6">
              <div className="text-center py-12">
                <AlertCircle className="mx-auto h-12 w-12 text-orange-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">18 Denúncias em Análise</h3>
                <p className="text-sm text-muted-foreground">
                  Sendo processadas pela equipe
                </p>
              </div>
            </TabsContent>

            <TabsContent value="fiscalizacao" className="mt-6">
              <div className="text-center py-12">
                <AlertCircle className="mx-auto h-12 w-12 text-blue-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Denúncias em Fiscalização</h3>
                <p className="text-sm text-muted-foreground">
                  Equipe de campo realizando verificações
                </p>
              </div>
            </TabsContent>

            <TabsContent value="resolvidas" className="mt-6">
              <div className="text-center py-12">
                <AlertCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">188 Denúncias Resolvidas</h3>
                <p className="text-sm text-muted-foreground">
                  Concluídas com sucesso
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/dashboard/denuncias/mapa">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-blue-50 group-hover:bg-blue-100 transition-colors">
                  <MapPin className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Mapa de Denúncias</CardTitle>
                  <CardDescription>
                    Visualize todas as denúncias no mapa
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/denuncias/relatorio">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-purple-50 group-hover:bg-purple-100 transition-colors">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Relatórios</CardTitle>
                  <CardDescription>
                    Gere relatórios e análises
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/denuncias/estatisticas">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-green-50 group-hover:bg-green-100 transition-colors">
                  <AlertCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Estatísticas</CardTitle>
                  <CardDescription>
                    Análise detalhada de dados
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>
      </div>
    </div>
  );
}
