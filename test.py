import urllib.request, json

req = urllib.request.Request(
    'http://localhost:7777/rpc',
    data=json.dumps({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {
            'name': 'jarvis_end',
            'arguments': {
                'platform': 'claude',
                'narrative': 'Test seal'
            }
        }
    }).encode(),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as r:
    print(r.read().decode())