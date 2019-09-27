from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
from custom_indicators import *
from custom_functions import *


# Strategy:

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        """ Logging Function for This Strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        print(self.cross[0])

    def __init__(self):

        self.cheating = self.cerebro.p.cheat_on_open
        # Keep a reference to "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # Keep track of pending orders
        self.order = None

        # Add some idicators

        it = iTrend(self.datas[0],period=29)
        self.atr = bt.indicators.ATR()

        self.cross = bt.ind.CrossOver(it.trigger,it.itrend)

    def size_position(self, stop_amount, risk, method=0, exchange_rate=None, JPY_pair=False):

        price = self.data[0]
        stop = price - stop_amount
        risk = float(risk)/100.0

        if JPY_pair == True:  # check if a YEN cross and change the multiplier
            multiplier = 0.01
        else:
            multiplier = 0.0001

        # Calc how much to risk
        acc_value = self.broker.getvalue()
        cash_risk = acc_value * risk
        stop_pips_int = abs((price - stop) / multiplier)
        pip_value = cash_risk / stop_pips_int

        if method == 1:
            # pip_value = pip_value * price
            units = pip_value / multiplier
            return units

        elif method == 2:
            pip_value = pip_value * exchange_rate
            units = pip_value / multiplier
            return units

        else:  # is method 0
            units = pip_value / multiplier
            return units

    def notify_order(self, order):
        date = self.data.datetime.datetime().date()

        if order.status == order.Accepted:
            print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
            print('Order Accepted')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                date,
                order.status,
                order.ref,
                order.size,
                'NA' if not order.price else round(order.price, 5)
            ))

        if order.status == order.Completed:
            print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
            print('Order Completed')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                date,
                order.status,
                order.ref,
                order.size,
                'NA' if not order.price else round(order.price, 5)
            ))
            print('Created: {} Price: {} Size: {}'.format(bt.num2date(order.created.dt), order.created.price,
                                                          order.created.size))
            print('-' * 80)

        if order.status == order.Canceled:
            print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
            print('Order Canceled')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                date,
                order.status,
                order.ref,
                order.size,
                'NA' if not order.price else round(order.price, 5)
            ))

        if order.status == order.Rejected:
            print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
            print('WARNING! Order Rejected')
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                date,
                order.status,
                order.ref,
                order.size,
                'NA' if not order.price else round(order.price, 5)
            ))
            print('-' * 80)

    def notify_trade(self, trade):
        date = self.data.datetime.datetime()
        if trade.isclosed:
            print('-' * 32, ' NOTIFY TRADE ', '-' * 32)
            print('{}, Close Price: {}, Profit, Gross {}, Net {}'.format(
                date,
                trade.price,
                round(trade.pnl, 2),
                round(trade.pnlcomm, 2)))
            print('-' * 80)

    def operate(self, fromopen):

        if self.cross[0] > 0:
            if self.position:
                self.close()
            print('{} Send Buy, fromopen {}, close {}'.format(
                self.data.datetime.date(),
                fromopen, self.data.close[0])
            )
            self.order = self.buy(size=self.size_position(
                2.0, 1.0
            ))
            #self.sell(exectype=bt.Order.StopTrail, trailamount=2 * self.atr.atr[0])
        elif self.cross[0] < 0:
            if self.position:
                self.close()
            print('{} Send Sell, fromopen {}, close {}'.format(
                self.data.datetime.date(),
                fromopen, self.data.close[0])
            )
            self.order = self.sell(size=self.size_position(
                2.0, 1.0
            ))
            #self.buy(exectype=bt.Order.StopTrail, trailamount=2 * self.atr.atr[0])

    def next(self):

        date = self.data.datetime.date()
        close = self.data.close[0]

        print('{}: Close: ${}, Position Size: {}'.format(date, close, self.position.size))

        # Check to see if an order is pending. If so, we cannot create another

        if self.order:
            return

        if self.cheating:
            return
        self.operate(fromopen=True)

    def next_open(self):
        if not self.cheating:
            return
        self.operate(fromopen=True)



if __name__ == '__main__':

    # Create a cerebro entity
    cerebro = bt.Cerebro(cheat_on_open=True)

    # Add our strategy

    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    datapath = 'Data/NZDUSD_daily.csv'

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        openinterest=-1,
        dtformat='%d.%m.%Y %H:%M:%S.000'
    )


    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)


    # Set Commission:
    comminfo = forexSpreadCommisionScheme(spread=2, acc_counter_currency=False)
    cerebro.broker.addcommissioninfo(comminfo)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()

