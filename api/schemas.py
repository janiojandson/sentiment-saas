from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class SentimentRequest(BaseModel):
    """
    Modelo para requisição de análise de sentimento de um único texto
    """
    text: str = Field(..., min_length=1, description="Texto para análise de sentimento")
    model_type: Literal["fast", "accurate"] = Field(
        default="accurate", 
        description="Tipo de modelo a ser usado: 'fast' (rápido) ou 'accurate' (preciso)"
    )

class SentimentResponse(BaseModel):
    """
    Modelo para resposta da análise de sentimento
    """
    text: str = Field(..., description="Texto original analisado")
    sentiment: Literal["positive", "negative", "neutral"] = Field(..., description="Classificação do sentimento")
    confidence: float = Field(..., description="Nível de confiança da classificação (0-1)")
    model_used: str = Field(..., description="Modelo utilizado para a análise")

class BatchRequest(BaseModel):
    """
    Modelo para requisição de análise de sentimento em lote
    """
    texts: List[str] = Field(..., min_items=1, description="Lista de textos para análise")
    model_type: Literal["fast", "accurate"] = Field(
        default="fast", 
        description="Tipo de modelo a ser usado: 'fast' (rápido) ou 'accurate' (preciso)"
    )

class BatchResponse(BaseModel):
    """
    Modelo para resposta da análise de sentimento em lote
    """
    results: List[SentimentResponse] = Field(..., description="Lista de resultados da análise")

class SocialMention(BaseModel):
    """
    Modelo para representar uma menção em rede social
    """
    platform: str = Field(..., description="Plataforma de origem (Twitter, Instagram, etc)")
    text: str = Field(..., description="Conteúdo da menção")
    author: str = Field(..., description="Autor da menção")
    timestamp: datetime = Field(..., description="Data e hora da menção")
    url: Optional[str] = Field(None, description="URL da menção original")
    engagement: Optional[int] = Field(None, description="Métricas de engajamento (likes, shares, etc)")
    sentiment: Optional[str] = Field(None, description="Classificação de sentimento")
    confidence: Optional[float] = Field(None, description="Confiança da classificação de sentimento")

class SocialQuery(BaseModel):
    """
    Modelo para requisição de busca em redes sociais
    """
    query: str = Field(..., description="Termo de busca (marca, produto, etc)")
    platforms: List[str] = Field(default=["twitter"], description="Plataformas para busca")
    start_date: Optional[datetime] = Field(None, description="Data de início da busca")
    end_date: Optional[datetime] = Field(None, description="Data de fim da busca")
    limit: int = Field(default=100, description="Número máximo de resultados")

class SocialQueryResponse(BaseModel):
    """
    Modelo para resposta de busca em redes sociais
    """
    query: str = Field(..., description="Termo de busca utilizado")
    mentions: List[SocialMention] = Field(..., description="Lista de menções encontradas")
    total_count: int = Field(..., description="Número total de menções")
    sentiment_summary: dict = Field(..., description="Resumo da análise de sentimentos")