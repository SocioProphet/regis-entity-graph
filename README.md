# Regis Entity Graph

Here’s the **complete re-aggregation + reformalization** of what we built in this chat, packaged in a way you can **teach as a class** *and* **implement as a platform**—plus a **toy repo** with **faked Michael Heller data** that actually runs.

[Download the reference repo (toy, executable)](sandbox:/mnt/data/identity_is_prime_reference.zip)

---

## 0) The thesis in one line

**Identity is prime**: a human’s identity is not a single “profile,” but a **product of irreducible roles** (“prime topics”) that must not be silently multiplied together across scopes.
Our platform turns this from a slogan into **machine-checkable math + proofs + enforcement** in a **citizen fog** (local-first, protective), with optional bridges outward.

---

## 1) Canonical object model

### 1.1 Prime topics as a basis

Let (\mathcal{P}={P_1,\dots,P_k}) be **prime identity topics** (irreducible roles). For the worked example we use:

* (P_\text{ENG}): engineer/founder work-self
* (P_\text{HEALTH}): patient/health-self
* (P_\text{CHILD}): parent/child-context-self
* (P_\text{CIVIC}): citizen/civic-self
* (P_\text{ADS}): ad-tech/marketing scope (not “a person,” but a *realm*)

Each event carries an **indicator vector** (v \in {0,1}^k) (which primes are active).

### 1.2 Events (Event-IR) as the atomic substrate

An event is:
[
e = (\text{ts},\ \text{actor},\ \text{scope},\ \text{action},\ v,\ \text{attrs})
]
where **scope** includes at least:

* realm (\in{\text{FOG},\text{DEVICE},\text{APP},\text{CLOUD},\text{HSM}})
* device id, app id, optional jurisdiction / peer

This is the “single source of truth” layer: **logs → typed events → proofs**.

### 1.3 Constraints as a polytope (policy-as-geometry)

We define **allowed mixtures** of primes using linear constraints:
[
A v \le b
]
The simplest version is just “forbidden co-occurrences,” e.g.
[
\neg(P_\text{HEALTH}\wedge P_\text{ADS}),\quad
\neg(P_\text{CHILD}\wedge P_\text{ADS}),\quad
\neg(P_\text{CIVIC}\wedge P_\text{ADS})
]
This is the beginning of the “identity polytope.”

### 1.4 Why Ehrhart shows up (and what it is *not*)

If your allowed states are integer points (v \in \mathbb{Z}^k) inside a polytope (K), then **Ehrhart theory** counts lattice points in dilations (tK):
[
L_K(t)=|tK\cap\mathbb{Z}^k|
]
That gives a principled way to talk about **how many discrete identity-states** a system permits under scaling/aggregation, which is *not* the same thing as a “mean deviation distribution.” It’s combinatorial geometry, not descriptive statistics. (Also: it’s *Ehrhart*, not “Erhardt,” unless you meant something else.)

The key use here: **bounded disclosure** (“you may only observe (N) safe states”) becomes a **counting problem**, not vibes.

---

## 2) Entity resolution “better-than-Senzing”: what we keep, what we extend

Senzing is a practical ER engine with a clear notion of entities/records and published “entity specification” JSON patterns.
We used your slide-set as the “baseline surface area” (SDK objects, configuration, entity spec/schema patterns, and the graph-shaped worldview).

### 2.1 What we add that is structurally different

Senzing (and most ER stacks) answer: “Which records refer to the same entity?”
We answer that *plus*: “**Which merges are illegal for a human** (identity prime mixing), and can we **prove** we didn’t do them?”

So we add:

1. **Prime-topic labeling** on events + realms
2. **Policy polytope** that forbids dangerous mixtures
3. **Proof artifacts** that record *why* an edge/merge was allowed or blocked
4. **Congruence + affine/linear types** for nonces/handles/counters (where covert linkage hides)

Senzing’s “entity spec” becomes just *one adapter* in our citizen-fog pipeline.

---

## 3) The “hard” security lane: Hill-style abstract interpretation + congruence + linearity

Your Hill-inspired spine is the reason this isn’t “just another ER library”:

* We treat analyses as monotone functions over a lattice, compute fixpoints, and force termination with widenings.
* We switch domains depending on what must be proved (intervals → octagons → polyhedra; plus congruences for modular IDs).

This matches the motivation and method of abstract interpretation as a *sound* program reasoning approach (your design is consistent with the field’s standard framing).
The **congruence domain** shift you wrote (Mod (2^k) for handles/nonces/counters) is exactly the right “attacker-aligned” move: leaks often manifest as **modular structure**, not large real-valued drift.

---

## 4) Worked example with *faked* Michael Heller data (runs today)

The repo you can download includes a runnable toy:

* Input: `examples/michael_fog_events.json`
* Run:

  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python -m prime_er.cli --events examples/michael_fog_events.json --out /tmp/artifact.json
