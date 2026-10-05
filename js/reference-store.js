/* Local-only persistence. Dexie is vendored; no runtime CDN or server required. */
(() => {
  'use strict';
  let database;
  let writes = Promise.resolve();
  function db() {
    if (!database) {
      database = new Dexie('KalkPilotReferences');
      database.version(1).stores({ snapshots: '&id' });
    }
    return database;
  }
  function validate(projects) {
    if (!Array.isArray(projects)) throw new Error('Referenzprojekte müssen eine Liste sein.');
    for (const project of projects) {
      if (!project || typeof project.name !== 'string' || !Array.isArray(project.positions)) {
        throw new Error('Jedes Referenzprojekt benötigt Name und Positionsliste.');
      }
      for (const position of project.positions) {
        if (!position || typeof position.kurztext !== 'string' ||
            (position.kosten != null && !Array.isArray(position.kosten))) {
          throw new Error('Ungültige Referenzposition. Der vorhandene Bestand bleibt erhalten.');
        }
        for (const cost of position.kosten || []) {
          if (!cost || typeof cost !== 'object') throw new Error('Ungültige Kostenzeile.');
        }
      }
    }
    return projects;
  }
  window.KPReferenceStore = {
    validate,
    async load() {
      await writes;
      const saved = await db().snapshots.get('references');
      if (!saved) return null;
      if (saved.schema !== 1) throw new Error('Unbekannte Speicherversion; bitte Datensicherung prüfen.');
      return validate(JSON.parse(saved.json));
    },
    save(projects) {
      // Capture before awaiting: callers may subsequently change the live objects.
      const json = JSON.stringify(validate(projects));
      const operation = writes.catch(() => {}).then(() => db().snapshots.put({
        id: 'references', schema: 1, savedAt: new Date().toISOString(), json
      }));
      writes = operation;
      return operation;
    }
  };
})();
