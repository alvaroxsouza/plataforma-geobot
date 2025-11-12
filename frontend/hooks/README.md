# Sistema de Metadados

Este sistema fornece metadados dinâmicos do backend para o frontend, eliminando hard-coding e garantindo sincronização entre backend e frontend.

## 🎯 Objetivo

Buscar dinamicamente do backend:
- Status de denúncia
- Categorias de denúncia  
- Prioridades
- Labels, descrições, cores e ícones

## 📁 Arquivos Criados

### Backend
- `backend/src/geobot_plataforma_backend/api/routers/metadata_router.py` - Endpoints de metadados

### Frontend
- `frontend/services/metadata.ts` - Serviço para buscar metadados
- `frontend/hooks/useMetadata.ts` - Hook React para usar metadados com cache
- `frontend/hooks/index.ts` - Exportação de hooks

## 🚀 Como Usar

### No seu componente React

```tsx
import { useMetadata } from "@/hooks/useMetadata";

function MeuComponente() {
  const {
    // Arrays com todos os dados
    status,
    categorias,
    prioridades,
    
    // Funções auxiliares
    getStatusLabel,
    getStatusColor,
    getCategoriaLabel,
    getCategoriaIcone,
    getPrioridadeLabel,
    getPrioridadeColor,
    
    // Estado
    loading,
    error,
  } = useMetadata();
  
  // Exemplo 1: Renderizar select de prioridades
  return (
    <Select>
      {prioridades.map((p) => (
        <SelectItem key={p.value} value={p.value}>
          {p.label}
        </SelectItem>
      ))}
    </Select>
  );
  
  // Exemplo 2: Exibir badge de status
  return (
    <Badge className={getStatusColor("pendente")}>
      {getStatusLabel("pendente")}
    </Badge>
  );
  
  // Exemplo 3: Exibir categoria com ícone
  return (
    <div>
      <span>{getCategoriaIcone("calcada")}</span>
      <span>{getCategoriaLabel("calcada")}</span>
    </div>
  );
}
```

## 📡 Endpoints da API

### GET `/api/metadata/`
Retorna todos os metadados em uma única resposta

### GET `/api/metadata/status-denuncia`
Retorna apenas status de denúncia

### GET `/api/metadata/categorias-denuncia`
Retorna apenas categorias

### GET `/api/metadata/prioridades`
Retorna apenas prioridades

## 💾 Cache

Os metadados são **automaticamente cacheados** no cliente:
- Primeira requisição busca do backend
- Requisições seguintes usam o cache
- Cache compartilhado entre todos os componentes
- Não precisa fazer nada manualmente!

## ✅ Vantagens

1. **Sem hard-coding**: Dados vêm direto do backend
2. **Sincronização**: Frontend sempre reflete o backend
3. **Performance**: Cache automático reduz requisições
4. **Type-safe**: Tipos TypeScript completos
5. **Reutilizável**: Use em qualquer componente
6. **Fácil manutenção**: Altere apenas no backend

## 🔧 Adicionar Novos Metadados

1. Adicione o enum no backend em `domain/entity/enums.py`
2. Crie endpoint em `metadata_router.py`
3. Adicione tipos em `frontend/services/metadata.ts`
4. Atualize hook em `frontend/hooks/useMetadata.ts`
