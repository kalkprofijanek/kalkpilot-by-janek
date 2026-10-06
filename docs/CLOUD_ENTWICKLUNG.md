# KalkPilot mit Codex Cloud, Claude Code Web und Codespaces

## Gemeinsamer Ablauf

Der Firmenrechner benötigt nur den Browser. Entwicklungswerkzeuge, Python, Chromium und Testabhängigkeiten laufen in der jeweiligen Cloud-Maschine. Maßgeblicher Code liegt in GitHub; auf einem Feature-Branch arbeiten, Änderungen prüfen und über einen Pull Request zurückgeben. Kunden-LVs bleiben außerhalb von Git.

Diese Anleitung beschreibt Repository-Befehle; sie erzeugt keinen Codex-/Claude-Zugang und setzt keine Produktfreigaben des Unternehmens voraus. Unterstützte Repository-Verbindungen und die Cloud-Oberfläche werden beim jeweiligen Dienst eingerichtet.

## Codex Cloud oder Claude Code Web

1. Das GitHub-Repository und den gewünschten Branch als Projekt auswählen. Den vorhandenen Checkout verwenden; jede Cloud-Aufgabe ist bereits isoliert. Einen zusätzlichen Git-Worktree nur auf ausdrücklichen Wunsch erzeugen.
2. Im Cloud-Terminal aus dem Repository-Verzeichnis ausführen:

   ```sh
   bash scripts/setup-cloud.sh
   ```

   Die Installation liegt in `.venv`. Ist Chromium bereits vorhanden, wird es genutzt. Sonst lädt Playwright Chromium; notwendige Linux-Bibliotheken müssen im Cloud-Image vorhanden sein. Auf einem frischen Image mit entsprechenden Systemrechten kann `bash scripts/setup-cloud.sh --browser-deps` diese Voraussetzungen installieren. Netzwerk-/Credential-Sperren sind Cloud-Einstellungen und werden nicht durch die Skripte umgangen.

3. Entwicklungsserver starten:

   ```sh
   python3 scripts/dev.py
   ```

   Der Server verwendet Port 8000 und lauscht für Cloud-Portweiterleitungen auf `0.0.0.0`. Wenn Port 8000 belegt ist, den Prozess identifizieren; nur selbst gestartete Prozesse stoppen. Alternativ `--port 8001` wählen und den gleichen Port beim Healthcheck verwenden.

4. In einem zweiten Cloud-Terminal prüfen:

   ```sh
   python3 scripts/check_ready.py
   bash scripts/test-cloud.sh
   ```

   Für einen abweichenden Port unterstützt der Healthcheck `--url`, für die Startkonfiguration sind `KALKPILOT_HOST` und `KALKPILOT_PORT` vorgesehen. Es sind nicht geheime Entwicklungsvariablen; die App benötigt keine `.env` oder API-Secrets.

5. Die vom Cloud-Dienst angebotene Portvorschau verwenden, sofern diese Oberfläche eine Vorschau bereitstellt. Ein gestarteter Prozess allein erzeugt keine öffentlich erreichbare Webadresse. Fehlt die Portvorschau, denselben Branch in GitHub Codespaces öffnen oder die freigegebene Version über GitHub Pages benutzen.

6. Änderungen, Tests und verbleibende Abnahmen im PR festhalten. Cloud-Snapshots behalten keine laufenden Serverprozesse; nach einer neuen Sitzung den Entwicklungsserver erneut starten.

## GitHub Codespaces

1. In GitHub den Branch öffnen und **Code → Codespaces → Create codespace** wählen. Die Nutzung hängt von den GitHub-/Firmenfreigaben und verfügbaren Codespaces-Kontingenten ab.
2. `.devcontainer/devcontainer.json` verwendet ein Python-3.12-Image. `postCreateCommand` führt `scripts/setup-cloud.sh --browser-deps` aus; die Testwerkzeuge werden auf der Cloud-Maschine installiert.
3. Im Codespace-Terminal `python3 scripts/dev.py` starten.
4. Unter **Ports** den weitergeleiteten Port **8000 / KalkPilot** im Browser öffnen. Den Plattform-Standard **Private** beibehalten; die Konfiguration fordert keinen öffentlichen Port an.
5. Healthcheck und Tests wie oben ausführen. Eine lokale Python-, Node-, Docker- oder Editorinstallation auf dem Firmenrechner ist nicht nötig.

Codespaces-Vorschau und GitHub Pages haben unterschiedliche Website-Ursprünge. Der IndexedDB-Referenzbestand wird nicht automatisch geteilt. Mit **Sichern** eine JSON-Datei erstellen und in der anderen Oberfläche wieder laden.

## Veröffentlichung und KI-Nutzung

Das Repository verwendet bereits GitHub Pages aus `main` und der Repository-Wurzel. Ein Feature-Branch/PR veröffentlicht die neuen Änderungen noch nicht. Nach Review und Merge das vollständige statische Verzeichnis einschließlich `js/` und `vendor/` prüfen; es ist kein App-Build oder API-Backend erforderlich.

Codex/Claude Code kann sowohl das Repository entwickeln als auch als LLM selbst das fachliche Matching ausführen. Das Cloud-Werkzeug startet die echte Browser-App, bereitet den Auftrag vor und prüft die Antwort. Die LLM trifft die semantischen Entscheidungen dazwischen. Die öffentliche App importiert die konkreten Zuordnungen und ruft keine produktive KI-API auf. [Anleitung und Agenten-Auftrag](LLM_MATCHING.md).

## Was tatsächlich geprüft wurde

Die Skripte werden in der vorhandenen Codex-Cloud-Maschine ausgeführt. Die Regressionen prüfen den Entwicklungsserver auch aus einem anderen Arbeitsverzeichnis, tatsächliche Inhalte und die lokale Browser-Anwendung. Shell-Syntax, JSON und die offizielle Devcontainer-Spezifikation werden geprüft. Ein neuer Codespace, Claude-Code-Web-Zugang und die Portvorschau am tatsächlichen Firmenrechner wurden hier nicht gestartet bzw. extern verifiziert.

Aktuelle Ergebnisse für Version 1.4.0 BETA: alle **41 Regressionstests** bestanden. Die Devcontainer-JSON wurde gegen die offizielle Basisspezifikation validiert. Der Healthcheck prüft neun tatsächliche Inhalte statt nur einen offenen Port. Der reproduzierbare Fachmerkmalsvergleich und die Grenzen der Aussagekraft stehen in der [Matching-Verbesserungslogik](MATCHING_VERBESSERUNGSLOGIK.md).
