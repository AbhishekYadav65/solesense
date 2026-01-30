# SoleSense — Backend Simulation Engine (Refactored)

## 1. Purpose & Positioning

SoleSense Backend is a **deterministic, explainable simulation engine** that models:

* how pressure distributes across a shoe sole
* how that pressure evolves over time under different activities
* how pressure behavior degrades comfort
* how sustained pressure accumulates into material wear

This system is **intentionally not**:

* a medical diagnostic tool
* a biomechanical or gait model
* a real-world physics simulator
* a machine learning predictor

Instead, SoleSense is designed for:

* **comparative reasoning**
* **trend exploration**
* **explainable cause–effect analysis**
* **interactive visualization**

> Accuracy is deliberately sacrificed for **clarity, determinism, and interpretability**.

All intelligence lives in the backend.  
The frontend is strictly a **presentation and interaction layer**.

---

## 2. High-Level Architecture

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
├── utils/
│   └── validators.py       # Input hygiene & safety
└── README.md               # This document
```

**Separation of concerns is strict and enforced.**

* `core/` contains *all* simulation logic
* `utils/` protects the system from invalid inputs
* `app.py` is a thin JSON boundary
* No module performs another module's job

---

## 3. End-to-End Execution Flow

1. Client sends JSON to `/simulate` or `/compare`
2. Inputs are validated and sanitized (`utils/validators.py`)
3. Inputs are normalized into abstract parameters (`normalization.py`)
4. Initial pressure field is generated (`pressure_field.py`)
5. Pressure evolves over time (`temporal_evolution.py`)
6. Constraints enforce invariants every step (`constraints.py`)
7. Comfort penalties are computed (`comfort_engine.py`)
8. Wear accumulates monotonically (`wear_model.py`)
9. Post-analysis classifies system behavior (`orchestrator.py`)
10. Optional scenario comparison reasons about deltas (`scenario_compare.py`)
11. Results are serialized and returned (`app.py`)

At no point does the frontend need to understand simulation internals.

---

## 4. Core Simulation Modules (`core/`)

### 4.1 `normalization.py`

**Role:**  
Convert raw user inputs into **bounded, dimensionless control parameters**.

**Key principles:**

* Core never sees raw user values
* All outputs are normalized and bounded
* No inference, no prediction, no guessing

**Notable design choice — Activity Decomposition**

Activities are decomposed into **three independent effects**:

| Component            | Meaning                       |
| -------------------- | ----------------------------- |
| `activity_load`      | Scales total applied load     |
| `activity_variation` | Controls temporal fluctuation |
| `activity_wear_rate` | Scales wear accumulation      |

This prevents hidden coupling and preserves explainability.

---

### 4.2 `pressure_field.py`

**Role:**  
Generate the **initial spatial pressure distribution**.

**What it does:**

* Discretizes the sole into a fixed 2D grid
* Applies heel-to-toe distribution
* Applies arch-type bias (flat / normal / high)
* Shapes spread via contact capacity
* Smooths deterministically based on sole stiffness

**What it does not do:**

* No anatomy modeling
* No geometry deformation
* No real pressure units

**Output:**  
A relative pressure field, not a physical one.

---

### 4.3 `constraints.py`

**Role:**  
Enforce **hard invariants** safely and transparently.

**Guaranteed invariants:**

* All values are finite
* All values are bounded
* Force is conserved **when representable**
* Graceful saturation when capacity is exceeded

**Why this matters:**

* Prevents numerical explosions
* Prevents false comfort or wear artifacts
* Makes extreme inputs safe and explainable

Constraints never invent behavior — they only restrict it.

---

### 4.4 `temporal_evolution.py`

**Role:**  
Evolve pressure fields **over time**.

**Key behaviors:**

* Deterministic heel-to-toe modulation
* Activity-dependent temporal variation
* Pressure inertia via relaxation
* No randomness, no oscillatory chaos

This module makes SoleSense a **simulation**, not a static heatmap.

---

### 4.5 `comfort_engine.py`

**Role:**  
Infer comfort from **pressure behavior**, not anatomy.

Comfort is modeled as a **penalty system**, not a prediction.

**Penalties include:**

* Peak pressure
* High-pressure area
* Heel–forefoot imbalance
* Left–right asymmetry
* Temporal volatility
* Pressure persistence

**Output:**

```json
{
  "comfort_index": 0–100,
  "penalties": {
    "pressure_peak": ...,
    "high_pressure_area": ...,
    "zone_bias": ...,
    "asymmetry": ...,
    "temporal_variation": ...,
    "pressure_persistence": ...
  }
}
```

Every comfort change is directly explainable.

---

### 4.6 `wear_model.py`

**Role:**  
Accumulate **material wear** deterministically.

**Wear depends on:**

* Pressure magnitude
* Pressure persistence
* Spatial extent
* Activity wear rate
* Material durability

**Critical properties:**

* Wear is monotonic (never decreases)
* Wear does not feed back into pressure or comfort
* No fatigue physics are assumed

This preserves **causal clarity**.

---

### 4.7 `orchestrator.py`

**Role:**  
The **governor** of the entire system.

**Responsibilities:**

* Run full simulation loop
* Coordinate pressure → comfort → wear
* Collect histories
* Perform post-analysis:
  * stability classification
  * dominant factor detection
  * comfort–wear alignment regimes
* Expose two entry points:
  * `run_simulation`
  * `run_scenario_comparison`

No UI logic lives here.  
No validation lives here.  
Only coordination and reasoning.

---

### 4.8 `scenario_compare.py`

**Role:**  
Perform **what-if reasoning** between two simulations.

**Capabilities:**

* Outcome deltas
* Mechanism attribution
* Tradeoff detection
* Decision verdicts:
  * strictly_better
  * tradeoff
  * equivalent
  * worse

No new simulation is created here — it reasons only over outputs.

---

### 4.9 `constants.py`

**Role:**  
Centralize all tunable parameters.

Includes:

* Grid dimensions
* Pressure bounds
* Activity profiles
* Comfort weights
* Wear scaling
* Default simulation length

Changing constants never changes logic — only behavior scale.

---

## 5. Utils (`utils/validators.py`)

**Role:**  
Protect the core from invalid or ambiguous inputs.

**Validations include:**

* Required fields
* Numeric bounds
* Enum enforcement (arch type, activity)
* Explicit error messages

Core logic never validates inputs.  
API never guesses user intent.

---

## 6. API Layer (`app.py`)

`app.py` is a **pure JSON boundary**.

It contains:

* No simulation logic
* No inference
* No hidden assumptions

### Route: `POST /simulate`

Runs a single simulation.

**Input:**

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

**Output sections:**

* `overview` → headline interpretation
* `key_drivers` → causal explanation
* `evidence` → numeric justification
* `raw` → pressure & wear arrays for visualization

**Frontend should read:**

* `overview` → Display headline summary
* `key_drivers` → Show explanation of what's driving the results
* `evidence` → Present supporting numbers
* `raw` → Render heatmaps and history graphs

---

### Route: `POST /compare`

Runs a deterministic what-if comparison.

**Input:**

```json
{
  "baseline": { ... },
  "variant": { ... },
  "steps": 50
}
```

**Output:**

* Baseline summary
* Variant summary
* Mechanism-level comparison
* Tradeoff classification
* Explicit assumptions

Frontend never needs to re-analyze anything.

---

## 7. Determinism & Guarantees

* Same input → same output
* No randomness
* No ML
* No hidden state
* No time dependence outside simulation steps

This makes SoleSense:

* **testable** — Results are reproducible
* **debuggable** — Behavior is traceable
* **judge-defensible** — Logic is explainable

---

## 8. Explicit Assumptions & Limits

Returned in every response:

* What is modeled
* What is not modeled
* Interpretation limits
* Simplifications

**No hidden claims. No overreach.**

The backend explicitly declares its boundaries and does not make medical, diagnostic, or prescriptive claims.

---

## 9. How to Build a Frontend Using Only This Backend

A frontend developer needs only to:

1. Call `/simulate` or `/compare`
2. Read `overview`, `key_drivers`, `evidence`
3. Render `raw.final_pressure` as a heatmap
4. Animate `raw.wear_history[t]` over time

**Backend internals never need to be inspected.**

The API is designed to be completely self-sufficient — no knowledge of Python, NumPy, or simulation logic is required.

---

## 10. Design Philosophy

### Why Deterministic?

Determinism enables:

* Reproducible testing
* Comparative analysis
* Explainable outputs
* Trust in results

### Why Not ML?

Machine learning would:

* Introduce opacity
* Require training data we don't have
* Make outputs non-explainable
* Complicate validation

### Why Penalty-Based Comfort?

Penalty systems are:

* Fully explainable
* Tunable without retraining
* Transparent to judges
* Independent of user data

### Why Separate Activity Effects?

Decomposing activity into load, variation, and wear rate:

* Prevents hidden coupling
* Makes each effect independently understandable
* Allows precise control
* Enables clear explanations

---

## 11. Backend Status

✅ **Complete** — All modules implemented  
✅ **Refactored** — Clean architecture enforced  
✅ **Activity-aware** — Multiple activity modes supported  
✅ **Deterministic** — Reproducible results guaranteed  
✅ **Explainable** — Every output is justified  
✅ **Judge-ready** — Defensible and transparent  
✅ **Frontend-agnostic** — Pure API design

---

## 12. Example Usage Workflow

### Single Simulation

```bash
curl -X POST http://localhost:5000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "body_weight": 75,
    "foot_size": 43,
    "arch_type": "high",
    "activity_mode": "running",
    "sole_stiffness": 0.6,
    "material_durability": 0.8,
    "steps": 100
  }'
```

**Frontend actions:**
1. Parse `overview.headline` → show main finding
2. Parse `key_drivers` → explain why
3. Visualize `raw.final_pressure` → show pressure heatmap
4. Plot `raw.comfort_history` → show comfort over time
5. Plot `raw.wear_history` → show wear progression

### Scenario Comparison

```bash
curl -X POST http://localhost:5000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "baseline": {
      "body_weight": 70,
      "foot_size": 42,
      "arch_type": "normal",
      "activity_mode": "walking",
      "sole_stiffness": 0.5,
      "material_durability": 0.5,
      "steps": 50
    },
    "variant": {
      "body_weight": 70,
      "foot_size": 42,
      "arch_type": "normal",
      "activity_mode": "running",
      "sole_stiffness": 0.5,
      "material_durability": 0.5,
      "steps": 50
    }
  }'
```

**Frontend actions:**
1. Show baseline vs variant side-by-side
2. Display delta analysis
3. Highlight tradeoffs
4. Show decision verdict

---

## 13. Validation & Error Handling

The backend validates all inputs and returns clear error messages:

**Invalid arch type:**
```json
{
  "error": "Invalid arch_type. Must be one of: flat, normal, high"
}
```

**Out of range value:**
```json
{
  "error": "body_weight must be between 30 and 200"
}
```

**Missing required field:**
```json
{
  "error": "Missing required field: activity_mode"
}
```

All validation happens before simulation begins, ensuring fast failure.

---

## 14. Future Extensions (Potential)

While the current system is complete, potential extensions could include:

* Additional activity modes (hiking, jumping, etc.)
* More arch type variations
* Temperature effects on material properties
* Multi-material sole compositions
* Custom pressure distribution patterns

All extensions would maintain the core principles:
* Deterministic
* Explainable
* No ML
* No medical claims

---

## 15. Testing & Validation

The backend can be validated through:

1. **Determinism tests** — Same input always produces same output
2. **Bounds tests** — All outputs stay within valid ranges
3. **Conservation tests** — Force is preserved across transformations
4. **Monotonicity tests** — Wear never decreases
5. **Comparison tests** — Delta analysis is self-consistent

No statistical testing is required because the system is deterministic.

---

## 16. Summary

SoleSense Backend is a **complete, production-ready simulation engine** that:

* Models pressure, comfort, and wear deterministically
* Provides explainable, judge-defensible outputs
* Requires zero backend knowledge to use
* Makes no medical or prescriptive claims
* Supports comparative analysis and what-if scenarios

**The frontend's only job is to visualize and interact with these results.**

---

*Last updated: January 2026*  
*Version: 2.0 (Refactored)*