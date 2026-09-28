# Content Strategy Agent - Backend Architecture & Technical Guide

## 1. Architectural Philosophy & Value Proposition

The **Content Strategy Agent** is designed to solve a core inefficiency in growth and marketing: marketing teams repeatedly reinvent the wheel. Rather than being a generic content text generator, this agent is a **strategic memory and optimization engine** built around persistent learning:

```text
PAST CONTENT -> ANALYTICS -> HINDSIGHT MEMORY -> LLM REASONING -> STRATEGY -> ACTUAL RESULT -> LEARNING -> HINDSIGHT UPDATE -> IMPROVED STRATEGY
```

### Separation of Concerns: Application Database vs. Hindsight
* **Application Database (SQLite)**: Stores operational, relational records:
  - Registered brand identities and voice profiles (`brands`)
  - Normalized historical content references (`content_items`)
  - Point-in-time performance measurements (`content_performances`)
  - Generated strategy records and audit logs (`strategies`)
  - Post-mortem comparisons and outcome reviews (`strategy_outcomes`)
* **Hindsight Memory Engine**: Stores persistent, reusable strategic intelligence:
  - Reusable strategic rules (e.g., "Short-form practical debugging tutorials yield +116% median ER relative to baseline")
  - Brand voice patterns and audience tone preferences
  - Empirical experimental outcomes
  - Content gap opportunities

---

## 2. Directory Structure

```text
├── api/
│   ├── app.py                     # FastAPI application factory and CORS middleware
│   ├── dependencies/              # Dependency injection providers for repos & services
│   ├── errors/                    # Standardized error definitions and HTTP handlers
│   ├── routes/
│   │   ├── health.py              # Health check endpoint
│   │   ├── strategy.py            # Strategy generation and history retrieval
│   │   ├── outcome.py             # Strategy execution outcome and learning loop
│   │   └── memory.py              # Hindsight memory inspection
│   └── schemas/                   # Pydantic request and response models
│
├── agent/
│   ├── context/
│   │   └── grounded_context.py    # GroundedStrategyContext (strictly segregates facts from memories)
│   ├── evidence/
│   │   └── builder.py             # GroundedContextBuilder
│   ├── recall/
│   │   └── recall_selector.py     # Targeted, bounded recall queries
│   ├── strategy/
│   │   ├── generator.py           # Strategy synthesis
│   │   └── validator.py           # Grounding and schema validator
│   └── orchestrator/
│       └── agent_orchestrator.py  # Master end-to-end pipeline orchestrator
│
├── database/
│   ├── connection.py              # SQLite thread-safe connection manager with WAL mode
│   ├── schema.sql                 # DDL definitions
│   ├── models.py                  # Typed dataclasses for database entities
│   └── repositories/              # Repository data access objects (Brand, Content, Strategy, Outcome)
│
├── hindsight/
│   ├── client/
│   │   └── hindsight_client_wrapper.py  # Dual-mode client (Live server with resilient offline bank fallback)
│   ├── memory/
│   │   └── experience_manager.py        # Deduplicated experience retention
│   ├── recall/
│   │   └── experience_retriever.py      # Bounded, tag-filtered memory recall
│   └── schemas/
│       └── memory_models.py             # ReusableExperience, MemoryRecallQuery, MemoryRecallResult
│
├── llm/
│   ├── interface/
│   │   └── base.py                # BaseLLMProvider abstract interface
│   ├── providers/
│   │   ├── factory.py             # Provider factory (Mock, Ollama, OpenAI)
│   │   ├── mock_provider.py       # Deterministic, grounded mock provider for offline demos
│   │   ├── ollama_provider.py     # Local Ollama adapter (Qwen, Llama3)
│   │   └── openai_provider.py     # Generic OpenAI/Gemini adapter
│   ├── prompts/
│   │   └── strategy_prompts.py    # Grounded prompts strictly prohibiting metric calculations
│   └── schemas/
│       └── llm_output.py          # Structured strategy Pydantic schema
│
├── services/
│   └── analytics_service/
│       ├── service.py             # Official boundary adapter consuming SocialMediaAnalyticsEngine
│       └── evidence_extractor.py  # Deterministic fact, format ranking, and content gap extractor
│
├── learning/
│   ├── outcome_analysis/
│   │   └── analyzer.py            # OutcomeAnalyzer (actual performance vs baseline & plan)
│   ├── lesson_extraction/
│   │   └── extractor.py           # LessonExtractor (synthesizes non-causal reusable experiences)
│   ├── memory_update/
│   │   └── updater.py             # MemoryUpdater (stores experience in Hindsight & logs DB outcome)
│   └── learning_service.py        # Master learning loop coordinator
│
├── social_analytics/              # Pre-existing analytics engine (DO NOT MODIFY)
├── tests/                         # Full automated test suite across all 10 layers
├── docs/                          # Architecture, API, Hindsight, and Data Flow documentation
└── .env.example                   # Environment configuration template
```

---

## 3. Social Analytics Engine Boundary

The backend integrates with `social_analytics` exclusively via `AnalyticsService`:
```text
SocialMediaAnalyticsEngine (in social_analytics)
       ↓
AnalyticsResult (Validated Pydantic Contract)
       ↓
AnalyticsService (in services/analytics_service/)
       ↓
AnalyticsEvidenceExtractor (Extracts rankings, observations, and content gaps)
       ↓
GroundedStrategyContext (Fed to Agent Orchestrator & LLM)
```

No analytics formulas or metrics (medians, rates, percentage points) are duplicated or calculated by the LLM.

---

## 4. Local Run & Testing Commands

### Running the API Server
```bash
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Running the Test Suite
```bash
# Run all tests (Analytics + Agent + Database + Hindsight + Learning + E2E)
python -m pytest tests/ social_analytics/tests/ -v
```
