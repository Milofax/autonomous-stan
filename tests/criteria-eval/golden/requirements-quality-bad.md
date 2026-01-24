# Golden Examples: Schlechte Requirements

## Example 1: Subjektiv und vage
> - Die App soll benutzerfreundlich sein
> - Performance muss gut sein
> - Wir nutzen React und PostgreSQL für schnelle Queries
> - Das UI soll schön aussehen

**Expected Score: 1**
- specific: 1 - Vage
- measurable: 1 - "Benutzerfreundlich", "gut", "schön"
- actor-capability: 1 - Kein Akteur
- no-subjective: 1 - Voll subjektiv
- no-implementation: 1 - "React und PostgreSQL"
- testable: 1 - Nicht testbar
- independent: 2 - Unklar

---

## Example 2: Implementierungsdetails
> - Verwende Redis für Session-Caching
> - Implementiere JWT mit RS256 Algorithmus
> - Nutze PostgreSQL mit Connection Pooling
> - Setze Nginx als Reverse Proxy ein

**Expected Score: 2**
- specific: 3 - Technisch spezifisch
- measurable: 2 - Schwer messbar
- actor-capability: 1 - Kein Akteur
- no-subjective: 4 - Objektiv aber technisch
- no-implementation: 1 - Alles Implementierung
- testable: 3 - Technisch testbar
- independent: 2 - Technisch verflochten

---

## Example 3: Vermischt
> - User soll sich einloggen können (mit OAuth, Google, Apple, Email)
> - Dashboard muss schnell laden und schön sein
> - Export als CSV, Excel und PDF (nutze Apache POI)

**Expected Score: 2**
- specific: 3 - Teilweise spezifisch
- measurable: 2 - "Schnell", "schön" nicht messbar
- actor-capability: 3 - "User soll" ist okay
- no-subjective: 2 - "Schnell", "schön"
- no-implementation: 2 - "OAuth", "Apache POI"
- testable: 3 - Teilweise testbar
- independent: 3 - Vermischt
