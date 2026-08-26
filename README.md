# Notification Service

A backend-focused learning project designed to explore asynchronous task processing, database-backed queue mechanics, state management, and REST API design using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Python Background Workers**.

> [!NOTE]
> **Primary Project Purpose**: This project was built primarily as a **backend architecture learning exercise**. The Order Simulator (`/`) and Simulated Inbox (`/inbox`) frontend interfaces exist solely as demonstration tools to visualize and make the backend notification pipeline observable. The core engineering effort lies within the API layer, database-backed queue, worker thread processing, state transitions, and persistence.

---

## Overview

The **Notification Service** simulates an e-commerce notification lifecycle. When order events occur—such as placing an order, dispatching, routing for delivery, or final delivery—the application receives event requests and queues notification tasks in a persistent PostgreSQL database table.

A separate background worker continuously polls this queue, claims pending notifications, updates their state through a clear lifecycle (`pending` → `processing` → `sent`), generates notification messages, and persists the results. Simulated clients can then query the backend to display processed notifications.

---

## Main Learning Objectives

This repository was constructed to gain hands-on experience with core backend systems concepts:

- **Asynchronous Task Processing**: Decoupling long-running or background notification logic from the synchronous HTTP request/response cycle.
- **Database-Backed Queue Semantics**: Implementing queueing patterns using relational database tables (`NotificationQueue`).
- **Task State Transitions**: Managing explicit state boundaries (`pending` → `processing` → `sent`).
- **Background Worker Threads**: Spawning dedicated consumer loops using Python's `threading` module to process queued work.
- **RESTful API Design**: Structuring endpoints with FastAPI for event intake (`POST /orders`) and retrieval (`GET /notification/{id}`).
- **ORM & Database Integration**: Utilizing SQLAlchemy ORM for model mapping, session management, and PostgreSQL operations.
- **Separation of Concerns**: Keeping API endpoints, data models, queue handlers, worker loops, and frontend simulators decoupled.
- **Polling Mechanics**: Understanding how frontend clients fetch updated backend state via short polling.

---

## Architecture

The following diagram illustrates the end-to-end flow of notifications from event trigger to backend processing and client polling:

```mermaid
flowchart TD
    subgraph Frontend["Demonstration Frontend"]
        Simulator["Order Simulator\n(simulation/order.html)"]
        Inbox["Simulated Inbox\n(simulation/inbox.html)"]
    end

    subgraph Backend["FastAPI Backend (main.py)"]
        API_Orders["POST /orders"]
        API_Notif["GET /notification/{id}"]
    end

    subgraph Database["PostgreSQL Storage"]
        DBQueue[("Notification Queue Table\n(notification_queue)")]
    end

    subgraph WorkerService["Worker Engine (workers/)"]
        WorkerThread["Background Worker Thread\n(worker.py / events.py)"]
    end

    Simulator -->|1. Trigger Stage Event| API_Orders
    API_Orders -->|2. Insert status='pending'| DBQueue
    WorkerThread -->|3. Read status='pending'| DBQueue
    WorkerThread -->|4. Update status='processing'| DBQueue
    WorkerThread -->|5. Generate text & status='sent'| DBQueue
    Inbox -->|6. Poll GET /notification/{id}| API_Notif
    API_Notif -->|7. Fetch status='sent' records| DBQueue
    API_Notif -->|8. Return JSON payload| Inbox
```

### Component Breakdown

1. **Order Simulator (`simulation/order.html`)**: An interactive frontend UI that allows users to place orders and advance through order stages (`ORDER_PLACED`, `DISPATCHED`, `OUT_FOR_DELIVERY`, `DELIVERED`). Each stage sends a POST request to `/orders`.
2. **FastAPI API Layer (`main.py`)**: Handles incoming REST requests, parses payloads via Pydantic models, interacts with database handlers, and returns JSON responses.
3. **PostgreSQL Notification Queue (`db_methods/`)**: A persistent relational table (`notification_queue`) acting as a message queue for notification tasks.
4. **Background Worker Engine (`workers/`)**: Runs a consumer thread that polls PostgreSQL for pending jobs, executes state transitions, formats notification body text, and marks jobs completed.
5. **Simulated Inbox (`simulation/inbox.html`)**: A demonstration view that periodically polls `GET /notification/{order_id}` every second to render incoming notifications in real time.

---

## Notification Lifecycle

Every notification record transitions through three distinct operational states:

```
[ pending ] ──(Worker Claims Job)──> [ processing ] ──(Worker Generates Text)──> [ sent ]
```

### 1. `pending`
- **Trigger**: Created when the client issues a `POST /orders` request.
- **Behavior**: The FastAPI handler writes a row into `notification_queue` with `status = "pending"`, an empty message string (`msg = ""`), and a timestamp (`created_at`).
- **Purpose**: Indicates the task is queued and awaiting worker consumption.

### 2. `processing`
- **Trigger**: A background worker thread executes `read_one()` and identifies a record with `status == "pending"`.
- **Behavior**: The worker updates the row status to `"processing"` via `modify_status(id, "processing")`.
- **Purpose**: Prevents duplicate execution by signaling that a worker is actively processing the task.

### 3. `sent`
- **Trigger**: The worker formats the notification message text according to `notification_type` and writes it to DB (`modify_sms`).
- **Behavior**: Once the message content is updated, the worker sets `status = "sent"`.
- **Purpose**: Indicates the notification task has been successfully processed by the backend engine and is ready to be fetched by client consumers.

> [!IMPORTANT]
> In this simulation, **`sent`** means *"successfully processed by the backend notification service"*. It does not imply delivery to an external third-party communication service (e.g., SMTP or SMS gateway).

---

## Order Simulation

The order simulator models a standard four-stage e-commerce order lifecycle:

```
1. ORDER_PLACED ──> 2. DISPATCHED ──> 3. OUT_FOR_DELIVERY ──> 4. DELIVERED
```

For every order placed in the simulator UI:
1. Stage 1 (`ORDER_PLACED`) immediately fires a `POST /orders` request.
2. After a configurable stage delay, Stage 2 (`DISPATCHED`) fires a `POST /orders` request.
3. After a stage delay, Stage 3 (`OUT_FOR_DELIVERY`) fires a `POST /orders` request.
4. After a stage delay, Stage 4 (`DELIVERED`) fires a `POST /orders` request.

> [!NOTE]
> The order simulator interface exists primarily to generate realistic lifecycle events and provide visual feedback while testing the backend pipeline under consecutive POST operations.

---

## Simulated Inbox

The inbox component demonstrates how downstream clients consume processed notification messages:

- **Polling Loop**: The inbox issues periodic HTTP GET requests (`GET /notification/{order_id}`) roughly every 1 second.
- **Filtering**: The backend queries PostgreSQL for records matching `order_id` where `status == "sent"`.
- **Rendering**: When new notifications with `status == "sent"` are returned, the inbox dynamically appends formatted notification cards to the inbox view.

---

## Backend Components

| Component | Path | Responsibility |
| :--- | :--- | :--- |
| **API Entry Point** | `main.py` | Defines FastAPI application routes (`/`, `/inbox`, `/orders`, `/notification/{id}`). |
| **Pydantic Models** | `models.py` | Validates order request payloads (`orders`) and wraps queue insert logic (`notification`). |
| **Database Handler** | `db_methods/database_handler.py` | Enforces data access operations (add to queue, read pending, update status, read sent notifications). |
| **Database Setup** | `db_methods/db_initialise.py` | Configures SQLAlchemy engine, session builder, and `NotificationQueue` table schema. |
| **Worker Engine** | `workers/worker.py` | Defines worker thread creation (`create_workers`), stop control, and process loop logic. |
| **Worker Runner** | `workers/events.py` | Main execution entry point for starting background worker loops. |
| **UI Templates** | `simulation/` | Jinja2/HTML templates (`order.html`, `inbox.html`) for interactive visual testing. |

---

## Database Schema

The notification queue is stored in PostgreSQL under the `notification_queue` table:

```sql
CREATE TABLE notification_queue (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product VARCHAR NOT NULL,
    notification_type VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    status VARCHAR NOT NULL,
    msg TEXT
);
```

### Table Field Reference

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Auto-incrementing primary key for the notification record. |
| `order_id` | `INTEGER` | Unique identifier representing the associated order. |
| `product` | `VARCHAR` | Name of the product (e.g., "Pro Laptop", "Smartphone"). |
| `notification_type` | `VARCHAR` | Type of stage (`ORDER_PLACED`, `DISPATCHED`, `OUT_FOR_DELIVERY`, `DELIVERED`). |
| `created_at` | `TIMESTAMP` | UTC timestamp when the notification was queued. |
| `status` | `VARCHAR` | Current processing state: `pending`, `processing`, or `sent`. |
| `msg` | `TEXT` | Formatted notification text message generated by the background worker. |

---

## API Endpoints

### 1. Queue Order Event
- **Endpoint**: `POST /orders`
- **Description**: Receives order stage events from clients and queues a pending notification task in PostgreSQL.
- **Request Body**:
  ```json
  {
    "product_id": 4821,
    "product": "Pro Laptop",
    "notification_type": "ORDER_PLACED"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "code": 200,
    "message": "Your order placed!! We will notify you shortly!"
  }
  ```

---

### 2. Fetch Sent Notifications
- **Endpoint**: `GET /notification/{id}`
- **Description**: Returns all processed notifications (`status == "sent"`) for a specified order ID.
- **Path Parameter**: `id` (integer/string order ID, e.g., `4821`).
- **Response** (`200 OK`):
  ```json
  {
    "notifications": [
      {
        "id": 1,
        "order_id": 4821,
        "product": "Pro Laptop",
        "msg": "your Pro Laptop with order id: 4821 is placed!!"
      },
      {
        "id": 2,
        "order_id": 4821,
        "product": "Pro Laptop",
        "msg": "your Pro Laptop with order id: 4821 is ready to distpach!!"
      }
    ],
    "code": 200
  }
  ```

---

### 3. Order Simulator Page
- **Endpoint**: `GET /`
- **Description**: Renders the `order.html` simulator dashboard.

---

### 4. Inbox Page
- **Endpoint**: `GET /inbox`
- **Description**: Renders the `inbox.html` polling dashboard.

---

## Worker Processing Flow

The background worker operates as an independent consumer process:

1. **Initialization**: Running `python -m workers.events` invokes `create_workers()`, launching a daemon thread (`process`) in `workers/worker.py`.
2. **Queue Inspection**: The worker calls `read_one()`, executing a SQL query:
   ```sql
   SELECT * FROM notification_queue WHERE status = 'pending' LIMIT 1;
   ```
3. **State Claim**: If a job is found, the worker executes `modify_status(id, "processing")`.
4. **Message Formatting**: Based on `notification_type`, the worker constructs appropriate user messaging:
   - `ORDER_PLACED` → `"your <product> with order id: <order_id> is placed!!"`
   - `DISPATCHED` → `"your <product> with order id: <order_id> is ready to distpach!!"`
   - `OUT_FOR_DELIVERY` → `"your <product> with order id: <order_id> is out for delivery!!"`
   - `DELIVERED` → `"your <product> with order id: <order_id> is delivered!!"`
5. **Message Persistence**: The worker executes `modify_sms(id, msg)` to store text in PostgreSQL.
6. **Completion Mark**: The worker sets `status = "sent"` via `modify_status(id, "sent")`.
7. **Continuous Loop**: The worker repeats the loop to pick up the next `pending` job.

---

## Project Structure

```
notification-service/
├── db_methods/
│   ├── __init__.py
│   ├── database_handler.py     # Database queries, queue operations, & status updates
│   └── db_initialise.py        # SQLAlchemy engine setup & NotificationQueue ORM model
├── simulation/
│   ├── inbox.html              # Frontend Inbox demonstration template (polling UI)
│   └── order.html              # Frontend Order Simulator template (event generator)
├── workers/
│   ├── __init__.py
│   ├── events.py               # Worker entry point execution script
│   └── worker.py               # Worker thread logic and message generation
├── .env                        # Environment variables (Database URL)
├── .gitignore                  # Git ignore rules
├── main.py                     # FastAPI application & route definitions
├── models.py                   # Pydantic schemas and notification helper class
└── README.md                   # Project documentation
```

---

## Setup & Installation

### Prerequisites
- **Python 3.10+**
- **PostgreSQL Database** installed and running locally.

### 1. Clone Repository
```bash
git clone https://github.com/Utkarshaglitched/notification-service.git
cd notification-service
```

### 2. Create and Activate Virtual Environment
- **Windows**:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic jinja2
```

### 4. Configure PostgreSQL Database
Create a PostgreSQL database named `notification_service`:
```sql
CREATE DATABASE notification_service;
```

---

## Environment Variables

Create or edit the `.env` file in the root directory:

```env
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/notification_service
```

Replace `postgres`, `your_password`, and database details with your local PostgreSQL credentials.

---

## Running the Project

Running the full system requires two active terminal windows:

### Terminal 1: Start FastAPI Web Server
```bash
uvicorn main:app --port 9000 --reload
```
The web server will start at `http://127.0.0.1:9000/`.

### Terminal 2: Start Background Worker Process
```bash
python -m workers.events
```
The background worker will begin polling the database queue for pending tasks.

---

## Step-by-Step Example Flow

1. Open `http://localhost:9000/` in your browser.
2. Click **Place Order** on a product (e.g., "Pro Laptop").
3. `order.html` generates a random Order ID (e.g., `#7421`) and sends:
   ```http
   POST /orders
   { "product_id": 7421, "product": "Pro Laptop", "notification_type": "ORDER_PLACED" }
   ```
4. FastAPI receives the request and inserts a record into PostgreSQL:
   `status = 'pending'`, `msg = ''`.
5. The running worker thread in Terminal 2 detects the pending task via `read_one()`:
   - Updates status to `processing`.
   - Generates message: `"your Pro Laptop with order id: 7421 is placed!!"`.
   - Updates message in DB and sets status to `sent`.
6. Open `http://localhost:9000/inbox` in another tab or enter Order ID `7421`.
7. `inbox.html` polls `GET /notification/7421` every second, fetches the `sent` record, and displays the notification card.
8. As `order.html` timer progresses through `DISPATCHED`, `OUT_FOR_DELIVERY`, and `DELIVERED`, steps 3–7 repeat seamlessly for each stage.

---

## Technical Design Decisions

### Why use PostgreSQL as a queue?
Using a relational database table for queueing was intentionally chosen to study queue semantics, inspect raw row state transitions (`pending` → `processing` → `sent`), understand transactional commits/rollbacks, and observe state persistence without adding external messaging infrastructure during early backend learning.

### Why separate background workers?
In real-world applications, operations like sending emails or SMS messages take time. Executing notification processing inside the API request cycle would block API responses and slow down client experiences. Running background worker threads decouples job execution from API request handlers.

### Why polling in the Inbox?
Short HTTP polling was chosen for the demonstration UI to keep frontend client interaction simple and transparent while showcasing REST endpoint data retrieval.

---

## Limitations & Scope

As a learning simulation project, several production concepts are intentionally simplified:

- **Database-Backed Queue**: PostgreSQL is used as a queue rather than dedicated message brokers (e.g., Redis, RabbitMQ, Kafka).
- **Simulated Communications**: "Sent" status indicates successful database completion; no real email (SMTP/SendGrid) or SMS (Twilio) gateways are attached.
- **Worker Concurrency**: The worker thread model uses a basic polling loop without row-level locking (e.g., `SELECT FOR UPDATE SKIP LOCKED`) or distributed worker coordination.
- **Polling vs. Sockets**: Frontend inbox updates rely on HTTP polling rather than WebSockets or Server-Sent Events (SSE).
- **Error Recovery**: Retries, backoff policies, and Dead-Letter Queues (DLQ) are not currently implemented.

---

## What I Learned

Through building this project, I gained practical insights into:

- How REST APIs receive events and delegate tasks to persistent storage.
- How background workers consume tasks asynchronously out of band.
- Managing database state transitions explicitly and safely using ORM sessions.
- Designing API contracts between frontend clients, queues, and background services.
- The differences between synchronous HTTP handling and asynchronous background processing.
- Recognizing when backend systems outgrow database queues and require dedicated distributed event streaming platforms.

---

## Future Improvements

Potential enhancements for evolving this service toward production readiness:

- [ ] **Message Broker Integration**: Replace DB queue polling with **Redis Pub/Sub**, **RabbitMQ**, or **Apache Kafka**.
- [ ] **Task Framework**: Migrate background workers to **Celery** or **ARQ**.
- [ ] **Real-Time Push**: Implement **WebSockets** or **Server-Sent Events (SSE)** for instant inbox delivery.
- [ ] **Reliability Patterns**: Add exponential backoff retries and Dead-Letter Queues (DLQ) for failed tasks.
- [ ] **Row Locking**: Use `SELECT FOR UPDATE SKIP LOCKED` to support safe multi-worker scaling on PostgreSQL.
- [ ] **Notification Providers**: Integrate real notification delivery channels (SendGrid, Twilio, Firebase FCM).
- [ ] **Authentication**: Add JWT user auth to isolate user notification feeds securely.

---

## Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **FastAPI** | High-performance Python web framework for REST API endpoints. |
| **Python 3** | Core backend language for API logic and worker thread processing. |
| **PostgreSQL** | Relational database used for persistent notification queueing and storage. |
| **SQLAlchemy** | Python ORM for database schema definition, query building, and session management. |
| **Threading** | Python standard library `threading` module for background worker concurrency. |
| **HTML / CSS / JS** | Lightweight demonstration frontend for simulating order events and polling inbox feeds. |

---

## Demonstration UI

The project includes two visual interfaces for testing backend behavior:

- **Order Simulator (`/`)**: Simulates product purchases and triggers sequential POST requests across 4 delivery stages with visual progress tracking.
- **Simulated Inbox (`/inbox`)**: Allows filtering by Order ID or viewing all live notifications polled directly from the backend.

---

## Conclusion

This project served as a foundational exploration of backend architecture, task queueing, worker execution loops, and state management. The frontend simulation serves purely to make these backend mechanisms observable and easy to demonstrate in real time.
