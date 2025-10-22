"""
AgentsVille Trip Planner - Ferramentas

Este módulo contém todas as ferramentas utilizadas pelos agentes para realizar
tarefas específicas durante o planejamento e revisão de itinerários.
"""

from typing import Any, Dict, List

from evaluations import ALL_EVAL_FUNCTIONS, get_eval_results
from models import Activity, TravelPlan
from project_lib import call_activities_api_mocked

try:
    import numexpr as ne
except ImportError:
    # Fallback para avaliação básica de expressões matemáticas
    import ast
    import operator

    class SimpleEvaluator:
        """Avaliador simples de expressões matemáticas como fallback."""

        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }

        def evaluate(self, expr):
            return self._eval(ast.parse(expr, mode="eval").body)

        def _eval(self, node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                return self.operators[type(node.op)](
                    self._eval(node.left), self._eval(node.right)
                )
            elif isinstance(node, ast.UnaryOp):
                return self.operators[type(node.op)](self._eval(node.operand))
            else:
                raise ValueError(f"Unsupported node type: {type(node)}")

    ne = SimpleEvaluator()


def calculator_tool(input_expression: str) -> float:
    """Avalia uma expressão matemática e retorna o resultado como float.

    Args:
        input_expression: String contendo uma expressão matemática válida para avaliar

    Returns:
        float: O resultado da expressão avaliada

    Example:
        >>> calculator_tool("1 + 1")
        2.0
    """
    return float(ne.evaluate(input_expression))


def get_activities_by_date_tool(date: str, city: str) -> List[Dict[str, Any]]:
    """Recupera atividades disponíveis para uma data e cidade específicas.

    Args:
        date (str): Data no formato YYYY-MM-DD para buscar atividades
        city (str): Cidade para buscar atividades (apenas "AgentsVille" é suportado)

    Returns:
        List[Dict[str, Any]]: Lista de atividades disponíveis para a data e cidade especificadas
    """
    resp = call_activities_api_mocked(date=date, city=city)
    return [Activity.model_validate(activity).model_dump() for activity in resp]


def run_evals_tool(
    travel_plan: TravelPlan, vacation_info, client=None, model: str | None = None
) -> Dict[str, Any]:
    """Run all evaluation functions against the provided travel plan.

    Args:
        travel_plan: The travel plan to evaluate (TravelPlan or dict)
        vacation_info: VacationInfo instance or dict with the original request
        client: Optional OpenAI client to be used by evaluation functions
        model: Optional model name to pass to evaluation functions

    Returns:
        Dict[str, Any]: Results of the evaluations including success flag and failures
    """
    if isinstance(travel_plan, dict):
        travel_plan = TravelPlan.model_validate(travel_plan)

    # Accept vacation_info as dict or VacationInfo instance; eval functions expect VacationInfo
    try:
        # Lazy import to avoid circular imports at module import time
        from models import VacationInfo as _VacationInfo

        if isinstance(vacation_info, dict):
            vacation_info_obj = _VacationInfo.model_validate(vacation_info)
        elif isinstance(vacation_info, _VacationInfo):
            vacation_info_obj = vacation_info
        else:
            # Try to coerce
            vacation_info_obj = _VacationInfo.model_validate(vacation_info)
    except Exception:
        # If validation fails, pass through and let evals raise clear errors
        vacation_info_obj = vacation_info

    resp = get_eval_results(
        vacation_info=vacation_info_obj,
        final_output=travel_plan,
        eval_functions=ALL_EVAL_FUNCTIONS,
        client=client,
        model=model,
    )

    return {
        "success": resp.success,
        "failures": resp.failures,
    }


def run_evals_tool_with_global(travel_plan: TravelPlan) -> Dict[str, Any]:
    """Compatibility wrapper: Attempt to import `vacation_info` from main and run evaluations.

    This function keeps previous behavior for code that calls run_evals_tool(travel_plan)
    without providing `vacation_info`. New code should call `run_evals_tool(travel_plan, vacation_info)`.
    """
    try:
        from main import vacation_info  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "run_evals_tool requires `vacation_info` when called without context: %s"
            % e
        )

    return run_evals_tool(travel_plan=travel_plan, vacation_info=vacation_info)


def final_answer_tool(final_output: TravelPlan) -> TravelPlan:
    """Retorna o plano de viagem final.

    Args:
        final_output: O plano de viagem final para retornar

    Returns:
        TravelPlan: O plano de viagem final
    """
    return final_output


# Lista de todas as ferramentas disponíveis para o agente
ALL_TOOLS = [
    calculator_tool,
    get_activities_by_date_tool,
    run_evals_tool,
    final_answer_tool,
]


def get_tool_descriptions_string(tools: List[callable]) -> str:
    """Gera uma descrição de ferramenta a partir da docstring de uma função.

    Args:
        tools: Lista de funções para gerar descrições

    Returns:
        str: String formatada contendo os nomes das funções e suas descrições
    """
    resp = ""
    for tool in tools:
        function_name = tool.__name__
        function_doc = tool.__doc__ or "Nenhuma descrição fornecida."
        resp += f"* `{function_name}`: {function_doc}\n"
    return resp
