"use client";

import { useRef } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import listPlugin from "@fullcalendar/list";
import ptBrLocale from "@fullcalendar/core/locales/pt-br";
import { FiscalizacaoResponse } from "@/services/fiscalizacao";

interface CalendarioFiscalizacoesProps {
  fiscalizacoes: FiscalizacaoResponse[];
  onEventClick: (fiscalizacao: FiscalizacaoResponse) => void;
}

// Mapear status para cores
const getStatusColor = (status: string): string => {
  switch (status) {
    case "AGUARDANDO_SOBREVOO":
      return "#eab308"; // yellow
    case "AGUARDANDO_INFERENCIA":
    case "GERANDO_RELATORIO":
      return "#a855f7"; // purple
    case "CONCLUIDA":
      return "#22c55e"; // green
    case "CANCELADA":
      return "#ef4444"; // red
    default:
      return "#6b7280"; // gray
  }
};

const getStatusLabel = (status: string): string => {
  switch (status) {
    case "AGUARDANDO_SOBREVOO":
      return "Aguardando Sobrevoo";
    case "AGUARDANDO_INFERENCIA":
      return "Aguardando Inferência";
    case "GERANDO_RELATORIO":
      return "Gerando Relatório";
    case "CONCLUIDA":
      return "Concluída";
    case "CANCELADA":
      return "Cancelada";
    default:
      return status;
  }
};

export default function CalendarioFiscalizacoes({
  fiscalizacoes,
  onEventClick,
}: CalendarioFiscalizacoesProps) {
  const calendarRef = useRef<FullCalendar>(null);

  // Converter fiscalizações para eventos do calendário
  const events = fiscalizacoes.map((fisc) => {
    const dataPrevista = fisc.data_conclusao_prevista || fisc.data_inicio;
    const dataAtual = new Date();
    const dataEvento = new Date(dataPrevista);
    const atrasada = dataEvento < dataAtual && fisc.status_fiscalizacao !== "CONCLUIDA";

    return {
      id: fisc.id.toString(),
      title: `Fiscalização #${fisc.id}`,
      start: dataPrevista,
      end: dataPrevista,
      backgroundColor: atrasada ? "#ef4444" : getStatusColor(fisc.status_fiscalizacao),
      borderColor: atrasada ? "#dc2626" : getStatusColor(fisc.status_fiscalizacao),
      textColor: "#ffffff",
      extendedProps: {
        fiscalizacao: fisc,
        status: getStatusLabel(fisc.status_fiscalizacao),
        atrasada: atrasada,
      },
    };
  });

  return (
    <div className="fullcalendar-container">
      <FullCalendar
        ref={calendarRef}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
        initialView="dayGridMonth"
        locale={ptBrLocale}
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,timeGridWeek,listWeek",
        }}
        buttonText={{
          today: "Hoje",
          month: "Mês",
          week: "Semana",
          list: "Lista",
        }}
        events={events}
        eventClick={(info) => {
          const fiscalizacao = info.event.extendedProps.fiscalizacao as FiscalizacaoResponse;
          onEventClick(fiscalizacao);
        }}
        height="auto"
        eventTimeFormat={{
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }}
        slotLabelFormat={{
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }}
        eventContent={(arg) => {
          const status = arg.event.extendedProps.status;
          const atrasada = arg.event.extendedProps.atrasada;

          return (
            <div className="p-1 text-xs">
              <div className="font-semibold">{arg.event.title}</div>
              <div className="text-[10px] opacity-90">
                {status}
                {atrasada && " ⚠️"}
              </div>
            </div>
          );
        }}
        dayMaxEvents={3}
        moreLinkText={(num) => `+${num} mais`}
        nowIndicator={true}
        weekends={true}
        editable={false}
        selectable={false}
        selectMirror={true}
        dayMaxEventRows={true}
        eventClassNames={(arg) => {
          const atrasada = arg.event.extendedProps.atrasada;
          return atrasada ? "animate-pulse" : "";
        }}
      />

      <style jsx global>{`
        .fullcalendar-container {
          padding: 1rem;
          background: white;
          border-radius: 0.5rem;
        }

        .fc {
          font-family: inherit;
        }

        .fc-button {
          background-color: hsl(var(--primary)) !important;
          border-color: hsl(var(--primary)) !important;
          text-transform: capitalize;
          font-weight: 500;
          transition: all 0.2s;
        }

        .fc-button:hover {
          background-color: hsl(var(--primary) / 0.9) !important;
          border-color: hsl(var(--primary) / 0.9) !important;
        }

        .fc-button:focus {
          box-shadow: 0 0 0 2px hsl(var(--primary) / 0.2) !important;
        }

        .fc-button-active {
          background-color: hsl(var(--primary) / 0.8) !important;
        }

        .fc-toolbar-title {
          font-size: 1.5rem !important;
          font-weight: 700;
          color: hsl(var(--foreground));
        }

        .fc-col-header-cell {
          background-color: hsl(var(--muted));
          font-weight: 600;
          text-transform: uppercase;
          font-size: 0.75rem;
          padding: 0.75rem 0.5rem;
        }

        .fc-daygrid-day {
          transition: background-color 0.2s;
        }

        .fc-daygrid-day:hover {
          background-color: hsl(var(--muted) / 0.3);
        }

        .fc-daygrid-day-number {
          padding: 0.5rem;
          font-weight: 500;
        }

        .fc-event {
          cursor: pointer;
          border-radius: 0.25rem;
          padding: 0.125rem 0.25rem;
          font-size: 0.75rem;
          margin-bottom: 0.125rem;
          transition: all 0.2s;
        }

        .fc-event:hover {
          opacity: 0.8;
          transform: scale(1.02);
        }

        .fc-day-today {
          background-color: hsl(var(--primary) / 0.05) !important;
        }

        .fc-day-today .fc-daygrid-day-number {
          background-color: hsl(var(--primary));
          color: white;
          border-radius: 50%;
          width: 2rem;
          height: 2rem;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .fc-timegrid-slot {
          height: 3rem;
        }

        .fc-list-event:hover {
          background-color: hsl(var(--muted) / 0.5);
        }

        .fc-list-day-cushion {
          background-color: hsl(var(--muted));
          font-weight: 600;
        }

        .fc-more-link {
          color: hsl(var(--primary));
          font-weight: 500;
        }

        .fc-more-link:hover {
          text-decoration: underline;
        }

        /* Responsividade */
        @media (max-width: 768px) {
          .fc-toolbar {
            flex-direction: column;
            gap: 0.5rem;
          }

          .fc-toolbar-chunk {
            display: flex;
            justify-content: center;
          }

          .fc-toolbar-title {
            font-size: 1.25rem !important;
            margin: 0.5rem 0;
          }
        }
      `}</style>
    </div>
  );
}
