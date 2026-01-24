# Golden Examples: Schlechte Traceability

## Example 1: Keine Verbindungen
> **Ziel:** App verbessern
>
> **Features:**
> - Dark Mode
> - Performance
> - Bugs fixen

**Expected Score: 1**
- stories-linked-to-metrics: 1 - Keine Stories, keine Metrics
- requirements-linked-to-stories: 1 - Keine Stories
- goal-to-hypothesis: 1 - Keine Hypothesis
- no-orphan-features: 1 - Alle Features Orphans
- full-chain: 1 - Keine Kette
- bidirectional: 1 - Nicht verfolgbar

---

## Example 2: Stories ohne Metrics
> **User Stories:**
> - Als User möchte ich Dark Mode
> - Als User möchte ich schnellere Ladezeiten
> - Als Admin möchte ich Reports exportieren
>
> **Scope:**
> - Dark Mode
> - Performance
> - Export

**Expected Score: 2**
- stories-linked-to-metrics: 1 - Keine Metrics vorhanden
- requirements-linked-to-stories: 2 - Stories ohne Akzeptanzkriterien
- goal-to-hypothesis: 1 - Kein Goal, keine Hypothesis
- no-orphan-features: 4 - Scope-Items entsprechen Stories
- full-chain: 1 - Große Lücken
- bidirectional: 2 - Nur in eine Richtung

---

## Example 3: Orphan Features
> **Goal:** Mehr Umsatz
>
> **Metrics:** Revenue +20%
>
> **Story:** Als Kunde möchte ich kaufen.
>
> **Scope:**
> - Checkout Flow
> - Newsletter Integration
> - Social Login
> - Dark Mode
> - Admin Dashboard
> - Analytics

**Expected Score: 2**
- stories-linked-to-metrics: 2 - Vage Verknüpfung
- requirements-linked-to-stories: 1 - Keine Akzeptanzkriterien
- goal-to-hypothesis: 1 - Keine Hypothesis
- no-orphan-features: 1 - 5 von 6 Features ohne Story
- full-chain: 2 - Große Lücken
- bidirectional: 1 - Nicht verfolgbar
