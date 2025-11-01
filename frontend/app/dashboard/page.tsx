"use client";

import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { 
  Loader2, 
  LogOut, 
  User, 
  MapPin, 
  FileText, 
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Activity,
  BarChart3,
  Settings,
  Bell,
  ClipboardCheck,
  ListChecks
} from "lucide-react";

export default function DashboardPage() {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  // Estatísticas mockadas para demonstração
  const stats = [
    {
      title: "Denúncias Totais",
      value: "0",
      icon: FileText,
      description: "Total de denúncias registradas",
      trend: "+0%",
      color: "text-blue-600",
      bgColor: "bg-blue-50 dark:bg-blue-950",
    },
    {
      title: "Pendentes",
      value: "0",
      icon: Clock,
      description: "Aguardando análise",
      trend: "0",
      color: "text-yellow-600",
      bgColor: "bg-yellow-50 dark:bg-yellow-950",
    },
    {
      title: "Em Análise",
      value: "0",
      icon: Activity,
      description: "Sendo processadas",
      trend: "0",
      color: "text-orange-600",
      bgColor: "bg-orange-50 dark:bg-orange-950",
    },
    {
      title: "Concluídas",
      value: "0",
      icon: CheckCircle,
      description: "Análise finalizada",
      trend: "+0%",
      color: "text-green-600",
      bgColor: "bg-green-50 dark:bg-green-950",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header / Navbar */}
      <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <MapPin className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">GeoBot Platform</h1>
                <p className="text-xs text-muted-foreground">Sistema de Gestão de Denúncias</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute top-1 right-1 h-2 w-2 bg-red-600 rounded-full"></span>
              </Button>
              <Button variant="ghost" size="icon">
                <Settings className="h-5 w-5" />
              </Button>
              <Button variant="outline" onClick={logout}>
                <LogOut className="mr-2 h-4 w-4" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">
              Bem-vindo de volta, {user?.nome}! 👋
            </h2>
            <p className="text-muted-foreground">
              Aqui está um resumo das suas atividades na plataforma
            </p>
          </div>

          {/* Info Card */}
          <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
            <CardContent className="pt-6">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-primary/20 rounded-lg">
                  <AlertCircle className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2">
                    Bem-vindo à Plataforma GeoBot! 🚀
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Este é o seu dashboard principal. Aqui você poderá gerenciar denúncias,
                    processar imagens com IA, visualizar relatórios e muito mais. As funcionalidades
                    estão sendo desenvolvidas e estarão disponíveis em breve.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {stat.title}
                  </CardTitle>
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <stat.icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stat.description}
                  </p>
                  <div className="flex items-center mt-2">
                    <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
                    <span className="text-xs text-green-600">{stat.trend}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Quick Navigation */}
          <Card className="bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="mr-2 h-5 w-5" />
                Acesso Rápido aos Módulos
              </CardTitle>
              <CardDescription>
                Navegue diretamente para os módulos principais da plataforma
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                <Link href="/dashboard/denuncias">
                  <Card className="hover:shadow-md transition-all hover:scale-105 cursor-pointer border-2 hover:border-primary/50">
                    <CardContent className="pt-6 text-center">
                      <div className="mx-auto w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center mb-3">
                        <AlertCircle className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                      </div>
                      <h3 className="font-semibold mb-1">Denúncias</h3>
                      <p className="text-xs text-muted-foreground">Gerenciar ocorrências</p>
                    </CardContent>
                  </Card>
                </Link>

                <Link href="/dashboard/gerenciar-denuncias">
                  <Card className="hover:shadow-md transition-all hover:scale-105 cursor-pointer border-2 hover:border-primary/50">
                    <CardContent className="pt-6 text-center">
                      <div className="mx-auto w-12 h-12 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center mb-3">
                        <ListChecks className="h-6 w-6 text-green-600 dark:text-green-400" />
                      </div>
                      <h3 className="font-semibold mb-1">Gerenciar</h3>
                      <p className="text-xs text-muted-foreground">Enviar fiscalização</p>
                    </CardContent>
                  </Card>
                </Link>

                <Link href="/dashboard/fiscalizacao">
                  <Card className="hover:shadow-md transition-all hover:scale-105 cursor-pointer border-2 hover:border-primary/50">
                    <CardContent className="pt-6 text-center">
                      <div className="mx-auto w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center mb-3">
                        <ClipboardCheck className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                      </div>
                      <h3 className="font-semibold mb-1">Fiscalização</h3>
                      <p className="text-xs text-muted-foreground">Vistorias e inspeções</p>
                    </CardContent>
                  </Card>
                </Link>

                <Card className="opacity-50 cursor-not-allowed">
                  <CardContent className="pt-6 text-center">
                    <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-3">
                      <BarChart3 className="h-6 w-6 text-gray-600 dark:text-gray-400" />
                    </div>
                    <h3 className="font-semibold mb-1">Relatórios</h3>
                    <p className="text-xs text-muted-foreground">Em breve</p>
                  </CardContent>
                </Card>

                <Card className="opacity-50 cursor-not-allowed">
                  <CardContent className="pt-6 text-center">
                    <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-3">
                      <Settings className="h-6 w-6 text-gray-600 dark:text-gray-400" />
                    </div>
                    <h3 className="font-semibold mb-1">Configurações</h3>
                    <p className="text-xs text-muted-foreground">Em breve</p>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

          {/* Main Grid */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* User Profile Card */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="mr-2 h-5 w-5" />
                  Perfil do Usuário
                </CardTitle>
                <CardDescription>Suas informações cadastrais</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="h-16 w-16 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
                    <User className="h-8 w-8 text-primary-foreground" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-lg">{user?.nome}</p>
                    <p className="text-sm text-muted-foreground">ID: {user?.uuid}</p>
                  </div>
                </div>

                <div className="space-y-3 pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">E-mail:</span>
                    <p className="text-sm font-medium">{user?.email}</p>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">CPF:</span>
                    <p className="text-sm font-medium">{user?.cpf}</p>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Status:</span>
                    <div className="flex items-center">
                      {user?.ativo ? (
                        <>
                          <CheckCircle className="h-4 w-4 text-green-600 mr-1" />
                          <span className="text-sm font-medium text-green-600">Ativo</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="h-4 w-4 text-red-600 mr-1" />
                          <span className="text-sm font-medium text-red-600">Inativo</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <Button className="w-full mt-4" variant="outline">
                  <Settings className="mr-2 h-4 w-4" />
                  Editar Perfil
                </Button>
              </CardContent>
            </Card>

            {/* Actions Card */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Ações Rápidas</CardTitle>
                <CardDescription>
                  Acesse as principais funcionalidades da plataforma
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-2">
                  <Link href="/dashboard/denuncias/nova">
                    <Button 
                      className="h-24 w-full flex flex-col items-center justify-center space-y-2"
                      variant="outline"
                    >
                      <MapPin className="h-6 w-6" />
                      <div className="text-center">
                        <p className="font-semibold">Nova Denúncia</p>
                        <p className="text-xs text-muted-foreground">Registrar nova ocorrência</p>
                      </div>
                    </Button>
                  </Link>

                  <Link href="/dashboard/denuncias">
                    <Button 
                      className="h-24 w-full flex flex-col items-center justify-center space-y-2"
                      variant="outline"
                    >
                      <FileText className="h-6 w-6" />
                      <div className="text-center">
                        <p className="font-semibold">Denúncias</p>
                        <p className="text-xs text-muted-foreground">Ver todas as denúncias</p>
                      </div>
                    </Button>
                  </Link>

                  <Link href="/dashboard/fiscalizacao">
                    <Button 
                      className="h-24 w-full flex flex-col items-center justify-center space-y-2"
                      variant="outline"
                    >
                      <ClipboardCheck className="h-6 w-6" />
                      <div className="text-center">
                        <p className="font-semibold">Fiscalização</p>
                        <p className="text-xs text-muted-foreground">Gerenciar fiscalizações</p>
                      </div>
                    </Button>
                  </Link>

                  <Button 
                    className="h-24 flex flex-col items-center justify-center space-y-2"
                    variant="outline"
                    disabled
                  >
                    <BarChart3 className="h-6 w-6" />
                    <div className="text-center">
                      <p className="font-semibold">Relatórios</p>
                      <p className="text-xs text-muted-foreground">Em breve</p>
                    </div>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="mr-2 h-5 w-5" />
                Atividades Recentes
              </CardTitle>
              <CardDescription>Suas últimas ações na plataforma</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Nenhuma atividade registrada ainda</p>
                <p className="text-sm mt-2">
                  Comece criando sua primeira denúncia ou processando imagens
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-12 py-6 bg-background/50">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-muted-foreground">
            <p>© 2025 GeoBot Platform. Todos os direitos reservados.</p>
            <div className="flex space-x-4 mt-4 md:mt-0">
              <a href="#" className="hover:text-primary transition-colors">Ajuda</a>
              <a href="#" className="hover:text-primary transition-colors">Documentação</a>
              <a href="#" className="hover:text-primary transition-colors">Suporte</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
