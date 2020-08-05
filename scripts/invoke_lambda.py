import boto3
import json
from datetime import datetime


today = datetime.today().strftime('%m/%d/%y')
payload = {'date': today}
client = boto3.client('lambda')
response1 = client.invoke(
    FunctionName='nba-matchups-daily',
    Payload=json.dumps(payload),
)
resp_payload = json.loads(response1['Payload'].read().decode('utf-8'))

if 'errorType' in resp_payload:
    print("-------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------")
    print("------------------------- VALIDATION FAILED -----------------------------")
    print("-------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------")
    print(resp_payload)

else:
    print("-------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------")
    print("------------------------ VALIDATION SUCCESS -----------------------------")
    print("-------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------")