# Guia de Migração - Hard-coded para Metadados Dinâmicos

## 📋 Resumo

Este guia mostra como migrar código hard-coded para usar o sistema de metadados dinâmicos.

## ✅ Página Já Migrada

- ✅ `/dashboard/denuncias/[id]/page.tsx` - Página de detalhes da denúncia

## 📝 Páginas Pendentes

- ⏳ `/dashboard/denuncias/page.tsx` - Lista de denúncias
- ⏳ `/dashboard/gerenciar-denuncias/page.tsx` - Gerenciamento admin
- ⏳ `/dashboard/denuncias/equipamentos/[categoria]/page.tsx` - Por categoria
- ⏳ `/dashboard/denuncias/nova/page.tsx` - Nova denúncia

## 🔄 Padrão de Migração

### ❌ ANTES (Hard-coded)

```tsx
// Labels hard-coded
const categoriasLabels: Record<string, string> = {
  calcada: "Calçada",
  rua: "Rua",
  // ... mais valores
};

const statusLabels: Record<StatusDenuncia, string> = {
  pendente: "Pendente",
  em_analise: "Em Análise",
  // ... mais valores
};

const statusColors: Record<StatusDenuncia, string> = {
  pendente: "bg-yellow-100 text-yellow-800 border-yellow-200",
  // ... mais valores
};

// Uso
<Badge className={statusColors[denuncia.status]}>
  {statusLabels[denuncia.status]}
</Badge>

// Select hard-coded
<Select>
  <SelectItem value="baixa">Baixa</SelectItem>
  <SelectItem value="media">Média</SelectItem>
  <SelectItem value="alta">Alta</SelectItem>
  <SelectItem value="urgente">Urgente</SelectItem>
</Select>
```

### ✅ DEPOIS (Dinâmico)

```tsx
import { useMetadata } from "@/hooks/useMetadata";

function MeuComponente() {
  // Adicionar hook
  const {
    prioridades,
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    getPrioridadeLabel,
    getPrioridadeColor,
    loading: metadataLoading,
  } = useMetadata();

  // Atualizar loading
  if (loading || metadataLoading) {
    return <Loader2 />;
  }

  // Uso dinâmico
  return (
    <>
      {/* Badge dinâmico */}
      <Badge className={getStatusColor(denuncia.status)}>
        {getStatusLabel(denuncia.status)}
      </Badge>

      {/* Select dinâmico */}
      <Select>
        {prioridades.map((p) => (
          <SelectItem key={p.value} value={p.value}>
            {p.label}
          </SelectItem>
        ))}
      </Select>
    </>
  );
}
```

## 📦 O que Remover

Remova estes objetos hard-coded:

```tsx
// ❌ REMOVER
const categoriasLabels: Record<string, string> = { ... };
const statusLabels: Record<StatusDenuncia, string> = { ... };
const statusColors: Record<StatusDenuncia, string> = { ... };
const prioridadeColors: Record<string, string> = { ... };
const prioridadeLabels: Record<string, string> = { ... };
```

## 🔧 Passos para Migrar uma Página

### 1. Adicionar Import

```tsx
import { useMetadata } from "@/hooks/useMetadata";
```

### 2. Adicionar Hook no Componente

```tsx
const {
  status: statusOptions,
  categorias: categoriaOptions,
  prioridades: prioridadeOptions,
  getStatusLabel,
  getStatusColor,
  getCategoriaLabel,
  getCategoriaIcone,
  getPrioridadeLabel,
  getPrioridadeColor,
  loading: metadataLoading,
} = useMetadata();
```

### 3. Atualizar Loading

```tsx
if (loading || metadataLoading) {
  return <LoadingComponent />;
}
```

### 4. Substituir Hard-coded

Procure e substitua:

| Antes | Depois |
|-------|--------|
| `statusLabels[status]` | `getStatusLabel(status)` |
| `statusColors[status]` | `getStatusColor(status)` |
| `categoriasLabels[cat]` | `getCategoriaLabel(cat)` |
| `prioridadeLabels[p]` | `getPrioridadeLabel(p)` |
| `prioridadeColors[p]` | `getPrioridadeColor(p)` |

### 5. Atualizar Selects

```tsx
// ANTES
<Select>
  <SelectItem value="baixa">Baixa</SelectItem>
  <SelectItem value="media">Média</SelectItem>
</Select>

// DEPOIS
<Select>
  {prioridadeOptions.map((p) => (
    <SelectItem key={p.value} value={p.value}>
      {p.label}
    </SelectItem>
  ))}
</Select>
```

### 6. Remover Constantes Hard-coded

Delete todas as constantes de labels e cores do topo do arquivo.

## 🎯 Benefícios da Migração

1. ✅ **Sincronização Backend/Frontend**: Dados sempre atualizados
2. ✅ **Manutenção Simplificada**: Altere apenas no backend
3. ✅ **Sem Duplicação**: Labels/cores em um único lugar
4. ✅ **Type-Safe**: TypeScript garante tipos corretos
5. ✅ **Performance**: Cache automático
6. ✅ **Escalável**: Fácil adicionar novos metadados

## 🚨 Atenção

- Não esqueça de adicionar `metadataLoading` na condição de loading
- Use sempre as funções `get*` para buscar labels/cores
- Arrays (`statusOptions`, `prioridadeOptions`) para renderizar listas
- O cache é compartilhado - primeira página carrega, demais reusam

## 📊 Progresso

| Página | Status | Data |
|--------|--------|------|
| `/denuncias/[id]` | ✅ Completo | 12/11/2025 |
| `/denuncias` | ⏳ Pendente | - |
| `/gerenciar-denuncias` | ⏳ Pendente | - |
| `/denuncias/nova` | ⏳ Pendente | - |
| `/denuncias/equipamentos/[cat]` | ⏳ Pendente | - |
