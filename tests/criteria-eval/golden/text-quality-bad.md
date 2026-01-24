# Golden Examples: Schlechte Textqualität

## Example 1: Fülltext
> "Also grundsätzlich könnte man vielleicht irgendwie User importieren, wobei das natürlich davon abhängt ob man Admin ist oder nicht, und dann gibt es da verschiedene Möglichkeiten die man nutzen könnte, je nachdem was man so braucht."

**Expected Score: 1**
- clarity: 1 - Verwirrend
- structure: 1 - Keine Struktur
- concise: 1 - Viele Füllwörter
- audience: 2 - Unklar
- actionable: 1 - Keine Handlungen

---

## Example 2: Unstrukturiert
> Der Import funktioniert so dass man eine Datei hochlädt und dann werden die User angelegt aber manchmal gibt es Fehler und dann muss man die Datei anpassen und es gibt auch Limits also 1000 Zeilen maximal und die Datei darf nicht zu groß sein also unter 10MB und man braucht Admin-Rechte.

**Expected Score: 2**
- clarity: 2 - Verständlich aber mühsam
- structure: 1 - Ein Satz, keine Gliederung
- concise: 2 - Redundant
- audience: 2 - Unklar für wen
- actionable: 2 - Handlungen versteckt

---

## Example 3: Zu technisch
> Die CSV-Ingestierung erfolgt via POST /api/v1/users/import mit multipart/form-data Content-Type. Der Parser nutzt Papa Parse mit dynamicTyping:true. Validation erfolgt gegen JSON Schema draft-07. Errors werden als 422 mit RFC 7807 Problem Details zurückgegeben.

**Expected Score: 2**
- clarity: 3 - Für Entwickler klar
- structure: 3 - Vorhanden
- concise: 4 - Dicht
- audience: 1 - Falsche Zielgruppe für User-Doku
- actionable: 1 - Keine User-Aktionen

---

## Example 4: Widersprüchlich
> Der Import ist einfach und schnell. Es gibt viele Optionen und Konfigurationsmöglichkeiten. Die Datei wird validiert, außer wenn sie zu groß ist. Fehler werden gemeldet, manchmal.

**Expected Score: 2**
- clarity: 1 - Widersprüche ("einfach" vs "viele Optionen", "außer wenn", "manchmal")
- structure: 2 - Grobe Struktur
- concise: 3 - Kurz aber vage
- audience: 2 - Unklar
- actionable: 1 - Keine klaren Handlungen
