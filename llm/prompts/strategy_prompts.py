"""
Prompt definitions for Grounded Content Strategy Generation.
Strictly prohibits mathematical calculations; enforces grounding in analytics and Hindsight memory.
"""

from __future__ import annotations

import json
from agent.context.grounded_context import GroundedStrategyContext


SYSTEM_STRATEGY_PROMPT = """You are an expert Senior Content Strategist AI Agent.
Your responsibility is to analyze historical performance and persistent memory to construct an evidence-grounded content strategy.

ABSOLUTE OPERATIONAL RULES:
1. NEVER calculate engagement rates, medians, percentages, or mathematical metrics. All metrics have already been calculated deterministically by the analytics engine and are provided in your context.
2. Rely EXCLUSIVELY on the provided CURRENT ANALYTICS FACTS and RECALLED HINDSIGHT EXPERIENCES.
3. If recalled Hindsight memories contain previous learnings, you MUST explicitly integrate them and cite them in your strategy recommendations.
4. If a content gap is identified, address it with high-priority themes.
5. Provide actionable, specific editorial angles rather than generic platitudes.
6. Return your output strictly as a valid JSON object matching the requested schema.
"""


def build_user_strategy_prompt(context: GroundedStrategyContext) -> str:
    context_data = context.to_prompt_context_dict()
    context_json = json.dumps(context_data, indent=2)

    return f"""Analyze the following grounded context and construct a comprehensive, empirical content strategy.

GROUNDED CONTEXT:
{context_json}

OUTPUT FORMAT REQUIREMENTS:
Return a JSON object with this exact structure:
{{
  "objective": "...",
  "rationale": "Detailed strategic rationale explaining how current analytics and recalled memories guided this strategy...",
  "content_themes": [
    {{
      "topic": "...",
      "priority": "high",
      "rationale": "...",
      "angle": "...",
      "is_gap_fill": false
    }}
  ],
  "recommended_formats": [
    {{
      "format_name": "short",
      "platform": "{context.target_platform}",
      "recommended_cadence": "2x per week",
      "rationale": "..."
    }}
  ],
  "posting_recommendations": {{
    "frequency_per_week": 3.0,
    "optimal_cadence_notes": "...",
    "platform_allocation": {{"{context.target_platform}": 1.0}}
  }},
  "recalled_experience_citations": [
    {{
      "memory_id": "...",
      "lesson": "...",
      "influence_on_strategy": "..."
    }}
  ],
  "suggested_experiments": [
    "..."
  ],
  "limitations": [
    "..."
  ]
}}
"""
