from datetime import datetime
from time import sleep

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


def markets_by_id(data):
    markets = {}
    for mkt in data:
        try:
            markets[mkt["marketMakerAddress"].lower()] = mkt
        except AttributeError:
            pass
    return markets


def gql_query(timestamp):
    transport = RequestsHTTPTransport("https://api.thegraph.com/subgraphs/name/polymarket/matic-markets-7")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    with open("query.gql") as fp:
        query = gql(fp.read())

    return client.execute(query, {"ts": timestamp})


def show_transaction(trx, mkt, count):
    print(f"# {count} # ****************************************")
    print(mkt['question'])
    print(f"Id: {trx['id']}")
    print(f"User: {trx['user']['id']}")

    amount = float(trx['tradeAmount']) / 1000000
    print(f"Amount: ${amount:.6f}")

    ts = int(trx['timestamp'])
    print(f"Timestamp: {datetime.utcfromtimestamp(ts)}")

    outcomeIndex = int(trx['outcomeIndex'])
    outcome = mkt['outcomes'][outcomeIndex]
    buy_or_sell = trx['type']
    print(f"Action: {buy_or_sell} {outcome}")

    num_shares = float(trx['outcomeTokensAmount']) / 1000000
    print(f"#shares: {num_shares:.6f}")

    average = amount / num_shares
    print(f"Avg Cost: ${average:.6f}")


def main():
    r = requests.get("https://strapi-matic.poly.market/markets?_limit=-1&active=true")
    if r.status_code != requests.codes.ok:
        r.raise_for_status()

    markets = markets_by_id(r.json())

    try:
        with open("watchlist.txt") as f:
            watchlist = f.read().splitlines()
    except Exception:
        watchlist = False

    count = 0
    timestamp = int(datetime.now().timestamp())
    while True:
        result = gql_query(timestamp)

        for trx in result["transactions"]:
            mkt = markets[trx["market"]["id"]]
            if watchlist:
                if mkt["question"] in watchlist:
                    show_transaction(trx, mkt, count)
            else:
                show_transaction(trx, mkt, count)
            count += 1

        try:
            timestamp = trx['timestamp']
        except Exception:
            pass
        sleep(2.0)


if __name__ == "__main__":
    exit(main())
