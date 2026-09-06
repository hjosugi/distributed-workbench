import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ExampleTests(unittest.TestCase):
    def test_hadoop_streaming_and_empty_input(self):
        def run(relative, data):
            return subprocess.run([sys.executable, str(ROOT / relative)], input=data,
                                  text=True, capture_output=True, check=True, timeout=5).stdout
        mapped = run('examples/hadoop/mapper.py', (ROOT / 'data/events.jsonl').read_text())
        shuffled = '\n'.join(sorted(mapped.splitlines())) + '\n'
        self.assertEqual(run('examples/hadoop/reducer.py', shuffled), 'book\t3\npen\t3\n')
        self.assertEqual(run('examples/hadoop/reducer.py', ''), '')

    def test_lambda_valid_and_invalid_events(self):
        spec = importlib.util.spec_from_file_location('quote_handler', ROOT / 'examples/serverless/handler.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.handler(json.loads((ROOT / 'data/lambda-event.json').read_text()), None)
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(json.loads(result['body']), {'total': 3600})
        for body in [{'quantities': [True]}, {'quantities': [-1]}, {'quantities': []}, {}, 'invalid json']:
            with self.subTest(body=body):
                self.assertEqual(module.handler({'body': body}, None)['statusCode'], 400)

if __name__ == '__main__': unittest.main()
