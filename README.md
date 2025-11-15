Smart Study Planner — Multi-Agent AI Scheduler

🧠 Problem Statement



Students often struggle to turn large study goals into realistic, day-by-day plans. Manual planning is slow, inconsistent, and rarely optimised.

This project solves that by generating automated study schedules based on tasks, availability, and workload.



🤖 Why Agents?



A single LLM is not enough for planning, checking, and refining a schedule.

A multi-agent workflow works far better:



One agent breaks down tasks



One agent builds a schedule



A critic evaluates



A refiner improves until approved



This creates a self-correcting, high-quality schedule.



🏗️ Architecture Overview

Root Agent (SequentialAgent)



1️⃣ TaskBreakdownAgent – converts user goals into tasks

2️⃣ SchedulingAgent – creates a draft schedule

3️⃣ ScheduleRefinementLoop – repeated critique → improve



Loop Structure



CriticAgent → checks if the schedule is realistic



RefinerAgent → fixes the schedule or approves via exit\_loop()



Custom Tools



compute\_study\_hours()



exit\_loop() (signals loop completion)



Architecture uses:



Sequential agents



Loop agents



Function tools



Gemini models (2.5-flash)



🖥️ Demo Output



A sample run produces:



Full breakdown of study tasks



A 7-day structured schedule



Improvements + refinements



Final APPROVED schedule



(Include a screenshot or text from your CMD if you want here.)



🔧 The Build — Tools \& Tech



Python ADK



Gemini 2.5 Flash



SequentialAgent + LoopAgent



FunctionTool



Custom Tools



CLI runner (adk run .)



🚀 If I Had More Time



Add Google Calendar export



Build a web UI



Add long-term memory for recurring study patterns



Deploy via Vertex Agent Engine



Add API access for mobile apps

