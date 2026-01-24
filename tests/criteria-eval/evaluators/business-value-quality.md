# Evaluation: Business Value Qualität

Du evaluierst eine **Business Value Sektion** gegen die Kriterien für klaren Geschäftswert und Problemdefinition.

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

1. **value-clear** (required): Ist der Mehrwert für User/Business klar formuliert?
   - 5: Konkreter, quantifizierbarer Mehrwert
   - 3: Mehrwert erkennbar aber vage
   - 1: Kein erkennbarer Mehrwert

2. **problem-defined** (required): Ist das Problem klar beschrieben?
   - 5: Problem konkret mit Auswirkungen beschrieben
   - 3: Problem angedeutet
   - 1: Kein Problem definiert

3. **jtbd-defined** (required): Sind Jobs to Be Done dokumentiert?
   - 5: Konkrete Jobs mit Situation → Motivation → Ergebnis
   - 3: Jobs angedeutet aber nicht strukturiert
   - 1: Keine Jobs to Be Done

4. **context-explained** (required): Ist der Kontext klar (Warum jetzt)?
   - 5: Auslöser und Timing klar dokumentiert
   - 3: Kontext teilweise erklärt
   - 1: Kein Kontext

5. **stakeholders-identified** (optional): Sind Stakeholder/Zielgruppen identifiziert?
   - 5: Alle Betroffenen mit Rollen genannt
   - 3: Hauptzielgruppe genannt
   - 1: Keine Stakeholder

6. **alternatives-considered** (optional): Wurden Alternativen betrachtet?
   - 5: Alternativen genannt und bewertet
   - 3: Alternativen erwähnt
   - 1: Keine Alternativen

## Beispiele

### Guter Business Value (Score 5):
> **Problem:** Enterprise-Admins verbringen durchschnittlich 4.2 Minuten pro User-Anlage. Bei Teams mit 50+ Usern bedeutet das >3.5 Stunden Onboarding-Zeit pro Quartal.
>
> **Mehrwert:** Zeitersparnis von 3+ Stunden pro Quartal für Enterprise-Admins. Reduzierte Support-Tickets (aktuell 340/Monat).
>
> **Jobs to Be Done:**
> | Job | Situation | Motivation | Ergebnis |
> |-----|-----------|------------|----------|
> | Team schnell onboarden | Neues Quartal, neue Mitarbeiter | Schnell produktiv werden | Alle haben Zugang in <1h |
>
> **Kontext:** Q1 2026 - Zwei Enterprise-Kunden haben wegen fehlendem Bulk-Import gekündigt.
>
> **Stakeholder:** Enterprise-Admins (primär), IT-Abteilung (sekundär), neue Mitarbeiter (betroffen).

- value-clear: 5 - Quantifiziert (3.5h, 340 Tickets)
- problem-defined: 5 - Konkret mit Auswirkungen
- jtbd-defined: 5 - Strukturierte JTBD-Tabelle
- context-explained: 5 - Timing und Auslöser klar
- stakeholders-identified: 5 - Alle genannt mit Rollen
- alternatives-considered: 3 - Nicht explizit genannt

### Schlechter Business Value (Score 1):
> "Das Feature wäre gut zu haben."

- value-clear: 1 - Kein konkreter Mehrwert
- problem-defined: 1 - Kein Problem genannt
- jtbd-defined: 1 - Keine Jobs
- context-explained: 1 - Kein Kontext
- stakeholders-identified: 1 - Keine Stakeholder
- alternatives-considered: 1 - Keine Alternativen

## Zu evaluieren

```
{BUSINESS_VALUE}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "business-value-quality",
  "checks": [
    {"id": "value-clear", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "problem-defined", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "jtbd-defined", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "context-explained", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "stakeholders-identified", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "alternatives-considered", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
