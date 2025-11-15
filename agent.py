# study_planner_agent/agent.py
from google.adk.agents.llm_agent import Agent
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.tools import FunctionTool
from google.adk.models.google_llm import Gemini
from google.genai import types

# -----------------------------
# Retry Options
# -----------------------------
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# -----------------------------
# Custom Calculation Tool (kept for future use)
# -----------------------------
def compute_study_hours(total_hours: float, days: int) -> dict:
    """Compute daily study hours needed."""
    try:
        total = float(total_hours)
        days = int(days)
    except Exception as e:
        return {"status": "error", "message": f"Invalid numeric input: {e}"}
    if days <= 0:
        return {"status": "error", "message": "Days must be > 0"}
    return {"status": "success", "hours_per_day": total / days}

# -----------------------------
# 1. Task Breakdown Agent
# -----------------------------
task_breaker = Agent(
    name="TaskBreakdownAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""
    The user will describe a study goal (for example: "Finish 10 chapters of Physics in 7 days, I am free 2 hours each evening").
    Your job: extract and break this description into a JSON list of subtasks (task name and estimated hours).
    Output ONLY JSON list. Example:
    [
      {"task":"Read Chapter 1", "hours":2},
      {"task":"Practice problems Ch1", "hours":2.5}
    ]
    """,
    output_key="breakdown"
)

# -----------------------------
# 2. Scheduling Agent
# -----------------------------
scheduling_agent = Agent(
    name="SchedulingAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""
    You are a scheduler. Use the task breakdown produced previously ({breakdown}).
    Also use any availability details the user provided in the conversation text.
    Create a simple day-by-day schedule that assigns hours to tasks and respects reasonable daily limits.
    Output a clear, human-readable schedule.
    """,
    output_key="schedule"
)

# -----------------------------
# 3. Critic Agent
# -----------------------------
critic_agent = Agent(
    name="CriticAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""
    Review the schedule below and decide whether it is balanced and realistic.

    Schedule:
    {schedule}

    If the schedule is acceptable, respond EXACTLY with: APPROVED
    Otherwise provide 2-3 concise, actionable suggestions to improve it.
    """,
    output_key="critique"
)

# -----------------------------
# 4. Refiner Agent (loop)
# -----------------------------
def exit_loop():
    """Signal the loop to stop when called by the refiner."""
    return {"status": "approved"}

refiner_agent = Agent(
    name="RefinerAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""
    You receive a critique and a schedule.

    Critique:
    {critique}

    Current schedule:
    {schedule}

    If the critique is EXACTLY "APPROVED", call the exit_loop() tool and return the current schedule unchanged.
    Otherwise, revise the schedule to address the critique and output the improved schedule.
    """,
    tools=[FunctionTool(exit_loop)],
    output_key="schedule"
)

# -----------------------------
# LoopAgent: Critic -> Refiner
# -----------------------------
loop = LoopAgent(
    name="ScheduleRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=3
)

# -----------------------------
# Root pipeline
# -----------------------------
root_agent = SequentialAgent(
    name="StudyPlannerRoot",
    sub_agents=[task_breaker, scheduling_agent, loop]
)

# ADK entrypoint for this module
def get_root_agent():
    return root_agent
