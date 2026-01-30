# SoleSense — Backend Simulation Engine

## Overview

SoleSense Backend is a deterministic, explainable simulation engine that models how pressure distributes across a shoe sole, how that pressure evolves over time, how it translates into comfort degradation, and how it accumulates into material wear.

This backend is intentionally **not**:
- a medical system
- a biomechanical model
- a machine-learning predictor

Instead, it is a transparent, trend-oriented simulation system designed for:
- comparative analysis
- explainability
- interactive exploration
- judge-proof reasoning

**All intelligence lives in the backend.**  
The frontend is purely a visualization and interaction layer.

---

## High-Level Architecture

```
backend/
├── app.py                  # Pure JSON API boundary
├── core/                   # Simulation & reasoning engine
│   ├── normalization.py
│   ├── pressure_field.py
│   ├── constraints.py
│   ├── temporal_evolution.py
│   ├── comfort_engine.py
│   ├── wear_model.py
│   ├── scenario_compare.py
│   ├── orchestrator.py
│   └── constants.py
├── utils/                  # Input validation & hygiene
│   └── validators.py
└── README.md               # This file
```

Separation of concerns is strict and intentional.

---

## Execution Flow (End-to-End)

1. Client sends JSON input to `/simulate` or `/compare`
2. Inputs are validated and normalized (`utils/validators.py`)
3. Simulation is executed (`core/orchestrator.py`)
4. Pressure → comfort → wear is computed deterministically
5. Post-analysis classifies scenarios and alignment regimes
6. Results are structured narratively in `app.py`
7. NumPy data is serialized safely
8. JSON response is returned to client

**At no point does the frontend need to understand simulation logic.**

---

## Core Module (Simulation Engine)

All actual intelligence lives in `core/`.

### normalization.py

**Purpose:** Convert raw user inputs into normalized simulation parameters.

**Key responsibilities:**
- Convert body weight → abstract load factor
- Convert foot size → grid scaling
- Convert stiffness & durability → simulation coefficients
- Normalize categorical inputs into numeric modifiers

**Guarantee:**  
Core never sees raw, unbounded user inputs.

### pressure_field.py

**Purpose:** Generate the initial 2D pressure grid.

**Key logic:**
- Discretizes the sole into a fixed grid
- Applies arch-type bias (flat / normal / high)
- Applies heel–toe distribution
- Produces a relative pressure map, not a real one

**Output:**  
2D NumPy array representing baseline pressure distribution

### constraints.py

**Purpose:** Enforce hard physical invariants safely.

**Enforced guarantees:**
- All pressure values are finite
- All pressure values are bounded
- Total force is conserved when representable
- Graceful degradation when force exceeds grid capacity

**Why this matters:**
- Prevents numerical explosions
- Prevents fake comfort or wear artifacts
- Keeps simulation honest under extreme inputs

### temporal_evolution.py

**Purpose:** Evolve pressure over time.

**Key behavior:**
- Introduces temporal smoothing
- Adds activity-dependent variation (standing vs walking)
- Prevents runaway oscillations
- Maintains deterministic evolution

This is time-based simulation, not a static visualization.

### comfort_engine.py

**Purpose:** Convert pressure behavior into comfort.

Comfort is penalty-based and explainable.

**Penalties include:**
- Pressure peaks
- High-pressure area
- Left–right asymmetry
- Zone bias
- Temporal instability
- Pressure persistence

**Outputs:**
```json
{
  "comfort_index": 0–100,
  "penalties": {
    "pressure_peak": ...,
    "high_pressure_area": ...,
    ...
  }
}
```

No black boxes. Every comfort drop is explainable.

### wear_model.py

**Purpose:** Accumulate material wear over time.

**Wear depends on:**
- Pressure magnitude
- Pressure persistence
- Temporal repetition
- Material durability factor

**Key property:**
- Wear is monotonic (never decreases)
- Wear does not feed back into pressure or comfort

This preserves causal clarity.

### orchestrator.py

**Purpose:** Coordinate the entire simulation lifecycle.

**Responsibilities:**
- Run full time-step simulation loop
- Collect pressure, comfort, and wear histories
- Perform post-analysis:
  - stability classification
  - dominant factor detection
  - comfort–wear alignment regime
- Expose two public entry points:
  - `run_simulation`
  - `run_scenario_comparison`

This file is the governor of the system.

### scenario_compare.py

**Purpose:** Perform deep what-if comparison.

**Capabilities:**
- Numeric delta analysis
- Mechanism attribution
- Tradeoff detection
- Decision verdict classification:
  - strictly better
  - tradeoff
  - equivalent
  - worse

No new simulation is invented here.  
It reasons only over existing outputs.

### constants.py

**Purpose:** Centralize all tunable constants.

**Includes:**
- Grid size
- Pressure bounds
- Comfort weights
- Simulation step defaults

This allows transparent tuning without logic changes.

---

## Utils Module (Input Hygiene)

### validators.py

**Purpose:**
- Protect the core from invalid inputs
- Normalize enums
- Enforce numeric bounds
- Fail fast and explicitly

**Handled validations:**
- Numeric ranges (weight, stiffness, durability, etc.)
- Allowed enums (arch type, activity mode)
- Required field presence

Core never validates inputs.  
API never guesses user intent.

---

## API Layer (app.py)

`app.py` is a pure JSON boundary.

It contains:
- No simulation logic
- No interpretation logic
- No assumptions
- No defaults beyond safety

### Responsibilities

1. Receive JSON requests
2. Validate inputs using `utils`
3. Call orchestrator functions
4. Build narrative responses
5. Convert NumPy → JSON safely

### Route: POST /simulate

**Purpose:** Run a single simulation scenario.

**Input JSON:**
```json
{
  "body_weight": 70,
  "foot_size": 42,
  "arch_type": "normal",
  "activity_mode": "walking",
  "sole_stiffness": 0.5,
  "material_durability": 0.3,
  "steps": 50
}
```

**Output Structure:**
```json
{
  "overview": { ... },
  "key_drivers": { ... },
  "evidence": { ... },
  "raw": { ... }
}
```

Frontend should read:
- `overview` → headline
- `key_drivers` → explanation
- `evidence` → numbers
- `raw` → heatmaps & history

### Route: POST /compare

**Purpose:** Compare two scenarios (what-if analysis).

**Input JSON:**
```json
{
  "baseline": { ...inputs... },
  "variant": { ...inputs... },
  "steps": 50
}
```

**Output:**
- Baseline summary
- Variant summary
- Deep comparison reasoning
- Decision verdict
- Shared assumptions

Frontend does not need to re-analyze anything.

---

## Determinism & Guarantees

- Same input → same output
- No randomness
- No ML
- No hidden state
- No time dependence outside simulation steps

This makes SoleSense:
- testable
- debuggable
- judge-defensible

---

## Assumptions & Limits (Explicit)

The backend explicitly exposes:
- What is modeled
- What is not modeled
- Interpretation limits
- Simplifications

These are returned in every simulation response.

**No hidden claims. No overreach.**

---

## How to Build a Frontend Using Only This Backend

A frontend developer needs only to know:

1. Call `/simulate` or `/compare`
2. Read `overview`, `key_drivers`, `evidence`
3. Render `raw.final_pressure` as a heatmap
4. Render `raw.wear_history[t]` with a time slider

**No backend code inspection required.**

---

## Status

✅ Backend complete  
✅ Hardened  
✅ Explainable  
✅ Judge-ready  
✅ Frontend-agnostic