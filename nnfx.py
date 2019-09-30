import sys
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt
from custom_indicators import *
from custom_functions import *
import BinaryGenerator as BG
import itertools
import time
import os
import glob


class NNFX(bt.Strategy):
    params = dict(
        base_ind='itrend',
        base_params=(40,),
        c1_ind='itrend',
        c1_params=(40,),
        c2_ind='cmf',
        c2_params=(35,),
        volume_ind='wae',
        volume_params=(80, 20, 40, 20, 2.0, 3.7),
        exit_ind='ssl',
        exit_params=(30,),
        atr_period=14,
        sl=1.5,
        tp=1.0,
        risk=2.0,
        oneplot=False,
        verbose=False,
    )

    def log(self, txt, dt=None):
        """Logging Function"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        """Initialization"""

        # Strategy Declarations
        self.order = None
        self.broker.set_coc=True
        self.accn_currency = 'USD'

        self.inds = dict()
        self.igs = dict()
        self.closes = dict()
        self.open_orders = dict()
        self.data_dict = dict()
        for i, d in enumerate(self.datas):
            # Data Dictionary
            self.data_dict[d._name] = d

            # Open Orders
            self.open_orders[d] = {
            'sl': [],
            'tp': [],
            'tracker':[]
            }

            # Closes
            self.closes[d] = d.close

            # Binary Generator
            self.igs[d] = BG.IndicatorGenerator(d)

            self.inds[d] = dict()
            # Money Management Indicators
            self.inds[d]['atr'] = bt.indicators.ATR(d,period=self.p.atr_period, plot=False)

            # Generate Strategy Binary Indicators

            self.inds[d]['baseline'], self.inds[d]['too_far'] = self.igs[d].baseline_indicator(self.p.base_ind, self.p.base_params, plot=False)
            self.inds[d]['c1'] = self.igs[d].entry_indicator(self.p.c1_ind, self.p.c1_params, plot=True)
            self.inds[d]['c2'] = self.igs[d].entry_indicator(self.p.c2_ind, self.p.c2_params, plot=False)
            self.inds[d]['volume'] = self.igs[d].volume_indicator(self.p.volume_ind, self.p.volume_params, plot=False)
            self.inds[d]['exit'] = self.igs[d].exit_indicator(self.p.exit_ind, self.p.exit_params, plot=False)

            if i > 0:  # Check we are not on the first loop of data feed:
                if self.p.oneplot == True:
                    d.plotinfo.plotmaster = self.datas[0]

    def refresh_conditions(self):
        self.trade_conditons = dict()
        self.trade_conditons[1.0] = dict()
        self.trade_conditons[-1.0] = dict()
        for i, d in enumerate(self.datas):
            self.trade_conditons[1.0][d] = {
                'baseline': self.inds[d]['baseline'] > 0,
                'c1': self.inds[d]['c1'] > 0,
                'c2': self.inds[d]['c2'] > 0,
                'volume': self.inds[d]['volume'] > 0
            }
            self.trade_conditons[-1.0][d] = {
                'baseline': self.inds[d]['baseline'] < 0,
                'c1': self.inds[d]['c1'] < 0,
                'c2': self.inds[d]['c2'] < 0,
                'volume': self.inds[d]['volume'] < 0
            }

    def decide_trade(self,d):

        buy = all(list(self.trade_conditons[1.0][d].values()))
        sell = all(list(self.trade_conditons[-1.0][d].values()))

        if buy:
            return 1.0
        elif sell:
            return -1.0
        else:
            return 0.0

    def clean_orders(self):

        # Clean Open Orders Dictionary
        for i, d in enumerate(self.datas):
            for o in self.open_orders[d]['sl']:
                if not o.alive():
                    self.open_orders[d]['tracker'].remove(o.ref)
                    self.open_orders[d]['sl'].remove(o)
            for o in self.open_orders[d]['tp']:
                if not o.alive():
                    self.open_orders[d]['tp'].remove(o)

    def notify_order(self, order):

        # Call Custom Notification Function to Keep Code Clean
        dt, dn = self.datetime.date(), order.data._name
        res = notifier(order, dt, self.open_orders[order.data]['tracker'],verbose=self.p.verbose)
        # Take Profit Hit, Initialize Trailing Stop Order
        if res:
            size = res[0]
            price = res[1]
            if size > 0:
                move_stop = self.buy(data=order.data,
                                     size=size,
                                      exectype=bt.Order.StopTrail,
                                      trailamount=self.params.sl*self.inds[order.data]['atr'][0])
            elif size < 0:
                move_stop = self.sell(size=size,
                                     exectype=bt.Order.StopTrail,
                                     trailamount=self.params.sl*self.inds[order.data]['atr'][0])


        self.bar_executed = len(self)
        self.order = None

    def notify_trade(self, trade):

        # Call Custom Notification Function to Keep Code Clean
        date = self.data.datetime.datetime().date()
        notifier(trade, date,[],verbose=self.p.verbose)

    def size_position(self, d, stop_amount, risk):
        pair = d._name
        base = pair[0:3]
        counter = pair[3:]

        if counter == self.accn_currency:
            method = 0
        elif base == self.accn_currency:
            method = 1
        elif base != self.accn_currency and counter != self.accn_currency:
            method = 2
            exchange_pair = self.accn_currency+counter

            # Check if Exchange Pair Exists
            if exchange_pair in list(self.data_dict.keys()):
                exchange_rate = self.closes[self.data_dict[exchange_pair]][0]
            # Check if Reverse of Exchange Pair Exists
            elif counter+self.accn_currency in list(self.data_dict.keys()):
                exchange_rate = self.closes[self.data_dict[counter+self.accn_currency]][0]
                exchange_rate = 1/exchange_rate

        price = self.closes[d][0]
        stop = price - stop_amount
        risk = float(risk) / 100.0

        if base == 'JPY' or counter == 'JPY':
            JPY_pair = True
        else:
            JPY_pair = False

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

    def pullback(self,d):

        # Baseline Crossing Logic (Did we go too far? Need to Look for a Pullback?)
        if self.inds[d]['baseline'] != 0.0 and self.inds[d]['too_far'][0]:
            # Too far from baseline - no trading should occur
            if self.p.verbose: print('CAUTION BASELINE CROSS TOO FAR - CHECKING FOR PULLBACK')
            self.trade_conditons[self.inds[d]['baseline'][0]][d]['baseline'] = False
        elif self.inds[d]['baseline'][-1] != 0.0 and self.inds[d]['too_far'][-1] and not self.inds[d]['too_far'][0]:
            # Previous Candle was a Baseline Cross more than 1xATR
            # We are currently not "too far" from the baseline
            if self.p.verbose: print('PULLBACK DETECTED - BASELINE SAYS GO')
            self.trade_conditons[1.0][d]['baseline'] = self.inds[d]['baseline'][-1]>0
            self.trade_conditons[-1.0][d]['baseline'] = self.inds[d]['baseline'][-1]<0

    def continuation(self,d):

        # This is Where We Check the Logic for Continuation Trades

        # Get last fifty bars of baseline flip data
        base_hist = list(self.inds[d]['baseline'].get(size=30))
        base_hist.reverse()

        # Iterate through base flip history and get index of last flip:
        idx = next((i for i, x in enumerate(base_hist) if x != 0.0), None)

        if not idx:
            return None

        base = base_hist[idx]

        # Get Confirmation indicator Data since last baseline flip:
        c1_hist = list(self.inds[d]['c1'].get(size=idx))
        c1_hist.reverse()

        # Check if a confirmation flip has been detected
        if -1.0 * base in c1_hist:
            flips = len(list(itertools.groupby(c1_hist, lambda c1_hist: c1_hist > 0))) - 1
            # Check if we have a double confirmation flip
            if flips == 2:
                # Continuation Opportunity Detected!
                # Double Check Confirmation Indicator 2
                if self.inds[d]['c2'][0] == c1_hist[0]:
                    if self.p.verbose: print('CONTINUATION TRADE DETECTED')
                    # Update the Corresponding Buy/Sell Conditions
                    for key in self.trade_conditons[self.inds[d]['c1'][0]][d]:
                        self.trade_conditons[self.inds[d]['c1'][0]][d][key] = True

    def bridge_too_far(self,d):

        # Determine how long ago last flip in C1 Occurred

        c1_hist = list(self.inds[d]['c1'].get(size=10))
        c1_hist.reverse()

        try:
            idx = c1_hist.index(-1.0 * self.inds[d]['baseline']) - 1
        except:
            idx = 100

        trade = self.decide_trade(d)
        if idx > 7 and trade != 0.0:
            if self.p.verbose: print('BRIDGE TOO FAR, DO NOT TRADE')
            self.trade_conditons[trade][d]['c1'] = False

    def next(self):

        # Make Sure we have the most recent trading conditions:
        self.refresh_conditions()
        self.clean_orders()

        # Echo Current Closing Price
        #self.log('Current Closing Price: %.5f' % self.dataclose[0])

        # Check if We have a Pending Order and Exit Function to Avoid Creating Duplicate
        for i, d in enumerate(self.datas):
            if len(self.open_orders[d]['sl']) > 0 or len(self.open_orders[d]['tp']) > 0:
                continue

            # Apply Strategy Trading Logic
            pos = self.getposition(d).size

            # Check if we are in the Market - Only Proceed if we are not
            if not pos:

                # Check Pullback & Bridge too Far Logic
                if self.inds[d]['baseline'] != 0.0:
                    self.pullback(d)
                    self.bridge_too_far(d)

                # Continuation Trade Logic
                elif self.inds[d]['baseline'] == 0.0:
                    self.continuation(d)

                # Check Entry Conditions & Place Trades

                if self.decide_trade(d) > 0.0:
                    # Enter Long Position
                    # Calculate Risk Profile
                    size = round(self.size_position(d, self.p.sl * self.inds[d]['atr'], self.p.risk)/2)
                    price = self.closes[d]
                    tp = price + self.p.tp * self.inds[d]['atr']
                    sl = price - self.p.sl * self.inds[d]['atr']

                    # Generate Bracket Orders
                    # Bracket 1: To Scale Out at Break Even
                    main = self.buy(data=d,
                                    size=2*size,
                                    exectype=bt.Order.Market,
                                    transmit=False)
                    stop_loss = self.sell(data=d,
                                          size=2*size,
                                          exectype=bt.Order.Stop,
                                          price=sl,
                                          parent=main,
                                          transmit=False)
                    take_profit = self.sell(data=d,
                                            size=size,
                                            exectype=bt.Order.Limit,
                                            price=tp,
                                            parent=main,
                                            transmit=True)

                    self.open_orders[d]['sl'].append(stop_loss)
                    self.open_orders[d]['tp'].append(take_profit)
                    self.open_orders[d]['tracker'].append(stop_loss.ref)

                elif self.decide_trade(d) < 0.0:
                    # Enter Long Position
                    # Calculate Risk Profile
                    size = round(self.size_position(d, self.p.sl * self.inds[d]['atr'], self.p.risk)/2)
                    price = self.closes[d]
                    tp = price - self.p.tp * self.inds[d]['atr']
                    sl = price + self.p.sl * self.inds[d]['atr']

                    # Generate Bracket Orders
                    # Bracket 1: To Scale Out at Break Even
                    main = self.sell(data=d,
                                     size=2*size,
                                     exectype=bt.Order.Market,
                                     transmit=False)
                    stop_loss = self.buy(data=d,
                                         size=2*size,
                                         exectype=bt.Order.Stop,
                                         price=sl,
                                         parent=main,
                                         transmit=False)
                    take_profit = self.buy(data=d,
                                           size=size,
                                           exectype=bt.Order.Limit,
                                           price=tp,
                                           parent=main,
                                           transmit=True)

                    self.open_orders[d]['sl'].append(stop_loss)
                    self.open_orders[d]['tp'].append(take_profit)
                    self.open_orders[d]['tracker'].append(stop_loss.ref)

            else:

                buyexit_conds = [self.inds[d]['exit'] > 0, self.inds[d]['baseline'] > 0, self.inds[d]['c1'] > 0, self.inds[d]['c2'] > 0]
                sellexit_conds = [self.inds[d]['exit'] < 0, self.inds[d]['baseline'] < 0, self.inds[d]['c1'] < 0, self.inds[d]['c2'] < 0]

                if pos > 0:
                    # Check for Sell Exit Signal
                    if any(sellexit_conds):
                        self.order = self.close(data=d)

                elif pos < 0:
                    # Check for Buy Exit Signal
                    if any(buyexit_conds):
                        self.order = self.close(data=d)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add our strategy

    cerebro.addstrategy(NNFX)

    # Get Data Files from Data Folder
    paths, names = file_browser()

    dpath = 'Data/'
    datasets = [
        (dpath+path,name) for path, name in zip(paths,names)
    ]

    # Create a Data Feeds and Add to Cerebro

    for i in range(len(datasets)):
        data = bt.feeds.GenericCSVData(dataname=datasets[i][0],
                                   openinterest=-1,
                                   dtformat='%d.%m.%Y %H:%M:%S.000')
        cerebro.adddata(data, name=datasets[i][1])

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add Analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Set Commission:
    for i in range(len(datasets)):
        pair = datasets[i][1]
        base = pair[0:3]
        counter = pair[3:]
        acc_counter = True if 'USD' == counter else False
        jpy_pair = True if 'JPY' in [base, counter] else False

        comminfo = forexSpreadCommisionScheme(spread=2, acc_counter_currency=acc_counter, JPY_pair=jpy_pair)
        cerebro.broker.addcommissioninfo(comminfo, name=pair)
        cerebro.broker.setcommission(leverage=20, name=pair)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    t0 = time.time()
    strategies = cerebro.run()
    t1 = time.time()
    firstStrat = strategies[0]

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('Backtest Time: %.2fs' % (t1-t0))

    # print the analyzers
    printTradeAnalysis(firstStrat.analyzers.ta.get_analysis())
    printSQN(firstStrat.analyzers.sqn.get_analysis())

    #cerebro.plot(style='candle')
