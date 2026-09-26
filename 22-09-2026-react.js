// ============================================================
// Senior React Interview Prep — 22-09-2026
// Focus: medium-to-hard questions jo senior/lead level interviews mein
// commonly poocha jaata hai. (Continuation of 18-09-2026-react.js —
// yahan deeper/advanced topics hain: Fiber, concurrent features,
// advanced hook patterns, component design patterns, testing.)
// ============================================================


// ------------------------------------------------------------
// SECTION 1: REACT INTERNALS
// ------------------------------------------------------------

// Q1. React Fiber architecture kya hai aur ye reconciliation ko kaise
//     better banata hai purane "Stack" reconciler se?
//
// THEORY:
// Fiber React ka reconciliation engine hai (React 16+). Purana stack
// reconciler synchronous, recursive tha — ek baar tree traverse start
// hone ke baad beech mein rokh nahi sakte the (main thread block ho
// jaata tha, bade trees mein jank/dropped frames aate the).
// Fiber har component instance ke liye ek JS object ("fiber node")
// banata hai jo linked list (child/sibling/return pointers) ki tarah
// structured hai — is wajah se work ko chhote units mein todha ja
// sakta hai, pause/resume/abort kiya ja sakta hai, aur priority
// assign ki ja sakti hai (high-priority updates jaise user input,
// low-priority jaise data fetch ke baad render).
// Do phases:
// 1. Render/Reconciliation phase — interruptible, "work-in-progress"
//    tree banta hai (yahi phase concurrent features enable karta hai)
// 2. Commit phase — synchronous, DOM mein actual mutations apply hoti
//    hain (isko interrupt nahi kiya ja sakta, warna UI inconsistent
//    dikhegi)


// ------------------------------------------------------------
// Q2. useTransition aur useDeferredValue — concurrent rendering
//     features kab use karoge?
//
// THEORY:
// Dono "urgent vs non-urgent update" differentiate karne ke liye hain.
// - useTransition: state update ko low-priority mark karta hai, taaki
//   urgent updates (jaise typing) block na ho. isPending flag milta
//   hai loading indicator ke liye.
// - useDeferredValue: ek value ka "deferred" version deta hai jo peeche
//   se update hota hai — jab prop/state seedha control nahi kar sakte
//   (jaise parent se aayi value) tab useful hai.

import { useState, useTransition, useDeferredValue, useMemo } from "react";

function SearchResults({ query }) {
  const deferredQuery = useDeferredValue(query);
  // Expensive filtering deferred query pe hoti hai — typing lag-free rehti hai
  const results = useMemo(() => expensiveFilter(deferredQuery), [deferredQuery]);
  return <ResultsList items={results} />;
}

function SearchBox() {
  const [query, setQuery] = useState("");
  const [isPending, startTransition] = useTransition();

  function handleChange(e) {
    const value = e.target.value;
    setQuery(value); // urgent: input turant update ho (typing responsive)
    startTransition(() => {
      // agar heavy filtering yahin state mein hoti to isse wrap karte
    });
  }

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <span>Updating...</span>}
      <SearchResults query={query} />
    </>
  );
}

function expensiveFilter(q) { return []; /* placeholder */ }


// ------------------------------------------------------------
// Q3. React StrictMode dev mode mein components ko DOUBLE render/
//     double effect-invoke kyun karta hai?
//
// THEORY:
// StrictMode intentionally (dev-only, production mein nahi) components
// ko mount -> unmount -> remount karta hai aur effects ko double-fire
// karta hai, taaki impure/side-effect-heavy code (jo future concurrent
// features ke saath break ho sakta hai) jaldi pakda ja sake. Agar
// useEffect cleanup missing hai ya effect idempotent nahi hai (jaise
// bina guard ke API call, ya subscription without cleanup) to bugs
// turant dikh jaate hain dev mein. Fix: proper cleanup likho, effect
// ko assume karo ki wo kabhi bhi dobara chal sakta hai.


// ------------------------------------------------------------
// SECTION 2: ADVANCED HOOKS & PATTERNS
// ------------------------------------------------------------

// Q4. useState vs useReducer — kab useReducer choose karoge?
//     (Complex state logic ka example)
//
// THEORY:
// useReducer tab better hai jab:
// - next state previous state pe depend karta hai in complex ways
// - multiple sub-values ek saath update hote hain (ek action se)
// - state transitions ko centralize/test karna hai (reducer pure
//   function hai, easily unit-testable, component se decoupled)
// - deeply nested update logic ko child components mein pass karna hai
//   (dispatch function stable reference hota hai, prop-drilling simpler)

import { useReducer } from "react";

function cartReducer(state, action) {
  switch (action.type) {
    case "ADD_ITEM":
      return { ...state, items: [...state.items, action.payload], total: state.total + action.payload.price };
    case "REMOVE_ITEM": {
      const item = state.items.find((i) => i.id === action.payload);
      return { ...state, items: state.items.filter((i) => i.id !== action.payload), total: state.total - (item?.price ?? 0) };
    }
    case "CLEAR":
      return { items: [], total: 0 };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

function Cart() {
  const [state, dispatch] = useReducer(cartReducer, { items: [], total: 0 });
  return (
    <div>
      <p>Total: {state.total}</p>
      <button onClick={() => dispatch({ type: "CLEAR" })}>Clear</button>
    </div>
  );
}


// ------------------------------------------------------------
// Q5. useRef ke teen major use-cases kya hain? (DOM access ke alawa)
//
// THEORY:
// 1. DOM node reference (focus, scroll, measure)
// 2. Mutable value jo re-render trigger NAHI karta (jaise interval ID,
//    previous value track karna, render count) — useState use karte to
//    har update pe re-render hota
// 3. forwardRef + useImperativeHandle ke saath parent ko child ke
//    internal methods expose karna (imperative API design)

import { useRef, forwardRef, useImperativeHandle, useEffect } from "react";

const CustomInput = forwardRef((props, ref) => {
  const inputRef = useRef(null);
  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current.focus(),
    clear: () => { inputRef.current.value = ""; },
  }));
  return <input ref={inputRef} {...props} />;
});

function usePrevious(value) {
  const ref = useRef();
  useEffect(() => { ref.current = value; }, [value]);
  return ref.current; // is render ke pehle wali value (previous)
}


// ------------------------------------------------------------
// Q6. Custom hook likho jo debounced API call kare (data fetching +
//     race condition handling).
//
// THEORY:
// Common bug: fast typing pe multiple API calls fire hote hain, aur
// agar responses out-of-order aayein to purani (stale) response naye
// result ko overwrite kar sakti hai ("race condition"). Fix: cleanup
// mein flag/AbortController use karo taaki stale response ignore ho.

function useDebouncedSearch(query, delay = 300) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) { setResults([]); return; }
    setLoading(true);
    const controller = new AbortController();

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search?q=${query}`, { signal: controller.signal });
        const data = await res.json();
        setResults(data);
      } catch (err) {
        if (err.name !== "AbortError") console.error(err);
      } finally {
        setLoading(false);
      }
    }, delay);

    return () => {
      clearTimeout(timer);   // pending debounce cancel
      controller.abort();    // in-flight request cancel -> stale response ignore
    };
  }, [query, delay]);

  return { results, loading };
}


// ------------------------------------------------------------
// SECTION 3: COMPONENT DESIGN PATTERNS
// ------------------------------------------------------------

// Q7. Compound Components pattern kya hai? (jaise <Select><Option/></Select>)
//
// THEORY:
// Multiple components ek saath mil kar ek cohesive UI banate hain,
// implicit state Context ke through share karte hain, taaki consumer
// ko internal wiring pata na ho — flexible composition milta hai
// (JSX children ka order/structure consumer decide karta hai).

import { createContext, useContext } from "react";

const TabsContext = createContext(null);

function Tabs({ children, defaultTab }) {
  const [active, setActive] = useState(defaultTab);
  return <TabsContext.Provider value={{ active, setActive }}>{children}</TabsContext.Provider>;
}

function Tab({ id, children }) {
  const { active, setActive } = useContext(TabsContext);
  return (
    <button onClick={() => setActive(id)} style={{ fontWeight: active === id ? "bold" : "normal" }}>
      {children}
    </button>
  );
}

function TabPanel({ id, children }) {
  const { active } = useContext(TabsContext);
  return active === id ? <div>{children}</div> : null;
}

// Usage: <Tabs defaultTab="a"><Tab id="a">A</Tab><TabPanel id="a">Content</TabPanel></Tabs>


// ------------------------------------------------------------
// Q8. Render Props vs Higher-Order Components (HOC) vs Custom Hooks
//     — teeno cross-cutting logic share karte hain, farak kya hai?
//
// THEORY:
// - HOC: function jo component leke naya component return karta hai
//   (withAuth(Component)). Problem: "wrapper hell" (deeply nested
//   wrapped components), prop naming collisions.
// - Render Props: component ek function-as-child/prop leta hai jo
//   data ke saath render karta hai. Problem: nested render props se
//   JSX unreadable ho jaata hai ("callback hell" jaisa).
// - Custom Hooks: modern preferred approach — no extra component
//   wrapping, cleaner composition, easy to combine multiple hooks.
//   Limitation: sirf function components mein use ho sakte hain, aur
//   UI render nahi kar sakte (sirf logic share karte hain).


// ------------------------------------------------------------
// Q9. React.memo use karne ke baad bhi component re-render ho raha
//     hai — possible reasons?
//
// THEORY:
// React.memo shallow comparison karta hai props ka. Common gotchas:
// 1. Inline object/array/function props — har render pe naya reference
//    banta hai (===  comparison fail) -> useMemo/useCallback se stabilize karo
// 2. children prop bhi ek prop hai — agar parent JSX children pass
//    kar raha hai jo change ho rahe hain, memo useless hai
// 3. Context consumption — agar component Context consume karta hai,
//    Context value change hone pe memo bypass ho jaata hai
// 4. key prop change ho rahi hai (React poora naya instance treat karta hai)

const ExpensiveRow = React.memo(function ExpensiveRow({ data, onClick }) {
  return <div onClick={onClick}>{data.label}</div>;
});

function Parent({ items }) {
  // BAD: naya function har render pe -> memo useless
  // return items.map(i => <ExpensiveRow key={i.id} data={i} onClick={() => handle(i)} />)

  // GOOD: stable callback reference
  const handleClick = useMemo(() => (id) => console.log(id), []);
  return items.map((i) => <ExpensiveRow key={i.id} data={i} onClick={() => handleClick(i.id)} />);
}


// ------------------------------------------------------------
// SECTION 4: ERROR HANDLING, SUSPENSE, TESTING
// ------------------------------------------------------------

// Q10. Suspense for data fetching kaise kaam karta hai (conceptually)?
//
// THEORY:
// Suspense component ko "throw a promise" pattern pe based hai —
// agar data fetch karne wala resource abhi ready nahi hai, wo ek
// Promise throw karta hai; nearest Suspense boundary use catch karke
// fallback UI dikhata hai jab tak promise resolve na ho. React 18+
// mein frameworks (Next.js, Relay) ye abstraction provide karte hain.
// Combined with lazy(): code-splitting + data-fetching dono ke liye
// unified loading-state pattern milta hai.

const LazyChart = React.lazy(() => import("./Chart"));

function Dashboard() {
  return (
    <React.Suspense fallback={<div>Loading chart...</div>}>
      <LazyChart />
    </React.Suspense>
  );
}


// ------------------------------------------------------------
// Q11. Component testing (React Testing Library) mein "test
//      implementation details nahi, behavior test karo" ka matlab?
//
// THEORY:
// RTL philosophy: user jaisa interact karta hai waise hi test karo —
// getByRole/getByText/getByLabelText use karo (internal state/props
// access mat karo). Isse refactoring (internal implementation change)
// pe tests break nahi hote, sirf actual user-facing behavior break
// hone pe fail hote hain. shallow rendering (Enzyme style) is
// anti-pattern maana jaata hai kyunki wo implementation-coupled hota hai.

// import { render, screen, fireEvent } from "@testing-library/react";
// test("increments counter on click", () => {
//   render(<Counter />);
//   fireEvent.click(screen.getByRole("button", { name: /increment/i }));
//   expect(screen.getByText("Count: 1")).toBeInTheDocument();
// });


// ------------------------------------------------------------
// Q12. Portals kya hote hain aur kab use karte ho? (modals/tooltips)
//
// THEORY:
// ReactDOM.createPortal(child, domNode) — component ko React tree
// mein logically wahin rakhte hue (props/context/event bubbling normal
// rehta hai) actual DOM mein kahin aur render karta hai (jaise
// document.body). Use-case: modals/tooltips/dropdowns jinhe parent ke
// CSS overflow:hidden ya z-index stacking context se escape karna ho.

import ReactDOM from "react-dom";

function Modal({ children }) {
  return ReactDOM.createPortal(
    <div className="modal-overlay">{children}</div>,
    document.getElementById("modal-root")
  );
}
