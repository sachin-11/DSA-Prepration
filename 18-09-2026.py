# ============================================================
# Senior Python Interview Prep — 18-09-2026
# Interviewer profile: Mohammad Sanaullah, Technology Lead @ Infosys
# Skills: Python, FastAPI, AWS, React, SRE & CI/CD
# Current work: SRE Dashboard (American Airlines client), Document Generator
# -> Iska matlab questions ka mix hoga: Core Python (senior level) +
#    FastAPI (async APIs) + AWS (monitoring/deploy) + SRE (observability,
#    incident mgmt) + CI/CD (docker/k8s/pipelines). System design bhi expect karo.
# ============================================================


# ------------------------------------------------------------
# SECTION 1: CORE PYTHON (senior level)
# ------------------------------------------------------------

# Q1. GIL (Global Interpreter Lock) kya hai? Multi-threading vs multi-processing?
#
# THEORY:
# GIL ek mutex hai jo CPython interpreter ke andar ek time pe sirf ek
# thread ko Python bytecode execute karne deta hai. Isliye pure-Python
# threads truly parallel nahi chalte (single CPU core jaisa behave karte
# hain), chahe machine mein kitne bhi cores ho.
# - I/O-bound tasks (API call, DB query, file read, sleep) -> threading
#   theek hai, kyunki I/O wait ke time thread GIL release kar deta hai,
#   dusra thread chal sakta hai.
# - CPU-bound tasks (heavy math, image processing) -> threading se koi
#   speedup nahi milega, isliye multiprocessing use karo — har process
#   ka apna interpreter + apna GIL hota hai, true parallel execution.
# - asyncio -> single thread, GIL irrelevant yahan, cooperative
#   multitasking se high I/O concurrency milti hai (FastAPI isi pe hai).

import time
import threading
import multiprocessing


def cpu_task(n):
    return sum(i * i for i in range(n))


def benchmark_threading_vs_processing():
    n = 5_000_000

    start = time.perf_counter()
    threads = [threading.Thread(target=cpu_task, args=(n,)) for _ in range(2)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    print("threading:", time.perf_counter() - start)   # GIL ki wajah se koi speedup nahi

    start = time.perf_counter()
    procs = [multiprocessing.Process(target=cpu_task, args=(n,)) for _ in range(2)]
    [p.start() for p in procs]
    [p.join() for p in procs]
    print("multiprocessing:", time.perf_counter() - start)   # real parallel, faster


# ------------------------------------------------------------
# Q2. Decorators kaise kaam karte hain? Apna decorator likho with args.
#
# THEORY:
# Decorator ek higher-order function hai — ek function leta hai aur
# usko wrap karke naya function return karta hai, jisse original
# function ka code change kiye bina uska behavior extend ho jaye
# (logging, timing, auth check, retry, caching — sab decorators se hota hai).
# functools.wraps use karna zaroori hai warna wrapped function ka
# __name__/__doc__ lost ho jata hai (debugging/introspection break hoti hai).

import functools


def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper


@timing_decorator
def slow_add(a, b):
    time.sleep(0.1)
    return a + b


# Parameterized decorator (decorator factory) — extra level of nesting
def retry(times=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    print(f"attempt {attempt + 1} failed: {e}")
            raise last_exc
        return wrapper
    return decorator


@retry(times=2)
def flaky_call():
    raise ValueError("temporary failure")


# ------------------------------------------------------------
# Q3. Generators vs Iterators? yield kaise memory bachata hai?
#
# THEORY:
# Iterator: koi bhi object jisme __iter__() aur __next__() defined ho.
# Generator: function jisme yield ho — call karte hi wo run nahi hota,
# balki ek generator object return hota hai. Har next() call pe function
# yield tak execute hota hai, state (local variables) pause ho jati hai,
# aur agli baar wahi se resume hota hai.
# Fayda: poori list ek saath memory mein banani nahi padti — values
# lazily, ek-ek karke generate hoti hain. Large files/streams ke liye
# ye critical hai (memory O(1) vs O(n)).

def read_large_file_lazy(path):
    with open(path) as f:
        for line in f:
            yield line.strip()


def demo_generator_memory():
    gen = (x * x for x in range(10**7))   # lazy, memory mein sirf ek value hoti he
    print(next(gen), next(gen), next(gen))   # 0 1 4
    # lst = [x * x for x in range(10**7)]   # eager -> poori list RAM mein


# ------------------------------------------------------------
# Q4. async/await internally kaise kaam karta hai? Event loop kya hai?
#
# THEORY:
# asyncio ek single-threaded event loop chalata hai jo coroutines ko
# schedule/resume karta hai. Jab koi coroutine "await" karti hai
# (jaise asyncio.sleep, ya async DB/HTTP call), wo control event loop
# ko wapas de deti hai. Loop tab tak dusre ready tasks run kar sakta
# hai jab tak current task I/O complete hone ka wait kar raha ho.
# Isi wajah se ek single thread mein hazaron concurrent I/O operations
# efficiently handle ho jate hain — FastAPI ka high throughput isi
# model se aata hai.
# GOTCHA: async function ke andar koi blocking call (time.sleep,
# sync requests.get, sync DB driver) mat use karo — wo poore event
# loop ko block kar dega, saari requests slow ho jayengi.

import asyncio


async def fetch_data(delay, name):
    print(f"{name} started")
    await asyncio.sleep(delay)   # non-blocking wait, loop ko control wapas
    print(f"{name} done")
    return name


async def run_concurrently():
    # sequential await hota to total time = sum(delays) = 3s
    # asyncio.gather se concurrent -> total time = max(delays) = 2s
    results = await asyncio.gather(
        fetch_data(2, "task1"),
        fetch_data(1, "task2"),
    )
    return results


# ------------------------------------------------------------
# Q5. Context managers (with statement) kaise banate ho?
#
# THEORY:
# `with` statement resource acquire/release ko guarantee karta hai,
# chahe block ke andar exception hi kyun na aaye (jaise file close,
# DB connection close, lock release). Do tarike: class-based
# (__enter__/__exit__ methods) ya @contextmanager decorator ke saath
# generator function (yield se pehle = setup, yield ke baad = teardown).

from contextlib import contextmanager


@contextmanager
def db_transaction(conn_name):
    print(f"BEGIN transaction on {conn_name}")
    try:
        yield conn_name
        print("COMMIT")
    except Exception:
        print("ROLLBACK")
        raise
    finally:
        print("close connection")


def demo_context_manager():
    with db_transaction("orders_db") as conn:
        print(f"using {conn}")


# ------------------------------------------------------------
# Q6. *args, **kwargs, positional-only / keyword-only params
#
# THEORY:
# *args -> extra positional arguments ek tuple mein collect hote hain.
# **kwargs -> extra keyword arguments ek dict mein collect hote hain.
# Function signature mein `*` ke baad wale params sirf keyword se pass
# ho sakte hain (keyword-only) — API design mein ye clarity ke liye
# use hota hai, taaki caller ko explicit likhna pade (typo/order mistake avoid).

def configure(*, host, port=8000, **extra_options):
    print(host, port, extra_options)


# configure("localhost")          # TypeError -> host positional se nahi chalega
# configure(host="localhost", timeout=30)   # sahi tarika


# ------------------------------------------------------------
# Q7. Shallow copy vs deep copy
#
# THEORY:
# copy.copy() (shallow): naya top-level object banta hai, lekin uske
# andar ke nested/mutable objects same reference share karte hain —
# nested object change karoge to original bhi change ho jayega.
# copy.deepcopy(): poora nested structure recursively naya ban jata
# hai, koi bhi shared reference nahi rehta.

import copy

original = {"a": [1, 2, 3]}
shallow = copy.copy(original)
deep = copy.deepcopy(original)

shallow["a"].append(4)
print(original["a"])   # [1, 2, 3, 4] -> shallow ne original ko bhi affect kiya
print(deep["a"])       # [1, 2, 3]    -> deep independent hai


# ============================================================
# SECTION 2: FASTAPI
# ============================================================

# Q8. FastAPI Flask se fast/different kaise hai?
#
# THEORY:
# - Starlette (ASGI framework) pe based hai -> native async support,
#   thread-per-request model (WSGI/Flask) ke bajaye event-loop based
#   concurrency, isliye high I/O throughput.
# - Pydantic se automatic request/response validation + serialization
#   (type hints se hi schema ban jati hai, manual validation nahi likhni padti).
# - Type hints se hi automatic OpenAPI/Swagger docs generate ho jate hain.
# - Dependency Injection system (Depends) built-in hai.

from pydantic import BaseModel, Field, validator


class UserCreate(BaseModel):
    name: str
    age: int = Field(gt=0, lt=120)
    email: str

    @validator("email")
    def email_must_have_at(cls, v):
        if "@" not in v:
            raise ValueError("invalid email")
        return v


# Q9. Dependency Injection example (Depends)
#
# THEORY:
# Depends() se FastAPI reusable dependencies (DB session, auth check,
# pagination params) automatically resolve/inject karta hai har request
# ke liye. yield-based dependency use karo jab cleanup zaroori ho
# (jaise DB connection close) — yield ke baad ka code response ke
# baad execute hota hai (try/finally jaisa guarantee).
"""
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db=Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
"""


# Q10. Background tasks vs Celery — kab kaunsa use karoge?
#
# THEORY:
# - BackgroundTasks (FastAPI built-in): halke, fire-and-forget kaam
#   (email bhejna, log likhna), response ke baad usi process mein
#   chalta hai. Agar app crash/restart ho jaye to task lost ho sakta hai.
# - Celery/RQ: heavy, retryable, distributed tasks (report/PDF generation,
#   large file processing) — separate worker process, persistent queue
#   (Redis/RabbitMQ), automatic retries + monitoring.
# -> "Document Generator" jaisa project heavy PDF/report generation
#    karega, isliye wahan likely Celery ya background worker use hua
#    hoga — unke actual project se related question ban sakta hai.
"""
from fastapi import BackgroundTasks

def send_email_log(email: str):
    print(f"sending email to {email}")

@app.post("/signup")
async def signup(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_log, email)
    return {"status": "signed up"}
"""


# Q11. Middleware example
#
# THEORY:
# Middleware har request/response ke beech mein chalta hai (global
# logging, auth header check, CORS, timing). dispatch(request, call_next)
# pattern mein call_next se pehle "before" logic, uske baad "after" logic likhte ho.
"""
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        print(f"{request.method} {request.url.path} took {duration:.3f}s")
        return response
"""


# Q12. FastAPI mein sync `def` vs `async def` endpoint ka farak?
#
# THEORY:
# - `async def` endpoint: event loop ke thread mein directly run hota
#   hai — non-blocking I/O ke liye best, par blocking code loop ko
#   freeze kar dega.
# - `def` (sync) endpoint: FastAPI automatically ise ek threadpool
#   mein run karta hai, taaki blocking libraries (sync DB driver, requests)
#   ka use karne pe bhi event loop block na ho.
# Common mistake: async def ke andar sync blocking call likhna — sab
# concurrent requests slow ho jati hain kyunki loop hi stuck hai.


# ============================================================
# SECTION 3: AWS (SRE dashboard context ke hisaab se important)
# ============================================================

# Q13. CloudWatch se custom metrics/logs kaise bhejte/padhte ho? (boto3)
#
# THEORY:
# CloudWatch AWS ka monitoring service hai — metrics (numeric time-series),
# logs, aur alarms (threshold breach pe SNS notify) store/manage karta hai.
# SRE dashboards typically CloudWatch se metrics pull karke visualize
# karte hain, ya custom application metrics (jaise "orders_processed")
# CloudWatch ko push karte hain.

"""
import boto3

cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")

# custom metric bhejna
cloudwatch.put_metric_data(
    Namespace="MyApp/SRE",
    MetricData=[{
        "MetricName": "RequestLatency",
        "Value": 123.4,
        "Unit": "Milliseconds",
    }],
)

# metric padhna (dashboard ke liye)
response = cloudwatch.get_metric_statistics(
    Namespace="MyApp/SRE",
    MetricName="RequestLatency",
    StartTime=start_time,
    EndTime=end_time,
    Period=60,
    Statistics=["Average", "p99"],
)
"""

# Q14. IAM Role vs IAM User vs Policy?
#
# THEORY:
# - User: ek specific person/service ki identity, long-term credentials
#   (access key/secret) rakhta hai.
# - Role: temporary credentials — services (EC2/Lambda/ECS task) role
#   "assume" karte hain, hardcoded keys ki zaroorat nahi padti.
# - Policy: JSON document jo permissions define karta hai (kaunsa
#   action, kaunsa resource) — user/role/group pe attach hoti hai.
# Best practice: EC2/Lambda ko IAM Role do (least privilege), hardcoded
# access keys production code mein kabhi commit mat karo.

# Q15. Auto Scaling kaise kaam karta hai?
#
# THEORY:
# CloudWatch alarm ek threshold define karta hai (e.g. avg CPU > 70%
# for 5 minutes) -> alarm trigger hone pe Auto Scaling policy naye
# instances launch karti hai (scale-out), load kam hone pe scale-in.
# Health checks (ELB/ALB) failing instances ko automatically replace
# karte hain — reliability ke liye critical hai.


# ============================================================
# SECTION 4: SRE CONCEPTS (unka core domain — deep questions expect karo)
# ============================================================

# Q16. SLI, SLO, SLA mein farak?
#
# THEORY:
# - SLI (Indicator): actual measured metric, e.g. "request success rate".
# - SLO (Objective): internal target for that metric, e.g. "99.9% over 30 days".
# - SLA (Agreement): external, contractual commitment with penalties —
#   usually SLO se thoda loose rakha jata hai taaki buffer/error budget rahe.

def calculate_error_budget(slo_percent, total_requests):
    # THEORY: error budget = allowed failure %; jab tak budget bacha hai
    # team confidently naye features/releases ship kar sakti hai.
    allowed_failure_percent = 100 - slo_percent
    allowed_failures = total_requests * (allowed_failure_percent / 100)
    return allowed_failures


print(calculate_error_budget(slo_percent=99.9, total_requests=1_000_000))
# -> 1000 failed requests allowed per month agar SLO 99.9% hai


# Q17. Golden Signals (monitoring ke 4 pillars — Google SRE book)
#
# THEORY:
# - Latency: request kitni der lagi (success vs error latency alag track karo)
# - Traffic: kitna load/demand aa raha hai (requests/sec)
# - Errors: failure rate (4xx/5xx, timeouts)
# - Saturation: system kitna "full" hai (CPU/memory/queue depth/connection pool)
# Dashboard design karte waqt in 4 signals ko har service ke liye
# minimum dikhana chahiye.

golden_signals = {
    "latency_p99_ms": 245,
    "traffic_rps": 1200,
    "error_rate_percent": 0.03,
    "saturation_cpu_percent": 62,
}


def is_healthy(signals, error_threshold=1.0, saturation_threshold=85):
    return (
        signals["error_rate_percent"] < error_threshold
        and signals["saturation_cpu_percent"] < saturation_threshold
    )


print(is_healthy(golden_signals))   # True


# Q18. Incident response / postmortem process?
#
# THEORY:
# Detect (alerting) -> Triage/severity assign -> Mitigate (rollback/hotfix,
# stop the bleeding first, root cause baad mein) -> Root Cause Analysis
# -> Blameless postmortem (focus process/system pe, logon pe nahi) ->
# Action items track karke prevent recurrence.

# Q19. Alerting best practice — symptom-based vs cause-based?
#
# THEORY:
# Symptom-based alerts prefer karo (e.g. "error rate high", "latency high")
# instead of cause-based (e.g. "CPU high", "disk 80% full") — symptom
# directly user-impact se juda hota hai; cause-based alerts noisy/false
# positive zyada dete hain (CPU high ho sakta hai but users affected na ho).


# ============================================================
# SECTION 5: CI/CD & DEPLOYMENT
# ============================================================

# Q20. CI/CD pipeline stages typically kya hote hain?
#
# THEORY:
# Lint/format -> Unit tests -> Build (Docker image) -> Security scan ->
# Push to registry (ECR) -> Deploy to staging -> Integration tests ->
# Deploy to prod (blue-green / canary / rolling).

# GitHub Actions jaisa minimal pipeline (YAML as string reference):
ci_pipeline_example = """
name: ci
on: [push]
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest
      - run: docker build -t myapp:${{ github.sha }} .
"""

# Q21. Blue-Green vs Canary vs Rolling deployment?
#
# THEORY:
# - Blue-Green: 2 identical environments, traffic instantly switch
#   (fast rollback bas switch wapas karo, par double infra cost during switch).
# - Canary: naya version thode traffic % pe test karo, gradually badhao
#   (risk kam hota hai, slow rollout, monitoring zaroori hai taaki
#   canary fail hone pe rollback ho sake).
# - Rolling: instances ek-ek/batch karke update hote hain (no downtime,
#   par thodi der mixed versions live rehte hain — backward compatibility zaroori).

# Q22. Dockerfile best practices (senior level gotchas)
#
# THEORY:
# - Multi-stage builds -> final image chhota rakhne ke liye (build tools
#   final image mein nahi jaate).
# - Layer caching order: kam-change-hone-wali cheezein (dependency
#   install) pehle copy karo, application code baad mein — taaki
#   rebuild fast ho (code change hone pe deps re-install na ho).
# - Non-root user se container run karo (security).
# - .dockerignore se .git, __pycache__, venv jaisi cheezein exclude karo.

dockerfile_example = """
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
RUN useradd -m appuser
USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
"""


# ============================================================
# SECTION 6: SYSTEM DESIGN
# ============================================================

# Q23. "Design a real-time SRE monitoring dashboard" — kaise approach karoge?
#
# THEORY (step-by-step approach interview mein bolne ke liye):
# 1. Data ingestion: services metrics push karte hain (CloudWatch/Prometheus)
#    ya dashboard pull karta hai via APIs.
# 2. Storage: time-series DB (CloudWatch Metrics, Prometheus, InfluxDB).
# 3. Backend (FastAPI): APIs expose karo aggregated data ke liye;
#    WebSocket/SSE se real-time push updates dashboard ko.
# 4. Alerting layer: threshold breach -> SNS/PagerDuty integration.
# 5. Frontend (React): charts (latency, error rate, traffic), auto-refresh,
#    service/environment filter.
# 6. Scalability: Redis caching frequently-queried aggregates ke liye,
#    pagination for logs, async endpoints for concurrent dashboard users.
# -> Ye unke actual project (American Airlines SRE Dashboard) se match
#    karta hai, isliye is tarah ka design question definitely aa sakta hai.

# Chhota code sketch — real-time push endpoint (WebSocket) idea:
"""
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws/metrics")
async def metrics_stream(websocket: WebSocket):
    await websocket.accept()
    while True:
        latest = await get_latest_golden_signals()   # DB/cache se fetch
        await websocket.send_json(latest)
        await asyncio.sleep(5)   # every 5s push
"""

# Q24. "Document Generator mein large PDF generate karte waqt API
# timeout na ho" — kaise design karoge?
#
# THEORY:
# HTTP request ko generation complete hone tak open mat rakho (client/
# gateway timeout ho jayega). Async job pattern use karo:
# 1. POST /generate -> turant job_id return karo, actual generation
#    background worker (Celery) ko queue kar do.
# 2. Client GET /status/{job_id} se poll kare, ya server WebSocket/
#    webhook se "done" notify kare.
# 3. Result S3 mein store karo, client ko download link do.

status_flow_example = """
POST /documents/generate   -> {"job_id": "abc123", "status": "queued"}
GET  /documents/abc123      -> {"status": "processing"}
GET  /documents/abc123      -> {"status": "done", "download_url": "s3://..."}
"""


# ============================================================
# SECTION 7: LIKELY BEHAVIORAL / PROJECT QUESTIONS (theory only, no code)
# ============================================================
# - "Tumne production issue kaise debug kiya jo reproduce nahi ho raha tha?"
# - "Ek baar jab deployment fail ho gaya, tumne kaise handle kiya?"
# - "Tumhare current project mein sabse bada scaling challenge kya tha?"
# - "Kabhi kisi legacy sync code ko async mein migrate kiya? Kya dikkat aayi?"
# - "Document Generator jaisa system design karo — large PDF generate karte
#    waqt API timeout na ho, iske liye kya approach loge?" (dekho Q24)
