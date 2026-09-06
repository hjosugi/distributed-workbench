"""Send sample structured logs to the local Logstash TCP input."""
import json
import socket
import time
with socket.create_connection(('127.0.0.1', 5000), timeout=5) as connection:
    for status in [201, 200, 409]:
        event = {'timestamp': time.time(), 'service': 'orders', 'status': status,
                 'request_id': f'fixture-{status}', 'duration_ms': 12}
        connection.sendall(json.dumps(event).encode() + b'\n')
print('Sent 3 logs; search architect-logs-* in Kibana.')
