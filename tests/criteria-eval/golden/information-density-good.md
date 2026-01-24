# Golden Examples: Gute Information Density

## Example 1: Technische Beschreibung
> "Admins importieren User via CSV. Das System validiert Email-Format und Pflichtfelder. Fehlerhafte Zeilen erscheinen im Report mit Zeilennummer. Import von 1000 Usern dauert unter 30 Sekunden."

**Expected Score: 5**
- no-filler: 5 - Keine Füllwörter
- no-conversational: 5 - Sachlich
- no-hedge-words: 5 - Keine Unsicherheit
- active-voice: 5 - "importieren", "validiert", "erscheinen", "dauert"
- concrete-verbs: 5 - Spezifische Verben
- no-redundancy: 5 - Keine Wiederholungen

---

## Example 2: Feature-Beschreibung
> "Der Bulk-Import ermöglicht CSV-Upload bis 1000 Zeilen. Validierung prüft Email-Format, Pflichtfelder und Duplikate. Fehler werden mit Zeilennummer und Grund gemeldet. Erfolgreiche Imports lösen Willkommens-Emails aus."

**Expected Score: 5**
- no-filler: 5 - Dicht
- no-conversational: 5 - Professionell
- no-hedge-words: 5 - Assertiv
- active-voice: 5 - "ermöglicht", "prüft", "werden gemeldet", "lösen aus"
- concrete-verbs: 5 - "ermöglicht", "prüft", "gemeldet", "lösen aus"
- no-redundancy: 5 - Keine Redundanz

---

## Example 3: Kurze Requirement-Liste
> - CSV-Upload: max 1000 Zeilen, < 10 MB
> - Validierung: Email-Format, Pflichtfelder
> - Fehler-Report: Zeilennummer + Grund
> - Performance: 100 User in < 30 Sekunden

**Expected Score: 5**
- no-filler: 5 - Telegram-Stil
- no-conversational: 5 - Rein sachlich
- no-hedge-words: 5 - Keine
- active-voice: 5 - Implizit aktiv
- concrete-verbs: 5 - N/A für Liste
- no-redundancy: 5 - Keine
