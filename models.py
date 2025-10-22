"""
AgentsVille Trip Planner - Modelos de Dados Simplificados

Este módulo contém todos os modelos Pydantic utilizados no projeto para validação
e estruturação de dados.
"""

from datetime import datetime, date
from typing import List, Dict, Any
from pydantic import BaseModel
from project_lib import Interest


class Traveler(BaseModel):
    """Representa um viajante com nome, idade e interesses."""

    name: str
    age: int
    interests: List[Interest]


class VacationInfo(BaseModel):
    """Informações sobre a viagem incluindo viajantes, destino, datas e orçamento."""

    travelers: List[Traveler]
    destination: str
    date_of_arrival: date
    date_of_departure: date
    budget: int


class Weather(BaseModel):
    """Informações meteorológicas para um dia específico."""

    temperature: float
    temperature_unit: str
    condition: str


class Activity(BaseModel):
    """Representa uma atividade disponível."""

    activity_id: str
    name: str
    start_time: datetime
    end_time: datetime
    location: str
    description: str
    price: int
    related_interests: List[Interest]


class ActivityRecommendation(BaseModel):
    """Recomendação de atividade com justificativas."""

    activity: Activity
    reasons_for_recommendation: List[str]


class ItineraryDay(BaseModel):
    """Plano de um dia específico do itinerário."""

    date: date
    weather: Weather
    activity_recommendations: List[ActivityRecommendation]


class TravelPlan(BaseModel):
    """Plano de viagem completo."""

    city: str
    start_date: date
    end_date: date
    total_cost: int
    itinerary_days: List[ItineraryDay]


class EvaluationResults(BaseModel):
    """Resultados de avaliação do itinerário."""

    success: bool
    failures: List[str] = []
    eval_functions: List[str] = []


class ToolCall(BaseModel):
    """Chamada de ferramenta para o agente ReAct."""

    tool_name: str
    arguments: Dict[str, Any] = {}
