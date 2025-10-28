"use client";

import { useState } from "react";
import { Plus, Search, Filter, ClipboardCheck, Calendar, Users, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Link from "next/link";

export default function FiscalizacaoPage() {
  const [searchQuery, setSearchQuery] = useState("");

  // Dados mockados para demonstração
  const stats = [
    { 
      label: "Total de Fiscalizações", 
      value: "156", 
      change: "+8%", 
      changeType: "positive",
      icon: ClipboardCheck,
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    { 
      label: "Agendadas", 
      value: "23", 
      change: "+5", 
      changeType: "neutral",
      icon: Calendar,
      color: "text-purple-600",
      bgColor: "bg-purple-50"
    },
    { 
      label: "Em Andamento", 
      value: "12", 
      change: "+2", 
      changeType: "neutral",
      icon: Users,
      color: "text-orange-600",
      bgColor: "bg-orange-50"
    },
    { 
      label: "Concluídas", 
      value: "121", 
      change: "+18%", 
      changeType: "positive",
      icon: ClipboardCheck,
      color: "text-green-600",
      bgColor: "bg-green-50"
    },
  ];

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Fiscalização</h1>
          <p className="text-muted-foreground">
            Gerencie vistorias, inspeções e fiscalizações de campo
          </p>
        </div>
        <Link href="/dashboard/fiscalizacao/nova">
          <Button size="lg" className="gap-2">
            <Plus className="h-5 w-5" />
            Nova Fiscalização
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
              <CardTitle>Lista de Fiscalizações</CardTitle>
              <CardDescription>
                Acompanhe todas as fiscalizações e vistorias
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar fiscalizações..."
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
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="todas">Todas</TabsTrigger>
              <TabsTrigger value="agendadas">Agendadas</TabsTrigger>
              <TabsTrigger value="em_andamento">Em Andamento</TabsTrigger>
              <TabsTrigger value="concluidas">Concluídas</TabsTrigger>
            </TabsList>

            <TabsContent value="todas" className="mt-6">
              <div className="text-center py-12">
                <ClipboardCheck className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Nenhuma fiscalização encontrada</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Comece agendando uma nova fiscalização
                </p>
                <Link href="/dashboard/fiscalizacao/nova">
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Agendar Fiscalização
                  </Button>
                </Link>
              </div>
            </TabsContent>

            <TabsContent value="agendadas" className="mt-6">
              <div className="text-center py-12">
                <Calendar className="mx-auto h-12 w-12 text-purple-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">23 Fiscalizações Agendadas</h3>
                <p className="text-sm text-muted-foreground">
                  Programadas para os próximos dias
                </p>
              </div>
            </TabsContent>

            <TabsContent value="em_andamento" className="mt-6">
              <div className="text-center py-12">
                <Users className="mx-auto h-12 w-12 text-orange-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">12 Fiscalizações em Andamento</h3>
                <p className="text-sm text-muted-foreground">
                  Equipe de campo em ação
                </p>
              </div>
            </TabsContent>

            <TabsContent value="concluidas" className="mt-6">
              <div className="text-center py-12">
                <ClipboardCheck className="mx-auto h-12 w-12 text-green-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">121 Fiscalizações Concluídas</h3>
                <p className="text-sm text-muted-foreground">
                  Finalizadas com sucesso
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/dashboard/fiscalizacao/calendario">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-purple-50 group-hover:bg-purple-100 transition-colors">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Calendário</CardTitle>
                  <CardDescription>
                    Visualize as fiscalizações agendadas
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/fiscalizacao/equipes">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-blue-50 group-hover:bg-blue-100 transition-colors">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Equipes</CardTitle>
                  <CardDescription>
                    Gerencie as equipes de fiscalização
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/dashboard/fiscalizacao/mapa">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-green-50 group-hover:bg-green-100 transition-colors">
                  <MapPin className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Mapa de Ações</CardTitle>
                  <CardDescription>
                    Visualize as fiscalizações no mapa
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        </Link>
      </div>

      {/* Types of Fiscalização */}
      <Card>
        <CardHeader>
          <CardTitle>Tipos de Fiscalização</CardTitle>
          <CardDescription>
            Selecione o tipo de fiscalização que deseja realizar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {[
              { title: "Vistoria", icon: ClipboardCheck, color: "blue" },
              { title: "Inspeção", icon: Search, color: "purple" },
              { title: "Rotina", icon: Calendar, color: "green" },
              { title: "Atend. Denúncia", icon: MapPin, color: "orange" },
              { title: "Reincidência", icon: Users, color: "red" },
            ].map((type, index) => {
              const Icon = type.icon;
              return (
                <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader className="text-center">
                    <div className={`mx-auto p-3 rounded-lg bg-${type.color}-50 mb-2`}>
                      <Icon className={`h-6 w-6 text-${type.color}-600`} />
                    </div>
                    <CardTitle className="text-sm">{type.title}</CardTitle>
                  </CardHeader>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
