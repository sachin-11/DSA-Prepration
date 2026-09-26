// ============================================================
// Senior Node.js Interview Prep — 22-09-2026
// Focus: medium-to-hard questions jo senior/lead level interviews mein
// commonly poocha jaata hai. (Continuation of 18-09-2026-node.js —
// yahan deeper/advanced topics hain: streams, cluster/worker_threads,
// scaling, security, memory management.)
// ============================================================


// ------------------------------------------------------------
// SECTION 1: STREAMS & BACKPRESSURE
// ------------------------------------------------------------

// Q1. Node Streams (Readable/Writable/Duplex/Transform) kyun use
//     karte hain, aur "backpressure" kya hai?
//
// THEORY:
// Streams chunks mein data process karte hain instead of pura file/
// response memory mein load karne ke — large files (video, logs, DB
// exports) handle karne ke liye memory-efficient hai.
// - Readable: source se data padhta hai (fs.createReadStream)
// - Writable: destination mein data likhta hai (fs.createWriteStream)
// - Duplex: dono (jaise TCP socket)
// - Transform: Duplex jo data ko modify bhi karta hai (jaise gzip)
//
// Backpressure: agar writable stream, readable se slower hai (consumer
// slow hai), buffer mein data accumulate hoke memory spike ho sakta
// hai. write() false return karta hai jab internal buffer full ho —
// tab tak pause karo jab tak 'drain' event na aaye. .pipe() ye sab
// automatically handle karta hai.

const fs = require("fs");
const zlib = require("zlib");

// GOOD: streaming pipe, backpressure auto-handled, constant memory usage
fs.createReadStream("large-file.txt")
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream("large-file.txt.gz"))
  .on("finish", () => console.log("done"))
  .on("error", (err) => console.error(err));

// Manual backpressure handling example:
function writeMillionLines(writable) {
  let i = 0;
  function write() {
    let ok = true;
    while (i < 1_000_000 && ok) {
      ok = writable.write(`line ${i}\n`);
      i++;
    }
    if (i < 1_000_000) {
      writable.once("drain", write); // buffer khali hone ka wait karo
    }
  }
  write();
}


// ------------------------------------------------------------
// SECTION 2: SCALING — CLUSTER, WORKER THREADS, CHILD PROCESS
// ------------------------------------------------------------

// Q2. cluster module vs worker_threads vs child_process — kab kaunsa
//     use karoge?
//
// THEORY:
// Node single-threaded event loop hai — CPU cores fully use karne ke
// liye multi-process/multi-thread strategy chahiye.
// - cluster: multiple Node PROCESSES fork karta hai (har ek apna event
//   loop + memory), master process incoming connections load-balance
//   karta hai (round-robin). Use-case: HTTP servers ko multi-core pe
//   scale karna. Processes memory share NAHI karte (IPC se communicate).
// - worker_threads: same process ke andar multiple THREADS, SharedArrayBuffer
//   se memory share kar sakte hain. Use-case: CPU-intensive sync work
//   (image processing, heavy computation) jo event loop block na kare.
// - child_process (spawn/exec/fork): alag process spawn karta hai,
//   kabhi kisi external command/script run karne ke liye (jaise
//   ffmpeg, python script), ya fork() se Node script alag process mein.

const cluster = require("cluster");
const os = require("os");

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) cluster.fork();
  cluster.on("exit", (worker) => {
    console.log(`Worker ${worker.process.pid} died, restarting...`);
    cluster.fork(); // resilience: crashed worker ko replace karo
  });
} else {
  // http.createServer(...).listen(3000) — har worker isko run karta hai
}

const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

function runCPUHeavyTask(data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(__filename, { workerData: data });
    worker.on("message", resolve);
    worker.on("error", reject);
  });
}

if (!isMainThread) {
  // heavy sync computation yahan event loop block kiye bina chal sakta hai
  const result = workerData * 2; // placeholder heavy work
  parentPort.postMessage(result);
}


// ------------------------------------------------------------
// SECTION 3: ERROR HANDLING & PROCESS RESILIENCE
// ------------------------------------------------------------

// Q3. Operational errors vs Programmer errors — production mein kaise
//     handle karte ho? uncaughtException/unhandledRejection ka role?
//
// THEORY:
// - Operational errors: expected runtime failures (DB down, invalid
//   input, network timeout) — inhe gracefully handle karo (try/catch,
//   error middleware), app crash nahi karni chahiye.
// - Programmer errors: bugs (undefined is not a function, type errors)
//   — ye unpredictable state create kar sakte hain, best practice hai
//   process ko crash hone do (process manager jaise PM2/k8s restart
//   karega) instead of "band-aid" recovery karna.
// uncaughtException/unhandledRejection sirf LAST RESORT logging ke
// liye use karo, phir process.exit() — inme se recover karke continue
// karna risky hai (app ka state corrupt ho sakta hai).

process.on("unhandledRejection", (reason) => {
  console.error("Unhandled Rejection:", reason);
  process.exit(1); // fail-fast, process manager restart karega
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught Exception:", err);
  process.exit(1);
});

// Express error-handling middleware (operational errors ke liye) — 4 params
// distinguishes it from normal middleware
function errorHandler(err, req, res, next) {
  const status = err.isOperational ? err.statusCode || 400 : 500;
  res.status(status).json({ message: err.isOperational ? err.message : "Internal Server Error" });
  if (!err.isOperational) console.error(err); // log unexpected errors fully
}


// ------------------------------------------------------------
// SECTION 4: MEMORY MANAGEMENT
// ------------------------------------------------------------

// Q4. Node app mein memory leak kaise detect/debug karte ho? Common
//     memory leak patterns kya hain?
//
// THEORY:
// Common leak sources:
// 1. Global variables mein unbounded array/object growth (cache jo
//    kabhi clear nahi hota)
// 2. Event listeners jo remove nahi hote (EventEmitter par baar-baar
//    .on() call karna without .off())
// 3. Closures jo bade objects ko unnecessarily reference karte rehte hain
// 4. Timers (setInterval) jo clear nahi hote
// Debugging: --inspect flag se Chrome DevTools attach karo, heap
// snapshots lo (do alag time points pe) aur compare karo growth ke
// liye. clinic.js / heapdump / node --prof jaise tools bhi use hote hain.

const emitter = new (require("events").EventEmitter)();

function subscribeToUpdates(handler) {
  emitter.on("update", handler);
  return () => emitter.off("update", handler); // cleanup function return karo
}

// BAD: unbounded cache -> memory leak
const cache = {};
function badCacheSet(key, value) { cache[key] = value; } // kabhi evict nahi hota

// GOOD: LRU-style bounded cache (using Map insertion order)
class LRUCache {
  constructor(limit = 100) { this.limit = limit; this.map = new Map(); }
  get(key) {
    if (!this.map.has(key)) return undefined;
    const val = this.map.get(key);
    this.map.delete(key); this.map.set(key, val); // move to most-recent
    return val;
  }
  set(key, value) {
    if (this.map.has(key)) this.map.delete(key);
    else if (this.map.size >= this.limit) this.map.delete(this.map.keys().next().value); // evict oldest
    this.map.set(key, value);
  }
}


// ------------------------------------------------------------
// SECTION 5: SECURITY
// ------------------------------------------------------------

// Q5. Express/Node API mein common security vulnerabilities aur unke
//     fixes? (senior interviews mein bohot poocha jaata hai)
//
// THEORY:
// 1. NoSQL/SQL Injection: user input directly query mein concatenate
//    karna -> parameterized queries/ORM use karo, never string-concat SQL
// 2. XSS: user input bina sanitize kiye render karna -> output encode
//    karo, Content-Security-Policy headers set karo
// 3. Missing rate limiting -> brute-force/DoS pe vulnerable ->
//    express-rate-limit jaise middleware
// 4. Sensitive data in JWT payload / weak JWT secret / no expiry ->
//    short-lived access tokens + refresh token rotation
// 5. Missing helmet() headers (X-Frame-Options, HSTS, etc.)
// 6. CORS misconfiguration (Access-Control-Allow-Origin: *) with
//    credentials -> specific origins whitelist karo
// 7. Prototype pollution: JSON.parse(userInput) ke through __proto__
//    inject karke Object.prototype pollute karna -> input validate karo,
//    Object.create(null) use karo jahan zaroori ho

const helmet = require("helmet");
const rateLimit = require("express-rate-limit");

// app.use(helmet());
// app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// JWT best practice example
const jwt = require("jsonwebtoken");

function issueTokens(user) {
  const accessToken = jwt.sign({ sub: user.id, role: user.role }, process.env.JWT_SECRET, { expiresIn: "15m" });
  const refreshToken = jwt.sign({ sub: user.id }, process.env.JWT_REFRESH_SECRET, { expiresIn: "7d" });
  return { accessToken, refreshToken };
}


// ------------------------------------------------------------
// SECTION 6: DATABASE PATTERNS
// ------------------------------------------------------------

// Q6. Connection pooling zaroori kyun hai? Transaction kaise handle
//     karte ho jab multiple async operations ek saath commit/rollback
//     karni ho?
//
// THEORY:
// Har DB query ke liye naya connection create karna expensive hai
// (TCP handshake, auth). Connection pool ek set of reusable connections
// maintain karta hai — requests unhe borrow/return karte hain. Pool
// size zyada important hai high-concurrency apps mein (bohot chhota
// -> requests queue mein wait karte hain; bohot bada -> DB overwhelm).
//
// Transactions: multiple writes ko atomic banane ke liye (all-or-nothing)
// — jaise money transfer (debit + credit dono succeed ya dono fail).

// pg (PostgreSQL) example:
// const { Pool } = require("pg");
// const pool = new Pool({ max: 20, idleTimeoutMillis: 30000 });
//
// async function transferMoney(fromId, toId, amount) {
//   const client = await pool.connect();
//   try {
//     await client.query("BEGIN");
//     await client.query("UPDATE accounts SET balance = balance - $1 WHERE id = $2", [amount, fromId]);
//     await client.query("UPDATE accounts SET balance = balance + $1 WHERE id = $2", [amount, toId]);
//     await client.query("COMMIT");
//   } catch (err) {
//     await client.query("ROLLBACK"); // koi bhi step fail ho to dono revert
//     throw err;
//   } finally {
//     client.release(); // connection pool mein wapas karo, hamesha (success/fail dono)
//   }
// }


// ------------------------------------------------------------
// SECTION 7: MODULE SYSTEM
// ------------------------------------------------------------

// Q7. CommonJS vs ES Modules (ESM) — key differences? Dono ek project
//     mein saath kaise use karte ho?
//
// THEORY:
// - CommonJS (require/module.exports): synchronous load, runtime
//   resolution, "this" module-scoped, dynamic require() (conditional
//   bhi ho sakta hai), circular dependency mein partial exports milta hai.
// - ESM (import/export): asynchronous load, static analysis possible
//   (isliye tree-shaking/dead-code-elimination ho sakta hai bundlers
//   mein), imports hoisted, strict mode default, top-level await support.
// Interop: "type": "module" in package.json se ESM default hota hai;
// .cjs/.mjs extensions se explicitly specify kar sakte ho. CommonJS
// module ko ESM mein import kiya ja sakta hai, but ESM ko CommonJS
// require() se directly import nahi kar sakte (dynamic import() use
// karna padta hai kyunki ESM load asynchronous hai).


// ------------------------------------------------------------
// SECTION 8: SYSTEM DESIGN-ISH
// ------------------------------------------------------------

// Q8. High-traffic Node API ko horizontally scale karte waqt kin
//     cheezon ka khayal rakhoge? (stateless design, session handling)
//
// THEORY:
// - App ko STATELESS rakho — in-memory session/cache use mat karo
//   (jaise express-session with MemoryStore), kyunki multiple instances
//   ke beech load balancer round-robin karega aur session data mismatch
//   hoga. Redis jaisa shared/external store use karo sessions/cache ke liye.
// - Sticky sessions se bacho jahan possible ho (scaling limit karta hai).
// - Health check endpoint (/health) expose karo load balancer/k8s ke liye.
// - Graceful shutdown: SIGTERM pe naye requests accept karna band karo,
//   in-flight requests complete hone do, phir exit (zero-downtime deploys).

process.on("SIGTERM", () => {
  console.log("SIGTERM received, closing server gracefully...");
  // server.close(() => process.exit(0));
  // + DB pool.end(), open connections cleanup
});
