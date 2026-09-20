// ============================================================
// Senior Node.js Interview Prep — 18-09-2026
// Interviewer profile: Mohammad Sanaullah, Technology Lead @ Infosys
// Full Stack (Python/FastAPI + React) + SRE & CI/CD background
// -> Node questions likely core concepts (event loop, async patterns,
//    streams) + kabhi-kabhi Python ke concepts se compare karne ko bolenge
//    (jaise "Node event loop vs Python asyncio event loop").
// ============================================================


// ------------------------------------------------------------
// SECTION 1: EVENT LOOP & ASYNC MODEL
// ------------------------------------------------------------

// Q1. Node.js event loop kaise kaam karta hai? Phases kya hain?
//
// THEORY:
// Node single-threaded JS execution hai, but libuv (C++ library) ke
// through background mein thread pool + OS async I/O use karta hai.
// Event loop ke phases (order mein):
// 1. Timers: setTimeout/setInterval callbacks jinka time pura ho gaya
// 2. Pending callbacks: kuch system-level callbacks (TCP errors, etc.)
// 3. Poll: naye I/O events fetch karta hai, I/O callbacks execute karta
//    (file read, network response) — agar kuch nahi to yahan wait karta
// 4. Check: setImmediate() callbacks yahan chalte hain
// 5. Close callbacks: socket.on('close') jaise cleanup callbacks
// Har phase ke beech microtask queue (Promise.then, process.nextTick)
// pura drain hoti hai — process.nextTick sabse high priority hai,
// Promise microtasks uske baad.

console.log("1 - sync");

setTimeout(() => console.log("2 - setTimeout (macrotask)"), 0);

Promise.resolve().then(() => console.log("3 - Promise (microtask)"));

process.nextTick(() => console.log("4 - nextTick (highest priority microtask)"));

console.log("5 - sync");

// Output order: 1, 5, 4, 3, 2
// (sync code -> nextTick -> promise microtasks -> macrotasks/timers)


// ------------------------------------------------------------
// Q2. Callback -> Promise -> async/await evolution, aur common gotchas?
//
// THEORY:
// - Callback hell: nested callbacks se unreadable/hard-to-maintain code.
// - Promises: .then chaining se flat structure, error handling .catch se.
// - async/await: Promise ke upar syntactic sugar, synchronous-looking
//   code, try/catch se error handling.
// GOTCHA 1: async function ke andar agar await ka error try/catch mein
// nahi wrap kiya to unhandled promise rejection -> process crash ho
// sakta hai (Node newer versions mein by default).
// GOTCHA 2: forEach ke andar await kaam nahi karta jaisa expect karte
// ho — forEach async callbacks ko await nahi karta, sab parallel-ish
// fire ho jate hain bina order guarantee ke. for...of use karo sequential
// ke liye, ya Promise.all with map() parallel ke liye.

async function fetchUser(id) {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`failed: ${res.status}`);
  return res.json();
}

// WRONG: forEach await ko respect nahi karta
async function badSequential(ids) {
  ids.forEach(async (id) => {
    const user = await fetchUser(id);   // ye "fire and forget" ho jata
    console.log(user);
  });
  console.log("done");   // ye pehle print ho jayega, users ke fetch hone se pehle
}

// RIGHT: sequential
async function sequentialFetch(ids) {
  const results = [];
  for (const id of ids) {
    results.push(await fetchUser(id));   // ek ek karke, order guaranteed
  }
  return results;
}

// RIGHT: parallel (jab order matter nahi karta, sabko concurrently chalana hai)
async function parallelFetch(ids) {
  return Promise.all(ids.map((id) => fetchUser(id)));
}


// ------------------------------------------------------------
// Q3. Node "single-threaded" hai to CPU-bound heavy task kaise handle
// karoge bina event loop block kiye?
//
// THEORY:
// - worker_threads module: actual OS thread mein heavy computation
//   chalao, main thread free rehta hai requests handle karne ke liye.
// - cluster module: multiple Node processes (per CPU core) spawn karo,
//   load balance requests across them — horizontal scaling within
//   single machine, har worker ka apna event loop/memory hota hai.
// - Child processes ya external queue (jaise Python Celery pattern)
//   bhi heavy/long tasks ke liye use hota hai.

const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

function runHeavyTaskInWorker(n) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(__filename, { workerData: n });
    worker.on("message", resolve);
    worker.on("error", reject);
  });
}

if (!isMainThread) {
  const n = workerData;
  let sum = 0;
  for (let i = 0; i < n; i++) sum += i * i;   // heavy CPU work, main thread block nahi hota
  parentPort.postMessage(sum);
}


// ------------------------------------------------------------
// SECTION 2: STREAMS (backend + document generator context ke liye relevant)
// ------------------------------------------------------------

// Q4. Streams kya hain aur backpressure kya hota hai?
//
// THEORY:
// Streams se data chunks mein process hota hai (poori file/response
// memory mein load kiye bina) — large files, HTTP responses, PDF
// generation jaisi cheezon ke liye memory-efficient. 4 types: Readable,
// Writable, Duplex, Transform.
// Backpressure: jab writable stream data consume karne mein slow ho
// readable se, to write() false return karta hai — producer ko rukna
// chahiye 'drain' event tak, warna memory mein buffer grow karta
// rahega (unbounded memory growth risk).

const fs = require("fs");

function copyLargeFile(src, dest) {
  const readStream = fs.createReadStream(src);
  const writeStream = fs.createWriteStream(dest);

  readStream.on("data", (chunk) => {
    const canContinue = writeStream.write(chunk);
    if (!canContinue) {
      readStream.pause();   // backpressure: producer ko rok do
      writeStream.once("drain", () => readStream.resume());
    }
  });

  readStream.on("end", () => writeStream.end());
}

// Modern/cleaner way: pipe() ya pipeline() (backpressure + errors auto-handle)
const { pipeline } = require("stream");

pipeline(
  fs.createReadStream("input.pdf"),
  fs.createWriteStream("output.pdf"),
  (err) => {
    if (err) console.error("pipeline failed:", err);
    else console.log("done");
  }
);


// ------------------------------------------------------------
// SECTION 3: EXPRESS / API PATTERNS
// ------------------------------------------------------------

// Q5. Express middleware pattern kaise kaam karta hai?
//
// THEORY:
// Middleware (req, res, next) => {} signature wala function hai jo
// request/response cycle ke beech chalta hai. next() call karne se
// control agle middleware/route handler ko jata hai — na call karo to
// request hang ho jayegi. Order matter karta hai (jaise auth middleware
// route handler se pehle lagana zaroori hai).

const express = require("express");
const app = express();

function loggingMiddleware(req, res, next) {
  const start = Date.now();
  res.on("finish", () => {
    console.log(`${req.method} ${req.path} - ${Date.now() - start}ms`);
  });
  next();   // agle middleware/handler ko control do
}

function authMiddleware(req, res, next) {
  const token = req.headers.authorization;
  if (!token) return res.status(401).json({ error: "unauthorized" });
  next();
}

app.use(loggingMiddleware);
app.get("/api/dashboard", authMiddleware, (req, res) => {
  res.json({ status: "ok" });
});

// Centralized error-handling middleware (4 args signature Express ke liye special)
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "internal server error" });
});


// Q6. EventEmitter pattern — Node ka pub/sub kaise kaam karta hai?
//
// THEORY:
// EventEmitter Node ke core mein event-driven architecture ka base
// hai (HTTP server, streams, sab isi pe based hain). .on() se listener
// register hota hai, .emit() se event trigger hota hai. Isse decoupled,
// pub/sub jaisa design ban sakta hai internal application events ke liye
// (jaise "alert.triggered" event pe multiple independent handlers react karein).

const EventEmitter = require("events");

class IncidentBus extends EventEmitter {}
const incidentBus = new IncidentBus();

incidentBus.on("incident:created", (incident) => {
  console.log("send Slack alert for", incident.id);
});

incidentBus.on("incident:created", (incident) => {
  console.log("log to CloudWatch:", incident.id);
});

incidentBus.emit("incident:created", { id: "INC-123", severity: "high" });


// ------------------------------------------------------------
// SECTION 4: MEMORY, ERRORS, PRODUCTION CONCERNS (SRE-relevant)
// ------------------------------------------------------------

// Q7. Node app mein memory leak kaise identify/debug karoge?
//
// THEORY:
// Common causes: global variables mein data accumulate hona, event
// listeners jo remove nahi hue, closures jo unnecessary references
// hold karte hain, unbounded caches. Debug tools: --inspect flag se
// Chrome DevTools heap snapshot compare karo (do snapshots lo, diff
// dekho kaunsa object type grow ho raha hai), process.memoryUsage()
// se heapUsed monitor karo production mein (CloudWatch custom metric
// jaisa Python file ke Q13 mein tha).

function checkMemoryUsage() {
  const usage = process.memoryUsage();
  console.log({
    heapUsedMB: (usage.heapUsed / 1024 / 1024).toFixed(2),
    rssMB: (usage.rss / 1024 / 1024).toFixed(2),
  });
}

// Q8. Unhandled promise rejection / uncaught exception — production
// mein kaise handle karte ho?
//
// THEORY:
// In events ko globally listen karke log/alert bhejna chahiye (SRE
// ke liye important — silent crashes ya zombie processes na rahein).
// Process ko crash hone dena hi better hai (graceful shutdown) instead
// of continuing in a corrupted state — process manager (PM2, k8s)
// automatically restart kar dega.

process.on("unhandledRejection", (reason) => {
  console.error("Unhandled Rejection:", reason);
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught Exception:", err);
  process.exit(1);   // graceful restart ke liye process manager pe chhodo
});


// ------------------------------------------------------------
// SECTION 5: NODE vs PYTHON (comparison — likely aa sakta hai kyunki
// interviewer dono stacks use karta hai)
// ------------------------------------------------------------

// Q9. Node event loop vs Python asyncio event loop — similarity/farak?
//
// THEORY:
// Dono single-threaded, cooperative concurrency models hain, non-blocking
// I/O ke liye best. Farak:
// - Node: event loop language runtime mein built-in hai, sab kuch by
//   default async-friendly hai (callbacks/promises everywhere), libuv
//   background thread pool file I/O jaise blocking OS calls ke liye use karta.
// - Python: asyncio explicit hai — async def/await likhna padta hai,
//   normal sync code (jaise requests library) by default event loop
//   ko block karega agar async-aware nahi hai. FastAPI mein sync def
//   endpoints automatically threadpool mein chalte hain (Node mein
//   aisa automatic fallback nahi hai).
// - CPU-bound: Node worker_threads, Python multiprocessing — dono
//   concept similar (true parallelism ke liye separate thread/process).


// ------------------------------------------------------------
// SECTION 6: LIKELY BEHAVIORAL/PROJECT QUESTIONS (theory only)
// ------------------------------------------------------------
// - "Production mein Node app slow/hang ho gaya tha, kaise debug kiya?"
//    (event loop block check -> blocking sync code dhoondo, CPU profile lo)
// - "Kabhi memory leak trace ki production Node service mein?"
// - "Node vs Python — kis decision criteria pe choose karoge naye service ke liye?"
