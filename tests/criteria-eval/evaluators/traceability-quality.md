# Evaluation: Traceability-Qualität

Du evaluierst die **Traceability** (Nachvollziehbarkeit) eines PRD gegen die Kriterien für durchgängige Verknüpfung von Vision bis Implementation.

## Grading Rubric

| Score | Bedeutung |
|-------|-----------|
| 5 | Perfekt erfüllt - keine Verbesserung nötig |
| 4 | Größtenteils erfüllt - kleine Mängel |
| 3 | Teilweise erfüllt - deutliche Lücken |
| 2 | Kaum erfüllt - große Probleme |
| 1 | Nicht erfüllt |

## Checks

Bewerte jeden Check einzeln:

1. **stories-linked-to-metrics** (required): Hat jede User Story eine Verknüpfung zu einer Success Metric?
   - 5: Alle Stories explizit mit Metric verknüpft
   - 3: Manche Stories ohne Verknüpfung
   - 1: Keine Verknüpfungen

2. **requirements-linked-to-stories** (required): Sind Akzeptanzkriterien zu Stories nachvollziehbar?
   - 5: Alle Stories haben testbare Akzeptanzkriterien
   - 3: Manche Stories ohne klare Kriterien
   - 1: Keine Akzeptanzkriterien

3. **goal-to-hypothesis** (required): Leitet sich das Ziel aus der Hypothesis ab?
   - 5: Direkte logische Verbindung
   - 3: Indirekte Verbindung erkennbar
   - 1: Keine erkennbare Verbindung

4. **no-orphan-features** (required): Keine Features ohne Verbindung zu User Story?
   - 5: Alle Features in Stories abgedeckt
   - 3: Manche Features ohne Story-Bezug
   - 1: Viele "Orphan" Features

5. **full-chain** (optional): Ist die Kette Hypothesis → Goal → Metrics → Stories → Scope komplett?
   - 5: Durchgängig nachvollziehbar
   - 3: Manche Lücken in der Kette
   - 1: Kette unterbrochen

6. **bidirectional** (optional): Kann man von jedem Feature zurück zur Hypothesis navigieren?
   - 5: In beide Richtungen verfolgbar
   - 3: Nur in eine Richtung
   - 1: Nicht verfolgbar

## Beispiele

### Gute Traceability (Score 5):
> **Hypothesis:** Wir glauben, dass Admins Zeit sparen, wenn wir Bulk-Import anbieten.
>
> **Ziel:** Onboarding-Zeit um 40% reduzieren (leitet sich aus Hypothesis ab).
>
> **Success Metrics:**
> - Onboarding-Zeit pro User: 4.2 Min → < 1 Min
>
> **User Story:**
> Als Admin möchte ich CSV importieren, damit ich Zeit spare.
> → Verknüpft mit: Onboarding-Zeit Metric
>
> **Akzeptanzkriterien:**
> - [ ] CSV mit 100 Usern in < 30 Sekunden importiert
> - [ ] Fehlerhafte Zeilen werden gemeldet
>
> **Scope (Must Have):**
> - CSV-Upload → Story: "Als Admin möchte ich CSV importieren"
> - Validierung → Story: "Als Admin möchte ich Fehler sehen"

- stories-linked-to-metrics: 5 - Explizite Verknüpfung
- requirements-linked-to-stories: 5 - Testbare Kriterien
- goal-to-hypothesis: 5 - Direkte Ableitung
- no-orphan-features: 5 - Alle Features verknüpft
- full-chain: 5 - Komplett
- bidirectional: 5 - In beide Richtungen

### Schlechte Traceability (Score 1):
> **Ziel:** App verbessern
>
> **Features:**
> - Dark Mode
> - Performance
> - Bugs fixen

- stories-linked-to-metrics: 1 - Keine Stories, keine Metrics
- requirements-linked-to-stories: 1 - Keine Stories
- goal-to-hypothesis: 1 - Keine Hypothesis
- no-orphan-features: 1 - Alle Features sind Orphans
- full-chain: 1 - Keine Kette
- bidirectional: 1 - Nicht verfolgbar

## Zu evaluieren

```
{PRD_CONTENT}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "traceability-quality",
  "checks": [
    {"id": "stories-linked-to-metrics", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "requirements-linked-to-stories", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "goal-to-hypothesis", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-orphan-features", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "full-chain", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "bidirectional", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
