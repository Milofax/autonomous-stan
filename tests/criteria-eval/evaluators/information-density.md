# Evaluation: Information Density

Du evaluierst einen **Text** gegen die Kriterien für dichte, klare Sprache ohne Füllwörter.

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

1. **no-filler** (required): Keine Füllwörter?
   - 5: Keine "sehr", "eigentlich", "grundsätzlich", "quasi", "halt", "irgendwie"
   - 3: Wenige Füllwörter
   - 1: Viele Füllwörter

2. **no-conversational** (required): Keine konversationelle Sprache?
   - 5: Keine "Lass uns...", "Ich denke...", "Vielleicht könnten wir..."
   - 3: Wenige konversationelle Phrasen
   - 1: Konversationell geschrieben

3. **no-hedge-words** (required): Keine Hedge-Wörter?
   - 5: Keine "vielleicht", "eventuell", "könnte sein", "möglicherweise"
   - 3: Wenige Hedge-Wörter
   - 1: Viele unsichere Formulierungen

4. **active-voice** (optional): Überwiegend Aktiv statt Passiv?
   - 5: Durchgehend aktive Formulierungen
   - 3: Mix aus Aktiv und Passiv
   - 1: Überwiegend Passiv

5. **concrete-verbs** (optional): Konkrete Verben?
   - 5: Keine generischen "machen", "tun", "haben", "sein"
   - 3: Wenige generische Verben
   - 1: Viele generische Verben

6. **no-redundancy** (optional): Keine redundanten Formulierungen?
   - 5: Keine "bereits schon", "neuen Innovation", "gemeinsam zusammen"
   - 3: Wenige Redundanzen
   - 1: Viele Redundanzen

## Beispiele

### Guter Text (Score 5):
> "Admins importieren User via CSV. Das System validiert Email-Format und Pflichtfelder. Fehlerhafte Zeilen erscheinen im Report mit Zeilennummer."

- no-filler: 5 - Keine Füllwörter
- no-conversational: 5 - Sachlich
- no-hedge-words: 5 - Keine Unsicherheit
- active-voice: 5 - "importieren", "validiert", "erscheinen"
- concrete-verbs: 5 - Spezifische Verben
- no-redundancy: 5 - Keine Wiederholungen

### Schlechter Text (Score 1):
> "Also, ich denke, wir könnten vielleicht irgendwie eine CSV-Import-Funktion machen. Das wäre eigentlich ganz gut, weil die User dann halt ihre Daten hochladen könnten. Grundsätzlich sollte das System dann quasi die Daten irgendwie verarbeiten."

- no-filler: 1 - "also", "eigentlich", "ganz", "halt", "grundsätzlich", "quasi", "irgendwie"
- no-conversational: 1 - "Ich denke", "wir könnten"
- no-hedge-words: 1 - "vielleicht", "irgendwie", "könnten"
- active-voice: 2 - Mix
- concrete-verbs: 1 - "machen", "wäre", "könnten"
- no-redundancy: 3 - Keine direkten Redundanzen

## Zu evaluieren

```
{TEXT}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "information-density",
  "checks": [
    {"id": "no-filler", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-conversational", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-hedge-words", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "active-voice", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "concrete-verbs", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-redundancy", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
