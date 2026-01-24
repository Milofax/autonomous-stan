# Evaluation: Requirements-Qualität (SMART)

Du evaluierst **Requirements/Akzeptanzkriterien** gegen die SMART-Prinzipien und Best Practices für testbare Anforderungen.

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

1. **specific** (required): Ist jedes Requirement spezifisch (WAS, nicht WIE)?
   - 5: Alle beschreiben WAS erreicht werden soll
   - 3: Manche mischen WAS und WIE
   - 1: Hauptsächlich Implementierungsdetails

2. **measurable** (required): Ist messbar wann das Requirement erfüllt ist?
   - 5: Alle haben klare Erfüllungskriterien
   - 3: Manche sind subjektiv
   - 1: Nicht messbar

3. **actor-capability** (required): Folgt das Format "[Akteur] kann [Fähigkeit]"?
   - 5: Alle folgen diesem Format
   - 3: Manche ohne Akteur oder Fähigkeit
   - 1: Kein erkennbares Format

4. **no-subjective** (required): Keine subjektiven Adjektive?
   - 5: Keine "schnell", "benutzerfreundlich", "schön"
   - 3: Wenige subjektive Begriffe
   - 1: Viele subjektive Adjektive

5. **no-implementation** (required): Keine Implementierungsdetails?
   - 5: Keine Technologie-Namen, Frameworks, Patterns
   - 3: Wenige technische Details
   - 1: Implementierung beschrieben statt Verhalten

6. **testable** (optional): Kann man Tests schreiben?
   - 5: Jedes Requirement ist direkt testbar
   - 3: Manche schwer zu testen
   - 1: Nicht testbar

7. **independent** (optional): Ist jedes Requirement unabhängig?
   - 5: Alle sind eigenständig
   - 3: Manche haben implizite Abhängigkeiten
   - 1: Stark verflochten

## Beispiele

### Gute Requirements (Score 5):
> - [ ] Admin kann CSV-Datei mit bis zu 1000 Zeilen hochladen
> - [ ] System validiert Email-Format für jede Zeile
> - [ ] Admin sieht Fehler-Report mit Zeilennummer und Fehlergrund
> - [ ] Import von 100 Usern ist in unter 30 Sekunden abgeschlossen

- specific: 5 - WAS, nicht WIE
- measurable: 5 - Klare Kriterien (1000 Zeilen, 30 Sekunden)
- actor-capability: 5 - "Admin kann", "System validiert"
- no-subjective: 5 - Keine subjektiven Begriffe
- no-implementation: 5 - Keine Technologie genannt
- testable: 5 - Jedes direkt testbar
- independent: 5 - Eigenständig

### Schlechte Requirements (Score 1):
> - Die App soll benutzerfreundlich sein
> - Performance muss gut sein
> - Wir nutzen React und PostgreSQL für schnelle Queries
> - Das UI soll schön aussehen

- specific: 1 - Vage
- measurable: 1 - "Benutzerfreundlich", "gut", "schön" nicht messbar
- actor-capability: 1 - Kein Akteur
- no-subjective: 1 - Voll mit subjektiven Adjektiven
- no-implementation: 1 - "React und PostgreSQL"
- testable: 1 - Wie testet man "schön"?
- independent: 2 - Unklar

## Zu evaluieren

```
{REQUIREMENTS}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "requirements-quality",
  "checks": [
    {"id": "specific", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "measurable", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "actor-capability", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-subjective", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-implementation", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "testable", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "independent", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
