"""DTOs para operações de denúncia"""
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, validator, Field

from src.geobot_plataforma_backend.domain.entity.enums import (
    StatusDenuncia,
    CategoriaDenuncia,
    Prioridade,
)


class DenunciaCriarDTO(BaseModel):
    """DTO para criação de denúncia
    
    Campos obrigatórios conforme Swagger:
    - categoria: Categoria da denúncia
    - prioridade: Prioridade da denúncia
    - observacao: Descrição detalhada do problema
    - logradouro: Nome da rua/avenida
    - bairro: Nome do bairro
    - cidade: Nome da cidade
    - estado: Sigla do estado (UF)
    - cep: Código postal
    
    Campos opcionais:
    - numero: Número do endereço
    - complemento: Complemento do endereço
    - latitude: Coordenada geográfica
    - longitude: Coordenada geográfica
    """
    categoria: CategoriaDenuncia
    prioridade: Prioridade
    observacao: str
    # Dados do endereço
    logradouro: str = Field(..., min_length=5, description="Logradouro deve ter pelo menos 5 caracteres")
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str = Field(..., min_length=2, max_length=2, description="Estado (UF) com 2 caracteres")
    cep: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @validator('logradouro')
    def validar_logradouro(cls, v: str) -> str:
        """Valida se o logradouro tem pelo menos 5 caracteres (sem espaços)"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Logradouro deve ter pelo menos 5 caracteres")
        return v

    @validator('estado')
    def validar_estado(cls, v: str) -> str:
        """Valida se o estado tem exatamente 2 caracteres"""
        if len(v) != 2:
            raise ValueError("Estado deve ter 2 caracteres (UF)")
        return v.upper()

    @validator('cep')
    def validar_cep(cls, v: str) -> str:
        """Valida formato do CEP"""
        if v and not v.replace("-", "").isdigit():
            raise ValueError("CEP inválido")
        return v

    class Config:
        from_attributes = True
        use_enum_values = False


class DenunciaAtualizarDTO(BaseModel):
    """DTO para atualização de denúncia
    
    Permite atualizar apenas os campos editáveis pelo usuário:
    - observacao: Nova descrição do problema (opcional)
    - prioridade: Nova prioridade da denúncia (opcional)
    
    Nota: Apenas denúncias com status 'pendente' podem ser atualizadas.
    Apenas o criador da denúncia pode realizar esta operação.
    """
    observacao: Optional[str] = None
    prioridade: Optional[Prioridade] = None

    class Config:
        from_attributes = True
        use_enum_values = False


class DenunciaResponseDTO(BaseModel):
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

    class Config:
        from_attributes = True
        use_enum_values = False
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
