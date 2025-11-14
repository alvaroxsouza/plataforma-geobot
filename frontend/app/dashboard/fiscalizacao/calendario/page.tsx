"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Home, ChevronRight, Calendar as CalendarIcon } from "lucide-react";
import Link from "next/link";
import { fiscalizacaoService, FiscalizacaoResponse } from "@/services/fiscalizacao";
import { toast } from "sonner";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import listPlugin from "@fullcalendar/list";
import ptBrLocale from "@fullcalendar/core/locales/pt-br";
import type { EventClickArg, EventInput } from "@fullcalendar/core";
import { useRouter } from "next/navigation";

export default function CalendarioFiscalizacaoPage() {
  const [fiscalizacoes, setFiscalizacoes] = useState<FiscalizacaoResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const calendarRef = useRef<FullCalendar>(null);
  const router = useRouter();

  useEffect(() => {
    carregarFiscalizacoes();
  }, []);

  const carregarFiscalizacoes = async () => {
    try {
      setIsLoading(true);
      const response = await fiscalizacaoService.getAll({ limit: 1000 });
      setFiscalizacoes(response);
    } catch (error: any) {
      console.error("Erro ao carregar fiscalizações:", error);
      toast.error(error?.response?.data?.detail || "Erro ao carregar fiscalizações");
    } finally {
      setIsLoading(false);
    }
  };

  const getEventColor = (status: string) => {
    const colors: Record<string, string> = {
      'AGUARDANDO_SOBREVOO': '#eab308', // yellow
      'AGUARDANDO_INFERENCIA': '#3b82f6', // blue
      'GERANDO_RELATORIO': '#a855f7', // purple
      'CONCLUIDA': '#22c55e', // green
      'CANCELADA': '#ef4444', // red
    };
    return colors[status] || '#6b7280'; // gray
  };

  // Converter fiscalizações para eventos do calendário
  const eventos: EventInput[] = fiscalizacoes.map((fisc) => {
    const dataInicio = fisc.data_inicio ? new Date(fisc.data_inicio) : new Date();
    const dataFim = fisc.data_conclusao_efetiva ? new Date(fisc.data_conclusao_efetiva) : undefined;
    
    let title = `#${fisc.id}`;
    if (fisc.fiscais && fisc.fiscais.length > 0) {
      title += ` - ${fisc.fiscais[0].nome}`;
    }
    
    return {
      id: fisc.id.toString(),
      title,
      start: dataInicio,
      end: dataFim,
      backgroundColor: getEventColor(fisc.status_fiscalizacao),
      borderColor: getEventColor(fisc.status_fiscalizacao),
      extendedProps: {
        fiscalizacao: fisc,
      },
    };
  });

  const handleEventClick = (info: EventClickArg) => {
    const fiscId = info.event.id;
    router.push(`/dashboard/fiscalizacao/${fiscId}`);
  };

  const handleDateClick = (info: any) => {
    toast.info(`Data selecionada: ${info.dateStr}`);
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/dashboard" className="hover:text-foreground transition-colors">
          <Home className="h-4 w-4" />
        </Link>
        <ChevronRight className="h-4 w-4" />
        <Link href="/dashboard/fiscalizacao" className="hover:text-foreground transition-colors">
          Fiscalização
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium">Calendário</span>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <CalendarIcon className="h-8 w-8" />
            Calendário de Fiscalizações
          </h1>
          <p className="text-muted-foreground">
            Visualize as fiscalizações organizadas por data
          </p>
        </div>
      </div>

      {/* Legenda */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Legenda de Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-yellow-500" />
              <span className="text-sm">Pendente</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-blue-500" />
              <span className="text-sm">Em Andamento</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-500" />
              <span className="text-sm">Concluída</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-500" />
              <span className="text-sm">Cancelada</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calendário */}
      <Card>
        <CardHeader>
          <CardTitle>Agenda de Fiscalizações</CardTitle>
          <CardDescription>
            {isLoading ? "Carregando..." : `${fiscalizacoes.length} fiscalização(ões) no total`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="calendar-container">
              <FullCalendar
                ref={calendarRef}
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
                initialView="dayGridMonth"
                locale={ptBrLocale}
                headerToolbar={{
                  left: 'prev,next today',
                  center: 'title',
                  right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
                }}
                buttonText={{
                  today: 'Hoje',
                  month: 'Mês',
                  week: 'Semana',
                  day: 'Dia',
                  list: 'Lista'
                }}
                events={eventos}
                eventClick={handleEventClick}
                dateClick={handleDateClick}
                height="auto"
                eventTimeFormat={{
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }}
                slotLabelFormat={{
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }}
                eventDisplay="block"
                displayEventTime={true}
                displayEventEnd={true}
                weekends={true}
                nowIndicator={true}
                dayMaxEvents={3}
                moreLinkText="mais"
              />
            </div>
          )}
        </CardContent>
      </Card>

      <style jsx global>{`
        .calendar-container {
          --fc-border-color: hsl(var(--border));
          --fc-button-bg-color: hsl(var(--primary));
          --fc-button-border-color: hsl(var(--primary));
          --fc-button-hover-bg-color: hsl(var(--primary) / 0.9);
          --fc-button-hover-border-color: hsl(var(--primary) / 0.9);
          --fc-button-active-bg-color: hsl(var(--primary) / 0.8);
          --fc-button-active-border-color: hsl(var(--primary) / 0.8);
          --fc-today-bg-color: hsl(var(--accent));
        }

        .fc .fc-button {
          text-transform: capitalize;
        }

        .fc .fc-toolbar-title {
          text-transform: capitalize;
          font-size: 1.5rem;
          font-weight: 600;
        }

        .fc .fc-col-header-cell {
          text-transform: uppercase;
          font-size: 0.75rem;
          font-weight: 600;
          background: hsl(var(--muted));
        }

        .fc .fc-daygrid-day-number {
          color: hsl(var(--foreground));
        }

        .fc .fc-event {
          cursor: pointer;
          border-radius: 0.25rem;
          padding: 2px 4px;
          font-size: 0.875rem;
        }

        .fc .fc-event:hover {
          opacity: 0.8;
        }
      `}</style>
    </div>
  );
}
