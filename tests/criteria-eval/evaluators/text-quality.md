# Evaluation: Text-Qualität

Du evaluierst einen **Text** gegen die allgemeinen Qualitätskriterien für Dokumentation.

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

1. **clarity** (required): Ist der Text klar und verständlich?
   - 5: Sofort verständlich, keine Mehrdeutigkeit
   - 3: Verständlich aber stellenweise unklar
   - 1: Verwirrend oder mehrdeutig

2. **structure** (required): Hat der Text eine logische Struktur?
   - 5: Klare Gliederung, roter Faden erkennbar
   - 3: Struktur vorhanden aber ungleichmäßig
   - 1: Keine erkennbare Struktur

3. **concise** (required): Ist der Text prägnant ohne Füllwörter?
   - 5: Jedes Wort trägt zur Aussage bei
   - 3: Einige unnötige Formulierungen
   - 1: Aufgebläht mit Fülltext

4. **audience** (optional): Ist der Text für die Zielgruppe angemessen?
   - 5: Perfekt auf Zielgruppe zugeschnitten
   - 3: Größtenteils passend
   - 1: Falsche Tonalität/Fachebene

5. **actionable** (optional): Sind Handlungsaufforderungen klar?
   - 5: Klare nächste Schritte wo nötig
   - 3: Manche Handlungen unklar
   - 1: Keine klaren Handlungen

## Beispiele

### Guter Text (Score 5):
> ## Bulk User Import
>
> Enterprise-Admins können User via CSV importieren.
>
> ### Voraussetzungen
> - Admin-Rechte
> - CSV-Datei (max 1000 Zeilen, < 10MB)
>
> ### Ablauf
> 1. "Import" Button klicken
> 2. CSV-Datei auswählen
> 3. Vorschau prüfen
> 4. "Importieren" bestätigen
>
> ### Fehlerbehandlung
> Fehlerhafte Zeilen erscheinen im Report mit Zeilennummer und Grund.

- clarity: 5 - Sofort verständlich
- structure: 5 - Klare Gliederung (Voraussetzungen → Ablauf → Fehler)
- concise: 5 - Kein Wort zu viel
- audience: 5 - Für Admins passend
- actionable: 5 - Klare Schritte

### Schlechter Text (Score 1):
> "Also grundsätzlich könnte man vielleicht irgendwie User importieren, wobei das natürlich davon abhängt ob man Admin ist oder nicht, und dann gibt es da verschiedene Möglichkeiten die man nutzen könnte, je nachdem was man so braucht."

- clarity: 1 - Verwirrend, keine klare Aussage
- structure: 1 - Keine Struktur
- concise: 1 - Viele Füllwörter
- audience: 2 - Unklar für wen
- actionable: 1 - Keine klaren Handlungen

## Zu evaluieren

```
{TEXT}
```

## Output Format

Antworte NUR mit diesem JSON (keine Erklärung davor oder danach):

```json
{
  "criteria": "text-quality",
  "checks": [
    {"id": "clarity", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "structure", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "concise", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "audience", "score": <1-5>, "explanation": "<kurz>"},
    {"id": "actionable", "score": <1-5>, "explanation": "<kurz>"}
  ],
  "overall_score": <1-5>,
  "summary": "<1-2 Sätze Gesamtbewertung>",
  "passed": <true wenn alle required checks >= 4>
}
```
