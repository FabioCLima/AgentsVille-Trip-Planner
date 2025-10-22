from datetime import date, datetime

import project_lib
from models import (
    Activity,
    ActivityRecommendation,
    ItineraryDay,
    Traveler,
    TravelPlan,
    VacationInfo,
    Weather,
)
from project_lib import Interest
from tools import calculator_tool, get_activities_by_date_tool, run_evals_tool


def test_calculator_tool_basic():
    assert calculator_tool("2 + 3 * 4") == 14.0


def test_get_activities_by_date_tool_returns_list():
    activities = get_activities_by_date_tool("2025-06-10", "AgentsVille")
    assert isinstance(activities, list)
    assert len(activities) >= 1


def make_sample_vacation_info():
    traveler = Traveler(name="Test", age=30, interests=[Interest.TECHNOLOGY])
    return VacationInfo(
        travelers=[traveler],
        destination="AgentsVille",
        date_of_arrival=date(2025, 6, 10),
        date_of_departure=date(2025, 6, 10),
        budget=100,
    )


def test_run_evals_tool_runs_ok():
    # create a minimal travel plan using the mock data shapes
    weather = Weather(temperature=25.0, temperature_unit="celsius", condition="clear")
    activity = Activity(
        activity_id="event-2025-06-10-0",
        name="FutureTech Breakfast Meet-Up",
        start_time=datetime(2025, 6, 10, 9, 0),
        end_time=datetime(2025, 6, 10, 11, 0),
        location="The Innovation Atrium",
        description="Indoors tech meetup",
        price=20,
        related_interests=[Interest.TECHNOLOGY],
    )

    activity_rec = ActivityRecommendation(
        activity=activity, reasons_for_recommendation=["Good match"]
    )
    itinerary_day = ItineraryDay(
        date=date(2025, 6, 10), weather=weather, activity_recommendations=[activity_rec]
    )
    travel_plan = TravelPlan(
        city="AgentsVille",
        start_date=date(2025, 6, 10),
        end_date=date(2025, 6, 10),
        total_cost=20,
        itinerary_days=[itinerary_day],
    )

    vacation_info = make_sample_vacation_info()

    # Patch project_lib.do_chat_completion and ChatAgent to avoid real API calls
    def fake_do_chat_completion(messages, client=None, model=None, **kwargs):
        # For the activity/weather compatibility check return "É_COMPATÍVEL"
        return "É_COMPATÍVEL"

    class DummyChatAgent:
        def __init__(self, system_prompt=None, client=None, model=None):
            pass

        def chat(self, *args, **kwargs):
            # Return a response that contains TOTALMENTE_INCORPORADO to make the feedback eval pass
            return "ANÁLISE:\n...\nSAÍDA FINAL:\nTOTALMENTE_INCORPORADO\nMOTIVO: ok"

    import evaluations

    # Patch both project_lib and evaluations module references used by evaluation functions
    project_lib.do_chat_completion = fake_do_chat_completion
    project_lib.ChatAgent = DummyChatAgent
    evaluations.do_chat_completion = fake_do_chat_completion
    evaluations.ChatAgent = DummyChatAgent

    result = run_evals_tool(travel_plan, vacation_info)
    # result should be a dict with success boolean and failures list
    assert isinstance(result, dict)
    assert "success" in result and "failures" in result
