Target license for lib: MIT

Not release yet - nothing is a "breaking change"
we don't need backward compat for anything

we have PDM installed locally
do not use node js npm whatever
python formatter? black

We do not re-share any dataset
we can provide download scripts
end users need to comply to dataset licences

minimize amount of code (do not keep unused, old; do not overcomplicate stuff - KISS, DRY, no code = no maintanance)
minimize docs - let's have a single source of truth for things, easier to maintain...
let's not keep a note about what was removed, what was before, etc (we track this in git)

DO NOT search full disk outside this repo dir

LLM-WIKI in docs/

Markdown + Mermaid (a lot!)

do not use git! User will do things -> list at the end if needed

Important:
- no leaks of knowledge to reidbench/ repo from the main repo (e.g. no reference to any doc etc.) -> keep reidbench standalone

Have in mind **Rich Hickey’s “Simple Made Easy”** talk:

### Core distinction

* **Simple ≠ Easy**

  * **Simple** = one thing, not interwoven/entangled.
  * **Easy** = convenient, familiar, close at hand.
  * Something can be easy but complex.
* Optimize for **simplicity**, not merely convenience.

### Hickey’s key rules

1. **Avoid complecting**

   * *Complect* = to interweave things that could be separate.
   * Complexity largely comes from things being tangled together.
   * Ask: **“What things have I accidentally made depend on each other?”**

2. **Prefer independent parts**

   * Separate concerns so they can be understood, tested, changed, and reasoned about independently.

3. **Don't confuse abstraction with complexity**

   * Good abstractions can make systems simpler.
   * An abstraction is valuable when it **hides complexity without introducing new entanglements**.

4. **Data is simpler than objects**

   * Data can be passed around, inspected, stored, transformed, and shared without requiring knowledge of an object's behavior/state.
   * Prefer **data + functions** over objects that bundle state and behavior when appropriate.

5. **Separate identity from state**

   * Identity is the thing that persists through time.
   * State is the value at a particular point in time.
   * Don't represent changing state as if it were the identity itself.

6. **Avoid mutable state**

   * Mutation introduces **time** into reasoning.
   * Immutable values are easier to reason about because they don't unexpectedly change underneath you.

7. **Separate time from values**

   * A value should ideally remain a value.
   * If something changes, model the successive values rather than constantly modifying one thing.

8. **Prefer generic mechanisms**

   * Don't create specialized machinery when a simple, composable mechanism will do.
   * General-purpose tools often reduce complexity.

9. **Don't use convenience as the design criterion**

   * “It's easier to write” isn't necessarily “it's simpler.”
   * Shorter code can contain more conceptual complexity.

10. **Composition beats complection**

    * Build systems by putting independent pieces **next to each other**, rather than weaving them together.

### The big mental model

Think of complexity as:

> **More things entangled with each other = more things you must understand simultaneously.**

Simplicity is therefore about **reducing the number of things you have to consider at once**.

### Practical checklist

When designing code, ask:

* Is this thing doing more than one independent job?
* Have I coupled two concerns that could be separate?
* Am I introducing mutable state unnecessarily?
* Am I mixing identity, state, and time?
* Could this be represented as plain data?
* Can these components be understood independently?
* Am I choosing this because it's **easy**, or because it makes the system **simple**?
* Can I compose existing simple parts instead of creating a new intertwined mechanism?

**One-line takeaway:**
**Make things independent, composable, and stable; avoid intertwining concerns, especially through mutable state and hidden time.**
