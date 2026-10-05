# Referenz- und Preisprüfung · BETA

Historische Referenzen können fachlich passen, obwohl ihre Preisbasis unvollständig ist. Die App bezeichnet gespeicherte Werte deshalb als **ungeprüfte Ansatzsummen**, auch in CSV-Ausgaben. Eine manuelle oder automatische Referenzübernahme ist keine Preisfreigabe.

Die Prüfung zeigt offene Geräte-/Kalkulationsbausteine, fehlende oder ungültige Ansatzwerte, Nullpreise bei Mengenansätzen, abweichende Faktoren, deaktivierte Kostenzeilen und Pauschalierungen (`sItemLSum` / `sItemLSumAbs` in Subitems). Diese Auffälligkeiten verhindern eine automatische Referenzübernahme. Manuelle Übernahme und Original-XML-Export bleiben möglich; die ursprünglichen Preise und Kalkulationsdaten werden nicht verändert.

Im Positionsdetail erscheint ein Vergleich aktiver Referenzen mit gleichem normalisiertem Kurz- oder Langtext und gleicher Einheit. Stunden-Einheiten wie h und Std werden zusammengeführt. Kurze Sammeltexte und fehlende Einheiten reichen nicht aus. Die Anzeige enthält die ausgewählte Referenz und höchstens neun weitere Kandidaten, getrennte XML-/LV-Mengen, Text, Kostenzeilen und Prüfhinweise. Sie erzeugt weder einen Durchschnittspreis noch ein fachliches Gleichheitsurteil. Ein gleichlautender Standardtext kann unterschiedliche Leistungen begleiten.

Die App rekonstruiert noch keinen geprüften vollständigen Einheitspreis aus Leistungsfaktoren, Pauschalen, Gerätebausteinen und Zuschlägen. Dazu müssen die Rechenregeln des Ursprungssystems und dessen Kontrollwerte nachvollzogen werden. Faktoren dürfen nicht pauschal multipliziert oder dividiert werden. Ein Nullpreis kann eine beigestellte oder anderweitig enthaltene Leistung bezeichnen; er wird nicht automatisch als Fehler korrigiert.

Browser-Regressionen prüfen, dass Faktoren, Nullpreise und Pauschalansätze automatische Übernahmen blockieren, Vergleichskandidaten gleiche Einheiten besitzen, HTML in Referenzdaten nicht ausgeführt wird und Preise unverändert bleiben. Kundendaten gehören nicht ins Repository.
