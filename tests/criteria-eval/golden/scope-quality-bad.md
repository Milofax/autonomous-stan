# Golden Examples: Schlechter Scope

## Example 1: Keine Priorisierung
> "Wir bauen einen CSV-Import mit allen Features die User brauchen könnten."

**Expected Score: 1**
- moscow-used: 1 - Keine Priorisierung
- must-have-minimal: 1 - "Alle Features" ist kein MVP
- wont-have-explicit: 1 - Keine Ausschlüsse
- wont-have-reasoned: 1 - Keine Begründungen
- no-scope-creep: 1 - Komplett offen
- phases-defined: 1 - Keine Phasen
- dependencies-clear: 1 - Keine Struktur

---

## Example 2: Alles ist Must Have
> ### Must Have
> - Login System
> - Dashboard
> - Reporting
> - Analytics
> - Admin Panel
> - API
> - Mobile App
> - Offline Mode
> - Multi-Language
> - Dark Mode

**Expected Score: 2**
- moscow-used: 2 - Nur eine Kategorie
- must-have-minimal: 1 - Viel zu viel für MVP
- wont-have-explicit: 1 - Keine Ausschlüsse
- wont-have-reasoned: 1 - Keine Begründungen
- no-scope-creep: 3 - Items sind einzeln
- phases-defined: 1 - Keine Phasen
- dependencies-clear: 1 - Keine Struktur

---

## Example 3: Keine Won't Haves
> ### In Scope
> - User Management
> - Data Import
> - Reporting
>
> ### Out of Scope
> - (keine)

**Expected Score: 2**
- moscow-used: 2 - Nur In/Out Scope, kein MoSCoW
- must-have-minimal: 3 - Unklar was MVP ist
- wont-have-explicit: 1 - Explizit leer
- wont-have-reasoned: 1 - Keine Begründungen
- no-scope-creep: 4 - Items sind einzeln
- phases-defined: 1 - Keine Phasen
- dependencies-clear: 1 - Keine Struktur

---

## Example 4: Überladene Items
> ### Must Have
> - [ ] CSV-Import mit Validierung und Progress-Bar und Error-Handling und Rollback und Audit-Log und Email-Benachrichtigung

**Expected Score: 2**
- moscow-used: 2 - Nur Must Have
- must-have-minimal: 1 - Item ist überladen
- wont-have-explicit: 1 - Keine Ausschlüsse
- wont-have-reasoned: 1 - Keine Begründungen
- no-scope-creep: 1 - "und... und... und..."
- phases-defined: 1 - Keine Phasen
- dependencies-clear: 1 - Keine Struktur
