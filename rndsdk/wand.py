#coding:utf8
import time, random
from sdk import Operation

def test1(op):
    for i in range(10):
        time.sleep(3)
        op.send('bbb', 'hello world')

def test2(op):
    stock_map = {
            'aapl': 100.0,
            'wbai': 20.0,
            'goog': 165.0,
            'baid': 144.0,
            'jd': 33.0,
            'intr': 39.0,
            'shne': 178.0,
            'msft': 43.90,
            'txn': 47.05,
        }
    stock_copy = stock_map.copy()
    while 1:
        r = random.randint(1,100) / 200.0
        time.sleep(r)
        stock = random.choice(stock_map.keys())
        steps = random.randint(-100, 100) / 100.0
        org_price = stock_map[stock]
        latest_price = stock_copy[stock] + steps
        stock_copy[stock] = latest_price
        counts = latest_price - org_price
        rge = counts / org_price * 100.0
        #print stock, steps, org_price, latest_price, counts, rge
        op.send('stock', '%s,%.3g,%.3g,%.3g,%.3g' % (stock, latest_price, counts, rge, steps))



if __name__ == "__main__":
    op = Operation('localhost:9021')
    # test1(op)
    test2(op)
