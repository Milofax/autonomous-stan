# Golden Examples: Schlechte User Stories

## Example 1: Kein Format
> "User soll Daten importieren können."

**Expected Score: 1**
- format: 1 - Kein Story-Format
- user-perspective: 1 - "User" generisch
- acceptance-criteria: 1 - Keine
- testable: 1 - Nicht testbar
- small-enough: 2 - Unklar

---

## Example 2: Ohne Akzeptanzkriterien
> **Als** User **möchte ich** importieren **damit** es schneller geht.

**Expected Score: 2**
- format: 4 - Format erkennbar
- user-perspective: 1 - "User" generisch
- acceptance-criteria: 1 - Keine
- testable: 1 - "Schneller" nicht messbar
- small-enough: 3 - Unklar

---

## Example 3: Epic statt Story
> **Als** Admin
> **möchte ich** ein komplettes User-Management-System mit Import, Export, Rollen, Berechtigungen, Audit-Log, SSO-Integration und API
> **damit** ich alles verwalten kann.
>
> **Akzeptanzkriterien:**
> - [ ] Alles funktioniert

**Expected Score: 2**
- format: 3 - Format vorhanden aber überladen
- user-perspective: 3 - Rolle genannt
- acceptance-criteria: 1 - "Alles funktioniert" ist keine Kriterium
- testable: 1 - Nicht testbar
- small-enough: 1 - Viel zu groß (Epic)

---

## Example 4: Technische Story
> **Als** System **möchte ich** PostgreSQL nutzen **damit** Daten gespeichert werden.

**Expected Score: 2**
- format: 3 - Format verwendet
- user-perspective: 1 - "System" ist kein User
- acceptance-criteria: 1 - Keine
- testable: 2 - Implizit testbar
- small-enough: 4 - Klein genug
