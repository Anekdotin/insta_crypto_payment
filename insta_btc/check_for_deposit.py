from app import db
from app.classes.shipping import Orders
from app.classes.crypto import Transactions
import json

import requests
from passwords import btc_url
from app import floating_decimals


# check to see if any orders waiting for a bch deposit
def getincommingcoin():
    # standard json header
    headers = {'content-type': 'application/json'}

    # method and params
    rpc_input = {
        "method": "listunspent",
        "params":
            {
                "minconf": 0,
                "maxconf": 100,
            }
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "1.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        btc_url,
        data=json.dumps(rpc_input),
        headers=headers,
    )

    response_json = response.json()
    print(response_json)
    return response_json


def rpc_call_for_incomming_deposits():
    # get the json response
    response_json = getincommingcoin()

    # this is a complicated response
    # turns array of json object

    # turns array of json object
    for i in (response_json['result']):

        address = i['address']
        amount = i['amount']
        txid = i['txid']
        confirmations = i['confirmations']

        print(("txid: ", i['txid']))
        print(("amount: ", i['amount']))
        print(("address: ", i['address']))
        print(("confirmations: ", i['confirmations']))
        print("*"*10)

        amount_decimal_form = floating_decimals(amount, 8)
        howmanyconfs = int(confirmations)

        add_transaction = Transactions(
            blockheight=0,
            address=address,
            txid=txid,
            confirmations=howmanyconfs,
            amount_btc=amount_decimal_form,
            amount_xmr=0,
            amount_bch=0
        )

        db.session.add(add_transaction)
        db.session.flush()


def check_if_orders():

    rpc_call_for_incomming_deposits()

    counter = 0

    see_if_orders_waiting_for_deposit = db.session \
        .query(Orders) \
        .filter(Orders.status == 1,
                Orders.order_payment_type == 1) \
        .all()

    if see_if_orders_waiting_for_deposit:
        for f in see_if_orders_waiting_for_deposit:
            the_amount = f.total_cost_btc
            see_if_any_deposits = db.session\
                .query(Transactions)\
                .filter(Transactions.amount_btc == the_amount)\
                .first()

            if see_if_any_deposits:
                f.status = 2
                db.session.add(f)

                counter += 1

    if counter >= 1:
        db.session.commit()


if __name__ == "__main__":
    check_if_orders()