import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard - GeoBot Platform",
  description: "Painel de controle da plataforma GeoBot",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
