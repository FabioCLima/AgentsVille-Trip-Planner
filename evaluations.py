"""
AgentsVille Trip Planner - Funções de Avaliação

Este módulo contém todas as funções de avaliação utilizadas para verificar
a qualidade dos itinerários gerados.
"""

import os
from inspect import signature
from typing import List

from openai import OpenAI

from models import Activity, EvaluationResults, TravelPlan, VacationInfo
from project_lib import ChatAgent, call_activity_by_id_api_mocked, do_chat_completion


class AgentError(Exception):
    """Exceção personalizada para erros de avaliação do agente."""

    pass


def eval_start_end_dates_match(
    vacation_info: VacationInfo, final_output: TravelPlan
) -> None:
    """Verifica se as datas de chegada e partida coincidem com as datas do itinerário.

    Args:
        vacation_info: Informações da viagem
        final_output: Plano de viagem final

    Raises:
        AgentError: Se as datas não coincidem ou são inválidas
    """
    if (
        vacation_info.date_of_arrival != final_output.start_date
        or vacation_info.date_of_departure != final_output.end_date
    ):
        raise AgentError(
            f"Datas não coincidem: {vacation_info.date_of_arrival} != {final_output.start_date} "
            f"ou {vacation_info.date_of_departure} != {final_output.end_date}"
        )

    if final_output.start_date > final_output.end_date:
        raise AgentError(
            f"Data de início é posterior à data de término: {final_output.start_date} > {final_output.end_date}"
        )


def eval_total_cost_is_accurate(
    vacation_info: VacationInfo, final_output: TravelPlan
) -> None:
    """Verifica se o custo total declarado corresponde à soma dos preços das atividades.

    Args:
        vacation_info: Informações da viagem
        final_output: Plano de viagem final

    Raises:
        AgentError: Se o custo total não corresponde ao calculado
    """
    actual_total_cost = 0

    for itinerary_day in final_output.itinerary_days:
        for activity_recommendation in itinerary_day.activity_recommendations:
            actual_total_cost += activity_recommendation.activity.price

    stated_total_cost = int(final_output.total_cost)

    if actual_total_cost != stated_total_cost:
        raise AgentError(
            f"Custo total declarado não corresponde ao calculado: {actual_total_cost} != {stated_total_cost}"
        )


def eval_total_cost_is_within_budget(
    vacation_info: VacationInfo, final_output: TravelPlan
) -> None:
    """Verifica se o custo total está dentro do orçamento especificado.

    Args:
        vacation_info: Informações da viagem
        final_output: Plano de viagem final

    Raises:
        AgentError: Se o custo total excede o orçamento
    """
    stated_total_cost = int(final_output.total_cost)
    if stated_total_cost > vacation_info.budget:
        raise AgentError(
            f"Custo total excede o orçamento: {stated_total_cost} > {vacation_info.budget}"
        )


def eval_itinerary_events_match_actual_events(
    vacation_info: VacationInfo, final_output: TravelPlan
) -> None:
    """Verifica se os eventos listados no itinerário correspondem aos eventos reais.

    Args:
        vacation_info: Informações da viagem
        final_output: Plano de viagem final

    Raises:
        AgentError: Se há eventos faltando ou não correspondentes
    """
    event_ids_not_matching = []
    event_ids_missing = []

    for itinerary_day in final_output.itinerary_days:
        for activity_recommendation in itinerary_day.activity_recommendations:
            event_id = activity_recommendation.activity.activity_id
            reference_event = call_activity_by_id_api_mocked(event_id)

            if reference_event is None:
                event_ids_missing.append(event_id)
            elif Activity(**reference_event) != activity_recommendation.activity:
                print(
                    "---\n"
                    f"Evento ID {event_id} não corresponde ao evento de referência:\n"
                    f"Evento de Referência: {reference_event}\n"
                    f"Evento da Atividade: {activity_recommendation.activity.model_dump()}"
                )
                event_ids_not_matching.append(event_id)

    if event_ids_missing or event_ids_not_matching:
        raise AgentError(
            f"IDs de eventos faltando: {event_ids_missing}\nIDs de eventos não correspondentes: {event_ids_not_matching}"
        )


def eval_itinerary_satisfies_interests(
    vacation_info: VacationInfo, final_output: TravelPlan
) -> None:
    """Verifica se o itinerário inclui atividades que correspondem aos interesses de cada viajante.

    Args:
        vacation_info: Informações da viagem
        final_output: Plano de viagem final

    Raises:
        AgentError: Se algum viajante não tem atividades correspondentes aos seus interesses
    """
    traveler_to_interests = {}
    traveler_to_interest_hit_counts = {}

    for traveler in vacation_info.travelers:
        traveler_to_interests[traveler.name] = traveler.interests
        traveler_to_interest_hit_counts[traveler.name] = 0

    for traveler_name in traveler_to_interests:
        for itinerary_day in final_output.itinerary_days:
            for activity_recommendation in itinerary_day.activity_recommendations:
                matching_interests = set(traveler_to_interests[traveler_name]) & set(
                    activity_recommendation.activity.related_interests
                )

                if matching_interests:
                    traveler_to_interest_hit_counts[traveler_name] += 1
                    print(
                        f"✅ Viajante {traveler_name} tem uma correspondência com interesse {matching_interests} "
                        f"em {activity_recommendation.activity.name}"
                    )

    travelers_with_no_interest_hits = [
        traveler
        for traveler, interest_hit_count in traveler_to_interest_hit_counts.items()
        if interest_hit_count == 0
    ]

    if travelers_with_no_interest_hits:
        raise AgentError(
            f"Viajantes {travelers_with_no_interest_hits} não têm correspondências com o itinerário."
        )


def eval_activities_and_weather_are_compatible(
    vacation_info: VacationInfo,
    final_output: TravelPlan,
    client: OpenAI | None = None,
    model: str | None = None,
) -> None:
    """Verifica se nenhuma atividade exclusivamente ao ar livre está agendada durante condições climáticas adversas.

    Args:
        vacation_info: Informações da viagem
        final_output: Plano de viagem final

    Raises:
        AgentError: Se há atividades ao ar livre agendadas durante mau tempo
    """
    # If no client is provided, create one from environment (backwards compatibility)
    if client is None:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your_api_key_here"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1"),
        )

    # Prompt para avaliar compatibilidade entre atividade e clima
    ACTIVITY_AND_WEATHER_ARE_COMPATIBLE_SYSTEM_PROMPT = """
    Você é um especialista em avaliar a compatibilidade entre atividades e condições climáticas.

    ## Tarefa
    Determine se uma atividade deve ser evitada devido às condições climáticas. 
    Considere se a atividade é exclusivamente ao ar livre e se as condições climáticas 
    podem arruinar a experiência. Quando não há informações suficientes, assuma que 
    a atividade É_COMPATÍVEL com o clima. Também, observe opções de backup mencionadas 
    na descrição da atividade.

    ## Formato de saída

        RACIOCÍNIO:
        [análise passo a passo da compatibilidade]

        RESPOSTA FINAL:
        [É_COMPATÍVEL, É_INCOMPATÍVEL]

    ## Exemplos
    Atividade: Piquenique no parque
    Descrição: Almoço ao ar livre com jogos e atividades
    Condição Climática: chuva
    RACIOCÍNIO: Esta atividade é exclusivamente ao ar livre e não há menção de opções de backup. A chuva arruinaria completamente a experiência.
    RESPOSTA FINAL: É_INCOMPATÍVEL

    Atividade: Visita ao museu
    Descrição: Exploração de arte e história em ambiente interno
    Condição Climática: chuva
    RACIOCÍNIO: Esta atividade é realizada em ambiente interno e não é afetada pelas condições climáticas externas.
    RESPOSTA FINAL: É_COMPATÍVEL
    """.strip()

    activities_that_are_incompatible = []

    for itinerary_day in final_output.itinerary_days:
        weather_condition = itinerary_day.weather.condition

        for activity_recommendation in itinerary_day.activity_recommendations:
            resp = do_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": ACTIVITY_AND_WEATHER_ARE_COMPATIBLE_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": f"Atividade: {activity_recommendation.activity.name}\n"
                        f"Descrição: {activity_recommendation.activity.description}\n"
                        f"Condição Climática: {weather_condition}",
                    },
                ],
                client=client,
                model=model or "gpt-4.1-nano",
            )

            if "É_COMPATÍVEL" in (resp or ""):
                is_compatible = True
            elif "É_INCOMPATÍVEL" in (resp or ""):
                is_compatible = False
            else:
                raise RuntimeError(
                    f"Resposta inesperada do modelo: {resp}. Esperado 'É_COMPATÍVEL' ou 'É_INCOMPATÍVEL'."
                )

            if is_compatible:
                print(
                    f"✅ Atividade {activity_recommendation.activity.name} (em {itinerary_day.date}) "
                    f"e clima '{weather_condition}' são compatíveis."
                )
            else:
                activities_that_are_incompatible.append(
                    activity_recommendation.activity.name
                )
                print(
                    f"❌ Atividade {activity_recommendation.activity.name} (em {itinerary_day.date}) "
                    f"e clima '{weather_condition}' são incompatíveis."
                )

    if activities_that_are_incompatible:
        raise AgentError(
            f"Atividades que podem ser arruinadas por mau tempo: {activities_that_are_incompatible}"
        )


def eval_traveler_feedback_is_incorporated(
    vacation_info: VacationInfo,
    final_output: TravelPlan,
    client: OpenAI | None = None,
    model: str | None = None,
) -> None:
    """Verifica se o feedback do viajante foi incorporado ao plano de viagem revisado.

    Args:
        vacation_info: Informações da viagem
        final_output: Plano de viagem final

    Raises:
        AgentError: Se o feedback do viajante não foi incorporado com sucesso
    """
    # If no client is provided, create one from environment (backwards compatibility)
    if client is None:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your_api_key_here"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1"),
        )

    TRAVELER_FEEDBACK = "Quero ter pelo menos duas atividades por dia."

    agent = ChatAgent(
        system_prompt="""Você é um especialista em avaliar se um plano de viagem incorpora o feedback do viajante.

    ## Formato de Saída

    Responda usando duas seções (ANÁLISE E SAÍDA FINAL) no seguinte formato:

        ANÁLISE:
        * [análise passo a passo]

        SAÍDA FINAL:
        [TOTALMENTE_INCORPORADO, PARCIALMENTE_INCORPORADO, NÃO_INCORPORADO, ou DESCONHECIDO]
        MOTIVO: [raciocínio para a saída final]

    """,
        client=client,
        model=model or "gpt-4.1",
    )

    resp = agent.chat(
        f"""Feedback do Viajante: {TRAVELER_FEEDBACK}
    Plano de Viagem Revisado: {final_output.model_dump_json()}
    """
    )

    if "SAÍDA FINAL:" not in resp:
        raise RuntimeError(
            f"Resposta inesperada do modelo: {resp}. Esperado 'SAÍDA FINAL:'."
        )

    if "TOTALMENTE_INCORPORADO" not in resp:
        final_output_text = resp.split("SAÍDA FINAL:")[-1].strip()
        raise AgentError(
            f"Feedback do viajante não foi incorporado com sucesso ao plano de viagem revisado. "
            f"Resposta: {final_output_text}"
        )


# Lista de todas as funções de avaliação
ALL_EVAL_FUNCTIONS = [
    eval_start_end_dates_match,
    eval_total_cost_is_accurate,
    eval_itinerary_events_match_actual_events,
    eval_itinerary_satisfies_interests,
    eval_total_cost_is_within_budget,
    eval_activities_and_weather_are_compatible,
    eval_traveler_feedback_is_incorporated,
]


def get_eval_results(
    vacation_info: VacationInfo,
    final_output: TravelPlan,
    eval_functions: List[callable],
    client: OpenAI | None = None,
    model: str | None = None,
) -> EvaluationResults:
    """Avalia o resultado final do agente de itinerário contra um conjunto de funções de avaliação.

    Args:
        vacation_info: Informações da viagem utilizadas para gerar o itinerário
        final_output: Resultado final do agente de itinerário
        eval_functions: Lista de funções de avaliação para aplicar

    Returns:
        EvaluationResults: Objeto contendo o status de sucesso, falhas e nomes das funções de avaliação utilizadas
    """
    from project_lib import print_in_box

    if not isinstance(vacation_info, VacationInfo):
        raise ValueError("vacation_info deve ser uma instância de VacationInfo")
    if not isinstance(final_output, TravelPlan):
        raise ValueError("final_output deve ser uma instância de TravelPlan")
    if not isinstance(eval_functions, list) or not all(
        callable(fn) for fn in eval_functions
    ):
        raise ValueError("eval_functions deve ser uma lista de funções chamáveis")

    eval_results = []
    for eval_fn in eval_functions:
        try:
            # Determine whether the eval function accepts optional client/model args
            try:
                params = signature(eval_fn).parameters
            except Exception:
                params = {}

            kwargs = {}
            if "client" in params:
                kwargs["client"] = client
            if "model" in params:
                kwargs["model"] = model

            eval_fn(vacation_info, final_output, **kwargs)
        except AgentError as e:
            error_msg = str(e)
            print_in_box(error_msg, title="Erro de Avaliação")
            print("\n\n")

            eval_results.append(error_msg)

    return EvaluationResults(
        success=len(eval_results) == 0,
        failures=eval_results,
        eval_functions=[fn.__name__ for fn in eval_functions],
    )
