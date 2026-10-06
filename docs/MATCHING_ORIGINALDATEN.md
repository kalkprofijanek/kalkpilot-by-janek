# Matching mit Originalreferenzen · 1.5.0 BETA

Version 1.5.0 ergänzt die Fachmerkmalprüfung um Tätigkeiten und Leistungsumfang. Liefern, Einbauen, Aufstellen, Umsetzen, Vorhalten, Entfernen, Lösen, Laden, Transportieren, Entsorgen und Verdichten werden getrennt betrachtet. Ein Bauzaun zum Umsetzen ist keine vollständige Aufbauleistung. Ein Transportansatz ohne Entsorgung kann nur ein Teilansatz sein. Explizite Ausschlüsse werden berücksichtigt; Synonyme wie Verlegen/Einbauen und Hinterfüllung herstellen/einbauen bleiben möglich. Die Erkennung ist eine Textmusterprüfung mit begrenztem Kontext, keine allgemeine semantische Freigabe.

Der KI-Auftrag enthält sämtliche aktiven Referenzen samt Kostenarten-/Gerätekennungen, Mengen, Einheiten, Faktoren und Leistungsfaktor-Flags. Gerätebausteine und Kostenarten beziehen Preise in i2 aus Stammdaten. Diese Verweise sind vorhandene Ansätze. Preise werden nicht geraten und nicht als fachliches Rangsignal verwendet. Vor der Antwort soll die LLM Gegenargumente zur ersten Auswahl prüfen. Preisbezogene Angaben werden im optionalen JSON-Feld `priceInformation` bzw. in der Excel-Spalte **Preishinweise** getrennt von fachlichen Unterschieden zurückgegeben.

Bei neu importierten GAEB-XML-Dateien wird vorhandener `LblTx`-Titelkontext separat exportiert. Er bleibt Hintergrund mit eigener Quelle und wird nicht automatisch zum Leistungsumfang einer Position. Nicht vorliegende Anlagen oder Querverweise werden nicht erfunden.

## Umfang und Grenzen der bisherigen Prüfung

- **69 gezielte synthetische Fachprüffälle**, einschließlich positiver Gegenbeispiele, Tätigkeitsabgrenzung, Negation, Einheiten, Rohrmaßen und Geotextilien. Die alte Merkmalsprüfung klassifiziert 51 korrekt, die neue 69. Das belegt Regressionen gegen diese Fälle, keine allgemeine LLM-Erfolgsquote.
- **1.527 Originalpositionen aus vier Projekten**, jede gegen alle anderen Projekte geprüft: **1.032.136 gerichtete Positionsvergleiche je vollständigem Lauf**. Das eigene Projekt und gelerntes/bereits eingebautes Matching-Wissen werden ausgeschlossen. Dieser Lauf untersucht die Regelrangfolge; er ruft kein Modell auf.
- **200 ausgewogene Originalfälle**, 50 je Projekt, als getrennte Browser-/Copilot-Prüfpakete vorbereitet. Je Paket sind alle Referenzen aus den anderen drei Projekten enthalten. Es werden keine engen Kandidatenlisten als vollständiger Vergleichsbestand ausgegeben.
- Die Erwartungsfelder dieser 200 Fälle bleiben zunächst leer und mit `unreviewed` gekennzeichnet. Ein Expertenbenchmark braucht unabhängig bestätigte Passungen, zulässige Teilansätze und Fälle ohne Treffer. Vorbereitete Fälle oder KI-Vorbewertungen werden nicht als fachlich bestätigte Fälle gezählt.
- Browser-/Cloud-Regressionen prüfen Stammdatenverweise ohne Score-Abzug, Trennung von Preis- und Fachfeedback, absolute Vergleichsbeträge, Titelkontext sowie Erhaltung der Gerätekennungen und Leistungs-/Kostenfaktoren im XML-Rundlauf.

Die größte der vier Projektteilmengen enthält rund 73 Prozent des Bestands. Ein Prüfsatz mit 50 Fällen je Projekt verhindert, dass allein diese Teilmenge die Bewertung dominiert. Die Aufgaben werden zusätzlich nach Leistungskategorien verteilt.

## Reproduzieren im Cloud-Terminal

Originaldateien und Ergebnisse bleiben außerhalb des öffentlichen Repositories:

```sh
.venv/bin/python scripts/matching_originals_cloud.py \
  --references /workspace/attachments/referenzen.json \
  --baseline-ref 6e2f42a \
  --output-dir /workspace/analysis/original-holdout

.venv/bin/python scripts/prepare_original_review_cloud.py \
  --references /workspace/attachments/referenzen.json \
  --rankings /workspace/analysis/original-holdout/holdout-rankings.json \
  --output-dir /workspace/analysis/original-review-packets
```

Der Dateipfad zur Referenzdatenbank ist anzupassen. Der erste Befehl erzeugt Ranglisten und einen unbewerteten Prüfsatz. Der zweite erzeugt vier Projektordner mit Referenz-JSON ohne Zielprojekt, ladbarem LV-Prüfauszug, vollständigem JSON-/Excel-Matching-Auftrag und getrennten fachlichen Bewertungsfeldern. Referenz-IDs sind lokal je Auftrag. Die erzeugten LV-Prüfauszüge dienen dem App-Test und sind keine zertifizierten Original-GAEB-Exporte.

## Test mit Microsoft 365 Copilot im Firmenbrowser

1. Einen Projektordner wählen. Dessen Referenz-JSON in KalkPilot laden; andere Projekte dürfen für diesen Prüflauf nicht aktiv sein.
2. `pruef-lv.x83` als neues LV laden.
3. `copilot-auftrag.xlsx` mit dem angezeigten KI-Auftrag in Microsoft 365 Copilot bearbeiten lassen. Alle Langtext- und Strukturspalten müssen berücksichtigt werden.
4. Die Antwort als Excel oder vollständige Tabelle in KalkPilot importieren. Preisbezug bleibt bei i2-Stammdaten; jede KI-Auswahl steht zur fachlichen Prüfung.
5. Erwartete Passung, zulässige Referenzen und fachlichen Grund erst nach unabhängiger Bewertung in `fachpruefung.json` ergänzen. Ergebnisse getrennt je Projekt/Leistungsfamilie auswerten.

Die größeren Arbeitsmappen wurden unabhängig als Exceldateien geprüft. Die tatsächliche Modellqualität und Upload-/Leselimits des firmeneigenen Microsoft-365-Copilot-Zugangs wurden hier nicht geprüft. Technisch vollständige Antwortzeilen beweisen nicht, dass die KI alle Referenzen gelesen hat.

[i2-Stammdaten, Geräteansätze und absolute Preisvergleiche](REFERENZPRUEFUNG.md) · [Bisherige Verbesserungslogik](MATCHING_VERBESSERUNGSLOGIK.md)
