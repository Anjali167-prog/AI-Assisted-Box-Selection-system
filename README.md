# AI-Assisted Box Selection System

An intelligent shipping box recommendation system built with Django and Django REST Framework.

Given an ecommerce order containing multiple products, the system determines the **cheapest shipping box** that can physically accommodate all items while respecting dimensional and weight constraints.

The recommendation engine uses a custom **3D bin-packing algorithm** to simulate product placement and returns exact placement coordinates and orientations for every packed item.

---

## Problem Statement

Warehouse operators often choose shipping boxes manually, leading to:

* Higher packaging costs
* Inefficient space utilization
* Increased shipping expenses
* Human error in box selection

This system automates the process by selecting the most cost-effective box capable of packing all ordered products.

---

## Key Features

### Product Management

* Create, update, retrieve, and delete products
* Store dimensions and weight

### Box Management

* Manage available shipping boxes
* Configure internal dimensions
* Define weight capacity and shipping cost

### Order Management

* Create orders containing multiple products
* Support configurable quantities

### Intelligent Box Recommendation

* Evaluates all available boxes
* Performs physical fit validation
* Considers weight restrictions
* Returns the lowest-cost valid box

### 3D Packing Engine

* Supports all six possible product orientations
* Calculates exact item placement coordinates
* Simulates real packing constraints
* Rejects boxes that cannot physically fit all items

### REST API

* Full CRUD APIs
* JSON-based request/response format
* Django REST Framework browsable API support

---

# Technology Stack

| Component     | Technology            |
| ------------- | --------------------- |
| Language      | Python 3.12+          |
| Framework     | Django 5.2            |
| API Framework | Django REST Framework |
| Database      | SQLite                |
| Testing       | Django Test Framework |
| Architecture  | Service-Oriented      |

---

# System Architecture

```text
box_selector/
│
├── products/
├── boxes/
├── orders/
├── api/
│
└── recommendation/
    └── services/
        ├── box_selector.py
        └── packing_engine.py
```

### Application Layers

#### Domain Layer

Contains core business entities:

* Product
* Box
* Order
* OrderItem

#### Service Layer

Contains business logic:

* Box selection
* Packing simulation
* Cost optimization

#### API Layer

Exposes REST endpoints using DRF ViewSets and serializers.

---

# Recommendation Workflow

The recommendation process follows these steps:

### Step 1 — Weight Validation

Remove boxes whose maximum weight capacity is lower than the order weight.

### Step 2 — Volume Validation

Remove boxes whose internal volume is smaller than the total product volume.

### Step 3 — Dimension Screening

Perform a fast dimensional feasibility check.

### Step 4 — 3D Packing Simulation

Attempt to place all products inside the box using the packing engine.

### Step 5 — Cost Optimization

Among all valid boxes, return the cheapest one.

---

# Packing Algorithm

The system uses a greedy 3D bin-packing strategy inspired by guillotine partitioning.

## Process

1. Expand order items by quantity
2. Sort products by volume (largest first)
3. Generate all six valid orientations
4. Attempt placement in available void spaces
5. Split remaining empty space into new voids
6. Continue until all products are packed

## Space Representation

Empty space inside a box is represented using rectangular regions called:

```python
Void(
    x,
    y,
    z,
    length,
    width,
    height
)
```

Each placement updates the available void list.

## Output

The engine returns:

* Selected box
* Product coordinates
* Product orientation
* Volume utilization

---

# API Endpoints

## Products

| Method | Endpoint            |
| ------ | ------------------- |
| GET    | /api/products/      |
| POST   | /api/products/      |
| GET    | /api/products/{id}/ |
| PATCH  | /api/products/{id}/ |
| DELETE | /api/products/{id}/ |

---

## Boxes

| Method | Endpoint         |
| ------ | ---------------- |
| GET    | /api/boxes/      |
| POST   | /api/boxes/      |
| GET    | /api/boxes/{id}/ |
| PATCH  | /api/boxes/{id}/ |
| DELETE | /api/boxes/{id}/ |

---

## Orders

| Method | Endpoint          |
| ------ | ----------------- |
| GET    | /api/orders/      |
| POST   | /api/orders/      |
| GET    | /api/orders/{id}/ |
| DELETE | /api/orders/{id}/ |

---

## Box Recommendation

### Endpoint

```http
POST /api/recommend-box/
```

### Request

```json
{
  "order_id": 1
}
```

### Success Response

```json
{
  "order_id": 1,
  "recommendation": {
    "box_name": "Small Box",
    "cost": "2.50",
    "volume_utilization_pct": 41.7,
    "placements": [...]
  }
}
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd box_selector
```

## Create Virtual Environment

```bash
python -m venv venv
```

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Apply Migrations

```bash
python manage.py migrate
```

## Start Server

```bash
python manage.py runserver
```

Server:

```text
http://127.0.0.1:8000
```

Browsable API:

```text
http://127.0.0.1:8000/api/
```

---

# Running Tests

Run complete test suite:

```bash
python manage.py test
```

Run recommendation tests:

```bash
python manage.py test recommendation
```

Run API tests:

```bash
python manage.py test api
```

Coverage:

```bash
coverage run --source='.' manage.py test
coverage report
```

---

# Design Decisions

### Why Greedy Packing?

The assignment requires a practical recommendation engine rather than mathematically optimal packing.

Advantages:

* Fast execution
* Simple implementation
* Deterministic behavior
* Scales well for typical ecommerce orders

### Why Cost-Based Selection?

Warehouses generally aim to minimize packaging cost while ensuring successful shipment.

The recommendation engine therefore prioritizes:

1. Physical feasibility
2. Weight compliance
3. Lowest box cost

---

# Author

Developed as part of a Django backend engineering assignment focused on:

* System design
* API development
* Algorithm implementation
* Automated testing
* Clean architecture principles
