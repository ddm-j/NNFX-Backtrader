import backtrader as bt
from custom_indicators import *

# Strategy Indicator Generators

class IndicatorGenerator(object):

    def __init__(self, data_feed):

        # Data Feed From Strategy() Class

        self.data = data_feed

        # ATR For Indicator Useage

        self.atr = bt.indicators.AverageTrueRange(self.data,period=14,plot=False)

        # List Of Available Indicators and How Many Parameters Each Takes

        self.indicators = {
            'itrend': 1,
            'cybercycle': 1,
            'adaptivecybercycle': 2,
            'heikenashi': 1,
            'cvi': 2,
            'cmf': 1,
            'ssl': 1,
            'aroon': 1,
            'ttf':1,
            'tdfi':2,
            'kijun':1,
            'ma': 2,
            'wae': 6,
            'ash': 7,
            'roof': 3,
            'mama': 2,
            'fama':2,
            'dosc':1,
            'idosc':2,
            'laguerre':1,
            'alaguerre':1,
            'butter':2,
            'squeeze':5,
            'schaff':4
        }

    def check_input(self,ind,params):
        if ind not in self.indicators.keys():
            raise InputError(ind,'Specified indicator not found in prescribed list of approved indicators.')
        elif len(params) != self.indicators[ind]:
            raise InputError(len(params),'Length of params not correct for chosen indicator.')

    def baseline_indicator(self, ind, params, plot=True):

        """
        Function that returns and binary baseline indicator for simple strategy logic useage
        :param ind: Indicator choice (string type) - must be in list of self.indicators
        :param params: Parameters for Indicator - must have right amount of parameters or error thrown
        :return: Binary Trade Entry Indicator

        """

        # Check Inputs
        self.check_input(ind,params)

        # Create Logic Blocks for Each Indicator

        if ind == 'kijun':
            ichi = bt.indicators.Ichimoku(self.data,kijun=params[0], plot=plot)
            base = ichi.kijun_sen

        elif ind == 'ma':
            ma = params[0](self.data,period=params[1],plot=plot)
            base = ma

        elif ind == 'itrend':
            itrend = iTrend(self.data,period=params[0])
            base = itrend.itrend

        elif ind == 'fama':
            mama = MAMA(self.data,fast=params[0],slow=params[1],plot=plot)
            base = mama.FAMA

        elif ind == 'mama':
            mama = MAMA(self.data,fast=params[0],slow=params[1],plot=plot)
            base = mama.MAMA

        elif ind == 'laguerre':
            lag = LaguerreFilter(self.data, period=params[0], plot=plot)
            base = lag.filter

        elif ind == 'alaguerre':
            alag = AdaptiveLaguerreFilter(self.data, length=params[0], plot=plot)
            base = alag.filter

        elif ind == 'butter':
            butterworth = Butterworth(self.data, period=params[0], poles=params[1], plot=plot)
            base = butterworth.butter


        # Baseline Crossover Detection
        baseline = bt.indicators.CrossOver(self.data.close,base,plot=plot)

        # Baseline Crossover too Far
        diff = bt.If(baseline>0, self.data.close-base, base-self.data.close)
        too_far = bt.If(diff > self.atr, True, False)

        return baseline, too_far

    def entry_indicator(self, ind, params, plot=True):
        """
        Function that returns and binary entry confirmation indicator for simple strategy logic useage
        :param ind: Indicator choice (string type) - must be in list of self.indicators
        :param params: Parameters for Indicator - must have right amount of parameters or error thrown
        :return: Binary Trade Entry Indicator

        """

        # Check Inputs
        self.check_input(ind,params)

        # Create Logic Blocks for Each Indicator

        if ind == 'itrend':
            itrend = iTrend(self.data, period=params[0], plot=plot)
            entry = bt.Cmp(itrend.trigger,itrend.itrend)
            return entry

        elif ind == 'cybercycle':
            cc = CyberCycle(self.data, period=params[0], plot=plot)
            entry = bt.Cmp(cc.trigger,cc.cycle)
            return entry

        elif ind == 'adaptivecybercycle':
            acc = AdaptiveCyberCycle(self.data, period=params[0], lag=params[1], plot=plot)
            entry = bt.Cmp(acc.signal,acc.trigger)
            return entry

        elif ind == 'ssl':
            ssl = SSLChannel(self.data, period=params[0], plot=plot)
            entry = bt.Cmp(ssl.sslu,ssl.ssld)
            return entry

        elif ind == 'aroon':
            aud = bt.indicators.AroonUpDown(self.data,period=params[0], plot=plot)
            entry = bt.Cmp(aud.aroonup,aud.aroondown)
            return entry

        elif ind == 'ttf':
            ttf = TrendTriggerFactor(self.data,period=params[0], plot=plot)
            long = bt.indicators.CrossUp(ttf.ttf,-100.0,plot=plot)
            short = bt.indicators.CrossDown(ttf.ttf,100.0,plot=plot)
            entry = long + -1*short
            return entry

        elif ind == 'tdfi':
            tdfi = TrendDirectionForceIndex(self.data,period=params[0],plot=plot)
            e1 = bt.If(tdfi.ntdf>params[1],1.0,0.0)
            e2 = bt.If(tdfi.ntdf<-params[1],-1.0,0.0)
            entry = e1+e2
            return entry

        elif ind == 'cmf':
            chaikin = ChaikinMoneyFlow(self.data, period=params[0], plot=plot)
            entry = bt.Cmp(chaikin.money_flow,0.0)
            return entry

        elif ind == 'ash':
            ash = ASH(self.data,
                      period=params[0],
                      smoothing=params[1],
                      mode=params[2],
                      rsifactor=params[3],
                      movav=params[4],
                      smoothav=params[5],
                      pointsize=params[6]
                      )
            entry = bt.Cmp(ash.bulls,ash.bears)
            return entry

        elif ind == 'roof':
            roof = RoofingFilter(self.data,hp_period=params[0],ss_period=params[1],smooth=params[2],plot=plot)
            entry = bt.Cmp(roof.iroof,0.0)
            return entry

        elif ind == 'mama':
            mama = MAMA(self.data, fast=params[0], slow=params[1], plot=plot)
            entry = bt.Cmp(mama.MAMA,mama.FAMA)
            return entry

        elif ind == 'dosc':
            dosc = DecyclerOscillator(self.data,hp_period=params[0],plot=plot)
            entry = bt.Cmp(dosc.osc,0.0)
            return entry

        elif ind == 'idosc':
            idosc = iDecycler(self.data,hp_period=params[0],smooth=params[1],plot=plot)
            entry = bt.Cmp(idosc.idosc,0.0)
            return entry

        elif ind == 'schaff':
            schaff = SchaffTrendCycle(self.data,fast=params[0],slow=params[1],cycle=params[2],factor=params[3],plot=plot)
            buy = bt.indicators.CrossUp(schaff.schaff,25.0,plot=plot)
            sell = bt.indicators.CrossDown(schaff.schaff,75.0,plot=plot)
            binary = buy - sell
            entry = SignalFiller(binary,plot=plot).signal
            return entry

    def volume_indicator(self, ind, params, plot=True):
        """
        Function that returns and binary volume confirmation indicator for simple strategy logic useage
        :param ind: Indicator choice (string type) - must be in list of self.indicators
        :param params: Parameters for Indicator - must have right amount of parameters or error thrown
        :return: Binary Trade Volume Indicator

        """

        # Check Inputs
        self.check_input(ind,params)

        # Create Logic Blocks

        if ind == 'cvi':
            chaikin = ChaikinVolatility(self.data,ema_period=params[0],roc_period=params[1], plot=plot)
            volume = chaikin.cvi > 0.0
            return volume

        elif ind == 'tdfi':
            tdfi = TrendDirectionForceIndex(self.data,period=params[0],plot=plot)
            volume1 = bt.If(tdfi.ntdf>params[1],1.0,0.0)
            volume2 = bt.If(tdfi.ntdf<-params[1],-1.0,0.0)
            volume = volume1+volume2
            return volume

        elif ind == 'wae':
            wae = WaddahAttarExplosion(self.data,
                                       sensitivity=params[0],
                                       fast=params[1],
                                       slow=params[2],
                                       channel=params[3],
                                       mult=params[4],
                                       dead=params[5],plot=plot)
            # Buy Volume
            buy = bt.All(wae.utrend>wae.exp,
                         wae.utrend>wae.dead,
                         wae.exp>wae.dead)
            sell = bt.All(wae.dtrend>wae.exp,
                          wae.dtrend>wae.dead,
                          wae.exp>wae.dead)
            volume = buy-sell
            return volume

        elif ind == 'squeeze':

            sqz = SqueezeVolatility(self.data,period=params[0],mult=params[1],period_kc=params[2],mult_kc=params[3],movav=params[4])
            return sqz.sqz

    def exit_indicator(self, ind, params, plot=True):
        """
        Function that returns and binary exit confirmation indicator for simple strategy logic useage
        :param ind: Indicator choice (string type) - must be in list of self.indicators
        :param params: Parameters for Indicator - must have right amount of parameters or error thrown
        :return: Binary Trade Exit Indicator

        """

        # Check Inputs
        self.check_input(ind,params)

        # Create Logic Blocks for Binaries

        if ind == 'heikenashi':
            heiken = HeikenAshi(self.data, plot=plot)
            ups = [heiken.signal(-i if i > 0 else i) == 1.0 for i in range(0,params[0])]
            downs = [heiken.signal(-i if i > 0 else i) == -1.0 for i in range(0, params[0])]
            exit = bt.Or(bt.All(*ups),bt.All(*downs)) * heiken.signal
            return exit

        elif ind == 'ssl':
            ssl = SSLChannel(self.data, period=params[0], plot=plot)
            exit = bt.Cmp(ssl.sslu, ssl.ssld)
            return exit

        elif ind == 'itrend':

            itrend = iTrend(self.data,period=params[0],plot=plot)
            exit = bt.Cmp(itrend.trigger,itrend.itrend)
            return exit

        elif ind == 'mama':

            mama = MAMA(self.data,fast=params[0],slow=params[1],plot=plot)
            exit = bt.Cmp(mama.MAMA,mama.FAMA)
            return exit

        elif ind == 'dosc':
            dosc = DecyclerOscillator(self.data,hp_period=params[0],plot=plot)
            exit = bt.Cmp(dosc.osc,0.0)
            return exit

class InputError(Exception):

    def __init__(self,expression,message):
        self.expression = expression
        self.message = message
