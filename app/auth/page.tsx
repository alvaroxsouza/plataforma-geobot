"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { LoginForm } from "@/components/auth/LoginForm";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { ForgotPasswordForm } from "@/components/auth/ForgotPasswordForm";
import { MapPin, Shield } from "lucide-react";

export default function AuthPage() {
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Lado Esquerdo - Branding */}
      <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-primary via-primary/90 to-primary/80 p-12 flex-col justify-between text-primary-foreground">
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <MapPin className="h-10 w-10" />
            <h1 className="text-4xl font-bold">GeoBot Platform</h1>
          </div>
          <p className="text-xl opacity-90">
            Plataforma inteligente de segmentação de imagens e gerenciamento de denúncias
          </p>
        </div>

        <div className="space-y-6">
          <div className="flex items-start space-x-4">
            <div className="bg-primary-foreground/20 p-3 rounded-lg">
              <Shield className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Segurança em Primeiro Lugar</h3>
              <p className="opacity-80">
                Seus dados são protegidos com as melhores práticas de segurança
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <div className="bg-primary-foreground/20 p-3 rounded-lg">
              <MapPin className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Geolocalização Precisa</h3>
              <p className="opacity-80">
                Rastreie e gerencie denúncias com precisão geográfica
              </p>
            </div>
          </div>
        </div>

        <div className="text-sm opacity-60">
          © 2025 GeoBot Platform. Todos os direitos reservados.
        </div>
      </div>

      {/* Lado Direito - Formulários */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md">
          {/* Logo para mobile */}
          <div className="md:hidden flex items-center justify-center space-x-2 mb-8">
            <MapPin className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">GeoBot</h1>
          </div>

          <Card className="shadow-lg">
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl font-bold">
                {showForgotPassword ? "Recuperar Senha" : "Bem-vindo"}
              </CardTitle>
              <CardDescription>
                {showForgotPassword
                  ? "Recupere o acesso à sua conta"
                  : "Entre na sua conta ou crie uma nova"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {showForgotPassword ? (
                <ForgotPasswordForm onBack={() => setShowForgotPassword(false)} />
              ) : (
                <Tabs defaultValue="login" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="login">Entrar</TabsTrigger>
                    <TabsTrigger value="register">Cadastrar</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="login" className="space-y-4">
                    <LoginForm />
                    <div className="text-center">
                      <Button
                        variant="link"
                        className="text-sm text-muted-foreground"
                        onClick={() => setShowForgotPassword(true)}
                      >
                        Esqueceu sua senha?
                      </Button>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="register" className="space-y-4">
                    <RegisterForm />
                  </TabsContent>
                </Tabs>
              )}
            </CardContent>
          </Card>

          {/* Footer para mobile */}
          <div className="md:hidden text-center text-sm text-muted-foreground mt-8">
            © 2025 GeoBot Platform
          </div>
        </div>
      </div>
    </div>
  );
}
