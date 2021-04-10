import json

import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def markets_by_id(data):
    markets = {}
    for mkt in data:
        markets[mkt["marketMakerAddress"].lower()] = mkt
    return markets


def main():
    r = requests.get("https://strapi-matic.poly.market/markets?_limit=-1")
    if r.status_code != requests.codes.ok:
        response.raise_for_status()

    markets = markets_by_id(r.json())
    
    transport = RequestsHTTPTransport("https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    with open("query.gql") as fp:
        query = gql(fp.read())

    result = client.execute(query)

    out_json = json.dumps(result, indent=2)

    print(markets[result['transactions'][0]['market']['id']]['question'])
    print(result['transactions'][0]['user']['id'])
    print(result['transactions'][0]['tradeAmount'])

if __name__ == "__main__":
    exit(main())
