# Golden Examples: Gute User Stories

## Example 1: Vollständige Story
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

**Expected Score: 5**
- format: 5 - Exaktes Format
- user-perspective: 5 - Spezifische Rolle mit Kontext
- acceptance-criteria: 5 - Vier konkrete Kriterien
- testable: 5 - Alle testbar
- small-enough: 5 - Klar abgegrenzt

---

## Example 2: Mehrere Stories
> **Story 1: CSV hochladen**
> **Als** Admin **möchte ich** CSV auswählen **damit** ich den Import starten kann.
> - [ ] File-Picker öffnet sich
> - [ ] Nur .csv Dateien wählbar
>
> **Story 2: Import-Vorschau**
> **Als** Admin **möchte ich** Vorschau sehen **damit** ich Fehler vor Import erkenne.
> - [ ] Erste 10 Zeilen werden angezeigt
> - [ ] Fehlerhafte Zeilen sind rot markiert
>
> **Story 3: Import bestätigen**
> **Als** Admin **möchte ich** Import bestätigen **damit** User angelegt werden.
> - [ ] "Importieren" Button aktiv wenn keine Fehler
> - [ ] Progress-Bar während Import

**Expected Score: 5**
- format: 5 - Alle folgen Format
- user-perspective: 5 - Konsistente Rolle
- acceptance-criteria: 5 - Jede Story hat Kriterien
- testable: 5 - Alle testbar
- small-enough: 5 - Gut aufgeteilt
