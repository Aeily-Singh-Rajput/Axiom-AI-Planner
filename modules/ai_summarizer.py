"""
AI Summarizer Module
Uses OpenRouter API for:
- text summarization
- study plan generation
- AI academic insights
"""

import os
import re
from datetime import datetime
from openai import OpenAI
from axiom_planner.modules.data_manager import filter_active_tasks

# =========================
# GROQ KEY ROTATION CONFIG
# =========================

def _get_groq_keys():
    keys_str = os.getenv("GROQ_API_KEYS", "")
    return [k.strip() for k in keys_str.split(",") if k.strip()]

def _generate_with_fallback(model, messages, temperature):
    keys = _get_groq_keys()
    if not keys:
        raise Exception("No Groq API keys found. Please set GROQ_API_KEYS.")

    for i, key in enumerate(keys):
        try:
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=key,
                timeout=10.0
            )
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Key Rotation] Key {i+1} failed: {e}")
            if i == len(keys) - 1:
                raise Exception("All provided Groq API keys failed due to limits or errors.")
            continue


# =========================
# HTML FORMATTER
# =========================

def _convert_markdown_to_html(text):
    """Convert simple markdown-like formatting to HTML."""
    
    if not text:
        return ""

    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    html = re.sub(r"(?m)^\*\s*", "• ", html)

    html = html.replace("\n", "<br/>")

    return html


# =========================
# TEXT SUMMARIZER
# =========================

def summarize_text(text):
    """
    Summarizes extracted text using OpenRouter AI.
    """

    if not text or len(text.strip()) == 0:
        return "No text provided for summarization."

    keys = _get_groq_keys()
    if not keys:
        return "AI summarization not available. Please set GROQ_API_KEYS."

    try:

        truncated = text[:10000]

        prompt = f"""
You are an intelligent academic assistant.

Summarize the following study material clearly and concisely.

Then provide:
1. Key concepts
2. Important topics
3. Three actionable next steps for the student

Study Material:
{truncated}
"""

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI academic productivity assistant "
                    "specialized in helping students learn efficiently."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        summary_text = _generate_with_fallback(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7
        )

        if summary_text:
            return summary_text.strip()

        return "Summary not available."

    except Exception as e:

        print(f"[AI Summarizer Error] {e}")

        return f"Could not generate summary: {str(e)[:150]}"


# =========================
# STUDY PLAN GENERATOR
# =========================

def generate_study_plan(assignments, exams, stress):
    """
    Generates a personalized 7-day AI study plan.
    """

    keys = _get_groq_keys()
    if not keys:
        return "AI study plan generation not available. Please set GROQ_API_KEYS."
        
    # Filter out completed items
    assignments = filter_active_tasks(assignments)
    exams = filter_active_tasks(exams)

    try:

        today = datetime.today().date()

        plan_input = f"Current date: {today}\n\n"

        # =========================
        # ASSIGNMENTS
        # =========================

        plan_input += "Assignments:\n"

        if assignments:
            for a in assignments:

                try:
                    days_left = (
                        datetime.strptime(
                            a["deadline"],
                            "%Y-%m-%d"
                        ).date() - today
                    ).days

                except:
                    days_left = "Unknown"

                plan_input += (
                    f"- {a['title']} | "
                    f"Due in: {days_left} days | "
                    f"Difficulty: {a.get('difficulty', 'Unknown')} | "
                    f"Size: {a.get('size', 'Unknown')}\n"
                )

        else:
            plan_input += "- No assignments available.\n"

        # =========================
        # EXAMS
        # =========================

        plan_input += "\nExams:\n"

        if exams:
            for e in exams:

                try:
                    days_left = (
                        datetime.strptime(
                            e["exam_date"],
                            "%Y-%m-%d"
                        ).date() - today
                    ).days

                except:
                    days_left = "Unknown"

                plan_input += (
                    f"- {e['subject']} | "
                    f"Exam in: {days_left} days\n"
                )

        else:
            plan_input += "- No upcoming exams.\n"

        # =========================
        # STRESS
        # =========================

        if isinstance(stress, dict):

            stress_level = stress.get("level", "Unknown")

            stress_reasons = ", ".join(
                stress.get("reasons", [])
            )

        else:
            stress_level = str(stress)
            stress_reasons = ""

        plan_input += (
            f"\nStress Level: {stress_level}\n"
            f"Stress Reasons: {stress_reasons}\n\n"
        )

        # =========================
        # MAIN PROMPT
        # =========================

        plan_input += """
Generate a calm, motivating, realistic 7-day study plan.

IMPORTANT RULES:
- Keep workload balanced
- Prioritize urgent deadlines
- Avoid burnout
- Include breaks
- Include motivational advice
- Keep tone supportive and intelligent

FORMAT STRICTLY LIKE THIS:

Day 1:
- Task
- Task
- Break suggestion

Day 2:
- Task
- Task
- Revision

Continue until Day 7.

At the end include:
Motivation:
<short motivational insight>
"""

        # =========================
        # API CALL
        # =========================

        messages=[
            {
                "role": "system",
                "content": (
                    "You are Axiom AI Planner, "
                    "a premium AI-powered academic productivity assistant."
                )
            },
            {
                "role": "user",
                "content": plan_input
            }
        ]

        plan_text = _generate_with_fallback(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.8
        )

        if plan_text:
            return plan_text.strip()

        return "Could not generate study plan."

    except Exception as e:

        print(f"[AI Study Planner Error] {e}")

        return f"Could not generate study plan: {str(e)[:150]}"


# =========================
# STUDY PLAN PARSER
# =========================

def parse_study_plan_text(study_plan_text):
    """
    Parse study plan into collapsible sections.
    """

    if not study_plan_text or not study_plan_text.strip():
        return []

    def _clean_title(text):

        title = re.sub(r"\*\*(.+?)\*\*", r"\1", text)

        title = title.replace("#", "")
        title = title.replace("*", "")

        return title.strip()

    lines = [
        line.strip()
        for line in study_plan_text.splitlines()
        if line.strip()
    ]

    sections = []

    current_title = None
    current_body = []

    def add_section():

        if current_title is not None:

            sections.append({
                "title": _clean_title(current_title),
                "details": _convert_markdown_to_html(
                    "\n".join(current_body).strip()
                )
            })

    for line in lines:

        normalized = line.strip('*- ').strip()

        is_day_section = (
            normalized.lower().startswith("day ")
            and len(normalized) < 80
        )

        if is_day_section:

            add_section()

            current_title = normalized
            current_body = []

        elif (
            line.startswith("###")
            or (
                line.startswith("**")
                and "day" in line.lower()
            )
        ):

            add_section()

            current_title = line
            current_body = []

        elif current_title is None:

            current_title = "Study Plan"

            current_body.append(line)

        else:

            current_body.append(line)

    add_section()

    if not sections and study_plan_text.strip():

        sections = [{
            "title": "Study Plan",
            "details": _convert_markdown_to_html(
                study_plan_text.strip()
            )
        }]

    return sections
