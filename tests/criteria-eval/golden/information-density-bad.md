# Golden Examples: Schlechte Information Density

## Example 1: Füllwörter-Flut
> "Also, ich denke, wir könnten vielleicht irgendwie eine CSV-Import-Funktion machen. Das wäre eigentlich ganz gut, weil die User dann halt ihre Daten hochladen könnten. Grundsätzlich sollte das System dann quasi die Daten irgendwie verarbeiten."

**Expected Score: 1**
- no-filler: 1 - "also", "eigentlich", "ganz", "halt", "grundsätzlich", "quasi", "irgendwie"
- no-conversational: 1 - "Ich denke", "wir könnten"
- no-hedge-words: 1 - "vielleicht", "irgendwie", "könnten"
- active-voice: 2 - Mix
- concrete-verbs: 1 - "machen", "wäre", "könnten"
- no-redundancy: 3 - Keine direkten Redundanzen

---

## Example 2: Hedge-Words
> "Möglicherweise könnte eventuell ein CSV-Import vielleicht sinnvoll sein. Es wäre denkbar, dass User davon profitieren würden. Unter Umständen sollten wir das in Betracht ziehen."

**Expected Score: 1**
- no-filler: 2 - Wenige direkte Füller
- no-conversational: 3 - Passiv statt konversationell
- no-hedge-words: 1 - "Möglicherweise", "könnte", "eventuell", "vielleicht", "denkbar", "würden", "Unter Umständen"
- active-voice: 1 - Durchgehend Passiv/Konjunktiv
- concrete-verbs: 2 - "sein", "wäre", "sollten"
- no-redundancy: 2 - "Möglicherweise... eventuell... vielleicht"

---

## Example 3: Konversationell
> "Lass uns mal schauen, was wir so machen können. Ich würde sagen, vielleicht wäre es cool, wenn wir so einen Import hätten. Was meinst du? Könnte man ja mal ausprobieren."

**Expected Score: 1**
- no-filler: 2 - "mal", "so", "ja"
- no-conversational: 1 - "Lass uns", "Ich würde sagen", "Was meinst du"
- no-hedge-words: 1 - "vielleicht", "wäre", "könnte"
- active-voice: 2 - Mix
- concrete-verbs: 1 - "machen", "hätten", "ausprobieren"
- no-redundancy: 3 - Keine Redundanz

---

## Example 4: Redundant
> "Der neue innovative CSV-Import ermöglicht es, CSV-Dateien zu importieren. Diese Importfunktion importiert die Daten und verarbeitet sie zur Verarbeitung. Am Ende ist der Import dann abgeschlossen und fertig."

**Expected Score: 2**
- no-filler: 3 - Wenige Füller
- no-conversational: 4 - Sachlich
- no-hedge-words: 4 - Keine Hedge-Words
- active-voice: 4 - Aktiv
- concrete-verbs: 2 - "ermöglicht", aber viel "importiert/verarbeitet"
- no-redundancy: 1 - "Import importiert", "verarbeitet zur Verarbeitung", "abgeschlossen und fertig"
