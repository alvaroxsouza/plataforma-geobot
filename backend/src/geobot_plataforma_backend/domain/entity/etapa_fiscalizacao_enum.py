"""
Enum para status das etapas de fiscalização
"""
from enum import Enum


class EtapaFiscalizacaoEnum(str, Enum):
    """Status das etapas de uma fiscalização"""
    
    # Etapas principais
    PENDENTE = "pendente"  # Fiscalização criada, não iniciada
    SOBREVOO = "sobrevoo"  # Etapa de captura aérea
    ABASTECIMENTO = "abastecimento"  # Etapa de upload de imagens
    ANALISE_IA = "analise_ia"  # Etapa de processamento com IA
    RELATORIO = "relatorio"  # Etapa de geração de relatório
    CONCLUIDA = "concluida"  # Fiscalização finalizada
    CANCELADA = "cancelada"  # Fiscalização cancelada
    
    def __str__(self):
        return self.value
    
    def proxima_etapa(self) -> 'EtapaFiscalizacaoEnum':
        """Retorna a próxima etapa no fluxo"""
        sequencia = [
            self.PENDENTE,
            self.SOBREVOO,
            self.ABASTECIMENTO,
            self.ANALISE_IA,
            self.RELATORIO,
            self.CONCLUIDA,
        ]
        
        if self in sequencia:
            idx = sequencia.index(self)
            if idx < len(sequencia) - 1:
                return sequencia[idx + 1]
        
        return self.CONCLUIDA
    
    @staticmethod
    def pode_transicionar(etapa_atual: 'EtapaFiscalizacaoEnum', etapa_nova: 'EtapaFiscalizacaoEnum') -> bool:
        """Verifica se a transição entre etapas é válida"""
        sequencia = [
            EtapaFiscalizacaoEnum.PENDENTE,
            EtapaFiscalizacaoEnum.SOBREVOO,
            EtapaFiscalizacaoEnum.ABASTECIMENTO,
            EtapaFiscalizacaoEnum.ANALISE_IA,
            EtapaFiscalizacaoEnum.RELATORIO,
            EtapaFiscalizacaoEnum.CONCLUIDA,
        ]
        
        # Sempre pode cancelar
        if etapa_nova == EtapaFiscalizacaoEnum.CANCELADA:
            return etapa_atual != EtapaFiscalizacaoEnum.CONCLUIDA
        
        # Volta para a mesma etapa é permitido (refresh)
        if etapa_atual == etapa_nova:
            return True
        
        # Ir para próxima etapa
        if etapa_atual in sequencia and etapa_nova in sequencia:
            idx_atual = sequencia.index(etapa_atual)
            idx_nova = sequencia.index(etapa_nova)
            return idx_nova == idx_atual + 1
        
        return False
