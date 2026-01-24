# Golden Examples: Guter Scope

## Example 1: Vollständiges MoSCoW
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

**Expected Score: 5**
- moscow-used: 5 - Alle 4 Kategorien
- must-have-minimal: 5 - Nur Core-Funktionalität
- wont-have-explicit: 5 - Klare Ausschlüsse
- wont-have-reasoned: 5 - Begründungen vorhanden
- no-scope-creep: 5 - Items fokussiert
- phases-defined: 4 - Implizit durch Must/Should/Could
- dependencies-clear: 3 - Logisch aber nicht explizit

---

## Example 2: Mit Dependencies
> ### Must Have (MVP)
> - [ ] User Login (OAuth) → Basis für alles
> - [ ] Dashboard View (abhängig von: Login)
> - [ ] Data Export CSV (abhängig von: Dashboard)
>
> ### Should Have
> - [ ] Dark Mode (unabhängig)
> - [ ] Keyboard Shortcuts (abhängig von: Dashboard)
>
> ### Could Have
> - [ ] Mobile App
>
> ### Won't Have
> - Offline-Mode (Grund: Architektur-Aufwand übersteigt Nutzen für MVP)
> - Multi-Tenancy (Grund: V2 Feature, benötigt DB-Redesign)

**Expected Score: 5**
- moscow-used: 5 - Alle Kategorien
- must-have-minimal: 5 - Basis-Features
- wont-have-explicit: 5 - Klar benannt
- wont-have-reasoned: 5 - Mit Begründung
- no-scope-creep: 5 - Fokussiert
- phases-defined: 4 - MVP/Iteration erkennbar
- dependencies-clear: 5 - Explizit dokumentiert
