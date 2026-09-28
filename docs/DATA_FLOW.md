# End-to-End Data Flow Specification

## 1. Complete System Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Frontend / Marketing Team
    participant API as FastAPI Layer
    participant Orch as Agent Orchestrator
    participant Analytics as SocialMediaAnalyticsEngine
    participant EvBuilder as Evidence & Gap Builder
    participant Hindsight as Hindsight Memory Bank
    participant LLM as Provider-Agnostic LLM
    participant DB as SQLite Application DB
    participant Learning as Learning Service

    Note over User,DB: PHASE 1: GENERATE STRATEGY (Interaction 1)
    User->>API: POST /api/v1/strategy/generate
    API->>Orch: execute_strategy_pipeline(...)
    Orch->>Analytics: run_analysis(account, date_window)
    Analytics-->>Orch: AnalyticsResult (JSON Contract)
    Orch->>DB: Persist content items & performance records
    Orch->>EvBuilder: build_context(brand, analytics)
    EvBuilder->>Hindsight: recall(bank_id, bounded_queries)
    Hindsight-->>EvBuilder: Recalled Memories (e.g. past lessons)
    EvBuilder-->>Orch: GroundedStrategyContext
    Orch->>LLM: generate_strategy(system_prompt, grounded_context)
    LLM-->>Orch: LLMStrategyOutput (Structured JSON)
    Orch->>Orch: Validate output against grounded context
    Orch->>DB: Persist StrategyRecord
    Orch-->>API: ContentStrategy
    API-->>User: StrategyResponse (Strategy A)

    Note over User,Learning: PHASE 2: EXECUTE STRATEGY & OBSERVE PERFORMANCE
    User->>User: Marketing team executes Strategy A in the market
    User->>Analytics: New posts published & metrics collected

    Note over User,Hindsight: PHASE 3: OUTCOME ANALYSIS & MEMORY UPDATE
    User->>API: POST /api/v1/strategy/outcome
    API->>Learning: process_strategy_outcome(strategy_id, new_analytics)
    Learning->>DB: Get Strategy A
    DB-->>Learning: StrategyRecord
    Learning->>Learning: OutcomeAnalyzer: Compare actuals vs baseline & plan
    Learning->>Learning: LessonExtractor: Extract reusable lesson
    Learning->>Hindsight: retain(bank_id, ReusableExperience)
    Hindsight-->>Learning: memory_id
    Learning->>DB: Persist StrategyOutcomeRecord with memory_id
    Learning-->>API: StrategyOutcomeAnalysis
    API-->>User: OutcomeResponse

    Note over User,LLM: PHASE 4: FUTURE STRATEGY (Interaction 2)
    User->>API: POST /api/v1/strategy/generate (New request)
    API->>Orch: execute_strategy_pipeline(...)
    Orch->>Analytics: run_analysis(account, new_date_window)
    Analytics-->>Orch: New AnalyticsResult
    Orch->>EvBuilder: build_context(brand, new_analytics)
    EvBuilder->>Hindsight: recall(bank_id, query)
    Note right of Hindsight: Hindsight recalls lesson learned in Phase 3!
    Hindsight-->>EvBuilder: Recalled Memory [mem_xyz: "Short practical debugging tutorials..."]
    EvBuilder-->>Orch: GroundedStrategyContext (With cited memory!)
    Orch->>LLM: generate_strategy(system_prompt, grounded_context)
    LLM-->>Orch: LLMStrategyOutput (Strategy B)
    Note over LLM,Orch: Strategy B adapts recommendations based on recalled memory
    Orch->>DB: Persist Strategy B
    Orch-->>API: ContentStrategy (Strategy B)
    API-->>User: StrategyResponse (Strategy B incorporating learned lessons!)
```

---

## 2. Segregated Data Envelopes

To prevent model hallucination and mathematical errors, data is strictly segregated into three distinct planes:

| Data Plane | Source | Authority Level | Permitted Operations |
| :--- | :--- | :--- | :--- |
| **Deterministic Facts** | `AnalyticsResult` | Absolute truth (Ground Truth) | Quoting, format ranking, and baseline comparisons. LLM is strictly prohibited from modifying or calculating. |
| **Persistent Memory** | `Hindsight` | Empirical experience | Synthesizing past lessons into editorial guidelines and citing as operational rules. |
| **Hypotheses & Angles** | `LLM Provider` | Generative reasoning | Formulating creative editorial angles, narrative hooks, and experimental hypotheses. |

---

## 3. Database vs Hindsight Record Lifecycle

| Entity | Application DB Store | Hindsight Memory Store |
| :--- | :--- | :--- |
| `BrandProfile` | `brands` table | Bank configuration |
| `NormalizedContent` | `content_items` table | None (avoid raw dumps) |
| Performance Metrics | `content_performances` table | None (avoid raw metrics) |
| Generated Strategy | `strategies` table | Strategy hypothesis reference |
| Post-Mortem Comparison | `strategy_outcomes` table | `strategy_outcome` tag |
| Strategic Lesson | Lesson text column | `ReusableExperience` item |
