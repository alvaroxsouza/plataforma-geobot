"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LucideIcon } from "lucide-react";

interface QuickActionProps {
  title: string;
  description: string;
  icon: LucideIcon;
  onClick?: () => void;
  disabled?: boolean;
}

export function QuickAction({
  title,
  description,
  icon: Icon,
  onClick,
  disabled = false,
}: QuickActionProps) {
  return (
    <Button
      className="h-24 flex flex-col items-center justify-center space-y-2"
      variant="outline"
      onClick={onClick}
      disabled={disabled}
    >
      <Icon className="h-6 w-6" />
      <div className="text-center">
        <p className="font-semibold">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </Button>
  );
}

interface QuickActionsCardProps {
  actions: Array<{
    title: string;
    description: string;
    icon: LucideIcon;
    onClick?: () => void;
    disabled?: boolean;
  }>;
}

export function QuickActionsCard({ actions }: QuickActionsCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Ações Rápidas</CardTitle>
        <CardDescription>
          Acesse as principais funcionalidades da plataforma
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2">
          {actions.map((action, index) => (
            <QuickAction key={index} {...action} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
