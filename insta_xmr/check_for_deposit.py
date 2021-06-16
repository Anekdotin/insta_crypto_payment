from app import db
from app.classes.shipping import Orders
from app.classes.crypto import Transactions
from app.classes.monero import MoneroBlockHeight
import json
from requests.auth import HTTPDigestAuth
import requests
from passwords import xmr_url, xmr_rpc_password, xmr_rpc_username
from app import floating_decimals
from decimal import Decimal


def get_amount(amount):
    """
    decode cryptonote amount format to user friendly format.

    """

    cryptonote_display_decimal_point = 12
    str_amount = str(amount)
    fraction_size = 0

    if '.' in str_amount:
        point_index = str_amount.index('.')
        fraction_size = len(str_amount) - point_index - 1
        while fraction_size < cryptonote_display_decimal_point\
                and '0' == str_amount[-1]:
            str_amount = str_amount[:-1]
            fraction_size = fraction_size - 1
        if cryptonote_display_decimal_point < fraction_size:
            return False
        str_amount = str_amount[:point_index] + str_amount[point_index + 1:]
    if not str_amount:
        return False
    if fraction_size < cryptonote_display_decimal_point:
        str_amount = str_amount + '0' *\
                     (cryptonote_display_decimal_point - fraction_size)

    return str_amount


def get_money(amount):
    """
    decode cryptonote amount format to user friendly format.

    """

    cryptonote_display_decimal_point = 12
    s = amount

    if len(s) < cryptonote_display_decimal_point + 1:
        # add some trailing zeros, if needed, to have constant width
        s = '0' * (cryptonote_display_decimal_point + 1 - len(s)) + s
    idx = len(s) - cryptonote_display_decimal_point
    s = s[0:idx] + "." + s[idx:]

    return s


def checkincomming(fromblockheight):
    """
    Get rpc incomming deposts
    :param fromblockheight:
    :return:
    """
    # standard json header
    headers = {'content-type': 'application/json'}

    rpc_input = {
        "method": "get_bulk_payments",
        "params":
            {"payment_ids ": False,
             "min_block_height": fromblockheight}
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        xmr_url,
        data=json.dumps(rpc_input),
        headers=headers,
        auth=HTTPDigestAuth(xmr_rpc_username, xmr_rpc_password))

    response_json = response.json()

    return response_json


def searchjson():
    blockbacklog = 100
    current_blockheight_query = db.session.query(MoneroBlockHeight).get(1)
    current_block = current_blockheight_query.blockheight

    blocksfromcurrent = current_block - blockbacklog

    response_json = checkincomming(fromblockheight=blocksfromcurrent)

    if response_json is None or response_json["result"] == {}:
        print(response_json)
        print("no incomming")
    else:
        for incpayments in response_json["result"]["payments"]:

            new_transaction_blockheight = incpayments['block_height']
            howmanyconfirmations = current_block - new_transaction_blockheight
            incomming_address = incpayments['address']
            hashid = incpayments['tx_hash']
            amount_in_xmr = Decimal(get_money(str(incpayments['amount'])))

            add_transaction = Transactions(
                blockheight=new_transaction_blockheight,
                address=incomming_address,
                txid=hashid,
                confirmations=howmanyconfirmations,
                amount_btc=0,
                amount_xmr=amount_in_xmr,
                amount_bch=0
            )

            db.session.add(add_transaction)
            db.session.flush()


def find_new_deposits():
    searchjson()

    counter = 0

    see_if_orders_waiting_for_deposit = db.session \
        .query(Orders) \
        .filter(Orders.status == 1,
                Orders.order_payment_type == 3) \
        .all()

    if see_if_orders_waiting_for_deposit:
        for f in see_if_orders_waiting_for_deposit:
            the_amount = f.total_cost_xmr
            see_if_any_deposits = db.session\
                .query(Transactions)\
                .filter(Transactions.amount_xmr == the_amount)\
                .first()

            if see_if_any_deposits:

                f.status = 2
                db.session.add(f)

                counter += 1

    if counter >= 1:
        db.session.commit()


if __name__ == "__main__":
    find_new_deposits()