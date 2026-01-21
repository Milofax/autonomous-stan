# /stan build-template

Baue ein neues Template interaktiv.

## Anweisungen

1. Sammle Template-Informationen:
   - **Name:** Wie soll das Template heißen? (z.B. "api-spec", "story")
   - **Typ:** Welcher Typ? (manifest, prd, plan, custom)
   - **Beschreibung:** Wofür ist das Template?

2. Baue Template-Inhalt interaktiv:
   - Frage nach gewünschten Abschnitten
   - Für jeden Abschnitt:
     - Überschrift
     - Beschreibung was rein soll
     - Beispiel-Struktur

3. Am ENDE: Criteria verknüpfen
   - Liste verfügbare Criteria aus `criteria/` Verzeichnis
   - Zeige für jedes Criteria: Name + Beschreibung
   - MultiSelect: Welche Criteria sollen verknüpft werden?

4. Erstelle Template-Datei:
   ```yaml
   ---
   type: {type}
   criteria:
     - {selected_criteria_1}
     - {selected_criteria_2}
   ---

   # {Name}

   {Abschnitte}
   ```

5. Speichere in `templates/{name}.md.template`

6. Bestätige:
   ```
   Template erstellt: templates/{name}.md.template

   Verknüpfte Criteria:
   - {criteria_1}
   - {criteria_2}

   Nutzen mit: Referenziere in stan.md oder PRD
   ```

## Wichtig

- Template MUSS Frontmatter haben
- Criteria-Verknüpfung am ENDE, nicht am Anfang
- Beschreibungen, keine Prompts im Template
