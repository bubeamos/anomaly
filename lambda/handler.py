import os
import json
import gzip
import base64
import urllib.request
from datetime import datetime, time

import boto3

sns = boto3.client('sns')
TOPIC_ARN          = os.environ['SNS_TOPIC_ARN']
IPINFO_TOKEN       = os.environ['IPINFO_TOKEN']
ALLOWED            = set(os.environ['ALLOWED_COUNTRIES'].split(','))
start_str, end_str = os.environ['DISALLOWED_TIME_WINDOW'].split('-')
t0 = time.fromisoformat(start_str)
t1 = time.fromisoformat(end_str)

def lookup_country(ip: str) -> str:
    url = f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
        return data.get('country', '??')
    except Exception:
        return '??'

def lambda_handler(event, context):
    # 1) Decode CloudWatch Logs payload
    data   = event['awslogs']['data']
    raw    = gzip.decompress(base64.b64decode(data))
    payload = json.loads(raw)

    alerts = []
    for ev in payload.get('logEvents', []):
        # pure JSON thanks to your subscription filter
        record = json.loads(ev['message'])

        ip = record['ip']
        ts = datetime.fromisoformat(record['timestamp'])
        now_t = ts.time()

        # Check country violation
        country = lookup_country(ip)
        is_bad_country = country not in ALLOWED

        # Check time-window violation
        if t0 <= t1:
            is_bad_time = (t0 <= now_t <= t1)
        else:
            is_bad_time = (now_t >= t0 or now_t <= t1)

        # Build reason
        if is_bad_country and is_bad_time:
            reason = 'country+time-window'
        elif is_bad_country:
            reason = 'country'
        elif is_bad_time:
            reason = 'time-window'
        else:
            # no violation → skip
            continue

        alerts.append({
            'ip':        ip,
            'country':   country,
            'timestamp': record['timestamp'],
            'reason':    reason
        })

    # Publish if any violations found
    if alerts:
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='🚨 Anomaly Login Alert Detected',
            Message=json.dumps(alerts, indent=2)
        )
