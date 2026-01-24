# Evaluation: Scope-Qualität (MoSCoW)

Du evaluierst eine **Scope-Sektion** gegen die Kriterien für klare Priorisierung und Abgrenzung.

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

1. **moscow-used** (required): Ist MoSCoW Priorisierung verwendet?
   - 5: Alle 4 Kategorien (Must/Should/Could/Won't) vorhanden
   - 3: 2-3 Kategorien vorhanden
   - 1: Keine Priorisierung oder nur "In Scope/Out of Scope"

2. **must-have-minimal** (required): Sind Must Haves auf Minimum reduziert?
   - 5: Nur das absolut Notwendige für MVP
   - 3: Einige "nice-to-haves" als Must markiert
   - 1: Alles ist Must Have

3. **wont-have-explicit** (required): Ist dokumentiert was NICHT gemacht wird?
   - 5: Klare Won't Have Liste mit konkreten Items
   - 3: Einige Ausschlüsse genannt
   - 1: Keine Ausschlüsse dokumentiert

4. **wont-have-reasoned** (required): Sind Gründe für Ausschlüsse angegeben?
   - 5: Jedes Won't Have Item hat Begründung
   - 3: Manche haben Begründung
   - 1: Keine Begründungen

5. **no-scope-creep** (optional): Sind Items in sich abgeschlossen?
   - 5: Jedes Item ist eigenständig, kein "und außerdem..."
   - 3: Einige Items sind überladen
   - 1: Items sind unklar abgegrenzt

6. **phases-defined** (optional): Sind Implementation Phases definiert?
   - 5: Klare Phasen (MVP → Iteration → Polish)
   - 3: Grobe Phasen angedeutet
   - 1: Keine Phasen

7. **dependencies-clear** (optional): Sind Abhängigkeiten dokumentiert?
   - 5: Abhängigkeiten zwischen Items klar
   - 3: Manche Abhängigkeiten erkennbar
   - 1: Keine Abhängigkeiten dokumentiert

## Beispiele

### Guter Scope (Score 5):
> ### Must Have (MVP)
> - [ ] CSV-Upload Endpoint (max 1000 Zeilen)
> - [ ] Validierung: Email-Format, Pflichtfelder
> - [ ] Fehler-Report nach Import
>
> ### Should Have (Iteration 1)
> - [ ] Progress-Bar während Import
> - [ ] Undo für letzte Import-Batch
>
> ### Could Have (Future)
> - [ ] Excel-Support (.xlsx)
> - [ ] API-basierter Import
>
> ### Won't Have
> - Realtime-Sync mit externen Systemen (Grund: Scope zu groß, eigenes Projekt)
> - LDAP/AD Integration (Grund: Enterprise-Tier Feature, andere Roadmap)

- moscow-used: 5 - Alle 4 Kategorien
- must-have-minimal: 5 - Nur Core-Funktionalität
- wont-have-explicit: 5 - Klare Ausschlüsse
- wont-have-reasoned: 5 - Begründungen vorhanden
- no-scope-creep: 5 - Items sind fokussiert
- phases-defined: 4 - Implizit durch Must/Should/Could
- dependencies-clear: 3 - Nicht explizit aber logisch

### Schlechter Scope (Score 1):
> "Wir bauen einen CSV-Import mit allen Features die User brauchen könnten."

- moscow-used: 1 - Keine Priorisierung
- must-have-minimal: 1 - "Alle Features" ist kein MVP
- wont-have-explicit: 1 - Keine Ausschlüsse
- wont-have-reasoned: 1 - Keine Begründungen
- no-scope-creep: 1 - Komplett offen
- phases-defined: 1 - Keine Phasen
- dependencies-clear: 1 - Keine Struktur

## Zu evaluieren

```
{SCOPE}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "scope-quality",
  "checks": [
    {"id": "moscow-used", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "must-have-minimal", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "wont-have-explicit", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "wont-have-reasoned", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "no-scope-creep", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "phases-defined", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "dependencies-clear", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
