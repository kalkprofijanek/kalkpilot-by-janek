# KalkPilot by Janek

**[App online öffnen](https://kalkprofijanek.github.io/kalkpilot-by-janek/)** · **Version 1.5.0 BETA**

**Neu in 1.5.0 BETA:** Leistungsumfang genauer prüfen, Geräte-/Kostenartenverweise und Leistungsfaktoren erhalten sowie Preis- und Fachfeedback trennen. 69 Fachprüffälle und ein projektübergreifender Lauf über 1.527 Originalpositionen; 200 Originalfälle für den Copilot-Test vorbereitet. [Prüfumfang und Browser-Ablauf](docs/MATCHING_ORIGINALDATEN.md).

**LLM-Matching:** Microsoft 365 Copilot kann per Excel-Upload im Firmenbrowser arbeiten. Codex oder Claude Code kann in der Cloud das neue LV anhand eurer Referenzen zuordnen. Die App exportiert den Matching-Auftrag und importiert konkrete Referenz-IDs mit fachlicher Begründung. [Browser- und Cloud-Ablauf](docs/LLM_MATCHING.md).

Statische Browser-App für den Vergleich von Leistungsverzeichnissen mit Referenzkalkulationen. Die Startseite leitet auf `KalkPilot_by_Janek.html` weiter. Auf einem Firmenrechner genügt ein aktueller Edge- oder Chrome-Browser; es werden keine Programme oder API-Schlüssel benötigt.

## Verwendung im Browser

1. Referenzen als JSON oder zusammengehörige LV-/Kalkulationsdateien laden und aktivieren.
2. Das neue GAEB-LV unter **② Matching → Neues LV hochladen** laden. Dateien unter **Referenzprojekte** dienen als Vergleichsdaten und ersetzen diesen Import nicht.
3. Unter **KI-Arbeitsweg** Microsoft 365 Copilot für Excel oder Codex/Claude für JSON wählen. Den Matching-Auftrag herunterladen und zusammen mit dem angezeigten Auftrag in der KI hochladen. [Copilot-Ablauf](docs/MATCHING_VERBESSERUNGSLOGIK.md) · [Cloud-Ablauf](docs/LLM_MATCHING.md).
4. Die Antwort über **KI-Antwort (Excel / JSON) importieren** laden oder als vollständige Tabelle einfügen. Die LLM wählt konkrete Referenzen; Preise bleiben unverändert und jede Position startet zur fachlichen Prüfung. Anschließend gewünschte Vorschläge übernehmen. Der optionale **Regelvergleich** ist ein zusätzlicher Vergleichsweg.
5. Referenzdaten regelmäßig mit **Sichern** als JSON herunterladen. IndexedDB gehört zum Browserprofil und zur Website-Adresse; Firmenrichtlinien, Browserwechsel oder das Löschen von Websitedaten können den lokalen Bestand entfernen.

Für eine zusätzliche manuelle Prüfung steht weiterhin **ChatGPT-Prüfpaket · BETA** bereit. Dessen Antwort kann als Review-Notiz eingefügt werden; dieser Notizweg verändert keine Zuordnungen. Beim LLM-Matching dagegen wird die strukturierte Antwort mit konkreten Referenz-IDs eingelesen. Uploads erfolgen ausschließlich durch den Nutzer; die App sendet keine Dateien an KI-Dienste.

Das Prüfpaket ist ein Referenzentwurf, keine geprüfte selbstständige Angebotskalkulation. Historische Werte, verschachtelte Bausteine und Faktoren benötigen eine fachlich bestätigte Berechnung. Kostenarten und Gerätepreise kommen beim i2-Import aus Stammdaten. Leere Exportpreise blockieren eine fachlich passende Referenz nicht allein; Kennungen, Mengen und Faktoren sind entscheidend.

## Bereitstellung

Der Workflow **Publish browser app** veröffentlicht den Branch **main** automatisch über GitHub Pages. Er führt zuerst die Browser-Tests aus und lädt anschließend nur die öffentlichen App-Dateien als Pages-Artefakt hoch. Der öffentliche App-Link lautet https://kalkprofijanek.github.io/kalkpilot-by-janek/. GitHub Pages muss auf **GitHub Actions** als Veröffentlichungsquelle eingestellt sein. Ein Feature-Branch allein ändert die Veröffentlichung nicht.

Den vollständigen Repository-Inhalt als statische Website bereitstellen, einschließlich `js/` und `vendor/`. Es gibt keinen Buildschritt und keine Laufzeit-CDNs. Nur die einzelne HTML-Datei zu kopieren reicht für diese Version nicht mehr. [Veröffentlichung und Prüfung](docs/VEROEFFENTLICHUNG.md).

## Entwicklung und Tests in der Cloud

Codex Cloud und Claude Code Web bearbeiten dieses Repository auf einem Branch. Alle folgenden Befehle laufen im **Cloud-Terminal**, nicht auf dem Firmenrechner:

```sh
bash scripts/setup-cloud.sh
python3 scripts/dev.py
```

Das Setup richtet die Testwerkzeuge in `.venv` ein. Der zweite Befehl startet die statische App auf Port 8000; Host und Port können über `--host`/`--port` oder `KALKPILOT_HOST`/`KALKPILOT_PORT` angepasst werden. Start und Nutzung der App benötigen keine API-Schlüssel.

In einem zweiten Cloud-Terminal:

```sh
python3 scripts/check_ready.py
bash scripts/test-cloud.sh
```

Der Healthcheck prüft tatsächliche App-Inhalte und lokale Skripte. Die Browser-Regressionssuite nutzt synthetische Daten und ihren eigenen temporären Webserver. Kundenreferenzen und Original-LVs gehören nicht ins Repository.

Für GitHub Codespaces ist `.devcontainer/devcontainer.json` enthalten: Das Cloud-Setup läuft automatisch; Port 8000 wird weitergeleitet. Im Codespace `python3 scripts/dev.py` starten und unter **Ports → 8000 → Im Browser öffnen** aufrufen. Der Port soll privat bleiben. Eine Vorschau hängt von der verwendeten Cloud-Oberfläche ab; wenn Codex/Claude keine Portvorschau anbietet, kann der gleiche Branch in Codespaces geöffnet werden.

[Cloud-Anleitung](docs/CLOUD_ENTWICKLUNG.md)

[Umbauplan und geprüfte GitHub-Projekte](docs/UMBAUPLAN.md) · [Architekturabgleich der Zusatzempfehlungen](docs/ARCHITEKTURABGLEICH.md) · [Drittanbieter-Lizenzen](THIRD_PARTY_NOTICES.md)

Referenzpreise erscheinen als **ungeprüfte Ansatzsummen**. Gerätebausteine sind zusammengesetzte Ansätze mit Preisbezug aus i2-Stammdaten. Im Positionsdetail lassen sich aktive Referenzen mit gleichem Text und gleicher Einheit vergleichen. Eine Referenzübernahme bestätigt keinen Angebotspreis.

Details zur [Referenz- und Preisprüfung](docs/REFERENZPRUEFUNG.md).

Die Positionsdetails trennen einfache historische Exportbeträge, i2-Stammdatenverweise, Leistungs-/Faktoransätze, ungültige Werte und ausgeschlossene Zeilen. Vergleichbare vollständige einfache Ansätze zeigen absolute Unterschiede pro Einheit und deren rechnerische Mengenwirkung; Preise verändern die fachliche Rangfolge nicht.

Das LLM-Matching-Paket enthält technische Fachmerkmale (Rohrdurchmesser, SDR, PE-Klasse, AVV und Einbauverfahren). Widersprüche und fehlende Anforderungen bleiben auch bei identischem Kurztext sichtbar.

Die gemeinsame Fachprüfung für Regelvergleich und KI-Import berücksichtigt außerdem ausdrücklich benannte Transportentfernungen und Förderwege. Meter und Kilometer werden vereinheitlicht; unterschiedliche eindeutige Strecken begrenzen die Passung als Fachwiderspruch. Fehlende Referenzangaben, Bereiche und Näherungswerte bleiben zur Prüfung offen. Die Erkennung erfasst direkt an Transportbegriffe angeschlossene Entfernungen, nicht beliebige Längen im Text.

Der vertiefte Matching-Ausbau prüft außerdem Rohrwerkstoffe, Maßeinheiten der Außendurchmesser, nachgestellte Leistungsausschlüsse und offene Abrechnungsbasen. Die Vorauswahl großer Referenzbestände berücksichtigt Fachwidersprüche vor dem Kürzen; die Sammelübernahme beachtet dieselben Fach-, Struktur- und Mehrdeutigkeitsprüfungen wie die automatische Übernahme. [Änderungen, Prüffälle und Grenzen](docs/MATCHING_VERTIEFUNG.md).

Ein erster Praxistest mit zwei öffentlichen X83-LVs umfasst 829 vollständig abgeglichene Importpositionen und 285.480 projektübergreifende Vergleiche je Lauf. Daraus entstanden Verbesserungen für DN/OD und Innenmaße, AVV-Schreibweisen, Tätigkeitsabgrenzung, Bauhöhen und Bogenwinkel sowie ein unbewerteter Prüfsatz mit 60 Fällen. [Quellen, Ergebnisse und Wiederholung](docs/OEFFENTLICHE_LV_PRUEFUNG.md).

[Codex-Arbeitsauftrag für die nächsten sechs Wochen](docs/CODEX_MATCHING_AUFTRAG.md): Arbeitspakete, Subagent-Rollen, fachliche Prüfkriterien und der Weg vom lokalen Stand über Pull Requests zur GitHub-Pages-Veröffentlichung.

## Matching-Prüflauf direkt aus dem Repository

In GitHub unter **Actions → Matching check → Run workflow** starten. Die Option **public_lvs** schaltet den Download und Vergleich der zwei öffentlichen Original-LVs ein. Auf Branches `codex/matching-*` startet der vollständige Prüflauf bereits beim Push. Die Aktion veröffentlicht die App nicht.

Der Lauf prüft Browser-/Cloud-Regressionen, synthetische Fachfälle sowie optional den Originalimport und die projektübergreifenden Vergleiche. Die öffentlichen Dateien werden anhand der Quellen in `config/public-lv-sources.json` abgerufen und per SHA-256 geprüft. Geänderte oder nicht mehr verfügbare Quellen führen zu einem sichtbaren Fehler. In GitHub werden ausschließlich Zähler, Quellennachweise und der synthetische Bericht als Artefakt gespeichert; Original-LVs und vollständige Prüfpakete werden nicht hochgeladen.

Lokal im Cloud-Terminal nach dem Setup:

```sh
python3 scripts/run_public_lv_check.py --output-dir /tmp/kalkpilot-public-check
```

Mit bereits vorhandenen Originalen ohne erneuten Download:

```sh
python3 scripts/run_public_lv_check.py \
  --source-dir /workspace/analysis/public-lv-review/originale \
  --output-dir /tmp/kalkpilot-public-check
```

Bei Verwendung der durch `scripts/setup-cloud.sh` angelegten Umgebung stattdessen `.venv/bin/python` verwenden. Lokal bleiben vollständige Importberichte, Ranglisten und Copilot-/JSON-Prüfpakete im gewählten Ausgabeordner verfügbar. Ohne Originaldaten lässt sich die synthetische Prüfung in GitHub mit deaktiviertem **public_lvs** starten. Ein neuer Workflow ist über die Actions-Oberfläche regulär verfügbar, sobald die Workflow-Datei im Standardbranch liegt; der Push-Auslöser funktioniert bereits auf dem passenden Feature-Branch.
