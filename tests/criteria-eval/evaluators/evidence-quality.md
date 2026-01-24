# Evaluation: Evidenz-Qualität

Du evaluierst eine **Evidenz-Sektion** gegen die Kriterien für belastbare, nachvollziehbare Evidenz.

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

1. **sources-present** (required): Gibt es mindestens eine Evidenzquelle?
   - 5: Mehrere verschiedene Quellen (Research, Daten, Analogien)
   - 3: Eine Quelle vorhanden
   - 1: Keine Quellen, nur Behauptungen

2. **sources-cited** (required): Sind die Quellen nachvollziehbar?
   - 5: Datum, Methode, Sample Size dokumentiert
   - 3: Quelle genannt aber Details fehlen
   - 1: Vage Verweise ("Studien zeigen...")

3. **not-assumed** (required): Basiert die Evidenz auf Fakten?
   - 5: Nur verifizierte Fakten und Daten
   - 3: Mix aus Fakten und plausiblen Annahmen
   - 1: Hauptsächlich "ich glaube" oder Annahmen

4. **relevant-to-hypothesis** (required): Stützt die Evidenz die Hypothesis?
   - 5: Direkte Verbindung zur Hypothesis
   - 3: Indirekt relevant
   - 1: Keine erkennbare Verbindung

5. **contradictions-addressed** (optional): Werden Gegenargumente erwähnt?
   - 5: Gegenargumente genannt und adressiert
   - 3: Gegenargumente angedeutet
   - 1: Keine Gegenargumente

6. **recency** (optional): Ist die Evidenz aktuell?
   - 5: < 2 Jahre alt oder zeitlos
   - 3: 2-5 Jahre alt
   - 1: > 5 Jahre alt oder undatiert

## Beispiele

### Gute Evidenz (Score 5):
> **User Research:** 12 Interviews mit churned Enterprise-Kunden (Q4 2025) - 9 von 12 nannten "keine Bulk-Import Funktion" als Hauptgrund für Wechsel.
>
> **Marktanalyse:** 4 von 5 Konkurrenten (Competitor A, B, C, D) bieten CSV-Import. Competitor E ohne Import hat 30% niedrigere Retention (G2 Reviews, Dez 2025).
>
> **Interne Daten:** Support-Tickets zu "User anlegen" sind 340/Monat (23% aller Tickets). Durchschnittliche Anlage-Zeit pro User: 4.2 Min.
>
> **Gegenargument:** Manche User bevorzugen manuelle Anlage für Kontrolle - adressiert durch optionalen "Review vor Import" Schritt.

- sources-present: 5 - Research, Marktanalyse, interne Daten
- sources-cited: 5 - Zeiträume, Zahlen, Quellen genannt
- not-assumed: 5 - Alles durch Daten belegt
- relevant-to-hypothesis: 5 - Alle Punkte stützen Bulk-Import
- contradictions-addressed: 5 - Gegenargument genannt und gelöst
- recency: 5 - Q4 2025, Dez 2025

### Schlechte Evidenz (Score 1):
> "User wollen das bestimmt. Andere Apps haben das auch."

- sources-present: 1 - Keine echte Quelle
- sources-cited: 1 - Keine Details
- not-assumed: 1 - "Bestimmt" ist Annahme
- relevant-to-hypothesis: 1 - Keine Verbindung
- contradictions-addressed: 1 - Keine
- recency: 1 - Undatiert

## Zu evaluieren

```
{EVIDENCE}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "evidence-quality",
  "checks": [
    {"id": "sources-present", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "sources-cited", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "not-assumed", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "relevant-to-hypothesis", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "contradictions-addressed", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "recency", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
