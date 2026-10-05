# KalkPilot by Janek

Statische Browser-App für den Vergleich von Leistungsverzeichnissen mit Referenzkalkulationen. Die Startseite leitet auf `KalkPilot_by_Janek.html` weiter. Auf einem Firmenrechner genügt ein aktueller Edge- oder Chrome-Browser; es werden keine Programme oder API-Schlüssel benötigt.

## Verwendung im Browser

1. Referenzen als JSON oder zusammengehörige LV-/Kalkulationsdateien laden.
2. Neues LV laden und Matching starten. Fachliche Unterschiede und unaufgelöste Bausteine prüfen.
3. Für eine manuelle KI-Prüfung **ChatGPT-Prüfpaket · BETA** herunterladen und selbst im freigegebenen ChatGPT-Browser hochladen. Die App überträgt keine Daten an KI-Dienste. Das Paket enthält Leistungsbeschreibungen und historische Kostenansätze; der Nutzer entscheidet über den Upload.
4. ChatGPT-Antwort als Review-Notizen einfügen und fachlich prüfen. Sie ändert keine Preise oder ausgewählten Positionen automatisch.
5. Referenzdaten regelmäßig mit **Sichern** als JSON herunterladen. IndexedDB gehört zum Browserprofil und zur Website-Adresse; Firmenrichtlinien, Browserwechsel oder das Löschen von Websitedaten können den lokalen Bestand entfernen.

Das Prüfpaket ist ein Referenzentwurf, keine geprüfte selbstständige Angebotskalkulation. Historische Werte, verschachtelte Bausteine und Faktoren benötigen eine fachlich bestätigte Berechnung. Nicht aufgelöste Bausteinpreise verhindern die automatische Übernahme; eine bewusste manuelle Auswahl bleibt möglich.

## Bereitstellung

Den vollständigen Repository-Inhalt als statische Website bereitstellen, einschließlich `js/` und `vendor/`. Es gibt keinen Buildschritt und keine Laufzeit-CDNs. Nur die einzelne HTML-Datei zu kopieren reicht für diese Version nicht mehr. Bei Veröffentlichung über GitHub Pages bleibt der relative Pfad zu den lokalen Skripten gültig. Die vorhandene Produktionsveröffentlichung wird durch einen Feature-Branch nicht geändert.

## Entwicklung und Tests

```sh
python3 -m http.server 8000 --directory .
```

Browser-Regressionssuite mit synthetischen Daten:

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 -m unittest discover -s tests -v
```

Eine bereits installierte Chromium-Version kann über `KALKPILOT_CHROMIUM=/usr/bin/chromium` gewählt werden. Die Tests betreiben ihren eigenen temporären Webserver. Kundenreferenzen und Original-LVs gehören nicht ins Repository.

[Umbauplan und geprüfte GitHub-Projekte](docs/UMBAUPLAN.md) · [Drittanbieter-Lizenzen](THIRD_PARTY_NOTICES.md)
