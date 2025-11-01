"""DTOs para operações de denúncia"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.geobot_plataforma_backend.domain.entity.enums import (
    StatusDenuncia,
    CategoriaDenuncia,
    Prioridade,
)


@dataclass
class DenunciaCriarDTO:
    """DTO para criação de denúncia"""
    categoria: CategoriaDenuncia
    prioridade: Prioridade
    observacao: str
    # Dados do endereço
    logradouro: str
    numero: Optional[str]
    complemento: Optional[str]
    bairro: str
    cidade: str
    estado: str
    cep: str
    latitude: Optional[float]
    longitude: Optional[float]

    def __post_init__(self):
        """Validações básicas"""
        if not self.logradouro or len(self.logradouro.strip()) < 5:
            raise ValueError("Logradouro deve ter pelo menos 5 caracteres")
        if len(self.estado) != 2:
            raise ValueError("Estado deve ter 2 caracteres (UF)")
        if self.cep and not self.cep.replace("-", "").isdigit():
            raise ValueError("CEP inválido")


@dataclass
class DenunciaAtualizarDTO:
    """DTO para atualização de denúncia (apenas campos editáveis)"""
    observacao: Optional[str] = None
    prioridade: Optional[Prioridade] = None


@dataclass
class DenunciaResponseDTO:
    """DTO para resposta com dados da denúncia"""
    id: int
    uuid: str
    status: StatusDenuncia
    categoria: CategoriaDenuncia
    prioridade: Prioridade
    observacao: str
    usuario_nome: str
    usuario_email: str
    endereco: dict
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, denuncia):
        """Cria DTO a partir da entidade"""
        return cls(
            id=denuncia.id,
            uuid=str(denuncia.uuid),
            status=denuncia.status,
            categoria=denuncia.categoria,
            prioridade=denuncia.prioridade,
            observacao=denuncia.observacao,
            usuario_nome=denuncia.usuario.nome,
            usuario_email=denuncia.usuario.email,
            endereco={
                "logradouro": denuncia.endereco.logradouro,
                "numero": denuncia.endereco.numero,
                "bairro": denuncia.endereco.bairro,
                "cidade": denuncia.endereco.cidade,
                "estado": denuncia.endereco.estado,
                "cep": denuncia.endereco.cep,
                "latitude": float(denuncia.endereco.latitude) if denuncia.endereco.latitude else None,
                "longitude": float(denuncia.endereco.longitude) if denuncia.endereco.longitude else None,
            },
            created_at=denuncia.created_at,
            updated_at=denuncia.updated_at,
        )

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "status": self.status.value,
            "categoria": self.categoria.value,
            "prioridade": self.prioridade.value,
            "observacao": self.observacao,
            "usuario": {
                "nome": self.usuario_nome,
                "email": self.usuario_email,
            },
            "endereco": self.endereco,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
