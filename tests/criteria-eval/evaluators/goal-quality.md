# Evaluation: Ziel-Qualität

Du evaluierst ein **Ziel** gegen die SMART-Kriterien.

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

1. **concrete** (required): Ist das Ziel konkret und spezifisch?
   - 5: Eindeutig, keine Interpretationsspielraum
   - 3: Verständlich aber vage Aspekte
   - 1: Unklar, zu abstrakt

2. **measurable** (required): Ist messbar wann das Ziel erreicht ist?
   - 5: Klare Metriken oder Erfolgskriterien definiert
   - 3: Implizit messbar aber nicht explizit
   - 1: Keine Messbarkeit erkennbar

3. **achievable** (required): Ist das Ziel realistisch erreichbar?
   - 5: Klar machbar mit gegebenen Ressourcen
   - 3: Ambitioniert aber möglich
   - 1: Unrealistisch oder unmöglich

4. **relevant** (required): Ist das Ziel relevant für das Projekt?
   - 5: Direkt auf Projektziel ausgerichtet
   - 3: Indirekt relevant
   - 1: Keine erkennbare Relevanz

5. **time-bound** (optional): Gibt es einen Zeitrahmen?
   - 5: Konkretes Datum oder Zeitraum
   - 3: Ungefährer Zeitrahmen ("bald", "Q2")
   - 1: Kein Zeitrahmen

## Beispiele

### Gutes Ziel (Score 5):
> "Bis Ende Q1 2026 eine REST API implementieren die 1000 Requests/Sekunde bei <100ms Latenz handhabt."

- concrete: 5 - REST API, spezifische Performance-Anforderungen
- measurable: 5 - 1000 req/s, <100ms klar messbar
- achievable: 5 - Standard-Anforderung, machbar
- relevant: 5 - API ist Kernfunktionalität
- time-bound: 5 - "Ende Q1 2026"

### Schlechtes Ziel (Score 1):
> "Die App soll besser werden."

- concrete: 1 - Was heißt "besser"?
- measurable: 1 - Keine Metrik
- achievable: 1 - Nicht bewertbar ohne Konkretisierung
- relevant: 1 - Zu vage für Relevanz-Bewertung
- time-bound: 1 - Kein Zeitrahmen

## Zu evaluieren

```
{GOAL}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "goal-quality",
  "checks": [
    {"id": "concrete", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "measurable", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "achievable", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "relevant", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "time-bound", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
