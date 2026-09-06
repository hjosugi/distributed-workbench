"""Real loopback DNS/UDP, framed TCP, and HTTPS experiments."""
import json
from pathlib import Path
import secrets
import socket
import ssl
import struct
import subprocess
import tempfile
import threading
from urllib.request import urlopen
from .server import make_server


def dns_roundtrip():
    # A one-name authoritative fixture, not a recursive resolver.
    query_id = secrets.randbelow(65536)
    question = b'\x06orders\x04test\x00' + struct.pack('!HH', 1, 1)
    request = struct.pack('!6H', query_id, 0x0100, 1, 0, 0, 0) + question
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(('127.0.0.1', 0))
        server.settimeout(3)
        def answer():
            raw, address = server.recvfrom(512)
            if raw != request: return
            header = struct.pack('!6H', query_id, 0x8500, 1, 1, 0, 0)
            record = b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 30, 4) + socket.inet_aton('127.0.0.1')
            server.sendto(header + question + record, address)
        thread = threading.Thread(target=answer, daemon=True)
        thread.start()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(3)
            client.sendto(request, server.getsockname())
            reply, source = client.recvfrom(512)
        thread.join(timeout=3)
        if source != server.getsockname() or struct.unpack('!H', reply[:2])[0] != query_id:
            raise ValueError('unexpected DNS response')
        return {'name': 'orders.test', 'A': socket.inet_ntoa(reply[-4:]), 'ttl': 30}


def recv_exact(stream, length):
    chunks = bytearray()
    while len(chunks) < length:
        part = stream.recv(length - len(chunks))
        if not part: raise EOFError('connection closed in the middle of a frame')
        chunks.extend(part)
    return bytes(chunks)


def tcp_roundtrip():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        listener.settimeout(3)
        def echo():
            connection, _ = listener.accept()
            with connection:
                connection.settimeout(3)
                size = struct.unpack('!I', recv_exact(connection, 4))[0]
                if size > 65536: return
                body = recv_exact(connection, size)
                connection.sendall(struct.pack('!I', len(body)) + body)
        thread = threading.Thread(target=echo, daemon=True)
        thread.start()
        with socket.create_connection(listener.getsockname(), timeout=3) as client:
            frame = struct.pack('!I', 5) + b'hello'
            client.sendall(frame[:2])
            client.sendall(frame[2:6])
            client.sendall(frame[6:])
            size = struct.unpack('!I', recv_exact(client, 4))[0]
            result = recv_exact(client, size).decode()
        thread.join(timeout=3)
        return {'echo': result, 'framing': '4-byte big-endian length prefix'}


def https_roundtrip():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        cert, key = root / 'cert.pem', root / 'key.pem'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-keyout', str(key), '-out', str(cert), '-days', '1',
                        '-subj', '/CN=localhost', '-addext', 'subjectAltName=DNS:localhost,IP:127.0.0.1'],
                       check=True, capture_output=True)
        with make_server('127.0.0.1', 0, root / 'orders.db') as server:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.load_cert_chain(cert, key)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            trusted = ssl.create_default_context(cafile=str(cert))
            try:
                with urlopen(f'https://127.0.0.1:{server.server_port}/health', context=trusted, timeout=3) as response:
                    body = json.load(response)
                try:
                    with socket.create_connection(('127.0.0.1', server.server_port), timeout=3) as raw:
                        with trusted.wrap_socket(raw, server_hostname='wrong.test'):
                            pass
                except ssl.SSLCertVerificationError:
                    mismatch_rejected = True
                else:
                    mismatch_rejected = False
                return {'https': body, 'wrong_hostname_rejected': mismatch_rejected}
            finally:
                server.shutdown()
                thread.join(timeout=3)


if __name__ == '__main__':
    print(json.dumps({'dns': dns_roundtrip(), 'tcp': tcp_roundtrip(), 'https': https_roundtrip()}, indent=2))
