# AI-Assisted Box Selection System

An intelligent shipping box recommendation system built with Django and Django REST Framework, featuring a **Gemini-powered AI explanation layer**.

Given an ecommerce order containing multiple products, the system determines the **cheapest shipping box** that can physically accommodate all items while respecting dimensional and weight constraints. The recommendation engine uses a custom **3D bin-packing algorithm** to simulate product placement and returns exact placement coordinates and orientations for every packed item.

---

## Problem Statement

Warehouse operators often choose shipping boxes manually, leading to:

* Higher packaging costs
* Inefficient space utilization
* Increased shipping expenses
* Human error in box selection

This system automates the process by selecting the most cost-effective box capable of packing all ordered products.

---

## Assumptions

* All products and boxes are **rectangular cuboids** with fixed length, width, and height.
* Products may be rotated into any of the six valid axis-aligned orientations during packing.
* Products cannot be **stacked** or intersect each other inside the box.
* Dimensions are in **centimeters**, weight in **grams**.
* Box internal dimensions represent the maximum usable space (ignoring wall thickness).
* The cheapest valid box is always preferred over a more expensive one, even if the latter provides better volume utilization.
* An order with zero items returns no recommendation.

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     box_selector (Django 5.2)                │
│                                                              │
│  ┌──────────┐  ┌────────┐  ┌────────┐  ┌──────────────┐   │
│  │ products │  │  boxes  │  │ orders │  │recommendation│   │
│  │  (app)   │  │ (app)   │  │ (app)  │  │    (app)     │   │
│  └────┬─────┘  └───┬────┘  └────┬───┘  └──────┬───────┘   │
│       │             │            │              │           │
│       ▼             ▼            ▼              ▼           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ Product  │ │   Box    │ │  Order   │ │  Services:   │   │
│  │  Model   │ │  Model   │ │  +Item   │ │  box_selector│   │
│  └──────────┘ └──────────┘ └──────────┘ │  packing_eng │   │
│                                          │  ai_explainer│   │
│  ┌────────────────────────────────────┐  └──────────────┘   │
│  │        API Layer (DRF ViewSets)    │                      │
│  │  /api/products/  /api/boxes/       │                      │
│  │  /api/orders/    /api/recommend-box/│                     │
│  └────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
box_selector/
│
├── products/                          # Product model & admin
├── boxes/                             # Box model & admin
├── orders/                            # Order & OrderItem models
├── api/                               # DRF ViewSets & serializers
│
├── recommendation/                    # Business logic
│   ├── services/
│   │   ├── box_selector.py            # Recommendation orchestrator
│   │   ├── packing_engine.py          # 3D bin-packing algorithm
│   │   └── ai_explainer.py            # Gemini AI explanation
│   ├── management/commands/
│   │   └── test_gemini.py             # Debug command for Gemini API
│   └── tests/
│       ├── test_packing_engine.py
│       ├── test_box_selector.py
│       └── test_ai_explainer.py
│
├── api/tests.py                       # API endpoint tests
└── box_selector/                      # Django project settings
```

---

## Key Features

### Product, Box & Order Management
* Full CRUD via REST API for products, boxes, and orders
* Support configurable quantities per product

### Intelligent Box Recommendation
* Evaluates all available boxes through a multi-stage filter pipeline
* Performs physical fit validation via 3D packing simulation
* Considers weight restrictions
* Returns the lowest-cost valid box

### 3D Packing Engine
* Supports all six possible product orientations (via dimension permutation)
* Calculates exact item placement coordinates
* Uses greedy guillotine-cut space partitioning
* Rejects boxes that cannot physically fit all items

### AI-Powered Explanation (Gemini)
* Generates a natural-language explanation for each recommendation
* Uses **Google Gemini 2.0 Flash Lite** via the `google-genai` SDK
* Gracefully falls back to `null` if the API key is missing or quota is exceeded
* JSON-structured output with `recommended_box` and `reason` fields

---

## Technology Stack

| Component        | Technology                    |
| ---------------- | ----------------------------- |
| Language         | Python 3.12+                  |
| Web Framework    | Django 5.2                    |
| API Framework    | Django REST Framework 3.16+   |
| Database         | SQLite                        |
| AI Integration   | Google Gemini API  |
| AI SDK           | google-genai                  |
| Testing          | Django Test Runner            |
| CI/CD            | GitHub Actions                |
| Architecture     | Service-Oriented              |

---

## Recommendation Workflow

The recommendation process follows a five-stage pipeline:

### Step 1 — Weight Validation
Remove boxes whose maximum weight capacity is lower than the total order weight.

### Step 2 — Volume Validation
Remove boxes whose internal volume is smaller than the total product volume.

### Step 3 — Dimension Screening
Perform a fast dimensional feasibility check (each sorted product dimension vs. corresponding sorted box dimension).

### Step 4 — 3D Packing Simulation
Attempt to place all products inside the box using the greedy guillotine-cut packing engine.

### Step 5 — Cost Optimization
Among all valid boxes, return the cheapest one (boxes are ordered by cost ascending).

---

## Packing Algorithm

The system uses a greedy 3D bin-packing strategy inspired by guillotine partitioning.

### Process

1. Expand order items by quantity into a flat list
2. Sort products by volume descending (largest-first heuristic)
3. Generate all unique orientations via dimension permutations (deduplicated for symmetric products)
4. For each product, examine available voids sorted by volume descending
5. Place the product in the first void where any orientation fits
6. Split the remaining empty space into three new rectangular voids (right, front, top)
7. Continue until all products are packed or an item cannot fit

### Space Representation

Empty space inside a box is represented as rectangular void regions:

```python
Void(x, y, z, length, width, height)
```

Each placement updates the available void list by removing the consumed void and appending the three new sub-voids.

### Output

The engine returns placement data for every packed item, including position coordinates and orientation dimensions.

---

## Algorithm Complexity

| Operation                  | Complexity       | Notes                              |
| -------------------------- | ---------------- | ---------------------------------- |
| Orientation generation     | O(6) per product | Constant — max 6 permutations      |
| Dimensional screening      | O(p)             | p = unique products                |
| Packing simulation         | O(n · v · 6)     | n = total items, v = active voids  |
| Worst-case void count      | O(3n)            | Each placement creates ≤3 new voids |
| Overall selection (boxes)  | O(b · n · v · 6) | b = number of candidate boxes      |

For typical ecommerce orders (fewer than 20 items, fewer than 10 box types), execution is effectively instant.

---

## API Endpoints

### Products

| Method | Endpoint            |
| ------ | ------------------- |
| GET    | /api/products/      |
| POST   | /api/products/      |
| GET    | /api/products/{id}/ |
| PATCH  | /api/products/{id}/ |
| DELETE | /api/products/{id}/ |

### Boxes

| Method | Endpoint         |
| ------ | ---------------- |
| GET    | /api/boxes/      |
| POST   | /api/boxes/      |
| GET    | /api/boxes/{id}/ |
| PATCH  | /api/boxes/{id}/ |
| DELETE | /api/boxes/{id}/ |

### Orders

| Method | Endpoint          |
| ------ | ----------------- |
| GET    | /api/orders/      |
| POST   | /api/orders/      |
| GET    | /api/orders/{id}/ |
| PUT    | /api/orders/{id}/ |
| PATCH  | /api/orders/{id}/ |
| DELETE | /api/orders/{id}/ |

### Box Recommendation

```http
POST /api/recommend-box/
```

#### Request

```json
{
  "order_id": 1
}
```

#### Success Response

```json
{
  "order_id": 1,
  "recommendation": {
    "box_id": 2,
    "box_name": "Medium Box",
    "cost": "4.00",
    "box_dimensions": {
      "length": 30.0,
      "width": 20.0,
      "height": 15.0
    },
    "box_max_weight": 3000.0,
    "volume_utilization_pct": 41.7,
    "placements": [
      {
        "product_id": 1,
        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
        "orientation": {"length": 10.0, "width": 8.0, "height": 5.0}
      }
    ],
    "explanation": {
      "recommended_box": "Medium Box",
      "reason": "Medium Box is the cheapest option that fits all 3 items within its 3000g weight capacity and 9000cm³ volume."
    }
  }
}
```

The `explanation` field will be `null` when no Gemini API key is configured or the API call fails.

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd box_selector
```

### Create Virtual Environment

```bash
python -m venv venv
```

| Platform      | Activate Command       |
| ------------- | ---------------------- |
| Linux / macOS | `source venv/bin/activate` |
| Windows       | `venv\Scripts\activate`   |

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Migrations

```bash
python manage.py migrate
```

### (Optional) Configure Gemini API Key

Obtain a Gemini API key from Google AI Studio and add it to your `.env` file:

```env
GEMINI_API_KEY=your-api-key
```

### Start Server

```bash
python manage.py runserver
```

* Server: http://127.0.0.1:8080
* Browsable API: http://127.0.0.1:8080/api/

---

## Running Tests

```bash
python manage.py test          # complete test suite
python manage.py test api      # API endpoint tests
python manage.py test recommendation  # service layer tests
python manage.py test_gemini   # test Gemini connectivity
```

Coverage:

```bash
pip install coverage
coverage run --source=products,boxes,orders,api,recommendation manage.py test
coverage report
```

---

## Design Decisions

### Why Greedy Packing?

The assignment requires a practical recommendation engine rather than mathematically optimal packing.

Advantages:
* Fast execution
* Simple implementation
* Deterministic behavior
* Scales well for typical ecommerce orders

### Why Cost-Based Selection?

Warehouses generally aim to minimize packaging cost while ensuring successful shipment.

Priorities:
1. Physical feasibility
2. Weight compliance
3. Lowest box cost

### Why Gemini for AI Explanations?

The explanation layer is intentionally **optional and non-blocking** — the box recommendation itself does not depend on the AI call. Gemini was chosen because it provides a simple API, a free development tier, and generates clear human-readable explanations without affecting the deterministic recommendation engine.

---

## Author

Developed as part of a Django backend engineering assignment focused on:

* System design
* API development
* Algorithm implementation
* Automated testing
* Clean architecture principles

## Submission Contents

This repository includes the following supporting documents required for the assignment:

- `README.md` – Project overview and setup instructions
- `AI_USAGE.md` – AI tools used, representative prompts, accepted/rejected outputs, mistakes identified, and verification steps
- `TEST_OUTPUT.md` – Test execution output
- `CHAT_TRANSCRIPT.pdf` – Export of the development conversation used during the assignment

### Chat Transcript (Online)

For convenience, the development conversation can also be viewed using the ChatGPT shared conversation link:
https://chatgpt.com/share/6a3c3007-0cf8-83e8-ba27-52ba10e865ef