# Evaluation: Hypothesis-Qualität

Du evaluierst eine **Key Hypothesis** gegen die Kriterien für testbare, evidenzbasierte Hypothesen.

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

1. **structure** (required): Folgt die Hypothesis dem Format "Wir glauben... wenn wir... weil..."?
   - 5: Exakt dieses Format, alle drei Teile vorhanden
   - 3: Ähnliches Format, aber Teile fehlen oder unklar
   - 1: Kein erkennbares Format

2. **testable** (required): Ist die Hypothesis falsifizierbar?
   - 5: Klar widerlegbar durch Experiment/Daten
   - 3: Theoretisch testbar, aber schwer zu widerlegen
   - 1: Nicht falsifizierbar (z.B. "User werden es mögen")

3. **specific-target** (required): Ist die Zielgruppe spezifisch benannt?
   - 5: Konkrete Persona oder Segment (z.B. "Enterprise-Admins mit >50 Usern")
   - 3: Grobe Kategorie (z.B. "Admins")
   - 1: Generisch ("User", "alle", "Kunden")

4. **outcome-measurable** (required): Ist das erwartete Ergebnis messbar?
   - 5: Quantitativ messbar (z.B. "Conversion um 20% steigern")
   - 3: Qualitativ beschrieben aber beobachtbar
   - 1: Vage ("verbessern", "mögen", "besser")

5. **rationale-grounded** (required): Ist die Begründung durch Evidenz gestützt?
   - 5: Verweist auf konkrete Daten/Research
   - 3: Plausible Annahme, aber keine Evidenz genannt
   - 1: Keine Begründung oder nur Bauchgefühl

6. **single-focus** (optional): Testet die Hypothesis genau EINE Annahme?
   - 5: Eine klare Annahme
   - 3: Zwei verwandte Annahmen
   - 1: Mehrere vermischte Annahmen

## Beispiele

### Gute Hypothesis (Score 5):
> "Wir glauben, dass Enterprise-Admins mit mehr als 50 Usern ihre Onboarding-Zeit um 40% reduzieren werden, wenn wir Bulk-Import via CSV implementieren, weil 73% der befragten Admins in unserem Survey manuelle User-Anlage als größten Painpoint nannten."

- structure: 5 - Perfektes "Wir glauben... wenn wir... weil..." Format
- testable: 5 - 40% Reduktion ist messbar und widerlegbar
- specific-target: 5 - "Enterprise-Admins mit mehr als 50 Usern"
- outcome-measurable: 5 - "Onboarding-Zeit um 40% reduzieren"
- rationale-grounded: 5 - "73% der befragten Admins in unserem Survey"
- single-focus: 5 - Eine Annahme: Bulk-Import spart Zeit

### Schlechte Hypothesis (Score 1):
> "User werden das neue Design mögen."

- structure: 1 - Kein "Wir glauben... wenn wir... weil..." Format
- testable: 1 - "Mögen" ist nicht falsifizierbar
- specific-target: 1 - "User" ist generisch
- outcome-measurable: 1 - Keine Metrik
- rationale-grounded: 1 - Keine Begründung
- single-focus: 1 - Unklar was genau getestet wird

## Zu evaluieren

```
{HYPOTHESIS}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "hypothesis-quality",
  "checks": [
    {"id": "structure", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "testable", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "specific-target", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "outcome-measurable", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "rationale-grounded", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "single-focus", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
