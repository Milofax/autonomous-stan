# Evaluation: Success Metrics Qualität

Du evaluierst eine **Success Metrics Sektion** gegen die Kriterien für messbare, actionable Erfolgskriterien.

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

1. **metrics-defined** (required): Gibt es mindestens eine quantitative Metric?
   - 5: Mehrere klare, quantitative Metrics
   - 3: Eine Metric vorhanden
   - 1: Keine quantitativen Metrics

2. **baseline-present** (required): Ist für jede Metric eine Baseline dokumentiert?
   - 5: Alle Metrics haben aktuelle Baseline-Werte
   - 3: Manche Metrics ohne Baseline
   - 1: Keine Baselines

3. **target-specific** (required): Ist für jede Metric ein konkretes Ziel definiert?
   - 5: Alle Ziele sind konkrete Zahlen (nicht "verbessern")
   - 3: Manche Ziele vage
   - 1: Keine konkreten Ziele

4. **measurement-method** (required): Ist dokumentiert WIE gemessen wird?
   - 5: Methode für jede Metric dokumentiert
   - 3: Manche Methoden unklar
   - 1: Keine Messmethoden

5. **north-star** (required): Gibt es eine North Star Metric?
   - 5: Klarer primärer Erfolgsindikator definiert
   - 3: Mehrere gleichwertige Metrics ohne Priorisierung
   - 1: Keine Priorisierung erkennbar

6. **no-vanity-metrics** (optional): Sind die Metrics actionable?
   - 5: Alle Metrics führen zu Handlungen
   - 3: Mix aus actionable und vanity
   - 1: Nur Vanity Metrics (Pageviews, Downloads ohne Kontext)

7. **leading-lagging** (optional): Gibt es Leading und Lagging Indicators?
   - 5: Beide Typen vorhanden und unterschieden
   - 3: Nur ein Typ
   - 1: Nicht unterschieden

## Beispiele

### Gute Success Metrics (Score 5):
> | Metrik | Baseline | Ziel | Messmethode |
> |--------|----------|------|-------------|
> | Onboarding-Zeit pro User | 4.2 Min | < 1 Min | Timer im Admin-Dashboard |
> | Support-Tickets "User anlegen" | 340/Monat | < 50/Monat | Zendesk Tag-Filter |
> | Bulk-Import Adoption | 0% | > 60% | Feature-Flag Analytics |
>
> **North Star Metric:** Onboarding-Zeit pro User

- metrics-defined: 5 - Drei klare Metrics
- baseline-present: 5 - Alle haben Baseline
- target-specific: 5 - Konkrete Ziele
- measurement-method: 5 - Alle dokumentiert
- north-star: 5 - Klar definiert
- no-vanity-metrics: 5 - Alle actionable
- leading-lagging: 4 - Adoption ist leading, Zeit ist lagging

### Schlechte Success Metrics (Score 1):
> "Wir wollen mehr User und bessere Zahlen."

- metrics-defined: 1 - Keine konkreten Metrics
- baseline-present: 1 - Keine Baseline
- target-specific: 1 - "Mehr" und "besser" sind vage
- measurement-method: 1 - Nicht dokumentiert
- north-star: 1 - Keine Priorisierung
- no-vanity-metrics: 1 - "Mehr User" ohne Kontext ist Vanity
- leading-lagging: 1 - Nicht unterschieden

## Zu evaluieren

```
{METRICS}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "success-metrics-quality",
  "checks": [
    {"id": "metrics-defined", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "baseline-present", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "target-specific", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "measurement-method", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "north-star", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-vanity-metrics", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "leading-lagging", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
