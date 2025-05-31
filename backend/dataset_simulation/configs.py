from pydantic import BaseModel, Field
from typing import Dict, Tuple


class ConfigsModel(BaseModel):
    num_sensors: int = Field(default=10, description="Número de sensores")
    wait_time: int = Field(default=5, description="Tempo entre envio de leituras")
    verbose: bool = Field(default=False, description="Modo verbose")


class ReadingsModel(BaseModel):
    api_url: str = Field(default="http://localhost:81", description="URL da API para envio de leituras")
    max_distance: float = Field(default=110.0, description="Distância máxima")
    min_distance_to_clean: float = Field(default=10.0, description="Distância mínima para 'limpar' o bueiro")
    pct_to_clean: float = Field(default=0.3, description="Chance de 'limpar' o bueiro")
    region_modificator: Dict[str, Tuple[int, int]] = Field(default={}, description="Modificadores de região")
    region_modificator_default: Tuple[int, int] = Field(default=(4, -1), description="Modificador de região padrão")


class TicksModelModel(BaseModel):
    tick_days: int = Field(default=0, description="Número de dias por tick")
    tick_hours: int = Field(default=0, description="Número de horas por tick")
    tick_minutes: int = Field(default=15, description="Número de minutos por tick")
    tick_seconds: int = Field(default=0, description="Número de segundos por tick")


class CoordinatesModel(BaseModel):
    latitude: float = Field(default=-16.6869, description="Latitude da coordenada")
    longitude: float = Field(default=-49.2648, description="Longitude da coordenada")
    latitude_range: float = Field(default=0.06, description="Faixa de latitude")
    longitude_range: float = Field(default=0.06, description="Faixa de longitude")


class SimulationModel(BaseModel):
    reading_configs: ReadingsModel = Field(default_factory=lambda: ReadingsModel(), description="Configurações de leitura")
    ticks: TicksModelModel = Field(default_factory=lambda: TicksModelModel(), description="Ticks da simulação")
    coordinates: CoordinatesModel = Field(default_factory=lambda: CoordinatesModel(), description="Coordenadas da simulação")
    configs: ConfigsModel = Field(default_factory=lambda: ConfigsModel(), description="Configurações da simulação")
    