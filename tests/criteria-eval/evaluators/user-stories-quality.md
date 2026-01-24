# Evaluation: User Stories Qualität

Du evaluierst **User Stories** gegen die Kriterien für gut formulierte, testbare Stories.

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

1. **format** (required): Folgen Stories dem "Als X möchte ich Y damit Z" Format?
   - 5: Alle Stories folgen dem Format exakt
   - 3: Format erkennbar aber unvollständig
   - 1: Kein erkennbares Format

2. **user-perspective** (required): Ist die User-Perspektive klar?
   - 5: Spezifische Rolle/Persona genannt
   - 3: Generische Rolle ("User")
   - 1: Keine User-Perspektive

3. **acceptance-criteria** (required): Hat jede Story Akzeptanzkriterien?
   - 5: Alle Stories haben konkrete Kriterien
   - 3: Manche Stories ohne Kriterien
   - 1: Keine Akzeptanzkriterien

4. **testable** (required): Sind die Akzeptanzkriterien testbar?
   - 5: Alle Kriterien sind direkt testbar
   - 3: Manche Kriterien schwer testbar
   - 1: Nicht testbar

5. **small-enough** (optional): Sind Stories klein genug für einen Sprint?
   - 5: Klar abgegrenzt, schätzbar
   - 3: Etwas groß aber machbar
   - 1: Epic-Größe, muss aufgeteilt werden

## Beispiele

### Gute User Stories (Score 5):
> **Story: Bulk User Import**
>
> **Als** Enterprise-Admin mit mehr als 50 Team-Mitgliedern
> **möchte ich** User via CSV-Datei importieren
> **damit** ich bei Quartals-Onboardings Zeit spare.
>
> **Akzeptanzkriterien:**
> - [ ] Admin kann CSV-Datei (max 1000 Zeilen, < 10MB) hochladen
> - [ ] System validiert Email-Format für jede Zeile
> - [ ] Fehlerhafte Zeilen erscheinen im Report mit Zeilennummer
> - [ ] Import von 100 Usern dauert < 30 Sekunden

- format: 5 - Exakt "Als... möchte ich... damit..."
- user-perspective: 5 - Spezifische Rolle mit Kontext
- acceptance-criteria: 5 - Vier konkrete Kriterien
- testable: 5 - Alle direkt testbar
- small-enough: 5 - Klar abgegrenzt

### Schlechte User Stories (Score 1):
> "User soll Daten importieren können."

- format: 1 - Kein Story-Format
- user-perspective: 1 - "User" zu generisch
- acceptance-criteria: 1 - Keine
- testable: 1 - Nicht testbar
- small-enough: 2 - Unklar

## Zu evaluieren

```
{USER_STORIES}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "user-stories-quality",
  "checks": [
    {"id": "format", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "user-perspective", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "acceptance-criteria", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "testable", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "small-enough", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
