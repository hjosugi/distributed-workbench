"""Real Kafka integration through the broker's official command-line clients."""
import json
from pathlib import Path
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ['docker', 'compose', 'exec', '-T', 'kafka']

def kafka(command, *args, data=None):
    result = subprocess.run(PREFIX + ['/opt/kafka/bin/' + command, '--bootstrap-server', 'kafka:9092', *args],
                            input=data, text=True, capture_output=True, cwd=ROOT, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout

topic = 'architect-' + uuid.uuid4().hex
kafka('kafka-topics.sh', '--create', '--topic', topic, '--partitions', '1', '--replication-factor', '1')
try:
    events = [json.loads(line) for line in (ROOT / 'data/events.jsonl').read_text().splitlines()]
    # Console producer uses --bootstrap-server as documented in Kafka 4.x.
    kafka('kafka-console-producer.sh', '--topic', topic, data=''.join(json.dumps(x) + '\n' for x in events))
    for group in ['analytics-' + topic, 'billing-' + topic]:
        raw = kafka('kafka-console-consumer.sh', '--topic', topic, '--group', group, '--from-beginning',
                    '--max-messages', str(len(events)), '--timeout-ms', '30000')
        actual = [json.loads(line) for line in raw.splitlines() if line.strip()]
        assert actual == events, (group, actual)
    print('PASS: Kafka publish, ordered consume, independent consumer groups')
finally:
    kafka('kafka-topics.sh', '--delete', '--topic', topic)
