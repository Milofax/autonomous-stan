# Golden Examples: Gute Traceability

## Example 1: Vollständige Kette
> **Hypothesis:** Wir glauben, dass Enterprise-Admins Zeit sparen, wenn wir Bulk-Import anbieten.
>
> **Ziel:** Onboarding-Zeit um 40% reduzieren.
>
> **Success Metrics:**
> | Metrik | Baseline | Ziel |
> |--------|----------|------|
> | Onboarding-Zeit/User | 4.2 Min | < 1 Min |
>
> **User Story:**
> Als Admin möchte ich User via CSV importieren, damit ich bei großen Teams Zeit spare.
> → **Verknüpft mit:** Onboarding-Zeit Metric
>
> **Akzeptanzkriterien:**
> - [ ] CSV mit 100 Usern in < 30 Sekunden
> - [ ] Fehlerhafte Zeilen im Report
>
> **Scope:**
> - [ ] CSV-Upload → Story: CSV importieren
> - [ ] Validierung → Story: CSV importieren (Akzeptanzkriterium 2)

**Expected Score: 5**
- stories-linked-to-metrics: 5 - Explizit verknüpft
- requirements-linked-to-stories: 5 - Testbare Kriterien
- goal-to-hypothesis: 5 - "Zeit sparen" → "Zeit reduzieren"
- no-orphan-features: 5 - Alle verknüpft
- full-chain: 5 - Komplett
- bidirectional: 5 - Beidseitig

---

## Example 2: Multi-Story PRD
> **Goal:** Trial-Conversion um 25% steigern.
>
> **Metrics:**
> - Trial-to-Paid: 12% → 18%
> - Time-to-First-Value: 48h → 24h
>
> **Story 1:** Als Erstbesucher möchte ich in 2 Klicks starten.
> → Metric: Time-to-First-Value
> - [ ] Signup ohne Email-Verifikation
> - [ ] Demo-Daten vorinstalliert
>
> **Story 2:** Als Trial-User möchte ich Wert sofort sehen.
> → Metric: Trial-to-Paid
> - [ ] Onboarding zeigt 3 Quick Wins
> - [ ] Progress-Indicator für Setup

**Expected Score: 5**
- stories-linked-to-metrics: 5 - Jede Story verknüpft
- requirements-linked-to-stories: 5 - Alle haben Kriterien
- goal-to-hypothesis: 4 - Hypothesis fehlt, aber Goal → Metrics klar
- no-orphan-features: 5 - Alle in Stories
- full-chain: 4 - Fast komplett
- bidirectional: 5 - Verfolgbar
