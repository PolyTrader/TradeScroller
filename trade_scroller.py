import json
import csv
from datetime import datetime, timedelta
from time import sleep

import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def markets_by_id(data):
    markets = {}
    for mkt in data:
        markets[mkt["marketMakerAddress"].lower()] = mkt
    return markets


def gql_query(timestamp):
    transport = RequestsHTTPTransport(
        "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic"
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    with open("query.gql") as fp:
        query = gql(fp.read())

    return client.execute(query, {"ts": timestamp})


def show_transaction(trx, mkt, count, aliases):
    print(f"# {count} # ****************************************")
    print(mkt["question"])
    print(f"Id: {trx['id']}")
    user_address = trx["user"]["id"]
    if aliases:
        username = next((i[1] for i in aliases if i[0] == user_address), None)
    else:
        username = None

    if username:
        print(f"User: {username}")
    else:
        print(f"User: {user_address}")

    amount = float(trx["tradeAmount"]) / 1000000
    print(f"Amout: ${amount}")

    ts = int(trx["timestamp"])
    print(f"Timestamp: {datetime.utcfromtimestamp(ts)}")

    outcomeIndex = int(trx["outcomeIndex"])
    outcome = mkt["outcomes"][outcomeIndex]

    buy_or_sell = trx["type"]

    print(f"Action: {buy_or_sell} {outcome}")

    num_shares = float(trx["outcomeTokensAmount"]) / 1000000

    print(f"#shares: {num_shares}")


def main():
    r = requests.get("https://strapi-matic.poly.market/markets?_limit=-1&active=true")
    if r.status_code != requests.codes.ok:
        response.raise_for_status()

    markets = markets_by_id(r.json())

    try:
        with open("watchlist.txt") as f:
            watchlist = f.read().splitlines()
    except:
        watchlist = False

    try:
        with open("aliases.csv") as f:
            aliases = list(csv.reader(f))
    except:
        aliases = False

    count = 0
    timestamp = int(datetime.now().timestamp())
    while True:
        result = gql_query(timestamp)

        for trx in result["transactions"]:
            mkt = markets[trx["market"]["id"]]
            if watchlist:
                if mkt["question"] in watchlist:
                    show_transaction(trx, mkt, count, aliases)
            else:
                show_transaction(trx, mkt, count, aliases)
            count += 1

        try:
            timestamp = trx["timestamp"]
        except Exception:
            pass
        sleep(2.0)


if __name__ == "__main__":
    exit(main())
