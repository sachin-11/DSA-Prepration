// ============================================================
// Senior React Interview Prep — 18-09-2026
// Interviewer profile: Mohammad Sanaullah, Technology Lead @ Infosys
// Full Stack (Python/FastAPI backend + React frontend), SRE Dashboard project
// -> React questions likely dashboard-context mein honge: real-time data,
//    performance (large lists/charts), re-render optimization.
// ============================================================


// ------------------------------------------------------------
// SECTION 1: CORE REACT CONCEPTS
// ------------------------------------------------------------

// Q1. Virtual DOM aur reconciliation kaise kaam karta hai?
//
// THEORY:
// React state change hone pe pura naya Virtual DOM tree (JS object)
// banata hai, phir use purane Virtual DOM tree se "diff" karta hai
// (reconciliation algorithm). Jo actual changes hain sirf wahi real
// DOM mein apply hote hain (real DOM manipulation expensive hai,
// isliye minimize karna important hai). Same-level siblings compare
// karte waqt "key" prop se React batata hai kaunsa element same hai
// vs naya/removed — bina key ke React index se match karta hai jo
// list reorder hone pe bugs/extra re-renders create karta hai.

function BadList({ items }) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item.name}</li>  // BAD: index as key, reorder pe bug
      ))}
    </ul>
  );
}

function GoodList({ items }) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{item.name}</li>  // GOOD: stable unique id
      ))}
    </ul>
  );
}


// ------------------------------------------------------------
// Q2. useEffect dependency array — common gotchas?
//
// THEORY:
// - [] (empty array): effect sirf mount pe ek baar chalta hai.
// - koi dependency array nahi: effect HAR render ke baad chalta hai.
// - [dep1, dep2]: sirf tab chalta hai jab in values mein se koi change ho.
// Stale closure gotcha: effect ke andar jo function/state use ho raha
// hai, agar wo dependency array mein missing hai to effect purani
// (stale) value use karega, kyunki closure creation ke time ki value
// capture ho gayi thi.
// Cleanup function (return () => {...}) zaroori hai jab subscription/
// interval/event listener/websocket setup kiya ho — warna memory leak.

import { useEffect, useState } from "react";

function LiveMetrics({ serviceId }) {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(`wss://dashboard/ws/${serviceId}`);
    ws.onmessage = (event) => setMetrics(JSON.parse(event.data));

    return () => {
      ws.close();   // cleanup -> component unmount ya serviceId change pe
    };
  }, [serviceId]);   // serviceId change hote hi purana socket band, naya khulega

  return <div>{metrics ? metrics.latency : "loading..."}</div>;
}


// ------------------------------------------------------------
// Q3. useMemo vs useCallback — kab use karoge?
//
// THEORY:
// - useMemo: kisi expensive COMPUTATION ka result memoize karta hai,
//   sirf tab recompute hoga jab dependencies change hon.
// - useCallback: kisi FUNCTION reference ko memoize karta hai (taaki
//   child component ko wahi function reference mile, unnecessary
//   re-render na ho agar child React.memo se wrapped hai).
// Overuse mat karo — har cheez ko memoize karna khud ek overhead hai;
// sirf tab use karo jab profiling se pata chale ki re-render/recompute
// expensive hai.

import { useMemo, useCallback, useState } from "react";

function Dashboard({ rawMetrics }) {
  const [filter, setFilter] = useState("");

  // expensive aggregation sirf tab recompute ho jab rawMetrics/filter badle
  const filteredMetrics = useMemo(
    () => rawMetrics.filter((m) => m.service.includes(filter)),
    [rawMetrics, filter]
  );

  // child component ko stable function reference dene ke liye
  const handleRefresh = useCallback(() => {
    console.log("refreshing metrics...");
  }, []);

  return <MetricsChart data={filteredMetrics} onRefresh={handleRefresh} />;
}

const MetricsChart = React.memo(function MetricsChart({ data, onRefresh }) {
  // React.memo: props same rehne pe re-render skip -> onRefresh reference
  // stable na ho (useCallback ke bina) to ye memo bekaar ho jata
  return <div>{data.length} points</div>;
});


// ------------------------------------------------------------
// Q4. Custom hooks kaise banate/design karte ho?
//
// THEORY:
// Custom hook ek plain JS function hai jo "use" se start hota hai aur
// andar built-in hooks (useState/useEffect) use karta hai — logic
// reuse karne ka tarika hai bina component hierarchy complicate kiye
// (HOC/render-props ke comparison mein cleaner hota hai).

function usePolling(url, intervalMs) {
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      const res = await fetch(url);
      const json = await res.json();
      if (!cancelled) setData(json);
    }

    fetchData();
    const id = setInterval(fetchData, intervalMs);

    return () => {
      cancelled = true;   // race condition guard -> unmounted component pe setState nahi
      clearInterval(id);
    };
  }, [url, intervalMs]);

  return data;
}

function ServiceHealthWidget() {
  const health = usePolling("/api/health", 5000);
  return <div>{health ? health.status : "loading..."}</div>;
}


// ------------------------------------------------------------
// Q5. Controlled vs Uncontrolled components?
//
// THEORY:
// - Controlled: input ki value React state se driven hoti hai (value +
//   onChange) — single source of truth React state hai, predictable,
//   validation/formatting easy hai.
// - Uncontrolled: DOM khud apna state maintain karta hai, React ref
//   se value read karta hai jab zaroorat ho (form submit pe). Simple
//   forms/file inputs ke liye kabhi useful hai, but less React-idiomatic.

function ControlledInput() {
  const [value, setValue] = useState("");
  return <input value={value} onChange={(e) => setValue(e.target.value)} />;
}


// ------------------------------------------------------------
// SECTION 2: PERFORMANCE (dashboard-heavy context ke liye important)
// ------------------------------------------------------------

// Q6. Large list render karni ho (jaise dashboard mein 1000s of log rows)
// — performance kaise optimize karoge?
//
// THEORY:
// - Virtualization/windowing (react-window, react-virtualized): sirf
//   visible rows DOM mein render karo, baaki skip — DOM node count
//   drastically kam ho jata hai.
// - Pagination/infinite scroll: backend se chunks mein data lao.
// - React.memo + stable keys se unnecessary re-renders avoid karo.
// - Debounce/throttle high-frequency updates (jaise real-time metrics
//   stream) taaki UI har millisecond re-render na ho.

function useDebouncedValue(value, delayMs) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);   // purana timer cancel agar value fir badal gayi
  }, [value, delayMs]);

  return debounced;
}


// Q7. Code splitting / lazy loading kaise karte ho?
//
// THEORY:
// React.lazy() + Suspense se component ka JS bundle sirf tab load
// hota hai jab actually use ho raha ho — initial page load fast hota
// hai. Route-based splitting most common pattern hai (har page ka
// alag chunk).

import React, { Suspense, lazy } from "react";

const AnalyticsPage = lazy(() => import("./AnalyticsPage"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AnalyticsPage />
    </Suspense>
  );
}


// ------------------------------------------------------------
// SECTION 3: STATE MANAGEMENT & ARCHITECTURE
// ------------------------------------------------------------

// Q8. Context API vs Redux/Zustand — kab kaunsa?
//
// THEORY:
// - Context API: simple global state (theme, auth user, feature flags)
//   ke liye theek hai. GOTCHA: Context value change hote hi saare
//   consumers re-render hote hain, chahe unhe specific field na chahiye
//   ho — high-frequency updates (real-time metrics) ke liye Context
//   directly use karna performance issue de sakta hai.
// - Redux/Zustand/Recoil: complex state, frequent updates, ya jab
//   selective re-rendering chahiye (selectors se sirf relevant
//   component re-render ho) — dashboard jaisi app jahan multiple
//   independent widgets real-time data consume karte hain, wahan
//   ye better fit hai.

// Q9. Error Boundaries kya hote hain?
//
// THEORY:
// Class component jo componentDidCatch/getDerivedStateFromError
// implement karta hai — render tree ke kisi child mein JS error aane
// pe pura app crash hone se bachata hai, fallback UI dikhata hai.
// Hooks se error boundary nahi bana sakte (as of stable React) —
// class component hi chahiye, ya library (react-error-boundary) use karo.

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("Dashboard widget crashed:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong in this widget.</div>;
    }
    return this.props.children;
  }
}


// ------------------------------------------------------------
// SECTION 4: FULL-STACK / SRE-DASHBOARD SPECIFIC
// ------------------------------------------------------------

// Q10. FastAPI backend se React frontend real-time data kaise consume
// karega (WebSocket integration)?
//
// THEORY:
// Backend WebSocket endpoint metrics push karta hai (dekho python
// file ka Q23 system design section). Frontend mein reconnect logic
// zaroori hai — network drop pe socket automatically reconnect kare,
// warna dashboard "stuck" dikhega bina koi error ke.

function useWebSocketMetrics(url) {
  const [data, setData] = useState(null);

  useEffect(() => {
    let ws;
    let reconnectTimer;

    function connect() {
      ws = new WebSocket(url);
      ws.onmessage = (e) => setData(JSON.parse(e.data));
      ws.onclose = () => {
        reconnectTimer = setTimeout(connect, 3000);   // auto-reconnect
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      ws?.close();
    };
  }, [url]);

  return data;
}


// Q11. Server-Side Rendering (SSR) vs Client-Side Rendering (CSR) vs
// Static Site Generation (SSG)?
//
// THEORY:
// - CSR (plain React/Vite/CRA): browser blank HTML+JS download karta
//   hai, JS run hone ke baad content dikhta hai — SEO/first-paint
//   slower, but interactive app ke liye fine (internal dashboards
//   jahan SEO matter nahi karta).
// - SSR (Next.js): server pe HTML render hoke bheja jata hai, faster
//   first paint + SEO, but server load zyada.
// - SSG: build time pe hi HTML generate ho jata hai (blogs/docs jaise
//   content ke liye), fastest but dynamic data ke liye unsuitable.
// -> Internal SRE dashboard ke liye CSR (ya SSR with client-heavy
//    real-time updates) most likely choice hai, SEO priority nahi hoti.


// ------------------------------------------------------------
// SECTION 5: LIKELY BEHAVIORAL/PROJECT QUESTIONS (theory only)
// ------------------------------------------------------------
// - "Dashboard mein real-time updates ki wajah se UI lag kar raha tha,
//    kaise debug/fix kiya?" (throttle/debounce, virtualization, memoization)
// - "Kabhi koi memory leak React app mein trace ki?" (missing cleanup
//    in useEffect — event listeners, intervals, websockets)
// - "State management library kyun choose ki apne project mein?"
