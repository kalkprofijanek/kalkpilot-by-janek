"""The cloud agent runs the real app to prepare and validate matching files."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LLMCloudWorkflow(unittest.TestCase):
    def test_prepare_and_check_use_the_same_snapshot_and_reject_invented_ids(self):
        with tempfile.TemporaryDirectory(prefix='kalkpilot-llm-test-') as directory:
            data = Path(directory)
            references = data / 'refs.json'
            references.write_text(json.dumps([{'name': 'Synthetic', 'active': True,
                'positions': [{'oz': 'R1', 'kurztext': 'Baustelle einrichten', 'me': 'psch',
                               'menge': 1, 'kosten': [{'typ': 'L', 'menge': 1, 'preis': 12}]}]}]))
            lv = data / 'new.d83'
            lv.write_text('2101 01   1NNN         00000001000psch\n25Baustelle einrichten\n')
            command = [sys.executable, str(ROOT / 'scripts/llm_matching_cloud.py')]
            common = ['--references', str(references), '--lv', str(lv), '--output-dir', str(data / 'output')]
            prepared = subprocess.run(command + ['prepare'] + common,
                                      capture_output=True, text=True, timeout=60)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            request = json.loads((data / 'output/matching-request.json').read_text())
            response = {'schema': 'kalkpilot.llm-matches', 'schemaVersion': 1,
                        'requestId': request['requestId'], 'matches': [{
                            'targetId': 't1', 'status': 'matched', 'referenceIds': ['r1'],
                            'confidence': 'high', 'reason': 'Leistung und Einheit entsprechen einander.',
                            'differences': [], 'missingInformation': []}]}
            answer = data / 'answer.json'
            answer.write_text(json.dumps(response))
            checked = subprocess.run(command + ['check'] + common + ['--response', str(answer)],
                                     capture_output=True, text=True, timeout=60)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            report = json.loads((data / 'output/validation.json').read_text())
            self.assertEqual(report['suggested'], 1)
            self.assertEqual(report['accepted'], 0)
            self.assertFalse(report['priceApproval'])
            response['matches'][0]['referenceIds'] = ['invented']
            answer.write_text(json.dumps(response))
            invalid = subprocess.run(command + ['check'] + common + ['--response', str(answer)],
                                     capture_output=True, text=True, timeout=60)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn('Referenz-IDs', invalid.stderr)
