import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export default function proxy(request: NextRequest) {
  const token = request.cookies.get("token")?.value;
  const { pathname } = request.nextUrl;

  // Rotas públicas
  const publicRoutes = ["/auth"];
  const isPublicRoute = publicRoutes.some((route) => pathname.startsWith(route));

  // Se está tentando acessar rota pública e está autenticado, redireciona para dashboard
  if (isPublicRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Se está tentando acessar rota protegida e não está autenticado, redireciona para auth
  if (!isPublicRoute && pathname.startsWith("/dashboard") && !token) {
    return NextResponse.redirect(new URL("/auth", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/auth"],
};
