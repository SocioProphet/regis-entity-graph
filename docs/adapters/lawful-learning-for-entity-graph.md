# Lawful Learning Adapter for Regis Entity Graph

## Purpose

Regis Entity Graph consumes lawful learning as an entity-governance adapter. The general theory remains owned by ProCybernetica.

Regis owns the entity graph application: identity assertions, merge/split decisions, prime-topic constraints, policy polytopes, forbidden co-occurrences, and proof-bearing entity evidence.

Lawful learning adds calibrated constraint scoring, observer-stable evidence, and tunable slack penalties.

## Regis use cases

1. Score whether an entity merge is lawful.
2. Block merges that violate prime-topic separation.
3. Emit observer-stable evidence for each merge, split, or blocked edge.
4. Compare real prime-topic masks against shuffled negative controls.
5. Calibrate thresholds through validation rather than hand-picking.

## Entity merge law

Let `v_e` be the prime-topic indicator for an event or record.

A merge proposal `m=(e_i,e_j)` is lawful if:

```math
A(v_i\lor v_j)\le b.
```

Soft formulation:

```math
A(v_i\lor v_j)-b\le \xi_m,\qquad \xi_m\ge0.
```

The merge penalty is:

```math
\mu_m(w_m)\xi_m^2.
```

The merge truth score is:

```math
T(m)=L(m)E(m).
```

## Adapter output evidence

Each Regis merge decision should emit:

- merge proposal id;
- active prime topics;
- forbidden co-occurrence checks;
- lawful admissibility score;
- evidence confidence score;
- final truth score;
- ledger digest;
- observer id;
- replay metadata.

## Boundary

This adapter does not claim empirical performance. It defines the lawful merge-governance interface that Regis can implement once the ProCybernetica doctrine is accepted.
