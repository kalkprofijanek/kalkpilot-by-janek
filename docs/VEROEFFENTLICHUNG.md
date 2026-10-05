# KalkPilot online verwenden und veröffentlichen

**[App öffnen](https://kalkprofijanek.github.io/kalkpilot-by-janek/)**

Die App läuft als statische Website auf GitHub Pages. Auf dem Firmenrechner genügt ein aktueller Edge oder Chrome. Referenzen werden lokal im Browserprofil gespeichert; die App lädt keine Kundendateien auf GitHub oder zu einem KI-Anbieter hoch. Für ChatGPT wird das Prüfpaket heruntergeladen und anschließend vom Nutzer im ChatGPT-Browser hochgeladen.

## Release aus Codex Cloud oder Claude Code Web

1. Änderungen auf einem Branch bearbeiten; Original-LVs und Referenzdaten außerhalb des Repositorys behalten.
2. `bash scripts/test-cloud.sh` ausführen und Pull Request pushen. Die GitHub-Actions-Browserprüfung muss erfolgreich sein.
3. Den geprüften Pull Request nach `main` mergen. Unter **Settings → Pages → Build and deployment → Source** ist **GitHub Actions** eingestellt. Der Workflow **Publish browser app** prüft den Stand erneut und veröffentlicht automatisch. Bei Bedarf kann derselbe Workflow unter Actions manuell gestartet werden.
4. In GitHub unter **Actions** und **Settings → Pages** den erfolgreichen Build prüfen. Die App am obigen Link öffnen; Version kontrollieren und testweise ein LV sowie Referenzen laden.

Im Cloud-Terminal kann der tatsächlich veröffentlichte Commit geprüft werden:

```sh
gh run list --repo kalkprofijanek/kalkpilot-by-janek --workflow pages.yml --limit 1
python3 scripts/check_ready.py --url https://kalkprofijanek.github.io/kalkpilot-by-janek
```

Der erste Befehl prüft den Veröffentlichungsworkflow, der zweite die sieben öffentlich ausgelieferten App-Dateien. Für den zweiten Befehl muss die Cloud-Umgebung `kalkprofijanek.github.io` erreichen dürfen. Ein Netzwerkverbot in der Entwicklungsumgebung sagt nichts über die Erreichbarkeit im Firmenbrowser aus. Die Freigabe einer Cloud-Domain und die Veröffentlichung der App sind getrennte Vorgänge.

## Daten und BETA-Status

Die öffentliche Seite und eine Codespaces-Vorschau haben verschiedene Website-Adressen und damit getrennte lokale Datenbestände. Vor Browser-/Profilwechsel eine JSON-Sicherung herunterladen und anschließend importieren. Ein Update unter derselben Adresse übernimmt keine Daten aus einer anderen Adresse.

Ähnlichkeitspunkte sind keine Wahrscheinlichkeit für einen richtigen Preis. Fachliche Deckel bleiben bei verknüpften D83-Treffern und Projektboni wirksam. Die Detailansicht und das ChatGPT-Prüfpaket zeigen Referenz, Ähnlichkeit, Fachprüfung, offene Kalkulationsdaten und Übernahmeprüfung getrennt. Eine ausgewählte Referenz ist kein freigegebener Angebotspreis.

Der selbstständige Kalkulationsentwurf bleibt **BETA**. Vollständige Ressourcen-/Bausteinkataloge, geprüfte iTWO-Faktorsemantik und bestätigte Vergleichsergebnisse fehlen weiterhin. Die Prüfung am tatsächlichen Firmenrechner und ein iTWO-Reimport bleiben fachliche Abnahmen.
