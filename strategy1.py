import sys
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt
from custom_indicators import *
from custom_functions import *
import BinaryGenerator as BG
import itertools


class strategy1(bt.Strategy):
    params = dict(
        base_ind='kijun',
        base_params=(40,),
        c1_ind='idosc',
        c1_params=(50,5),
        c2_ind='itrend',
        c2_params=(30,),
        volume_ind='wae',
        volume_params=(80, 20, 40, 20, 2.0, 3.7),
        exit_ind='ssl',
        exit_params=(50,),
        atr_period=14,
        sl=1.5,
        tp=1.0,
        risk=2.0
    )

    def log(self, txt, dt=None):
        """Logging Function"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        """Initialization"""

        # Basic Declarations
        self.dataclose = self.datas[0].close
        self.order = None
        self.open_orders = {
            'sl': [],
            'tp': []
        }

        # Money Management Indicators
        self.atr = bt.indicators.ATR(period=self.p.atr_period, plot=False)

        # Binary Indicator Generator
        ig = BG.IndicatorGenerator(self.data)

        # Generate Strategy Binary Indicators
        self.baseline, self.too_far = ig.baseline_indicator(self.p.base_ind, self.p.base_params, plot=False)
        self.c1 = ig.entry_indicator(self.p.c1_ind, self.p.c1_params, plot=False)
        self.c2 = ig.entry_indicator(self.p.c2_ind, self.p.c2_params, plot=False)
        self.volume = ig.volume_indicator(self.p.volume_ind, self.p.volume_params, plot=False)
        self.exit = ig.exit_indicator(self.p.exit_ind, self.p.exit_params, plot=False)

        self.butter = AdaptiveLaguerreFilter(self.data,length=10)

    def refresh_conditions(self):
        self.trade_conditons = {
            1.0: {
                'baseline': self.baseline > 0,
                'c1': self.c1 > 0,
                'c2': self.c2 > 0,
                'volume': self.volume > 0
            },

            -1.0: {
                'baseline': self.baseline < 0,
                'c1': self.c1 < 0,
                'c2': self.c2 < 0,
                'volume': self.volume < 0
            }

        }

    def decide_trade(self):

        buy = all(list(self.trade_conditons[1.0].values()))
        sell = all(list(self.trade_conditons[-1.0].values()))

        if buy:
            return 1.0
        elif sell:
            return -1.0
        else:
            return 0.0

    def clean_orders(self):

        # Clean Open Orders Dictionary
        for o in self.open_orders['sl']:
            if not o.alive():
                self.open_orders['sl'].remove(o)
        for o in self.open_orders['tp']:
            if not o.alive():
                self.open_orders['tp'].remove(o)

    def notify_order(self, order):

        # Call Custom Notification Function to Keep Code Clean
        date = self.data.datetime.datetime().date()
        notifier(order, date)
        self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):

        # Call Custom Notification Function to Keep Code Clean
        date = self.data.datetime.datetime().date()
        notifier(trade, date)

    def size_position(self, stop_amount, risk, method=0, exchange_rate=None, JPY_pair=False):

        price = self.data[0]
        stop = price - stop_amount
        risk = float(risk) / 100.0

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

    def pullback(self):

        # Baseline Crossing Logic (Did we go too far? Need to Look for a Pullback?)
        if self.baseline != 0.0 and self.too_far[0]:
            # Too far from baseline - no trading should occur
            print('CAUTION BASELINE CROSS TOO FAR - CHECKING FOR PULLBACK')
            self.trade_conditons[self.baseline[0]]['baseline'] = False
        elif self.baseline[-1] != 0.0 and self.too_far[-1] and not self.too_far[0]:
            # Previous Candle was a Baseline Cross more than 1xATR
            # We are currently not "too far" from the baseline
            print('PULLBACK DETECTED - BASELINE SAYS GO')
            self.trade_conditons[1.0]['baseline'] = self.baseline[-1]>0
            self.trade_conditons[-1.0]['baseline'] = self.baseline[-1]<0

    def continuation(self):

        # This is Where We Check the Logic for Continuation Trades
        # Check if Baseline Flip Just Occurred
        if self.baseline != 0.0:
            return None

        # Get last fifty bars of baseline flip data
        base_hist = list(self.baseline.get(size=30))
        base_hist.reverse()

        # Iterate through base flip history and get index of last flip:
        idx = next((i for i, x in enumerate(base_hist) if x != 0.0), None)

        if not idx:
            return None

        base = base_hist[idx]

        # Get Confirmation indicator Data since last baseline flip:
        c1_hist = list(self.c1.get(size=idx))
        c1_hist.reverse()

        # Check if a confirmation flip has been detected
        if -1.0 * base in c1_hist:
            flips = len(list(itertools.groupby(c1_hist, lambda c1_hist: c1_hist > 0))) - 1
            # Check if we have a double confirmation flip
            if flips == 2:
                # Continuation Opportunity Detected!
                # Double Check Confirmation Indicator 2
                if self.c2[0] == c1_hist[0]:
                    print('CONTINUATION TRADE DETECTED')
                    # Update the Corresponding Buy/Sell Conditions
                    for key in self.trade_conditons[self.c1[0]]:
                        self.trade_conditons[self.c1[0]][key] = True

    def bridge_too_far(self):

        # Determine how long ago last flip in C1 Occurred

        c1_hist = list(self.c1.get(size=10))
        c1_hist.reverse()

        try:
            idx = c1_hist.index(-1.0 * self.baseline) - 1
        except:
            idx = 100

        trade = self.decide_trade()
        if idx > 7 and trade != 0.0:
            print('BRIDGE TOO FAR, DO NOT TRADE')
            self.trade_conditons[trade]['c1'] = False

    def next(self):

        # Make Sure we have the most recent trading conditions:
        self.refresh_conditions()
        self.clean_orders()

        print(len(self.open_orders['sl']))
        print(len(self.open_orders['tp']))

        # Echo Current Closing Price
        self.log('Current Closing Price: %.5f' % self.dataclose[0])

        # Check if We have a Pending Order and Exit Function to Avoid Creating Duplicate
        if len(self.open_orders['sl']) > 0 or len(self.open_orders['tp']) > 0:
            return

        # Apply Strategy Trading Logic

        # Check if we are in the Market - Only Proceed if we are not
        if not self.position:

            # Check Pullback & Bridge too Far Logic
            if self.baseline != 0.0:
                self.pullback()
                self.bridge_too_far()

            # Continuation Trade Logic
            elif self.baseline == 0.0:
                self.continuation()

            # Check Entry Conditions & Place Trades

            if self.decide_trade() > 0.0:
                # Enter Long Position
                # Calculate Risk Profile
                size = round(self.size_position(self.p.sl * self.atr, self.p.risk)/2)
                price = self.dataclose
                tp = price + self.p.tp * self.atr
                sl = price - self.p.sl * self.atr

                # Generate Bracket Orders
                # Bracket 1: To Scale Out at Break Even
                main = self.buy(size=2*size,
                                exectype=bt.Order.Market,
                                transmit=False)
                stop_loss = self.sell(size=2*size,
                                      exectype=bt.Order.Stop,
                                      price=sl,
                                      parent=main,
                                      transmit=False)
                take_profit = self.sell(size=size,
                                        exectype=bt.Order.Limit,
                                        price=tp,
                                        parent=main,
                                        transmit=True)

                self.open_orders['sl'].append(stop_loss)
                self.open_orders['tp'].append(take_profit)

            elif self.decide_trade() < 0.0:
                # Enter Long Position
                # Calculate Risk Profile
                size = round(self.size_position(self.p.sl * self.atr, self.p.risk)/2)
                price = self.dataclose
                tp = price - self.p.tp * self.atr
                sl = price + self.p.sl * self.atr

                # Generate Bracket Orders
                # Bracket 1: To Scale Out at Break Even
                main = self.sell(size=2*size,
                                 exectype=bt.Order.Market,
                                 transmit=False)
                stop_loss = self.buy(size=2*size,
                                     exectype=bt.Order.Stop,
                                     price=sl,
                                     parent=main,
                                     transmit=False)
                take_profit = self.buy(size=size,
                                       exectype=bt.Order.Limit,
                                       price=tp,
                                       parent=main,
                                       transmit=True)

                self.open_orders['sl'].append(stop_loss)
                self.open_orders['tp'].append(take_profit)

        else:


            buyexit_conds = [self.exit > 0]
            sellexit_conds = [self.exit < 0]

            if self.position.size > 0:
                # Check for Sell Exit Signal
                if any(sellexit_conds):
                    self.order = self.close()

            elif self.position.size < 0:
                # Check for Buy Exit Signal
                if any(buyexit_conds):
                    self.order = self.close()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add our strategy

    cerebro.addstrategy(strategy1)

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

    # Add Analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Set Commission:
    comminfo = forexSpreadCommisionScheme(spread=2, acc_counter_currency=False)
    cerebro.broker.addcommissioninfo(comminfo)
    cerebro.broker.setcommission(leverage=20)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    strategies = cerebro.run()
    firstStrat = strategies[0]

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # print the analyzers
    printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())
    printSQN(firstStrat.analyzers.sqn.get_analysis())

    cerebro.plot(style='candle')
