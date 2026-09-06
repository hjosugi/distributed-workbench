"""AWS Lambda handler. This stateless quote function does not place an order."""
import json

def handler(event, context):
    try:
        body = event.get('body', {})
        body = json.loads(body) if isinstance(body, str) else body
        quantities = body['quantities']
        if not isinstance(quantities, list) or not 1 <= len(quantities) <= 100:
            raise ValueError('quantities must have 1..100 entries')
        if any(type(x) is not int or not 1 <= x <= 1000 for x in quantities):
            raise ValueError('quantities must be integers in 1..1000')
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'total': sum(quantities) * 1200})}
    except (KeyError, TypeError, ValueError):
        return {'statusCode': 400, 'body': json.dumps({'error': 'invalid quantities'})}

if __name__ == '__main__':
    print(json.dumps(handler({'body': {'quantities': [2, 1]}}, None)))
