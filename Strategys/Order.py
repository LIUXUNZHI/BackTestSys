import socket
import json
import datetime
from DataBaseFun.DataBase import Trading_CONN
BEST_PRICE = 9999


def upload_order(code, vol, orderid, straid, method="Normal"):
    SQL = "INSERT INTO FUTURE_TRADE_ORDER VALUES ({0},{1},'{2}',{3},'{4}','{5}','{6}')".format(
        straid, orderid, code, vol, method, str(datetime.datetime.now())[:19], 'init'
    )
    cur = Trading_CONN.cursor()
    cur.execute(SQL)
    Trading_CONN.commit()

def send_order(code, price, vol, is_open, orderID, straID, **kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('10.0.0.87', 9876))
    order = {}
    order["code"] = code
    order["price"] = price
    order["vol"] = vol
    order["is_open"] = is_open
    order["ID"] = orderID
    order["AlgoID"] = orderID
    upload_order(code, vol, orderID, straID)
    if "method" in kwargs:
        order["method"] = kwargs["method"]
        if kwargs["method"] == "TWAP":
            order["batch"] = kwargs["batch"]
            order["interval"] = kwargs["interval"]
    js = json.dumps(order)
    s.send(bytes(js, 'UTF-8'))
    s.close()
    return

if __name__ == "__main__":
    send_order('cu1910', BEST_PRICE, 5,
              True, 4, 703, method="TWAP", batch=2, interval=10)
    #send_order('10001895', BEST_PRICE, -50,
               #False, 4, 703, method="TWAP", batch=5, interval=10)
'''
buffer = []
while True:
    d = s.recv(1024)
    if d:
        buffer.append(d)
    else:
        break
data = ''.join(buffer)

print(data)
'''

