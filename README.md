# KalkPilot by Janek

**[App online öffnen](https://kalkprofijanek.github.io/kalkpilot-by-janek/)** · **Version 1.1.1 BETA**

Statische Browser-App für den Vergleich von Leistungsverzeichnissen mit Referenzkalkulationen. Die Startseite leitet auf `KalkPilot_by_Janek.html` weiter. Auf einem Firmenrechner genügt ein aktueller Edge- oder Chrome-Browser; es werden keine Programme oder API-Schlüssel benötigt.

## Verwendung im Browser

1. Referenzen als JSON oder zusammengehörige LV-/Kalkulationsdateien laden.
2. Neues LV laden und Matching starten. Fachliche Unterschiede und unaufgelöste Bausteine prüfen.
3. Für eine manuelle KI-Prüfung **ChatGPT-Prüfpaket · BETA** herunterladen und selbst im freigegebenen ChatGPT-Browser hochladen. Die App überträgt keine Daten an KI-Dienste. Das Paket enthält Leistungsbeschreibungen und historische Kostenansätze; der Nutzer entscheidet über den Upload.
4. ChatGPT-Antwort als Review-Notizen einfügen und fachlich prüfen. Sie ändert keine Preise oder ausgewählten Positionen automatisch.
5. Referenzdaten regelmäßig mit **Sichern** als JSON herunterladen. IndexedDB gehört zum Browserprofil und zur Website-Adresse; Firmenrichtlinien, Browserwechsel oder das Löschen von Websitedaten können den lokalen Bestand entfernen.

Das Prüfpaket ist ein Referenzentwurf, keine geprüfte selbstständige Angebotskalkulation. Historische Werte, verschachtelte Bausteine und Faktoren benötigen eine fachlich bestätigte Berechnung. Nicht aufgelöste Bausteinpreise verhindern die automatische Übernahme; eine bewusste manuelle Auswahl bleibt möglich.

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
