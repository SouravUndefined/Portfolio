# Frontend Zero to Hero
### Learn modern web development through your own portfolio

---

> **How to use this book**
>
> Every example in every chapter is pulled directly from this codebase.
> When you read about a concept, you can open the actual file and see it working.
> The book grows with the project — every new component gets its own chapter section.
>
> You do not need prior frontend experience. You do need patience and curiosity.

---

## Table of Contents

**Part I — The Foundation**
- [Chapter 1: How a Web Page Actually Works](#chapter-1-how-a-web-page-actually-works)
- [Chapter 2: The Tools We Use and Why](#chapter-2-the-tools-we-use-and-why)
- [Chapter 3: A Map of the Codebase](#chapter-3-a-map-of-the-codebase)

**Part II — The Language**
- [Chapter 4: JavaScript You Need to Know](#chapter-4-javascript-you-need-to-know)
- [Chapter 5: JSX — HTML Inside JavaScript](#chapter-5-jsx--html-inside-javascript)

**Part III — React**
- [Chapter 6: Components — The Building Block](#chapter-6-components--the-building-block)
- [Chapter 7: Props — Talking Between Components](#chapter-7-props--talking-between-components)
- [Chapter 8: State — Giving Your UI Memory](#chapter-8-state--giving-your-ui-memory)
- [Chapter 9: Hooks — React's Superpowers](#chapter-9-hooks--reacts-superpowers)

**Part IV — Styling**
- [Chapter 10: How CSS Works in 5 Minutes](#chapter-10-how-css-works-in-5-minutes)
- [Chapter 11: Tailwind CSS — Styling at Speed](#chapter-11-tailwind-css--styling-at-speed)
- [Chapter 12: Our Design System](#chapter-12-our-design-system)

**Part V — The Real Codebase**
- [Chapter 13: App.jsx — How Everything Connects](#chapter-13-appjsx--how-everything-connects)
- [Chapter 14: Nav.jsx — Scroll-Aware Navigation](#chapter-14-navjsx--scroll-aware-navigation)
- [Chapter 15: Hero.jsx — The First Impression](#chapter-15-herojsx--the-first-impression)
- [Chapter 16: About.jsx — Layout and Images](#chapter-16-aboutjsx--layout-and-images)
- [Chapter 17: Tools.jsx — Data-Driven UI](#chapter-17-toolsjsx--data-driven-ui)
- [Chapter 18: SpendingTool.jsx — A Real Form with API](#chapter-18-spendingtool-jsx--a-real-form-with-api)
- [Chapter 19: ConsentModal.jsx — Privacy Gate Before Upload](#chapter-19-consentmodaljsx--privacy-gate-before-upload)
- [Chapter 20: Gallery.jsx — Photos and Hover Effects](#chapter-20-galleryjsx--photos-and-hover-effects)
- [Chapter 21: Footer.jsx — Links and Contact](#chapter-21-footerjsx--links-and-contact)

**Part VI — Building New Things**
- [Chapter 22: Adding a New Section](#chapter-22-adding-a-new-section)
- [Chapter 23: Patterns Reference Card](#chapter-23-patterns-reference-card)

**Appendix**
- [Glossary](#glossary)

---

# Part I — The Foundation

---

## Chapter 1: How a Web Page Actually Works

**What you'll understand after this chapter:**
A browser is just a program that reads three types of files. Every website — from Google to your portfolio — is made of exactly these three things.

---

### The three files a browser understands

| File | What it controls | Analogy |
|------|-----------------|---------|
| **HTML** | Structure — what's on the page | The skeleton |
| **CSS** | Appearance — how it looks | Skin and clothes |
| **JavaScript** | Behaviour — what happens when you interact | The brain and muscles |

When you type a URL, the browser fetches these files and paints a page. That's all a website is.

---

### The old way vs the new way

**Old way (2010s):** Server builds the HTML page, sends it complete to the browser. Every click that needed new data required a full page reload.

**New way (what we use):** The browser downloads a tiny HTML file and a JavaScript bundle. JavaScript builds the entire page in the browser, handles navigation, and fetches data without reloading. This is called a **Single Page Application (SPA)**.

Your portfolio is an SPA. There is one HTML file (`index.html`). Everything else is JavaScript that React turns into HTML on your screen.

Open `frontend/index.html` and you'll see almost nothing:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Sourav Mondal</title>
  </head>
  <body>
    <div id="root"></div>          <!-- React fills this in -->
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

That `<div id="root">` is empty. React takes it and builds the entire page inside it.

---

### What happens when you open souravspace.com

1. Browser requests the page from the server
2. Server sends `index.html` (practically empty)
3. Browser sees `<script src="/src/main.jsx">` and requests that file
4. Vite has compiled all your JSX into a single optimised JS bundle
5. That bundle runs, React takes over, and fills `#root` with your entire site
6. All of this happens in under a second

---

### Key takeaway

You're not writing HTML files. You're writing JavaScript (React) that *creates* HTML. That shift in thinking is the most important thing to understand before going further.

---

## Chapter 2: The Tools We Use and Why

**What you'll understand after this chapter:**
The purpose of every tool in the stack and why each one exists.

---

### React

React is a JavaScript library created by Facebook. Its job is one thing: **make it easy to build UIs by breaking them into reusable pieces called components**.

Without React, building an interactive page means manually finding DOM elements and updating them:

```javascript
// Without React — painful
document.getElementById('count').innerText = count + 1

// With React — just update state, React handles the DOM
setCount(count + 1)
```

React tracks what changed and updates only the parts of the page that need updating. This is called the **virtual DOM**.

---

### Vite

Your browser cannot run JSX (`<div className="card">`) — it only understands plain JavaScript. Vite is the **build tool** that:

1. Converts JSX → plain JavaScript
2. Bundles all your files into a few optimised files
3. Runs a local dev server with hot reload (changes appear instantly without refreshing)

You interact with Vite through two commands:

```bash
npm run dev    # start the dev server at localhost:5173
npm run build  # compile everything into the dist/ folder for production
```

---

### Tailwind CSS

Normally, styling requires writing separate `.css` files with class names:

```css
/* Traditional CSS */
.card {
  background-color: #111827;
  border: 1px solid #1e2a3d;
  border-radius: 1rem;
  padding: 1.25rem;
}
```

Then in HTML:
```html
<div class="card">...</div>
```

Tailwind eliminates the separate CSS file. You write utility classes directly on the element:

```jsx
<div className="bg-bg-700 border border-bg-600 rounded-2xl p-5">
```

Each class does exactly one thing. You compose them. Tailwind generates only the CSS classes you actually use — so the final CSS file is tiny.

---

### Lucide React

Every icon in the project (`TrendingUp`, `Building2`, `Github`) comes from Lucide. Icons are React components, so you use them like any other component:

```jsx
import { TrendingUp } from 'lucide-react'

<TrendingUp size={20} className="text-blue-400" strokeWidth={1.5} />
```

---

### The relationship between these tools

```
You write JSX + Tailwind classes
        ↓
Vite compiles it into HTML + CSS + JS
        ↓
Browser displays the result
        ↓
React keeps it interactive
```

---

## Chapter 3: A Map of the Codebase

**What you'll understand after this chapter:**
Where every file lives, what it does, and where to look when you want to change something specific.

---

### The folder structure

```
frontend/
│
├── public/                    ← Files served directly, no compilation
│   └── gallery/               ← Your wildlife photos
│       ├── IMG_5164.JPG.jpeg
│       └── (12 more photos)
│
├── src/                       ← Everything you write lives here
│   │
│   ├── components/            ← One file per section of the page
│   │   ├── Nav.jsx            → The sticky navigation bar
│   │   ├── Hero.jsx           → Full-screen landing section
│   │   ├── About.jsx          → About me section
│   │   ├── Tools.jsx          → Tools grid with categories
│   │   ├── SpendingTool.jsx   → The actual spending analyser UI
│   │   ├── SpendingToolModal.jsx → The popup wrapper for the tool
│   │   ├── ConsentModal.jsx   → Data-processing consent gate (shown before upload)
│   │   ├── Gallery.jsx        → Wildlife photo grid
│   │   └── Footer.jsx         → Contact and social links
│   │
│   ├── App.jsx                ← The root — assembles all sections
│   ├── main.jsx               ← Entry point — mounts App into index.html
│   └── index.css              ← Global styles and Tailwind directives
│
├── tailwind.config.js         ← Our custom colors, fonts, animations
├── index.html                 ← The single HTML shell
└── package.json               ← Project dependencies and npm scripts
```

---

### The two types of files in `public/` vs `src/`

**`public/`** — These files are copied to the server exactly as-is. No processing. A photo at `public/gallery/photo.jpg` is accessible in the browser at `/gallery/photo.jpg`.

**`src/`** — These files are processed by Vite. JSX gets compiled, Tailwind classes get processed, everything gets bundled and optimised.

> **Rule of thumb:** Images and fonts go in `public/`. Components and CSS go in `src/`.

---

### When you want to change something, look here

| What to change | File to edit |
|---------------|-------------|
| Navigation links | `src/components/Nav.jsx` — the `links` array at the top |
| Hero heading or tagline | `src/components/Hero.jsx` |
| Bio text or stats | `src/components/About.jsx` |
| Add/edit a tool | `src/components/Tools.jsx` — the `categories` array |
| Gallery photos | `src/components/Gallery.jsx` — the `photos` array |
| Footer social links | `src/components/Footer.jsx` — the `social` array |
| Site-wide colors | `frontend/tailwind.config.js` |
| Global fonts or custom CSS classes | `src/index.css` |
| Consent checkbox wording | `src/components/ConsentModal.jsx` — the `CHECKBOXES` array at the top |
| Privacy accordion text | `src/components/SpendingTool.jsx` — the `<details>` block inside `Idle` |

---

# Part II — The Language

---

## Chapter 4: JavaScript You Need to Know

**What you'll understand after this chapter:**
The specific JavaScript patterns used throughout this codebase. You don't need to know all of JavaScript — just these patterns.

---

### Variables: `const` and `let`

```javascript
const name = 'Sourav'    // cannot be reassigned
let count = 0            // can be reassigned: count = count + 1
```

Use `const` by default. Use `let` only when you know the value will change.

> **You'll almost never see `var` in modern JavaScript.** It's an old pattern with confusing behaviour. Ignore it.

---

### Arrow functions

There are two ways to write functions in modern JavaScript. In this codebase we use **arrow functions** exclusively:

```javascript
// Traditional function
function greet(name) {
  return 'Hello, ' + name
}

// Arrow function — same thing, shorter
const greet = (name) => {
  return 'Hello, ' + name
}

// Even shorter — when the body is just one expression, skip the braces and `return`
const greet = (name) => 'Hello, ' + name
```

Arrow functions appear everywhere:

```jsx
// In event handlers
<button onClick={() => setMenuOpen(!menuOpen)}>

// In array methods
const liveTools = categories.flatMap(c => c.tools.filter(t => t.live))

// As component callbacks
<Tools onOpenTool={() => setToolOpen(true)} />
```

---

### Destructuring

Destructuring lets you pull values out of objects and arrays cleanly:

```javascript
// Without destructuring
const title = tool.title
const desc  = tool.desc
const icon  = tool.icon

// With destructuring — same result, one line
const { title, desc, icon } = tool
```

This is used heavily in component props:

```jsx
// Instead of:
function LiveCard(props) {
  return <h4>{props.tool.title}</h4>
}

// We destructure immediately:
function LiveCard({ tool, onOpen, compact }) {
  return <h4>{tool.title}</h4>
}
```

Array destructuring is how `useState` works:

```javascript
const [count, setCount] = useState(0)
//      ↑          ↑
//  current    the setter function
//   value
```

---

### Template literals

Template literals are strings that can contain expressions:

```javascript
const name = 'Sourav'
const city = 'India'

// Old way
const bio = 'I am ' + name + ' from ' + city

// Template literal
const bio = `I am ${name} from ${city}`
```

In JSX, template literals are used for dynamic `className` strings:

```jsx
// Static part stays in the string, dynamic part goes in ${}
<header className={`fixed top-0 z-40 transition-all ${scrolled ? 'bg-bg-900/85 backdrop-blur-xl' : ''}`}>
```

---

### Ternary operator

The ternary is a one-line if/else:

```javascript
// If/else
if (scrolled) {
  return 'bg-bg-900/85'
} else {
  return ''
}

// Ternary — same thing
scrolled ? 'bg-bg-900/85' : ''
```

Real examples from the codebase:

```jsx
// In Tools.jsx — different padding based on compact prop
className={compact ? 'p-4' : 'p-5'}

// In SpendingTool.jsx — button text
Analyse My Spending{files.length > 1 ? ` (${files.length} files)` : ''}

// In Processing component
{fileCount > 1
  ? `Processing ${fileCount} files — the AI reads each page like a human.`
  : 'The AI reads each page like a human — large PDFs take 1–2 minutes.'}
```

---

### Short-circuit `&&`

In JavaScript, `false && anything` evaluates to `false` and stops. `true && value` evaluates to `value`. React treats `false` as "render nothing".

```jsx
// This renders <Spinner /> only when isLoading is true
{isLoading && <Spinner />}

// This renders the description only when compact is false
{!compact && <p className="text-ink-400 text-xs">{tool.desc}</p>}

// This renders the mobile menu only when menuOpen is true
{menuOpen && (
  <div className="md:hidden bg-bg-800/95 ...">
    {/* mobile links */}
  </div>
)}
```

---

### Array methods: `map`, `filter`, `flatMap`

These three are used constantly to render lists from data.

**`map`** — transform every item in an array:

```javascript
const numbers = [1, 2, 3]
const doubled = numbers.map(n => n * 2)
// → [2, 4, 6]
```

In JSX, `map` renders a list of components:

```jsx
{stats.map(({ value, label }) => (
  <div key={label} className="card p-4">
    <p className="text-xl font-bold">{value}</p>
    <p className="text-xs">{label}</p>
  </div>
))}
```

**`filter`** — keep only items that match a condition:

```javascript
const allTools = [
  { title: 'Spending Analyser', live: true },
  { title: 'Meeting Summarizer', live: false },
]
const live = allTools.filter(t => t.live)
// → [{ title: 'Spending Analyser', live: true }]
```

**`flatMap`** — map + flatten one level:

```javascript
// categories is an array of objects, each with a tools array
// flatMap gives us all tools in a single flat array
const liveTools = categories.flatMap(c => c.tools.filter(t => t.live))
```

---

### Spread operator `...`

The spread operator copies items from one array/object into another:

```javascript
// Copy an array and add items
const oldFiles = ['file1.pdf', 'file2.pdf']
const newFiles = [...oldFiles, 'file3.pdf']
// → ['file1.pdf', 'file2.pdf', 'file3.pdf']
```

Real example from `SpendingTool.jsx` — adding new files without duplicates:

```javascript
setFiles(prev => {
  const existing = new Set(prev.map(f => f.name))
  return [...prev, ...valid.filter(f => !existing.has(f.name))]
  //      ↑ spread existing files, then add new non-duplicate files
})
```

---

### Optional chaining `?.`

The `?.` operator safely accesses a property — if the thing before it is `null` or `undefined`, it returns `undefined` instead of throwing an error:

```javascript
// Without optional chaining — throws if inputRef.current is null
inputRef.current.click()

// With optional chaining — safely does nothing if current is null
inputRef.current?.click()
```

---

### `async` / `await`

This is how you write asynchronous code (like API calls) without it looking chaotic:

```javascript
// Without async/await — "callback hell"
fetch('/api/data')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err))

// With async/await — reads like normal code
async function loadData() {
  try {
    const res  = await fetch('/api/data')
    const data = await res.json()
    console.log(data)
  } catch (err) {
    console.error(err)
  }
}
```

`await` pauses execution until the promise resolves. `async` marks a function as one that uses `await`. The `try/catch` handles errors.

This is exactly how the spending analyser calls the API — see Chapter 18.

---

## Chapter 5: JSX — HTML Inside JavaScript

**What you'll understand after this chapter:**
What JSX is, how it differs from HTML, and how to read the patterns you see in every component.

---

### What is JSX?

JSX is a syntax extension for JavaScript that lets you write HTML-like code inside `.jsx` files. Your browser cannot run JSX directly — Vite compiles it into plain JavaScript.

Under the hood, this JSX:

```jsx
<div className="card p-4">
  <h3>Hello</h3>
</div>
```

...becomes this JavaScript:

```javascript
React.createElement('div', { className: 'card p-4' },
  React.createElement('h3', null, 'Hello')
)
```

You never write that second form. JSX is just a nicer way to write it. But understanding this is why:

- You need `React` imported in older codebases (modern React doesn't require it, but the transform still happens)
- You can't use `class` — it's a reserved word in JavaScript, so JSX uses `className`

---

### JSX vs HTML: the differences

| HTML | JSX | Reason |
|------|-----|--------|
| `class="..."` | `className="..."` | `class` is reserved in JS |
| `for="input-id"` | `htmlFor="input-id"` | `for` is reserved in JS |
| `onclick="fn()"` | `onClick={fn}` | Events are camelCase and take functions |
| `<img src="x">` | `<img src="x" />` | All tags must close |
| `<input>` | `<input />` | All tags must close |
| `style="color: red"` | `style={{ color: 'red' }}` | Inline styles are JS objects |
| HTML comments `<!-- -->` | JS comments `{/* */}` | Comments are JavaScript |

---

### The golden rule: `{}` means "switch to JavaScript"

Inside JSX, everything is treated as markup. When you need a JavaScript expression, wrap it in `{}`:

```jsx
const name  = 'Sourav'
const count = 3
const isLive = true

<h1>{name}</h1>                              // → Sourav
<p>You have {count} files</p>               // → You have 3 files
<p>{count * 2} total pages</p>              // → 6 total pages
<p>{isLive ? 'Live' : 'Coming soon'}</p>   // → Live
<p className={isLive ? 'text-green-400' : 'text-ink-400'}>Status</p>
```

You can put any JavaScript expression inside `{}`. You cannot put statements (like `if`, `for`, `while`) — only expressions that produce a value.

---

### The one-root-element rule

A component can only return one root element. This is because JSX compiles to a single `React.createElement` call.

```jsx
// WRONG — two roots
return (
  <h1>Title</h1>
  <p>Body</p>
)

// CORRECT — wrapped in a div
return (
  <div>
    <h1>Title</h1>
    <p>Body</p>
  </div>
)

// CORRECT — wrapped in a Fragment (renders nothing in DOM)
return (
  <>
    <h1>Title</h1>
    <p>Body</p>
  </>
)
```

---

### JSX is an expression

Because JSX compiles to a function call, you can use it anywhere you'd use a value:

```jsx
const badge = <span className="text-emerald-400">Live</span>

const button = (
  <button className="px-7 py-3 rounded-full bg-blue-500 text-white">
    Click me
  </button>
)

return <div>{badge} {button}</div>
```

---

### Common mistake: string vs expression

```jsx
// String — the literal text "true"
<button disabled="true">Click</button>

// Expression — the boolean true
<button disabled={true}>Click</button>
<button disabled>Click</button>   // shorthand for disabled={true}

// String — counts as a number
<Icon size="20" />

// Expression — actual number
<Icon size={20} />
```

For anything that's not a plain string, always use `{}`.

---

# Part III — React

---

## Chapter 6: Components — The Building Block

**What you'll understand after this chapter:**
What a component is, why we split the page into many components, and the rules all components follow.

---

### What is a component?

A component is a JavaScript function that returns JSX. That's the complete definition.

```jsx
function Greeting() {
  return <p>Hello, world!</p>
}
```

Components are the LEGO bricks of React. You build small, focused pieces and compose them into a complete page.

---

### Why not just write one big HTML file?

Imagine your portfolio as one giant file with 2,000 lines of HTML. When you want to change the navigation:
- You have to find it in 2,000 lines
- If the nav appears in multiple places, you have to change it in multiple places
- There's no clear boundary between concerns

With components:
- The nav is in `Nav.jsx`, and only there
- The gallery is in `Gallery.jsx`, and only there
- `App.jsx` simply assembles them like building blocks

---

### The rules of components

**1. Function name must start with a capital letter**

```jsx
function hero() { ... }   // WRONG — React treats this as a DOM element
function Hero() { ... }   // CORRECT
```

React uses the capitalisation to distinguish between:
- `<hero>` — an HTML element called "hero" (doesn't exist, will error)
- `<Hero>` — your Hero component

**2. Must return JSX or null**

```jsx
function Empty() {
  return null  // renders nothing — valid
}

function Card() {
  return (
    <div className="card">
      Content
    </div>
  )
}
```

**3. One component per concern, usually one file per component**

Nav, Hero, About, Tools, Gallery, Footer — each is its own file. When something changes, you know exactly where to look.

---

### `export default` and `import`

Every component file exports its component so other files can use it:

```jsx
// In Footer.jsx
export default function Footer() {
  return <footer>...</footer>
}

// In App.jsx
import Footer from './components/Footer'

// Now you can use it:
<Footer />
```

The `default` keyword means "this is the main thing this file exports". You can name it anything when you import:

```jsx
import Footer from './components/Footer'       // standard
import MyFooter from './components/Footer'     // also fine
```

---

### Sub-components: components inside a file

A file can export one main component and also define helper components for internal use. Look at `Tools.jsx`:

```jsx
// The main exported component
export default function Tools({ onOpenTool }) {
  return (
    <section>
      {liveTools.map((t) => (
        <LiveCard key={t.title} tool={t} onOpen={onOpenTool} />
      ))}
    </section>
  )
}

// Sub-components — only used within this file, not exported
function LiveCard({ tool, onOpen, compact }) {
  return <button>...</button>
}

function UpcomingCard({ tool }) {
  return <div>...</div>
}
```

`LiveCard` and `UpcomingCard` are not exported because nothing outside `Tools.jsx` uses them. They're private helpers.

---

### Exercise 6.1

Open `About.jsx`. Find:
1. The name of the exported component
2. How many elements are returned from the root
3. Whether any sub-components are defined in the file

---

## Chapter 7: Props — Talking Between Components

**What you'll understand after this chapter:**
How to pass data into a component and how to read it.

---

### The mental model

Think of a component like a function. A function takes inputs (arguments) and returns something. A component takes inputs (props) and returns JSX.

```javascript
// Regular function
function double(number) {
  return number * 2
}
double(5)  // → 10

// Component — same concept, different syntax
function Card({ title, description }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  )
}
<Card title="Spending Analyser" description="Upload your statement." />
```

---

### How props work

When you write `<Card title="Hello" count={3} />`, React collects all the attributes into a single object called `props` and passes it to the function:

```jsx
// What React does internally
Card({ title: "Hello", count: 3 })
```

You can access it as `props.title`, or destructure it directly:

```jsx
// Accessing via props object
function Card(props) {
  return <h3>{props.title}</h3>
}

// Destructuring — cleaner, what we use in this codebase
function Card({ title, count }) {
  return <h3>{title} ({count})</h3>
}
```

---

### Types of values you can pass as props

```jsx
// String — just write it directly
<Card title="Hello" />

// Number — needs curly braces
<Icon size={20} />

// Boolean — shorthand (no value = true)
<LiveCard compact />
<LiveCard compact={true} />  // same thing

// Object
<Component style={{ color: 'red', fontSize: 14 }} />

// Array
<Component items={['a', 'b', 'c']} />

// Function — this is how you pass callbacks
<Tools onOpenTool={() => setToolOpen(true)} />

// Another component or variable
<Component icon={TrendingUp} />
```

---

### Passing functions as props: callbacks

This is a critical pattern. It's how a child component triggers something in its parent.

```
App.jsx
  ├── knows whether modal is open (toolOpen state)
  │
  └── Tools.jsx
        └── knows when a live tool is clicked
```

`Tools.jsx` cannot directly change `toolOpen` in `App.jsx` — it doesn't have access. So `App.jsx` passes a function down:

```jsx
// App.jsx — passes the "open the modal" function as a prop
<Tools onOpenTool={() => setToolOpen(true)} />

// Tools.jsx — receives it and calls it when clicked
function Tools({ onOpenTool }) {
  return (
    <button onClick={onOpenTool}>Try it now</button>
  )
}
```

When the button is clicked, `onOpenTool()` is called, which runs `setToolOpen(true)` back in `App.jsx`, which causes the modal to open. The child component triggered a state change in its parent.

This pattern is called **lifting state up**.

---

### Real example: `LiveCard` in Tools.jsx

```jsx
// The component definition — declares what props it accepts
function LiveCard({ tool, onOpen, compact }) {
  const Icon = tool.icon  // the icon component stored in the data

  return (
    <button onClick={onOpen}>                   // calls the function from props
      <div className={compact ? 'p-4' : 'p-5'}> // uses compact prop for size
        <Icon size={compact ? 14 : 18} />       // smaller icon when compact
        <h4>{tool.title}</h4>                   // data from the tool object
        {!compact && <p>{tool.desc}</p>}        // only shows when NOT compact
      </div>
    </button>
  )
}

// Called in two different contexts:
<LiveCard tool={t} onOpen={onOpenTool} />         // full version
<LiveCard tool={t} onOpen={onOpenTool} compact /> // compact version
```

One component. Two appearances. Controlled entirely by props.

---

### Common mistake: confusing strings and functions

```jsx
// WRONG — this calls the function immediately when the component renders,
// not when the button is clicked
<button onClick={setToolOpen(true)}>Click</button>

// CORRECT — wrap it in an arrow function so it runs only on click
<button onClick={() => setToolOpen(true)}>Click</button>
```

---

## Chapter 8: State — Giving Your UI Memory

**What you'll understand after this chapter:**
What state is, how to create it, how to update it, and why it's the core of interactivity in React.

---

### The problem state solves

A regular variable doesn't cause a re-render:

```jsx
function Counter() {
  let count = 0   // just a variable

  return (
    <button onClick={() => { count = count + 1; console.log(count) }}>
      Count: {count}
    </button>
  )
}
```

`count` does increase (you can see it in the console), but the screen never updates. React doesn't know the variable changed.

State is a special variable that React *watches*. When it changes, React automatically re-renders the component with the new value.

---

### `useState` syntax

```jsx
import { useState } from 'react'

const [value, setValue] = useState(initialValue)
//     ↑          ↑               ↑
//  current    function to     starting value
//   value     update it
```

The name convention is `value` + `setValue` — just use meaningful names:

```jsx
const [count,    setCount]    = useState(0)
const [name,     setName]     = useState('')
const [toolOpen, setToolOpen] = useState(false)
const [stage,    setStage]    = useState('idle')
const [files,    setFiles]    = useState([])
```

---

### Updating state

Always use the setter function. Never mutate the state variable directly.

```jsx
// WRONG
count = count + 1           // direct mutation — React won't re-render
files.push(newFile)         // mutating an array in place — React won't re-render

// CORRECT
setCount(count + 1)
setFiles([...files, newFile])  // create a new array
```

When state changes, React calls your component function again with the new value. The component re-renders.

---

### State is local to each component instance

If you render `<Counter />` twice, each has its own separate `count`. They don't share state.

```jsx
<Counter />  // count = 0
<Counter />  // count = 0 (separate)
```

---

### Real state examples from this codebase

**App.jsx — modal open/close:**
```jsx
const [toolOpen, setToolOpen] = useState(false)

// toolOpen = false → modal is hidden
// toolOpen = true  → modal is visible

<SpendingToolModal
  open={toolOpen}
  onClose={() => setToolOpen(false)}
/>
```

**Nav.jsx — two independent pieces of state:**
```jsx
const [scrolled,  setScrolled]  = useState(false)
const [menuOpen, setMenuOpen] = useState(false)

// scrolled = false → navbar is transparent
// scrolled = true  → navbar gets blurred dark background

// menuOpen = false → hamburger menu is closed
// menuOpen = true  → hamburger menu is open
```

**SpendingTool.jsx — a state machine with 4 stages:**
```jsx
const [stage, setStage] = useState('idle')
// 'idle'       → show the file upload UI
// 'processing' → show the loading spinner
// 'done'       → show the download buttons
// 'error'      → show the error message and retry button
```

This is the **state machine pattern** — instead of multiple booleans (`isLoading`, `isError`, `isDone`) that could be in contradictory combinations, a single string represents exactly where you are.

---

### Lifting state up

When two components need to share state, move the state to their nearest common parent and pass it down as props.

```
App (owns: toolOpen)
├── Tools (receives: onOpenTool callback)
└── SpendingToolModal (receives: open, onClose)
```

`Tools` doesn't know about the modal. `SpendingToolModal` doesn't know about `Tools`. They're both connected through `App`.

---

### Exercise 8.1

Open `Nav.jsx`. Find:
1. The two state variables
2. What value each starts at
3. What causes each one to change

---

## Chapter 9: Hooks — React's Superpowers

**What you'll understand after this chapter:**
The three hooks used in this codebase: `useState`, `useEffect`, and `useRef`. What each one does and when to use it.

---

### What is a hook?

A hook is a special function that starts with `use`. Hooks let function components do things that previously required class components.

**The rules:**
1. Only call hooks at the top level of a component — not inside loops, conditions, or nested functions
2. Only call hooks from React function components — not from regular JavaScript functions

If you break these rules, React will throw an error.

---

### Hook 1: `useState`

You already know this from Chapter 8. It gives a component memory.

```jsx
const [value, setValue] = useState(initialValue)
```

---

### Hook 2: `useEffect`

`useEffect` lets you run side effects — things that happen *outside* the normal render flow.

**When you need it:**
- Listen to browser events (scroll, resize, keydown)
- Fetch data from an API
- Set up a timer
- Read from localStorage

**Syntax:**

```jsx
useEffect(() => {
  // 1. This runs after the component renders

  return () => {
    // 2. This cleanup runs before the next effect or when component unmounts
  }
}, [dependency1, dependency2])
  // 3. Dependency array — re-run the effect when these values change
  //    [] = run only once, when the component first appears
  //    [count] = re-run whenever count changes
  //    no array = run after every render
```

**Real example — Nav.jsx scroll detection:**

```jsx
useEffect(() => {
  const onScroll = () => setScrolled(window.scrollY > 30)

  window.addEventListener('scroll', onScroll, { passive: true })
  // ↑ Start listening to scroll events

  return () => window.removeEventListener('scroll', onScroll)
  // ↑ Cleanup: stop listening when Nav is removed from the page
  
}, [])  // ← [] means: set this up once, never re-run
```

**What `{ passive: true }` means:** It tells the browser "this listener will never call `preventDefault()`". The browser can then optimise scroll performance. Always use it for scroll listeners.

**Why cleanup matters:** If you add an event listener without removing it, every time the component re-mounts, you add another listener. You end up with dozens of listeners running the same code. The cleanup function prevents this.

---

### Hook 3: `useRef`

`useRef` creates a container that holds a value across renders *without triggering a re-render*. It's most commonly used to directly access a DOM element.

```jsx
const ref = useRef(initialValue)
// ref.current → the current value
```

**Real example — SpendingTool.jsx hidden file input:**

The custom drop zone is a styled `<div>`. But file selection only works with `<input type="file">`. The trick: hide the input, use a ref to click it programmatically.

```jsx
const inputRef = useRef(null)

// The visible styled drop zone
<div onClick={() => inputRef.current?.click()}>
  Drop PDFs here or click to browse
</div>

// The hidden input that actually triggers the file picker
<input
  ref={inputRef}
  type="file"
  className="hidden"
  onChange={onChange}
/>
```

`inputRef.current?.click()` is the same as calling `.click()` on the actual `<input>` DOM element — it opens the file picker.

**Another use: storing a value without re-rendering**

The abort controller in `SpendingTool.jsx` is stored in a ref, not state, because changing it shouldn't trigger a re-render:

```jsx
const abortRef = useRef(null)

// When starting analysis:
abortRef.current = new AbortController()

// The fetch uses it:
fetch(url, { signal: abortRef.current.signal })

// When resetting:
abortRef.current?.abort()
```

---

### Hook 4: `useCallback`

`useCallback` memoises a function — it keeps the same function reference between renders unless its dependencies change.

```jsx
// Without useCallback — new function reference every render
const onDrop = (e) => {
  e.preventDefault()
  addFiles(e.dataTransfer.files)
}

// With useCallback — same reference unless dependencies change
const onDrop = useCallback((e) => {
  e.preventDefault()
  addFiles(e.dataTransfer.files)
}, [])  // no deps = function never changes
```

In `SpendingTool.jsx`, `onDrop` is passed to a `<div>` as an event handler. Without `useCallback`, every render creates a new function, which could cause performance issues in complex components.

For most components you build, you won't need `useCallback`. It becomes relevant when you notice performance issues.

---

### Summary: which hook for which situation

| Situation | Hook to use |
|-----------|-------------|
| Data that, when changed, should update the screen | `useState` |
| Browser events (scroll, resize, keydown) | `useEffect` |
| Fetching data when component loads | `useEffect` |
| Accessing a DOM element directly | `useRef` |
| Storing a value that shouldn't trigger re-render | `useRef` |
| Caching a function reference for performance | `useCallback` |

---

# Part IV — Styling

---

## Chapter 10: How CSS Works in 5 Minutes

**What you'll understand after this chapter:**
The three CSS concepts you need before Tailwind makes complete sense.

---

### The Box Model

Every HTML element is a box. The box has four layers from inside out:

```
┌─────────────────────────────┐
│           margin            │
│  ┌─────────────────────┐    │
│  │       border        │    │
│  │  ┌───────────────┐  │    │
│  │  │    padding    │  │    │
│  │  │  ┌─────────┐  │  │    │
│  │  │  │ content │  │  │    │
│  │  │  └─────────┘  │  │    │
│  │  └───────────────┘  │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
```

- **Content** — the text or children inside the element
- **Padding** — space between content and border (inside the element)
- **Border** — the visible edge
- **Margin** — space outside the border (pushes other elements away)

In Tailwind: `p-4` is padding, `m-4` is margin, `border` adds a border.

---

### Display: block vs inline vs flex vs grid

**`block`** — takes up the full width. Stacks vertically. (`div`, `p`, `section`)

**`inline`** — takes up only what it needs. Flows in text. (`span`, `a`)

**`flex`** — children line up in a row (or column). You control alignment and spacing.

**`grid`** — children arranged in rows AND columns simultaneously.

In Tailwind: `flex`, `grid`, `block`, `inline-flex`, `hidden` (display: none).

---

### Position: static, relative, absolute, fixed

**`static`** (default) — follows normal document flow.

**`relative`** — same as static, but you can use `top`/`left` to shift it. Also creates a positioning context for absolute children.

**`absolute`** — removed from the flow. Positions relative to the nearest `relative` ancestor. Used for overlays and badges.

**`fixed`** — positions relative to the browser window. Stays in place when you scroll. Used by the navbar.

```jsx
// Nav stays at top of screen while you scroll
<header className="fixed top-0 inset-x-0 z-40">

// Gallery photo overlay — fills the photo container
<div className="absolute inset-0 bg-gradient-to-t from-black/65">
```

---

### The cascade (why `z-index` matters)

Elements later in the HTML stack on top of earlier elements. `z-index` overrides this stacking order. Higher z-index = on top.

```jsx
// Nav needs to appear above everything else
className="z-40"

// Most content has default z-index
// Modals/overlays usually use z-50
```

---

## Chapter 11: Tailwind CSS — Styling at Speed

**What you'll understand after this chapter:**
How to read Tailwind classes, compose them, and handle responsiveness and hover states.

---

### The core idea: one class, one property

Every Tailwind class does exactly one thing. You stack them to build any style.

```jsx
// A card — built from 4 utility classes
<div className="bg-bg-700 border border-bg-600 rounded-2xl p-5">
```

Breaking it down:
- `bg-bg-700` → background-color: our card surface color
- `border` → adds a 1px border
- `border-bg-600` → sets the border color
- `rounded-2xl` → border-radius: 1rem

---

### Spacing

The spacing scale in Tailwind uses a base unit of `0.25rem` (4px):

| Class | Value | Pixels |
|-------|-------|--------|
| `p-1` | 0.25rem | 4px |
| `p-2` | 0.5rem | 8px |
| `p-4` | 1rem | 16px |
| `p-6` | 1.5rem | 24px |
| `p-8` | 2rem | 32px |
| `p-10` | 2.5rem | 40px |

`p` = all sides. `px` = left + right. `py` = top + bottom. `pt` = top. `pb` = bottom. `pl` = left. `pr` = right.

Same scale for margin: `m`, `mx`, `my`, `mt`, `mb`, `ml`, `mr`.

**All section blocks in this site use `py-32`** (8rem top and bottom). That's the consistent vertical rhythm.

---

### Typography

```jsx
// Size scale
className="text-xs"    // 12px — "Coming soon" labels
className="text-sm"    // 14px — most body text, nav links
className="text-base"  // 16px — default
className="text-xl"    // 20px — card titles
className="text-3xl"   // 30px — section headings on mobile
className="text-4xl"   // 36px — section headings on desktop

// Weight
className="font-normal"   // 400
className="font-medium"   // 500
className="font-semibold" // 600
className="font-bold"     // 700
className="font-extrabold"// 800 — used for the hero "Sourav Mondal"

// Family
className="font-display"  // Syne — our heading font
className="font-sans"     // Inter — body text (default)

// Other
className="tracking-wide"    // wider letter-spacing
className="tracking-widest"  // very wide — used in section-label
className="leading-tight"    // tighter line-height
className="leading-relaxed"  // looser line-height — used in body paragraphs
className="uppercase"        // ALL CAPS — used in section-label
className="text-center"      // centered text
```

---

### Colors

Format: `{property}-{color}-{shade}`

```jsx
className="text-white"       // text color: white
className="text-blue-400"    // text color: blue at shade 400
className="bg-bg-700"        // background: card surface
className="border-bg-600"    // border color: our border shade
```

**Opacity modifier:** add `/N` where N is 0-100:

```jsx
className="bg-blue-500/10"   // blue-500 at 10% opacity (very subtle)
className="bg-blue-500/20"   // blue-500 at 20% opacity
className="border-white/5"   // barely visible white border
className="bg-bg-900/85"     // semi-transparent background (navbar on scroll)
```

---

### Flexbox

```jsx
<div className="flex">
  {/* children go in a row */}
</div>

<div className="flex items-center">
  {/* children vertically centered */}
</div>

<div className="flex items-center justify-between">
  {/* children: one on left, one on right */}
</div>

<div className="flex items-center gap-3">
  {/* 12px gap between children */}
</div>

<div className="flex flex-col">
  {/* children stacked vertically */}
</div>
```

Common child modifiers:
```jsx
className="flex-1"    // grow to fill remaining space
className="shrink-0"  // never shrink below content size (for icons next to text)
```

---

### Grid

```jsx
<div className="grid grid-cols-2 gap-4">
  {/* 2 equal columns */}
</div>

<div className="grid grid-cols-4 gap-3">
  {/* 4 equal columns */}
</div>

<div className="grid md:grid-cols-2 lg:grid-cols-4 gap-3">
  {/* 1 col on mobile, 2 on tablet, 4 on desktop */}
</div>
```

Spanning multiple cells:
```jsx
<div className="col-span-2">  {/* fills 2 columns */}
<div className="row-span-2">  {/* fills 2 rows (Gallery.jsx) */}
```

---

### Responsive design

Tailwind is **mobile-first**. A class applies to all screen sizes. Prefixes add it only above that breakpoint:

```
no prefix → applies to all sizes
sm:       → 640px and above
md:       → 768px and above
lg:       → 1024px and above
xl:       → 1280px and above
```

```jsx
// On mobile: text-3xl. On medium+ screens: text-4xl
className="text-3xl md:text-4xl"

// On mobile: hidden. On medium+ screens: flex
className="hidden md:flex"   // ← the desktop nav links

// On mobile: 1 column. On lg: 4 columns
className="grid-cols-1 lg:grid-cols-4"
```

---

### Hover and interaction states

```jsx
className="hover:text-white"            // text turns white on hover
className="hover:bg-blue-500/20"        // background appears on hover
className="hover:-translate-y-0.5"     // moves up 2px on hover
className="hover:scale-[1.02]"         // grows 2% on hover
className="hover:border-blue-500/40"   // border becomes visible on hover

// Always pair with transition for animation
className="transition-all duration-300"   // all properties animate
className="transition-colors"             // only colors animate (more performant)
```

**The `group` pattern** — hover on parent triggers styles on children:

```jsx
<div className="group">                              {/* 1. mark as group */}
  <img className="group-hover:scale-105" />          {/* 2. react to group hover */}
  <p className="opacity-0 group-hover:opacity-100" />{/* 3. same trigger */}
</div>
```

When the mouse hovers anywhere on the `group` div, all `group-hover:` classes inside it activate simultaneously. Used in `Gallery.jsx` for the photo overlay effect.

---

### Arbitrary values

When you need a specific value not on the default scale, use square brackets:

```jsx
className="text-[clamp(3.5rem,10vw,6.5rem)]"  // custom font size
className="w-[900px]"                           // exact 900px width
className="auto-rows-[180px]"                  // gallery grid row height
className="bg-blue-500/8"                       // 8% opacity (not on default scale)
```

---

### Transitions and Animations

```jsx
// Transition — smooths property changes
className="transition-all duration-300"   // 300ms ease
className="transition-colors"             // only color transitions
className="transition-opacity"            // only opacity transitions

// Transform
className="hover:scale-[1.03]"            // scale up
className="-translate-y-0.5"             // move 2px up
className="rotate-45"                    // rotate 45 degrees

// Built-in animations (defined in tailwind.config.js)
className="animate-spin"                  // spinning (loading icon)
className="animate-bounce"               // bouncing (down arrow in Hero)
className="animate-pulse"                // pulsing (progress bar)
className="animate-glow"                 // blue glow pulse (our custom animation)
```

---

## Chapter 12: Our Design System

**What you'll understand after this chapter:**
The custom colors, fonts, and utilities that are specific to this project.

These are defined in `tailwind.config.js` and `index.css`. They are NOT part of standard Tailwind.

---

### Colors

```
Background scale (dark navy):
  bg-900  #080c14  ← entire page background
  bg-800  #0d1220  ← alternate section background (Tools section)
  bg-700  #111827  ← card surface
  bg-600  #1e2a3d  ← borders, hovered card borders

Text scale (blue-tinted white):
  ink-200 #c8d6e8  ← primary text — cool near-white
  ink-400 #6b7fa0  ← secondary / muted text
  ink-600 #3d4f6a  ← very muted / placeholder / faint labels

Accent colors:
  blue-400 #60a5fa  ← links, active states, icon colors
  blue-500 #3b82f6  ← primary button background, highlight
  cyan-400 #22d3ee  ← gradient end color in gradient-text
  emerald-400 #34d399  ← live indicator dot, success states
  rose-400 #f472b6   ← error states
  sky-400 #38bdf8    ← report download button icon
```

---

### Custom utility classes (from index.css)

These work exactly like Tailwind classes — use them as `className="card"`:

```jsx
// card — the standard card/panel surface
className="card"
// expands to: bg-bg-700 border border-bg-600 rounded-2xl

// section-label — the small uppercase label above headings
className="section-label"
// expands to: text-xs font-semibold tracking-widest uppercase text-blue-400 mb-4

// gradient-text — blue-to-cyan gradient on text
className="gradient-text"
// expands to: bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent

// hero-bg — the Hero section's radial gradient background
className="hero-bg"
// expands to: a complex background with two radial gradients + base color

// glass-icon — frosted glass icon container
className="glass-icon"
// expands to: bg-white/5 border border-white/10 rounded-xl flex items-center justify-center
```

---

### Fonts

```jsx
className="font-display"  // Syne — use for ALL headings
className="font-sans"     // Inter — body text, applied globally by default
className="font-mono"     // JetBrains Mono — for code snippets
```

Headings (`h1`, `h2`, `h3`) automatically use Syne via the global CSS rule:
```css
h1, h2, h3 { font-family: 'Syne', sans-serif; }
```

---

### Custom animations (from tailwind.config.js)

```jsx
className="animate-fade-in"   // fades in from opacity 0
className="animate-slide-up"  // slides up from 20px below + fades in
className="animate-glow"      // pulses a blue box-shadow (SpendingTool card)
```

---

# Part V — The Real Codebase

---

## Chapter 13: App.jsx — How Everything Connects

**File:** [frontend/src/App.jsx](frontend/src/App.jsx)

---

### The full component

```jsx
import { useState } from 'react'
import Nav               from './components/Nav'
import Hero              from './components/Hero'
import About             from './components/About'
import Tools             from './components/Tools'
import Gallery           from './components/Gallery'
import Footer            from './components/Footer'
import SpendingToolModal from './components/SpendingToolModal'

export default function App() {
  const [toolOpen, setToolOpen] = useState(false)

  return (
    <div className="min-h-screen">
      <Nav />
      <main>
        <Hero />
        <About />
        <Tools onOpenTool={() => setToolOpen(true)} />
        <Gallery />
      </main>
      <Footer />
      <SpendingToolModal open={toolOpen} onClose={() => setToolOpen(false)} />
    </div>
  )
}
```

---

### Why state lives here

`toolOpen` controls whether the SpendingTool modal is visible. Two separate components need to interact with this value:
- `Tools` needs to set it to `true` (when you click a live tool)
- `SpendingToolModal` needs to read it (to know whether to show) and set it to `false` (when you close the modal)

Neither component knows about the other. The only place that talks to both is their parent: `App`. So state lives in `App`, and both components receive it via props.

```
App
├── toolOpen = false/true
│
├── Tools
│   └── when clicked → calls onOpenTool() → sets toolOpen=true in App
│
└── SpendingToolModal
    ├── reads: open={toolOpen}
    └── when closed → calls onClose() → sets toolOpen=false in App
```

---

### `min-h-screen`

The wrapping `<div className="min-h-screen">` ensures the page is at least the full viewport height, even if the content is shorter. Without it, the dark background would only cover as far as the content goes.

---

## Chapter 14: Nav.jsx — Scroll-Aware Navigation

**File:** [frontend/src/components/Nav.jsx](frontend/src/components/Nav.jsx)

---

### The key pattern: scroll detection with useEffect

```jsx
const [scrolled, setScrolled] = useState(false)

useEffect(() => {
  const onScroll = () => setScrolled(window.scrollY > 30)
  window.addEventListener('scroll', onScroll, { passive: true })
  return () => window.removeEventListener('scroll', onScroll)
}, [])
```

`window.scrollY` is how many pixels the page has been scrolled from the top. When it exceeds 30px, `scrolled` becomes `true`, which changes the navbar's class:

```jsx
<header className={`fixed top-0 inset-x-0 z-40 transition-all duration-300
  ${scrolled
    ? 'bg-bg-900/85 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/40'
    : ''
  }`}
>
```

**`backdrop-blur-xl`** is the frosted glass effect — it blurs whatever is behind the navbar.

---

### Data above the component

```jsx
const links = [
  { href: '#about',   label: 'About'   },
  { href: '#tools',   label: 'Tools'   },
  { href: '#gallery', label: 'Gallery' },
]
```

This array lives *outside* the component function. It never changes, so it doesn't need to be inside. Keeping it outside means it's not recreated on every render.

To add a nav link: add one line to this array. The component renders it automatically.

---

### The hamburger menu animation

Three `<span>` elements represent the three bars. On open, they animate into an ✕:

```jsx
<span className={`block w-5 h-px bg-ink-200 transition-all duration-200
  ${menuOpen ? 'rotate-45 translate-y-2' : ''}`} />
  {/* ↑ top bar: rotates +45° and moves down when open */}

<span className={`block w-5 h-px bg-ink-200 transition-all duration-200
  ${menuOpen ? 'opacity-0' : ''}`} />
  {/* ↑ middle bar: disappears when open */}

<span className={`block w-5 h-px bg-ink-200 transition-all duration-200
  ${menuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
  {/* ↑ bottom bar: rotates -45° and moves up when open */}
```

---

## Chapter 15: Hero.jsx — The First Impression

**File:** [frontend/src/components/Hero.jsx](frontend/src/components/Hero.jsx)

---

### Fluid typography with `clamp`

```jsx
className="text-[clamp(3.5rem,10vw,6.5rem)]"
```

`clamp(min, preferred, max)` — the font scales with viewport width (`10vw` = 10% of viewport) but never goes below `3.5rem` or above `6.5rem`. This makes the heading look good on every screen without breakpoint-specific overrides.

---

### Decorative background blobs

```jsx
<div className="absolute inset-0 pointer-events-none overflow-hidden">
  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                  w-[900px] h-[500px] bg-blue-700/8 rounded-full blur-3xl" />
  <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-cyan-600/5 rounded-full blur-3xl" />
</div>
```

- `pointer-events-none` — the blobs don't block clicks
- `blur-3xl` — heavy gaussian blur turns a coloured rounded div into a soft glow
- `bg-blue-700/8` — only 8% opacity, very subtle
- `overflow-hidden` on the parent clips the blobs to the section bounds

---

### Anchor-based navigation

Each section has an `id`:

```jsx
<section id="home" ...>  // Hero
<section id="about" ...> // About
<section id="tools" ...> // Tools
```

Nav links use `href="#about"` — clicking them scrolls to the matching `id`. The smooth scroll is handled by this CSS in `index.css`:

```css
html { scroll-behavior: smooth; }
```

No JavaScript needed for scrolling.

---

## Chapter 16: About.jsx — Layout and Images

**File:** [frontend/src/components/About.jsx](frontend/src/components/About.jsx)

---

### Unequal grid columns

`grid-cols-5` creates 5 equal columns. Then we span them:

```jsx
<div className="grid md:grid-cols-5 gap-12 lg:gap-16">
  <div className="md:col-span-2">  {/* takes 2/5 of width */}
    photo + stats
  </div>
  <div className="md:col-span-3">  {/* takes 3/5 of width */}
    text
  </div>
</div>
```

On mobile (no `md:` prefix), `col-span` has no effect and both divs stack vertically.

---

### Making images fill a square container

```jsx
<div className="relative rounded-2xl overflow-hidden aspect-square">
  <img
    src="/gallery/IMG_5176.JPG.jpeg"
    alt="Sourav Mondal"
    className="w-full h-full object-cover"
  />
  <div className="absolute inset-0 bg-gradient-to-t from-bg-900/60 to-transparent" />
</div>
```

- `aspect-square` → container is always a 1:1 square
- `overflow-hidden` → clips the image to the rounded corners
- `w-full h-full` → image fills the container
- `object-cover` → image crops to fill without distortion (like CSS `background-size: cover`)
- The `absolute inset-0` div is a gradient overlay that darkens the bottom of the photo

---

## Chapter 17: Tools.jsx — Data-Driven UI

**File:** [frontend/src/components/Tools.jsx](frontend/src/components/Tools.jsx)

---

### The data structure

The entire tools section is driven by one data array:

```jsx
const categories = [
  {
    label: 'Corporate Fellows',
    CategoryIcon: Building2,     // Lucide icon component
    tools: [
      {
        title: 'Spending Analyser',
        desc:  'Upload HDFC, SBI, ICICI statements...',
        icon:  TrendingUp,
        live:  true,
        tag:   'Finance',
      },
      { title: 'Meeting Summarizer', desc: '...', icon: ClipboardList },
      // ...more tools
    ],
  },
  // ...more categories
]
```

This separation of **data** from **markup** is one of the most important patterns in frontend development. To add a new tool, you add one object to the array. You never touch the rendering logic.

---

### Automatic derivation of live tools

```jsx
const liveTools = categories.flatMap(c => c.tools.filter(t => t.live))
```

Step by step:
1. `categories.flatMap(c => ...)` — iterate over categories
2. `c.tools.filter(t => t.live)` — from each category, keep only tools with `live: true`
3. `flatMap` flattens the result — instead of `[[tool1], [], [tool2]]` you get `[tool1, tool2]`

Result: `liveTools` is always up-to-date. Add `live: true` to any tool and it automatically appears in the "Live Now" section.

---

### Icons as data

Lucide icons are React components. Since components are just functions, you can store them in objects:

```jsx
const tool = { icon: TrendingUp }

// In the component:
const Icon = tool.icon      // Icon = TrendingUp (the component function)
<Icon size={18} />          // → <TrendingUp size={18} />
```

This works because in JavaScript, functions are first-class values — you can pass them around, store them in objects, assign them to variables.

---

### The `compact` prop pattern

The same `LiveCard` component renders in two contexts that need different sizes. The `compact` prop controls this:

```jsx
// Full size in "Live Now" section
<LiveCard tool={t} onOpen={onOpenTool} />

// Compact in category sections
<LiveCard tool={t} onOpen={onOpenTool} compact />
```

Inside `LiveCard`:
```jsx
function LiveCard({ tool, onOpen, compact }) {
  const Icon = tool.icon
  return (
    <div className={compact ? 'p-4' : 'p-5'}>      {/* size varies */}
      <Icon size={compact ? 14 : 18} />             {/* icon size varies */}
      <h4>{tool.title}</h4>
      {!compact && <p>{tool.desc}</p>}              {/* description hidden when compact */}
      {!compact && <p>Try it now →</p>}
    </div>
  )
}
```

One component handles both cases. Less duplication, one place to change if the design updates.

---

## Chapter 18: SpendingTool.jsx — A Real Form with API

**File:** [frontend/src/components/SpendingTool.jsx](frontend/src/components/SpendingTool.jsx)

This is the most complex component. Read it after you're comfortable with the earlier chapters.

---

### The state machine

Instead of multiple booleans, one `stage` value tracks where the user is:

```jsx
const STAGES = {
  IDLE:       'idle',        // show upload UI
  PROCESSING: 'processing',  // show loading
  DONE:       'done',        // show download buttons
  ERROR:      'error',       // show error + retry
}

const [stage, setStage] = useState(STAGES.IDLE)
```

The render logic becomes clean:

```jsx
{stage === STAGES.IDLE       && <Idle ... />}
{stage === STAGES.PROCESSING && <Processing ... />}
{stage === STAGES.DONE       && <Done ... />}
{stage === STAGES.ERROR      && <ErrorState ... />}
```

Exactly one sub-view is shown at any time. The states cannot conflict.

---

### File drag-and-drop

Three events make drag-and-drop work:

```jsx
<div
  onDrop={onDrop}           // fires when files are dropped
  onDragOver={onDragOver}   // fires while dragging over — MUST call e.preventDefault()
  onDragLeave={onDragLeave} // fires when drag leaves the area
>
```

**Why `onDragOver` must call `e.preventDefault()`:** By default, browsers don't allow dropping files onto elements. Calling `preventDefault()` in `onDragOver` tells the browser "yes, dropping is allowed here."

```jsx
const onDragOver  = (e) => { e.preventDefault(); setDragging(true) }
const onDragLeave = ()  => setDragging(false)
const onDrop = useCallback((e) => {
  e.preventDefault()
  setDragging(false)
  addFiles(e.dataTransfer.files)  // e.dataTransfer.files contains the dropped files
}, [])
```

The `dragging` state changes the drop zone border from subtle to visible:

```jsx
className={`border-2 border-dashed rounded-xl cursor-pointer
  ${dragging ? 'border-violet-400 bg-violet-600/10' : 'border-bg-600 hover:border-violet-500'}`}
```

---

### File validation

```jsx
const ACCEPTED = /\.(pdf|xlsx|xls|csv)$/i   // regex: matches these extensions

const addFiles = (fileList) => {
  const incoming = Array.from(fileList)  // convert FileList to array
  const errors = []
  const valid  = []

  incoming.forEach(f => {
    if (!ACCEPTED.test(f.name))    { errors.push(`${f.name}: only PDF / Excel / CSV`); return }
    if (f.size > 15 * 1024 * 1024) { errors.push(`${f.name}: too large (max 15 MB)`); return }
    valid.push(f)
  })

  if (errors.length) setError(errors.join(' · '))
  else setError('')

  setFiles(prev => {
    const existing = new Set(prev.map(f => f.name))
    return [...prev, ...valid.filter(f => !existing.has(f.name))]
  })
}
```

`15 * 1024 * 1024` = 15 MB in bytes (1 KB = 1024 bytes, 1 MB = 1024 KB).

`new Set(...)` creates a set of existing file names for O(1) lookup — faster than checking with `includes()`.

---

### Sending files to the API

```jsx
const startAnalysis = async () => {
  setStage(STAGES.PROCESSING)

  const formData = new FormData()
  files.forEach(f => formData.append('files', f))
  // FormData is the browser standard for sending files to a server

  abortRef.current = new AbortController()
  const timer = setTimeout(() => abortRef.current.abort(), 20 * 60 * 1000)
  // Abort after 20 minutes — prevents the request hanging forever

  try {
    const res = await fetch(`${API_BASE}/analyse`, {
      method:  'POST',
      body:    formData,
      signal:  abortRef.current.signal,
      headers: { 'X-Consent-Given': 'true' },   // tells the server consent was captured
    })

    clearTimeout(timer)

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Server returned ${res.status}`)
    }

    const data = await res.json()
    setResults({ csvUrl: data.csv_url, reportUrl: data.report_url })
    setStage(STAGES.DONE)

  } catch (err) {
    clearTimeout(timer)
    setError(err.name === 'AbortError'
      ? 'Request timed out after 20 minutes.'
      : err.message)
    setStage(STAGES.ERROR)
  }
}
```

**`AbortController`** — a browser API that lets you cancel a `fetch` request. We store it in a `ref` (not state) because cancelling the request shouldn't trigger a re-render.

**`X-Consent-Given: true` header** — a custom HTTP header sent with every `/analyse` request. The backend checks for this header and rejects the request with a 400 error if it is missing. This creates a hard server-side enforcement of consent — it is impossible to process files without the user first agreeing to the terms. See Chapter 19 for the component that captures this consent, and the Backend Guide Chapter 9 for the server-side check.

**Environment variable:**

```jsx
const API_BASE = import.meta.env.VITE_API_URL || ''
```

`VITE_API_URL` is set in a `.env` file at build time. On EC2 it's `https://souravspace.com`. The `VITE_` prefix is mandatory — Vite only exposes variables with this prefix to the browser (to prevent accidentally exposing server secrets).

---

### The consent gate pattern

The upload zone is never shown until the user explicitly consents. This is implemented by gating the entire `Idle`/`Processing`/`Done`/`Error` tree behind a `consentGiven` state variable.

```jsx
const [consentGiven, setConsentGiven] = useState(
  () => sessionStorage.getItem('spending_consent_given') === 'true'
)
```

**Why `sessionStorage` and not `localStorage`?**

`localStorage` persists across browser sessions (even after closing the tab). `sessionStorage` is cleared when the tab closes. For financial data, re-asking consent every new browser session is the right balance — you don't want to annoy users who reopen a tab within the same session, but you also don't want consent to silently carry over across days or devices.

```jsx
const handleConsent = () => {
  sessionStorage.setItem('spending_consent_given', 'true')
  setConsentGiven(true)
}
```

The lazy initializer `() => sessionStorage.getItem(...)` reads from `sessionStorage` on the very first render, before any state updates. This means: if the user already consented earlier in the same tab session, the `ConsentModal` never appears — the upload zone shows immediately.

In the JSX:

```jsx
{!consentGiven
  ? <ConsentModal onAccept={handleConsent} onCancel={() => {}} />
  : <>
      {stage === STAGES.IDLE       && <Idle ... />}
      {stage === STAGES.PROCESSING && <Processing ... />}
      {stage === STAGES.DONE       && <Done ... />}
      {stage === STAGES.ERROR      && <ErrorState ... />}
    </>
}
```

When `consentGiven` is false, only `ConsentModal` is mounted — the file input, drop zone, and the entire upload flow are not in the DOM at all.

---

### The privacy accordion

Below the "Powered by Groq" line in the `Idle` view, a native HTML `<details>/<summary>` element shows the full privacy policy without needing extra state or a library:

```jsx
<details className="rounded-xl border border-bg-600 overflow-hidden text-left">
  <summary className="...cursor-pointer...">
    <Shield size={12} className="text-blue-400" />
    Privacy & Data Processing Details
  </summary>
  <div className="px-4 py-4 bg-bg-800 text-xs ...">
    <p>What is processed: ...</p>
    <p>Third-party processor: Groq Cloud (US) ...</p>
    <p>Retention: ...</p>
    ...
  </div>
</details>
```

`<details>` is a native HTML disclosure widget — clicking `<summary>` toggles the rest open or closed. No React state needed. The browser handles the open/close behaviour.

To update the privacy text, edit the `<div>` inside `<details>` in `SpendingTool.jsx` at the bottom of the `Idle` function.

---

## Chapter 19: ConsentModal.jsx — Privacy Gate Before Upload

**File:** [frontend/src/components/ConsentModal.jsx](frontend/src/components/ConsentModal.jsx)

This chapter covers the consent modal that blocks access to the upload zone until the user explicitly agrees to the data processing terms. It is a legal and ethical requirement: India's DPDPA 2023 requires informed, specific, freely given consent before processing financial data.

---

### Why a dedicated component?

The consent UI could have been written inline inside `SpendingTool.jsx`. A separate component was chosen because:
- It is a distinct concern — displaying terms and capturing consent is not the same as uploading and analysing files
- The checkbox state and button logic are self-contained
- It is easier to update the wording or add/remove checkboxes without touching the upload logic

---

### The data structure: checkboxes as an array

```jsx
const CHECKBOXES = [
  {
    id: 'c1',
    text: <>I understand that pages of my bank statement PDF will be converted to images
             and sent to <strong className="text-white">Groq</strong> ...</>,
  },
  {
    id: 'c2',
    text: <>I understand that my uploaded files are <strong>deleted immediately</strong>...</>,
  },
  {
    id: 'c3',
    text: <>I <strong>consent</strong> to this processing for the sole purpose of...</>,
  },
]
```

The checkbox texts are defined as an array of objects **outside** the component, the same pattern used in `Nav.jsx` and `Tools.jsx`. To change the wording of a checkbox, edit the `text` field in this array. To add a new checkbox, add a new object with a unique `id`.

The `text` field is JSX (not a plain string) — notice the `<>...</>` fragment wrappers and `<strong>` tags. This allows formatting within the checkbox text.

---

### State: one boolean per checkbox

```jsx
const [checked, setChecked] = useState({ c1: false, c2: false, c3: false })

const allChecked = Object.values(checked).every(Boolean)

const toggle = (id) => setChecked(prev => ({ ...prev, [id]: !prev[id] }))
```

`{ c1: false, c2: false, c3: false }` — one state object holds all three checkbox values. This is slightly more compact than three separate `useState` calls.

`Object.values(checked).every(Boolean)` — converts `{ c1: true, c2: false, c3: true }` to `[true, false, true]` and checks if every value is truthy. Returns `false` if any checkbox is unchecked.

`{ ...prev, [id]: !prev[id] }` — spread the previous state and override just the one key that changed. `[id]` is a **computed property name** — the variable `id` becomes the key.

---

### The "I Agree" button disabled state

```jsx
<button onClick={onAccept} disabled={!allChecked}
        className="... disabled:opacity-40 disabled:cursor-not-allowed ...">
  I Agree & Continue →
</button>
```

`disabled={!allChecked}` — when any checkbox is unchecked, the button is disabled. Tailwind's `disabled:` prefix applies styles only when the element is disabled:
- `disabled:opacity-40` — grays out the button
- `disabled:cursor-not-allowed` — shows the ⛔ cursor

This prevents any click events from firing on a disabled button without any JavaScript check needed.

---

### Custom checkbox styling

The native `<input type="checkbox">` is hidden. A `<div>` mimics it visually:

```jsx
<label onClick={() => toggle(id)}>
  <div className={`mt-0.5 w-4 h-4 shrink-0 rounded border flex items-center justify-center
    transition-colors
    ${checked[id]
      ? 'bg-blue-500 border-blue-500'
      : 'border-bg-500 bg-bg-700 group-hover:border-blue-400'}`}>
    {checked[id] && (
      <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
        <path d="M1 4l3 3 5-6" stroke="white" strokeWidth="1.8"
              strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )}
  </div>
  <p>{text}</p>
</label>
```

When checked: blue background + blue border + white SVG checkmark. When unchecked: dark background + muted border. The entire `<label>` is clickable (including the text) — clicking anywhere on the label calls `toggle(id)`.

The checkmark is an inline SVG path — a simple `M 1 4 l 3 3 5-6` path that draws a checkmark. No icon library needed.

---

### Props

```jsx
export default function ConsentModal({ onAccept, onCancel }) {
```

| Prop | Type | What it does |
|------|------|-------------|
| `onAccept` | `() => void` | Called when user clicks "I Agree" with all boxes checked |
| `onCancel` | `() => void` | Called when user clicks "Cancel" |

`SpendingTool.jsx` passes `handleConsent` as `onAccept` (which writes to `sessionStorage` and sets `consentGiven = true`) and an empty function as `onCancel` (the modal just stays visible — the user must consent or close the entire tool modal).

---

## Chapter 20: Gallery.jsx — Photos and Hover Effects

**File:** [frontend/src/components/Gallery.jsx](frontend/src/components/Gallery.jsx)

---

### Data-driven photo grid

```jsx
const photos = [
  { file: 'IMG_5164.JPG.jpeg', alt: 'Blue pit viper — Agumbe forests', span: 'col-span-1 row-span-2' },
  { file: 'IMG_5172.JPG.jpeg', alt: 'Black-winged stilt wading',        span: 'col-span-2' },
  { file: 'IMG_5169.JPG.jpeg', alt: 'Painted stork portrait' },
  // ...
]
```

The `span` property controls how much grid space each photo takes. `undefined` (no span) = 1×1.

---

### Fixed-height grid rows

```jsx
<div className="grid grid-cols-2 md:grid-cols-4 auto-rows-[180px] gap-3">
```

`auto-rows-[180px]` sets every row to exactly 180px. A photo with `row-span-2` gets 360px + 3px gap = 363px. This creates the staggered masonry look without a dedicated masonry library.

---

### The hover overlay pattern

```jsx
<div className={`relative overflow-hidden rounded-xl group ${p.span || ''}`}>

  {/* The photo */}
  <img
    src={`/gallery/${p.file}`}
    alt={p.alt}
    loading="lazy"
    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
  />

  {/* Dark gradient overlay — invisible normally, fades in on hover */}
  <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/10 to-transparent
                  opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

  {/* Caption — invisible and shifted down, slides up and fades in on hover */}
  <p className="absolute bottom-3 left-3 right-3 text-white text-xs font-medium
                opacity-0 group-hover:opacity-100
                translate-y-1 group-hover:translate-y-0
                transition-all duration-300">
    {p.alt}
  </p>
</div>
```

**`group`** on the container activates `group-hover:` on all children simultaneously. Hovering anywhere on the photo card:
1. Scales the photo up 5% (`group-hover:scale-105`)
2. Fades in the dark gradient (`group-hover:opacity-100`)
3. Fades in and slides up the caption (`group-hover:opacity-100` + `group-hover:translate-y-0`)

**`loading="lazy"`** — images only download when they scroll into view. Without this, the browser would download all 12 photos at once on page load.

---

## Chapter 21: Footer.jsx — Links and Contact

**File:** [frontend/src/components/Footer.jsx](frontend/src/components/Footer.jsx)

---

### Social links as data

```jsx
const social = [
  { href: 'https://github.com/SouravM47',                    Icon: Github,    label: 'GitHub'    },
  { href: 'https://linkedin.com/in/sourav-mondal-6680b1232', Icon: Linkedin,  label: 'LinkedIn'  },
  { href: 'https://instagram.com/souravmondal',              Icon: Instagram, label: 'Instagram' },
]
```

To add a new social link: add one object. The render loop handles it:

```jsx
{social.map(({ href, Icon, label }) => (
  <a key={label} href={href}
     target="_blank" rel="noopener noreferrer"
     aria-label={label}
     className="w-9 h-9 rounded-lg bg-bg-700 border border-white/5
                text-ink-400 hover:text-white hover:border-blue-500/40
                flex items-center justify-center transition-all hover:-translate-y-0.5">
    <Icon size={15} strokeWidth={1.5} />
  </a>
))}
```

---

### External link safety

```jsx
target="_blank"          // opens in a new tab
rel="noopener noreferrer" // security: the new page cannot access window.opener
                          // and cannot read the referrer URL
aria-label={label}        // accessibility: screen reader announces "GitHub" for the icon
```

Always include all three for external links.

---

### `mailto:` links

```jsx
<a href="mailto:sourav72598@gmail.com">
  sourav72598@gmail.com
</a>
```

Clicking this opens the user's default email client with the `to` field pre-filled. No JavaScript needed.

---

# Part VI — Building New Things

---

## Chapter 22: Adding a New Section

This chapter walks through adding a "Testimonials" section from zero to deployed.

---

### Step 1 — Create the component file

Create `frontend/src/components/Testimonials.jsx`:

```jsx
const testimonials = [
  {
    name:   'Priya S.',
    role:   'Finance Manager',
    text:   'The spending analyser saved me hours every month. I actually understand where my money goes now.',
  },
  {
    name:   'Arjun K.',
    role:   'Freelance Developer',
    text:   'Finally an AI tool that actually works for real Indian bank statements.',
  },
]

export default function Testimonials() {
  return (
    <section id="testimonials" className="py-32 px-6 bg-bg-800/40">
      <div className="max-w-6xl mx-auto">

        <p className="section-label text-center">Testimonials</p>
        <h2 className="text-3xl md:text-4xl font-display font-bold text-white text-center mb-3 leading-tight">
          What people say
        </h2>
        <p className="text-ink-400 text-center max-w-md mx-auto mb-16">
          From people who use it every day.
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          {testimonials.map((t) => (
            <div key={t.name} className="card p-6 hover:border-blue-500/25 transition-colors">
              <p className="text-ink-200 leading-relaxed mb-5">"{t.text}"</p>
              <div>
                <p className="text-white text-sm font-semibold">{t.name}</p>
                <p className="text-ink-400 text-xs">{t.role}</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  )
}
```

---

### Step 2 — Add it to App.jsx

```jsx
import Testimonials from './components/Testimonials'  // add import

export default function App() {
  const [toolOpen, setToolOpen] = useState(false)

  return (
    <div className="min-h-screen">
      <Nav />
      <main>
        <Hero />
        <About />
        <Tools onOpenTool={() => setToolOpen(true)} />
        <Testimonials />   {/* add here */}
        <Gallery />
      </main>
      <Footer />
      <SpendingToolModal open={toolOpen} onClose={() => setToolOpen(false)} />
    </div>
  )
}
```

---

### Step 3 — Add to Nav links (optional)

In `Nav.jsx`:

```jsx
const links = [
  { href: '#about',        label: 'About'        },
  { href: '#tools',        label: 'Tools'        },
  { href: '#testimonials', label: 'Testimonials' },  // add
  { href: '#gallery',      label: 'Gallery'      },
]
```

---

### Step 4 — Add this section to this guide

When this guide is updated, add a new section under Part V following the same format as the existing component chapters.

---

## Chapter 23: Patterns Reference Card

Copy-paste these patterns when building new components.

---

### Section wrapper

```jsx
<section id="your-section-id" className="py-32 px-6">
  <div className="max-w-6xl mx-auto">
    {/* content */}
  </div>
</section>
```

Use `bg-bg-800/40` for alternating section backgrounds (Tools and About sections have it).

---

### Section heading block

```jsx
<p className="section-label text-center">Category Label</p>
<h2 className="text-3xl md:text-4xl font-display font-bold text-white text-center mb-3 leading-tight">
  Main heading here
</h2>
<p className="text-ink-400 text-center max-w-md mx-auto mb-16">
  One line of supporting copy.
</p>
```

---

### Card

```jsx
<div className="card p-5 hover:border-blue-500/25 transition-colors">
  {/* content */}
</div>
```

---

### Icon with glass background

```jsx
<div className="w-10 h-10 rounded-xl glass-icon">
  <SomeIcon size={18} className="text-blue-400" strokeWidth={1.5} />
</div>
```

---

### Primary button

```jsx
<button className="px-7 py-3 rounded-full bg-blue-500 text-white font-semibold text-sm
                   hover:bg-blue-400 transition-all hover:scale-[1.03]
                   shadow-lg shadow-blue-500/30">
  Button text
</button>
```

---

### Ghost (outline) button

```jsx
<button className="px-7 py-3 rounded-full border border-white/12 text-ink-200
                   hover:border-blue-500/40 hover:text-white text-sm font-medium
                   transition-all hover:bg-blue-500/6">
  Button text
</button>
```

---

### Rendering a list from data

```jsx
{items.map((item) => (
  <div key={item.id}>
    {item.name}
  </div>
))}
```

`key` must be a unique identifier for each item. React uses it to track which items changed.

---

### Two-column layout (equal)

```jsx
<div className="grid md:grid-cols-2 gap-10">
  <div>{/* left */}</div>
  <div>{/* right */}</div>
</div>
```

---

### Two-column layout (unequal, like About)

```jsx
<div className="grid md:grid-cols-5 gap-12">
  <div className="md:col-span-2">{/* 2/5 width */}</div>
  <div className="md:col-span-3">{/* 3/5 width */}</div>
</div>
```

---

### Three or four column card grid

```jsx
<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
  {/* 1 col mobile, 2 col tablet, 3 col desktop */}
</div>

<div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
  {/* 1 col mobile, 2 col tablet, 4 col desktop */}
</div>
```

---

### Hover overlay on an image

```jsx
<div className="relative overflow-hidden rounded-xl group">
  <img src={src} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
  <div className="absolute inset-0 bg-gradient-to-t from-black/65 to-transparent
                  opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
  <p className="absolute bottom-3 left-3 text-white text-xs
                opacity-0 group-hover:opacity-100 translate-y-1 group-hover:translate-y-0
                transition-all duration-300">
    Caption here
  </p>
</div>
```

---

### Conditional rendering

```jsx
{condition && <Component />}           // show only when true
{!condition && <Component />}          // show only when false
{a ? <ComponentA /> : <ComponentB />}  // one or the other
```

---

### External link (correct attributes)

```jsx
<a href="https://..." target="_blank" rel="noopener noreferrer" aria-label="Description">
  Link text
</a>
```

---

# Appendix

---

## Glossary

| Term | Plain English meaning |
|------|-----------------------|
| **Component** | A JavaScript function that returns JSX. The building block of React. |
| **JSX** | HTML-like syntax inside JavaScript files. Compiled to plain JS by Vite. |
| **Props** | Inputs to a component. Passed like HTML attributes. Accessed by destructuring. |
| **State** | Data that can change. When it changes, React re-renders the component. |
| **Hook** | A special React function starting with `use`. Only works inside components. |
| **useState** | Creates a state variable and a setter function. Returns `[value, setValue]`. |
| **useEffect** | Runs code after render. Used for events, data fetching, timers. |
| **useRef** | Holds a mutable value that doesn't trigger re-renders. Also gives DOM access. |
| **useCallback** | Caches a function so it's not recreated every render. |
| **Lifting state up** | Moving state to a common parent so multiple children can share it. |
| **Render** | React calling your component function to produce JSX, then updating the DOM. |
| **Re-render** | React calling the function again because state or props changed. |
| **Virtual DOM** | React's internal copy of the DOM. React diffs it against the real DOM and updates only what changed. |
| **Controlled component** | A form element whose value is controlled by React state. |
| **Event handler** | A function called when something happens (click, hover, scroll, change). |
| **Callback** | A function passed as a prop so a child component can call code defined in the parent. |
| **Destructuring** | Pulling values out of objects/arrays: `const { a, b } = obj`. |
| **Spread operator** | `...` — copies items from array/object: `[...old, newItem]`. |
| **Template literal** | Backtick string with expressions: `` `Hello ${name}` ``. |
| **Ternary** | Inline if/else: `condition ? valueIfTrue : valueIfFalse`. |
| **Short-circuit `&&`** | `condition && value` — returns `value` only if condition is truthy. |
| **Optional chaining `?.`** | Safely access nested properties — returns `undefined` instead of throwing. |
| **`async/await`** | Readable syntax for asynchronous operations like fetch. |
| **Promise** | An object representing a future value (e.g., the result of a fetch). |
| **`FormData`** | Browser API for sending files to a server. |
| **`AbortController`** | Browser API to cancel a fetch request. |
| **Tailwind** | Utility-first CSS framework. Classes like `p-4 text-sm` directly on elements. |
| **Utility class** | A single-purpose CSS class — `font-bold` only sets font-weight. |
| **Responsive prefix** | `sm:`, `md:`, `lg:` — Tailwind classes that activate at specific screen widths. |
| **`group`** | Tailwind pattern: hover on parent activates `group-hover:` on all children. |
| **`export default`** | Marks the main export. Imported with `import X from './file'`. |
| **`import`** | Brings code from another file or package into the current file. |
| **`map()`** | Array method that transforms every item. Returns a new array. |
| **`filter()`** | Array method that keeps only items matching a condition. Returns a new array. |
| **`flatMap()`** | `map()` + one level of flattening. Turns nested arrays into a flat one. |
| **Vite** | Build tool + dev server. Compiles JSX, bundles files, handles hot reload. |
| **`import.meta.env`** | Access to environment variables at build time. `VITE_` prefix required. |
| **SPA** | Single Page Application — one HTML file, JavaScript builds the entire UI. |
| **DOM** | Document Object Model — the browser's representation of the page as a tree of nodes. |
| **Viewport** | The visible area of the browser window. `vw` = viewport width, `vh` = viewport height. |

---

*Last updated: May 2026*
*Covers: Nav, Hero, About, Tools, SpendingTool, ConsentModal, Gallery, Footer*
*When a new component is added — add its Chapter under Part V and update this date.*
