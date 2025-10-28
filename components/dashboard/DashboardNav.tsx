"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  AlertCircle,
  ClipboardCheck,
  FileText,
  Image,
  BarChart3,
  Settings,
  HelpCircle,
} from "lucide-react";

interface DashboardNavProps {
  className?: string;
}

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Denúncias",
    href: "/dashboard/denuncias",
    icon: AlertCircle,
    disabled: false,
  },
  {
    title: "Fiscalização",
    href: "/dashboard/fiscalizacao",
    icon: ClipboardCheck,
    disabled: false,
  },
  {
    title: "Relatórios",
    href: "/dashboard/reports",
    icon: FileText,
    disabled: true,
  },
  {
    title: "Análise de Imagens",
    href: "/dashboard/analysis",
    icon: Image,
    disabled: true,
  },
  {
    title: "Estatísticas",
    href: "/dashboard/statistics",
    icon: BarChart3,
    disabled: true,
  },
  {
    title: "Configurações",
    href: "/dashboard/settings",
    icon: Settings,
    disabled: true,
  },
  {
    title: "Ajuda",
    href: "/dashboard/help",
    icon: HelpCircle,
    disabled: true,
  },
];

export function DashboardNav({ className }: DashboardNavProps) {
  const pathname = usePathname();

  return (
    <nav className={cn("space-y-2", className)}>
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href;

        return (
          <Link
            key={item.href}
            href={item.disabled ? "#" : item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
              item.disabled && "cursor-not-allowed opacity-50 hover:bg-transparent hover:text-muted-foreground"
            )}
            onClick={(e) => {
              if (item.disabled) e.preventDefault();
            }}
          >
            <Icon className="h-4 w-4" />
            {item.title}
            {item.disabled && (
              <span className="ml-auto text-xs bg-muted-foreground/20 px-2 py-0.5 rounded">
                Em breve
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
