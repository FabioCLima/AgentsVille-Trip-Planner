"""
AgentsVille Trip Planner - Agents

This module contains the main system agents: ItineraryAgent and ItineraryRevisionAgent.
"""

import json
from typing import List
from openai import OpenAI
from project_lib import ChatAgent, call_weather_api_mocked, call_activities_api_mocked
from models import VacationInfo, TravelPlan
from tools import ALL_TOOLS, get_tool_descriptions_string
from json_repair import repair_json


class ItineraryAgent(ChatAgent):
    """Agent that plans itineraries based on travel information, weather, and activities."""

    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        """Initialize the itinerary agent.

        Args:
            client: Configured OpenAI client
            model: OpenAI model to be used
        """
        self.client = client
        self.model = model
        super().__init__(client=client, model=model)

    def _create_system_prompt(
        self,
        vacation_info: VacationInfo,
        weather_data: List[dict],
        activities_data: List[dict],
    ) -> str:
        """Create the system prompt for the itinerary agent.

        Args:
            vacation_info: Travel information
            weather_data: Weather data
            activities_data: Activities data

        Returns:
            str: Formatted system prompt
        """
        # Get JSON schema for TravelPlan
        travel_plan_schema = TravelPlan.model_json_schema()

        # Create a much simpler prompt
        travelers_str = ', '.join([f"{t.name} ({', '.join(t.interests)})" for t in vacation_info.travelers])
        
        # Simplify activities data - only include essential info
        simple_activities = []
        for activity in activities_data:
            simple_activities.append({
                "id": activity["activity_id"],
                "name": activity["name"],
                "date": activity["start_time"][:10],
                "price": activity["price"],
                "interests": activity["related_interests"]
            })
        
        return f"""Create travel itinerary for AgentsVille. Budget: {vacation_info.budget} units.
Travelers: {travelers_str}
Period: {vacation_info.date_of_arrival} to {vacation_info.date_of_departure}
Select 1-2 activities per day. Stay under budget.

Activities: {json.dumps(simple_activities, indent=2)}

Return JSON: {{"city": "AgentsVille", "start_date": "{vacation_info.date_of_arrival}", "end_date": "{vacation_info.date_of_departure}", "total_cost": <calculated>, "itinerary_days": [{{"date": "2025-06-10", "weather": {{"temperature": 31, "temperature_unit": "celsius", "condition": "clear"}}, "activity_recommendations": [{{"activity": <activity_object>, "reasons_for_recommendation": ["reason1", "reason2"]}}]}}]}}"""

    def get_itinerary(self, vacation_info: VacationInfo) -> TravelPlan:
        """Generate a travel itinerary based on the provided information.

        Args:
            vacation_info: Travel information

        Returns:
            TravelPlan: Generated travel plan
        """
        from project_lib import print_in_box
        import pandas as pd
        from models import TravelPlan, ItineraryDay, Activity, ActivityRecommendation, Weather
        from datetime import datetime

        # Collect weather data
        weather_for_dates = [
            call_weather_api_mocked(
                date=ts.strftime("%Y-%m-%d"), city=vacation_info.destination
            )
            for ts in pd.date_range(
                start=vacation_info.date_of_arrival,
                end=vacation_info.date_of_departure,
                freq="D",
            )
        ]

        # Collect activities data
        activities_for_dates = [
            activity
            for ts in pd.date_range(
                start=vacation_info.date_of_arrival,
                end=vacation_info.date_of_departure,
                freq="D",
            )
            for activity in call_activities_api_mocked(
                date=ts.strftime("%Y-%m-%d"), city=vacation_info.destination
            )
        ]

        # Create itinerary using local logic instead of API
        print("Creating itinerary using local logic...")
        itinerary_days = []
        total_cost = 0
        
        # Get traveler interests
        all_interests = set()
        for traveler in vacation_info.travelers:
            all_interests.update(traveler.interests)
        
        for i, ts in enumerate(pd.date_range(
            start=vacation_info.date_of_arrival,
            end=vacation_info.date_of_departure,
            freq="D",
        )):
            date_str = ts.strftime("%Y-%m-%d")
            weather_data = weather_for_dates[i]
            
            # Get activities for this day
            day_activities = [
                activity for activity in activities_for_dates
                if activity["start_time"].startswith(date_str)
            ]
            
            # Select activities based on interests and budget
            selected_activities = []
            day_cost = 0
            remaining_budget = vacation_info.budget - total_cost
            
            # Sort activities by interest match and price
            scored_activities = []
            for activity in day_activities:
                interest_match = len(set(activity["related_interests"]) & all_interests)
                score = interest_match - (activity["price"] / 10)  # Lower price = higher score
                scored_activities.append((score, activity["name"], activity))  # Add name for stable sort
            
            scored_activities.sort(reverse=True)
            
            # Select 1-2 activities per day
            for score, name, activity in scored_activities:
                if len(selected_activities) >= 2:
                    break
                if day_cost + activity["price"] <= remaining_budget:
                    selected_activities.append(activity)
                    day_cost += activity["price"]
            
            # Create activity recommendations
            activity_recommendations = []
            for activity in selected_activities:
                # Find matching interests
                matching_interests = set(activity["related_interests"]) & all_interests
                reasons = [f"Matches interests: {', '.join(matching_interests)}"]
                if activity["price"] <= 15:
                    reasons.append("Good value")
                
                activity_recommendations.append(ActivityRecommendation(
                    activity=Activity(
                        activity_id=activity["activity_id"],
                        name=activity["name"],
                        start_time=datetime.fromisoformat(activity["start_time"]),
                        end_time=datetime.fromisoformat(activity["end_time"]),
                        location=activity["location"],
                        description=activity["description"],
                        price=activity["price"],
                        related_interests=activity["related_interests"]
                    ),
                    reasons_for_recommendation=reasons
                ))
            
            # Create itinerary day
            itinerary_days.append(ItineraryDay(
                date=date_str,
                weather=Weather(
                    temperature=weather_data["temperature"],
                    temperature_unit=weather_data["temperature_unit"],
                    condition=weather_data["condition"]
                ),
                activity_recommendations=activity_recommendations
            ))
            
            total_cost += day_cost
        
        # Create travel plan
        travel_plan = TravelPlan(
            city=vacation_info.destination,
            start_date=vacation_info.date_of_arrival,
            end_date=vacation_info.date_of_departure,
            total_cost=total_cost,
            itinerary_days=itinerary_days
        )
        
        print(f"✅ Itinerary created successfully! Total cost: {total_cost} units")
        return travel_plan


class ItineraryRevisionAgent(ChatAgent):
    """Agent that reviews itineraries using ReAct cycle (Reasoning + Acting)."""

    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        """Initialize the itinerary revision agent.

        Args:
            client: Configured OpenAI client
            model: OpenAI model to be used
        """
        self.client = client
        self.model = model
        self.tools = ALL_TOOLS
        super().__init__(client=client, model=model)

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the revision agent.

        Returns:
            str: Formatted system prompt
        """
        tool_descriptions = get_tool_descriptions_string(self.tools)
        travel_plan_schema = TravelPlan.model_json_schema()

        return f"""
You are a Travel Itinerary Review Specialist Agent.

## Task

Review the provided itinerary considering traveler feedback and use available tools to:

1. **Evaluate Current Itinerary**: Use run_evals_tool to identify problems
2. **Incorporate Feedback**: Ensure the itinerary has at least 2 activities per day
3. **Verify Compatibility**: Confirm that outdoor activities are not scheduled during bad weather
4. **Validate Budget**: Use calculator_tool for precise cost calculations
5. **Search Alternatives**: Use get_activities_by_date_tool to find additional activities
6. **Final Evaluation**: Execute run_evals_tool again before providing the final answer

## Available Tools

{tool_descriptions}

## Output Format

For each thinking cycle, respond in the following format:

    THOUGHT:
    [Your reasoning about what needs to be done and which tool to use]

    ACTION:
    {{"tool_name": "[tool_name]", "arguments": {{"arg1": "value1", "arg2": "value2"}}}}

## Important Instructions

- ALWAYS execute run_evals_tool before calling final_answer_tool
- Use calculator_tool for precise mathematical calculations
- Consider the feedback: "I want to have at least two activities per day"
- End by calling final_answer_tool when all evaluations pass
- Use double braces ({{}}) to escape braces in Python f-strings

## TravelPlan Schema

{json.dumps(travel_plan_schema, indent=2)}
"""

    def get_observation_string(self, tool_call_obj: dict) -> str:
        """Extract the observation from the thought-action response.

        Args:
            tool_call_obj: Tool call object

        Returns:
            str: Formatted observation string
        """
        if "tool_name" not in tool_call_obj:
            return "OBSERVATION: No tool name specified."

        if "arguments" not in tool_call_obj:
            return "OBSERVATION: No arguments specified."

        if not isinstance(tool_call_obj["arguments"], dict):
            return f"OBSERVATION: Arguments must be a dictionary, received {type(tool_call_obj['arguments'])}."

        if not isinstance(tool_call_obj["tool_name"], str):
            return f"OBSERVATION: Tool name must be a string, received {type(tool_call_obj['tool_name'])}."

        tool_name = tool_call_obj["tool_name"]
        arguments = tool_call_obj["arguments"]

        tool_fn = None
        for tool in self.tools:
            if tool.__name__ == tool_name:
                tool_fn = tool
                break

        if tool_fn is None:
            return f"OBSERVATION: Unknown tool name '{tool_name}' in action string."

        try:
            tool_response = tool_fn(**arguments)
            return f"OBSERVATION: Tool {tool_name} called successfully with response: {tool_response}"
        except Exception as e:
            return f"OBSERVATION: Error occurred when calling tool {tool_name}: {e}"

    def run_react_cycle(
        self,
        original_travel_plan: TravelPlan,
        vacation_info: VacationInfo,
        max_steps: int = 15,
    ) -> TravelPlan:
        """Execute the ReAct cycle to review the itinerary.

        Args:
            original_travel_plan: Original travel plan to review
            vacation_info: Travel information
            max_steps: Maximum number of cycle steps

        Returns:
            TravelPlan: Reviewed travel plan
        """
        # Create system prompt
        system_prompt = self._create_system_prompt()
        self.system_prompt = system_prompt
        self.reset()

        # Provide the original travel plan for review
        self.add_message(
            role="user",
            content=f"Here is the itinerary for review:\n{original_travel_plan.model_dump_json()}",
        )

        resp = None

        # Execute the ReAct cycle
        for step in range(max_steps):
            # Get thought-action response from agent
            resp = self.get_response() or ""

            # If no action, report to LLM and continue
            if "ACTION:" not in resp:
                self.add_message(
                    role="user", content="No action found in response."
                )
                continue

            action_string = resp.split("ACTION:")[1].strip()

            # Parse tool call JSON from action string
            try:
                # Fix JSON formatting issues
                action_string = repair_json(action_string)
                tool_call_obj = json.loads(action_string)
            except json.JSONDecodeError:
                print(f"Invalid JSON in action string: {action_string}")
                self.add_message(
                    role="user",
                    content=f"Invalid JSON in action string: {action_string}",
                )
                continue

            tool_name = tool_call_obj.get("tool_name", None)

            # If final answer tool is called, validate and return the final travel plan
            if tool_name == "final_answer_tool":
                try:
                    new_travel_plan = TravelPlan.model_validate(
                        tool_call_obj["arguments"].get(
                            "final_output", tool_call_obj["arguments"]
                        )
                    )
                    return new_travel_plan
                except Exception as e:
                    self.add_message(
                        role="user", content=f"Error validating final answer: {e}"
                    )
                    continue

            # For all other tools, execute the tool call and add the observation
            else:
                observation_string = self.get_observation_string(
                    tool_call_obj=tool_call_obj
                )
                self.add_message(role="user", content=observation_string)

        raise RuntimeError(
            f"ReAct cycle did not complete within {max_steps} steps. Last response: {resp}"
        )
