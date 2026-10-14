# Executive Business Review — Northstar Retail Group

**Fireworks AI → Northstar VP Customer Experience & VP Engineering**
**Deployment:** `northstar-flagship-support-ft-v1` · **Period:** Aug 1–31, 2026 (31 days)

---

## 1. Executive narrative

One month into production, the flagship support agent has proven it can carry
meaningful support volume with high reliability and improving quality. The
deployment handled **789,563 inference requests** across **143,430 Tier-1
tickets**, automating roughly **70% of Tier-1 volume** and contributing a
scenario-reported **35% reduction in average handle time** and a **+12-point
CSAT improvement**.

Why this matters: the model is no longer a proof of concept. It is doing real
support work every day, and the operational signals are moving in the right
direction — availability held at or above 99.8% all month, the error rate fell
from 1.34% to **0.66%**, median latency improved to **~525 ms**, and grounding
reached **96.5%**. Two operational events (a catalog sync and a promotional
traffic burst) were both caught and mitigated the same day.

The takeaway: the flagship deployment is healthy, the remaining opportunity is
(1) automating the final ~30% of Tier-1, and (2) replicating this proven
pattern across Northstar's four other brands.

## 2. Metric context — caveats worth knowing

| Outcome | Figure | Caveat |
| --- | --- | --- |
| Tier-1 automation | 70.8% (Aug 31); 67.97% weighted monthly | Weighted = total automated ÷ total Tier-1; the daily figures are single-day snapshots |
| Handle-time reduction | 35% | Reported vs. a pre-Fireworks baseline not present in this dataset; observed Aug trend is 8.15 → 7.35 min (~10%) |
| CSAT improvement | +12 points | Reported vs. a pre-Fireworks baseline; observed Aug trend is 80.6 → 84.2 (+3.6) |
| Reliability | availability ≥ 99.8%; error 1.34% → 0.66% | Two same-day incidents (Aug 9, Aug 21) |
| Latency | P50 ~525 ms; P95 (daily) ~1,455 ms | Daily-reported P95, not a true monthly P95 |
| Quality | grounding 96.5%; eval pass 95.3% | Customer-reported evaluation pass rates |

Spend was **$1,213.12** for the month (inference only), a blended **~$1.12 per
million tokens**. This is not a fully loaded program cost.

## 3. Expansion recommendation

**Recommend: expand, but in phases and gated on the flagship evidence.** The
flagship deployment has demonstrated the core capability, and the four
additional brands share the same underlying patterns (catalogs, return
policies, tone, support teams). The expansion case is credible — but it should
proceed brand-by-brand, not as a big-bang rollout.

Why expand now: the hardest technical risks (fine-tuning to brand tone,
catalog-grounded RAG, production reliability) have already been retired on the
flagship. Why phase it: each brand introduces new tone, policy, and data-isolation
requirements that should be validated before they scale.

## 4. Technical scaling plan

Three options were evaluated: **(a)** a shared base model with brand-specific
system prompts and isolated retrieval indexes, **(b)** separate fine-tuned
models per brand, and **(c)** a hybrid.

- **(a) Shared model + brand prompts + isolated retrieval** — lowest cost and
  operational complexity; best latency/throughput via shared prefix caching;
  policy isolation enforced at the retrieval, prompt, and access layers.
- **(b) Separate fine-tuned models** — strongest per-brand control but highest
  cost and maintenance burden; fine-tuning is not required to use private
  enterprise knowledge.
- **(c) Hybrid** — start shared; fine-tune only where a measured behavior gap
  proves it necessary.

**Recommendation:** begin every brand on **(a)**, and reserve fine-tuning for
proven gaps. A separate model or GPU does **not** automatically guarantee
privacy — isolation is a property of retrieval, prompt, and access controls,
which must be enforced regardless of architecture.

## 5. Pilot proposal

**Pilot: "Brand B — Home & Living"** (premium home furnishings; high catalog
and return-policy complexity; ~15k tickets/mo; established help desk). It is the
most representative stress test of the shared-model + isolated-index approach
before rolling out to higher-volume or less-mature brands.

Success criteria (acceptance gates, 30 days): weighted automation ≥65%, error
rate <1%, daily P95 <1,500 ms, grounded answer ≥95%, no CSAT regression. If any
gate fails for two consecutive weeks, roll back to the previous configuration.

Broader rollout is justified only by: stable gate performance, no cross-brand
policy leakage, and positive cost per ticket vs. the manual baseline.

## 6. Budget & timeline

Proposed sequence (illustrative — final cost requires pricing and volume
inputs):

1. **Weeks 1–2 — Pilot setup.** Catalog/index build, brand prompt, isolation
   tests, success criteria agreed.
2. **Weeks 3–6 — Brand B pilot.** 30-day pilot with weekly reviews and
   acceptance gates.
3. **Weeks 7+ — Staged rollout.** Queue Brands D, C, and E by priority,
   gated on each prior brand's results.

Cost scales roughly with support volume; the shared model amortizes inference
across brands. Each additional brand adds integration work proportional to its
catalog and policy complexity.

## 7. Executive talking points

1. The flagship model is doing real work: **~70% of Tier-1 automated** with
   availability ≥99.8% and grounding at **96.5%**.
2. **35% handle-time reduction and +12 CSAT** — the two outcomes that matter
   most to the customer experience.
3. Reliability improved **through the month** — error rate down from 1.34% to
   0.66%, latency down, and both operational events mitigated same-day.
4. The next value is in the **remaining ~30% of Tier-1** and in **replicating
   the pattern to four more brands.**
5. We recommend a **phased, gate-driven expansion** starting with a 30-day
   Home & Living pilot — low risk, clear success criteria, and a rollback path.

## 8. Biggest risk

**Operational resilience under change.** The two August incidents — a catalog
sync (Aug 9) and a promotional traffic burst (Aug 21) — both briefly degraded
latency and error rate. A multi-brand rollout multiplies these change events
(catalog refreshes, promotions, index rebuilds) across the fleet.

**Mitigation:** staged index swaps, prefix-cache warming before cutover,
predictive autoscaling tied to the promotion calendar, and per-brand rollback
gates. Hardening the flagship against change is the prerequisite for expanding
safely.
