# ============================================================
# HARDEST Deployment Questions — Senior/Staff Level — 18-09-2026
# Interviewer: SRE & CI/CD background, FastAPI + React + AWS stack,
# owns SRE Dashboard (American Airlines) + Document Generator project.
# -> Ye wahi questions hain jo interview mein "trap" ban jaate hain —
#    surface-level jawab (jaise "hum blue-green karte hain") kaafi nahi
#    hota, follow-up mein "par agar X ho jaye to?" poochhte hain.
#    Har question mein wahi follow-up depth pehले se diya hai.
# ============================================================


# ------------------------------------------------------------
# Q1. Zero-downtime deploy karte waqt DB schema migration bhi chahiye
# (jaise ek column rename/drop karna hai) — kaise karoge bina downtime
# ya errors ke, jab do versions of app thodi der ek saath chal rahe hon?
#
# THEORY (Expand-Contract pattern — ye hi asli senior-level answer hai):
# Rolling deploy ke waqt PURANA aur NAYA dono app version SAME database
# ko HIT karte hain (kuch minutes/hours ke liye). Agar tumne migration
# mein direct column rename/drop kiya, to purana version turant crash
# hoga (column not found).
#
# Solution — 3 phases:
# 1. EXPAND: naya column add karo (old column ko touch mat karo).
#    Dono old aur new code ab chal sakte hain — old column read/write
#    karta hai, new code dono columns ko sync rakhta hai (dual write)
#    ya backfill job chalata hai.
# 2. MIGRATE: backfill script se purana data naye column mein copy karo.
#    Deploy naye code ka jo sirf naya column use kare (read/write).
# 3. CONTRACT: jab confirm ho jaye ki koi bhi running instance purana
#    column use nahi kar raha (old version poora retire ho gaya), tab
#    ek ALAG migration se purana column drop karo.
#
# GOTCHA jo interviewer follow-up mein poochega:
# "Agar backfill job chal rahi ho aur usi waqt naya data insert ho, wo
#  backfill se miss to nahi ho jayega?" -> Answer: backfill ko idempotent
#  aur chunked rakho, aur dual-write phase mein naya code hamesha DONO
#  columns likhe jab tak contract phase na aaye.

migration_expand_example = """
-- Phase 1: EXPAND (safe, backward compatible)
ALTER TABLE users ADD COLUMN email_normalized VARCHAR(255) NULL;

-- App code (dual-write during transition):
-- old_email column continue read/write hota rahega
-- email_normalized bhi saath mein likha jayega

-- Phase 2: MIGRATE (backfill, chunked + idempotent)
UPDATE users SET email_normalized = LOWER(TRIM(old_email))
WHERE email_normalized IS NULL LIMIT 1000;   -- batches mein, load control ke liye

-- Phase 3: CONTRACT (sirf jab saare instances new code pe ho)
ALTER TABLE users DROP COLUMN old_email;
"""


# ------------------------------------------------------------
# Q2. Rolling deployment ke beech mein ek request already "in-flight"
# hai (processing chal rahi hai) aur usi waqt us pod/instance ko
# terminate karne ka signal aa gaya — data loss ya broken response
# kaise avoid karoge? (Graceful shutdown)
#
# THEORY:
# Kubernetes/orchestrator pehle SIGTERM bhejta hai, phir grace period
# (default 30s) ke baad SIGKILL (force kill) — is window mein app ko:
# 1. Naye incoming requests lena band karna chahiye (readiness probe
#    fail karo turant, taaki load balancer naya traffic bhejna band kare)
# 2. Already-accepted in-flight requests ko COMPLETE karne dena chahiye
# 3. Connections (DB pool, websocket) ko gracefully close karna chahiye
# 4. Grace period khatam hone se PEHLE process exit ho jana chahiye,
#    warna SIGKILL se abrupt termination (data corruption risk)
#
# GOTCHA follow-up: "Agar ek request 45 seconds leti hai process karne
# mein aur grace period sirf 30s hai?" -> terminationGracePeriodSeconds
# badhao K8s mein, AUR long-running kaam ko sync request-response se
# background job (Celery/queue) mein move karo — HTTP request lambe
# time tak open rakhna hi anti-pattern hai (dekho Q24 python file mein).

import signal
import sys
import time

shutting_down = False


def handle_sigterm(signum, frame):
    global shutting_down
    print("SIGTERM received — stopping new work, finishing in-flight requests")
    shutting_down = True


signal.signal(signal.SIGTERM, handle_sigterm)


def readiness_probe():
    # K8s ye endpoint poll karta hai -> False return karte hi load
    # balancer naya traffic bhejna band kar dega, existing connections
    # affect nahi hoti
    return not shutting_down


# FastAPI mein lifespan/shutdown event se cleanup:
fastapi_graceful_shutdown_example = """
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield
    # shutdown: DB pool close, in-flight background tasks ko finish
    # hone do, connections drain karo
    await db_pool.close()
    print("graceful shutdown complete")

app = FastAPI(lifespan=lifespan)
"""


# ------------------------------------------------------------
# Q3. WebSocket connections (SRE dashboard real-time metrics jaisa)
# rolling deployment ke beech mein kaise handle karoge? Ye normal HTTP
# requests se zyada tricky kyun hai?
#
# THEORY:
# WebSocket ek LONG-LIVED connection hai — normal HTTP request
# seconds mein complete ho jati hai, but websocket ghanton khula reh
# sakta hai. Rolling deploy mein jab purana pod terminate hota hai,
# uske saare open websocket connections bhi forcibly close ho jayenge
# — client ko abrupt disconnect dikhega.
#
# Solution:
# 1. Client-side: auto-reconnect logic ZAROORI hai (React file ka Q10
#    dekho) — disconnect ko handle karna client ki responsibility hai,
#    server 100% seamless nahi rakh sakta long-lived connections ke liye.
# 2. Server-side: deployment se PEHLE naye connections stop karo
#    (readiness probe fail), phir existing websocket clients ko ek
#    "server restarting, please reconnect" message bhejo taaki wo
#    proactively naye pod se reconnect kar sake (graceful vs abrupt).
# 3. Load balancer/ingress mein sticky sessions avoid karo agar
#    possible — taaki reconnect kisi bhi healthy pod pe jaa sake.
#
# GOTCHA follow-up: "1000 concurrent websocket clients hain aur deploy
# karna hai — sab ek saath reconnect karenge to naye pods pe thundering
# herd/spike aa sakta hai?" -> Answer: reconnect delay ko jitter/random
# backoff do (client side), taaki reconnects time ke saath spread ho
# jayein instead of ek hi second mein sabka retry.

websocket_graceful_notice_example = """
@app.websocket("/ws/metrics")
async def metrics_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while not shutting_down:
            await websocket.send_json(get_latest_metrics())
            await asyncio.sleep(5)
        # shutdown ho raha hai -> client ko batao gracefully
        await websocket.send_json({"type": "reconnect", "reason": "server restarting"})
        await websocket.close()
    except WebSocketDisconnect:
        pass
"""


# ------------------------------------------------------------
# Q4. Canary deployment mein automated rollback kaise design karoge
# (sirf "5% traffic naye version ko do" bolna kaafi nahi hai)?
#
# THEORY:
# Real canary sirf traffic split nahi hai — uske saath automated
# health-check-based decision engine chahiye:
# 1. Canary pe thoda traffic (5-10%) route karo.
# 2. Golden signals (Python file Q17 dekho) canary vs baseline (stable
#    version) compare karo — error rate, latency p99, saturation.
# 3. Agar canary ka error rate/latency baseline se significantly worse
#    hai (statistical threshold, e.g. >2x baseline error rate over N
#    minutes), automated rollback trigger ho (traffic wapas 0% canary pe).
# 4. Agar healthy rahe, gradually traffic % badhao (5% -> 25% -> 50% -> 100%).
#
# GOTCHA follow-up: "Canary ka sample size chhota hai (5% traffic) —
# statistically significant conclusion kaise nikaloge ki wo actually
# bura hai, random noise nahi?" -> Answer: minimum sample size/duration
# threshold set karo before decision (e.g. at least 1000 requests ya
# 10 minutes), aur confidence interval/statistical significance test
# use karo, sirf raw percentage compare mat karo.

canary_decision_pseudocode = """
def should_rollback(canary_metrics, baseline_metrics, min_requests=1000):
    if canary_metrics.request_count < min_requests:
        return False  # not enough data yet, wait more

    error_rate_ratio = canary_metrics.error_rate / max(baseline_metrics.error_rate, 0.001)
    latency_ratio = canary_metrics.p99_latency / max(baseline_metrics.p99_latency, 1)

    if error_rate_ratio > 2.0 or latency_ratio > 1.5:
        return True  # significantly worse -> auto rollback
    return False
"""


# ------------------------------------------------------------
# Q5. Deploy karte waqt ek background worker (Celery, jaise Document
# Generator ka PDF generation job) exactly BEECH mein hai ek 10-minute
# wali heavy task process karte waqt — deploy kaise karoge bina us
# task ko corrupt/lose kiye?
#
# THEORY:
# Ye Q2 (graceful shutdown) se harder hai kyunki task ka duration HTTP
# request se kahin zyada lamba hai — 30s grace period kaafi nahi hoga.
# Solutions (trade-offs ke saath):
# 1. Celery `worker_pool_restarts` / warm shutdown: naye tasks lena
#    band karo (worker "offline" mode), current task complete hone do
#    poori tarah, phir hi process exit karo — grace period bahut zyada
#    (task ki max duration + buffer) set karna padega.
# 2. Task ko CHECKPOINTABLE/resumable banao: agar task beech mein
#    mare, wo progress state (jaise "page 45/100 generated") persist
#    kare kahin (DB/Redis), aur restart pe wahi se resume ho jaye
#    instead of scratch se — complex but robust.
# 3. Deployment ko worker pods ke liye "drain" strategy do: naye
#    version ke worker pods spin up karo (dono versions parallel chalte
#    hain), purane workers ko sirf EXISTING queued/running tasks
#    complete karne do phir hi terminate karo (kind of blue-green for workers).
#
# GOTCHA follow-up: "Agar task itna lamba hai ki deploy pipeline khud
# timeout ho jaye (CI/CD waiting for old pods to drain)?" -> Answer:
# deploy pipeline ko async/non-blocking rakho drain ke liye — deploy
# "successful" mark karo jaise hi naye pods healthy hain, purane pods
# background mein independently drain hote rahein (separate lifecycle).

celery_graceful_worker_example = """
# celery worker ko warm shutdown signal (SIGTERM by default warm hai)
# celery -A app worker --loglevel=info
#
# Kubernetes deployment:
#   terminationGracePeriodSeconds: 900   # 15 min, task ki max duration se zyada
#   lifecycle:
#     preStop:
#       exec:
#         command: ["celery", "control", "cancel_consumer", "myqueue"]
#         # naye tasks lena band, existing task complete hone do
"""


# ------------------------------------------------------------
# Q6. Multi-service deployment mein ek service (Service A) ko naye API
# contract ki zaroorat hai jo Service B abhi tak deploy nahi hui —
# dono services independently deploy hoti hain (no coordinated deploy).
# Kaise design karoge taaki temporary breakage na ho?
#
# THEORY:
# Ye distributed systems ka classic hard problem hai — "coordinated
# deploy" avoid karna chahiye (fragile, scales badly with more services).
# Solution: BACKWARD AND FORWARD COMPATIBLE API changes.
# - Naya field ADD karo API response mein (mat REMOVE/RENAME purana).
# - Service A (consumer) ko pehle deploy karo jo NAYA field
#   optionally handle kare (agar missing ho to fallback/default use kare).
# - Service B (naya field bhejne wali) baad mein deploy karo.
# - Purana field kabhi tab tak mat hatao jab tak confirm na ho jaye ki
#   koi consumer usko use nahi kar raha (version deprecation policy,
#   jaise "field X deprecated as of v2, will be removed in v3").
# Ye bilkul Q1 wale expand-contract pattern jaisa hi hai, bas DB schema
# ki jagah API schema/contract pe apply ho raha hai.
#
# GOTCHA follow-up: "Agar breaking change avoid hi nahi ho sakta
# (jaise field ka TYPE change karna hai)?" -> Answer: API versioning
# (/v1/, /v2/ endpoints, ya header-based versioning) — dono versions
# parallel serve karo jab tak saare consumers migrate na ho jayein.


# ------------------------------------------------------------
# Q7. Ek bad deployment already production mein DB migration chala
# chuka hai (jaise ek column drop kar diya) aur ab pata chala ki rollback
# karna hai — normal "redeploy old image" kaafi kyun nahi hoga, aur
# kaise recover karoge?
#
# THEORY:
# Ye sabse dangerous scenario hai kyunki APPLICATION code rollback
# easy hai (purana image deploy kar do), lekin DATABASE state rollback
# nahi hota automatically — agar column already drop ho chuka hai,
# purana app version us column ko expect karega -> crash.
#
# Isliye migrations HAMESHA backward-compatible order mein likhi jaani
# chahiye (yahi Q1 ka expand-contract principle ka real reason hai):
# - Destructive migrations (drop column/table) ko ALWAYS ek separate,
#   LATER deploy mein karo — kabhi bhi same deploy mein jisme naya
#   code bhi ja raha ho.
# - Agar already gलत ho chuka hai: column ko wapas add karo (naya
#   migration), agar data already lost hai to backup/snapshot se
#   restore karna padega (point-in-time recovery) — yahi wajah hai
#   production DB pe automated backups/PITR enable rakhna critical hai.
#
# GOTCHA follow-up: "Migration rollback script khud likhte ho?" ->
# Answer: har migration ka `up` aur `down` dono likho (Alembic/Django
# migrations pattern), lekin destructive down-migrations (data ko
# wapas lana) hamesha possible nahi hota — isliye prevention
# (expand-contract + review process) rollback se zyada important hai.


# ------------------------------------------------------------
# Q8. Secrets (DB password, API keys) rotate karne hain PRODUCTION
# mein bina kisi service ko restart/downtime kiye — kaise?
#
# THEORY:
# Naive approach (secret change karke sabko restart) downtime deta
# hai aur race condition risk hai (kuch pods purana secret use kar
# rahe, kuch naya, agar old secret turant invalid ho jaye to purane
# pods crash honge before restart complete).
#
# Solution:
# 1. Secrets manager (AWS Secrets Manager/Vault) DUAL support kare —
#    naya aur purana secret dono thodi der valid rahein (grace period).
# 2. Naya secret create karo (purana invalidate mat karo abhi).
# 3. Rolling restart karo services ka — application startup pe secret
#    dynamically fetch kare (hardcoded env var se nahi), taaki naye
#    pods naya secret automatically pick karein.
# 4. Jab confirm ho jaye saare pods naya secret use kar rahe hain,
#    tab purana secret revoke karo.
# Database credentials ke liye ye aur tricky hai — DB level pe bhi do
# valid credentials simultaneously support karne padte hain rotation
# window mein (jaise Postgres mein 2 roles, gradually migrate).


# ------------------------------------------------------------
# Q9. Kubernetes rolling update mein `maxSurge` aur `maxUnavailable`
# ka exact trade-off kya hai — production incident context mein
# explain karo.
#
# THEORY:
# - maxUnavailable: rolling update ke dauraan kitne pods DOWN ho sakte
#   hain ek time pe (capacity kam hone ka risk).
# - maxSurge: kitne EXTRA pods (beyond desired count) temporarily
#   create ho sakte hain (resource/cost spike ka risk, cluster mein
#   enough headroom chahiye).
# Trade-off: maxUnavailable=0 + maxSurge=1 sabse safe hai (kabhi
# capacity kam nahi hoti, ek extra pod hamesha spin hota hai pehle)
# lekin cluster resources tight hon to naya pod schedule hi nahi hoga
# (Pending state) — deployment STUCK ho jayega silently.
#
# GOTCHA follow-up: "Deployment stuck ho gaya (nayi pods Pending hain),
# kaise debug karoge?" -> `kubectl describe pod` se events dekho
# (resource limits, node affinity, PodDisruptionBudget conflicts).
# PodDisruptionBudget bhi yahan interact karta hai — agar PDB minAvailable
# bahut high set hai, rolling update aur node drain dono stuck ho sakte hain.

k8s_rolling_update_example = """
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: app
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
"""


# ------------------------------------------------------------
# Q10. Deployment ke turant baad cache (Redis/CDN) purana stale data
# serve kar raha hai naye code ke saath — cache invalidation deployment
# ke saath kaise coordinate karoge?
#
# THEORY:
# Classic "cache invalidation is hard" problem, deployment context mein:
# - Agar naya deploy response SHAPE change karta hai (jaise naya field
#   add/remove), purana cached response naye code ke expectations se
#   mismatch ho sakta hai (deserialize error ya missing field crash).
# - Solution: cache KEY mein version/schema identifier include karo
#   (jaise `user:123:v2`), taaki naya code automatically purana-shape
#   cache miss kare aur fresh fetch kare — explicit cache-flush deploy
#   step se better hai (jo poore cache ko cold kar deta, traffic spike
#   backend pe dega).
# - CDN ke liye: cache-control headers + versioned asset URLs
#   (jaise `app.abc123.js`, hash filename mein) — naya deploy naya
#   filename, purana cache automatically irrelevant ho jata hai, CDN
#   purge ki zaroorat hi nahi padti.


# ============================================================
# QUICK-FIRE: agar time kam ho, ye 3 concepts sabse zyada baar
# "hardest" deployment questions mein core hote hain — inhe pakka karo:
# 1. Expand-Contract pattern (DB migrations + API contracts dono ke liye)
# 2. Graceful shutdown (SIGTERM handling, readiness probe, connection draining)
# 3. Automated rollback decision-making (metrics-based, not just "wait and see")
# ============================================================
