import backtrader as bt
import backtrader.indicators as bitind
import numpy as np
from scipy import stats
import math

class iFisher(bt.Indicator):

    lines = ('ifisher','scaled','smoothed')
    params = (('scaling',5.0),('period',20),('smoothing',5))

    plotlines = dict(scaled=dict(_plotskip=True, ),
                     smoothed=dict(_plotskip=True, ))

    plotinfo = dict(
        plot=True,
        plotname='Inverse Fisher Transform',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):

        self.addminperiod(self.p.period)

        hi = bt.indicators.Highest(self.data, period=self.p.period)
        lo = bt.indicators.Lowest(self.data, period=self.p.period)

        # Calculate Rescaling

        self.lines.scaled = s = (2*self.p.scaling)*((self.data-lo)/(hi-lo))-self.p.scaling
        self.lines.smoothed = ss = bt.indicators.SMA(s, period=self.p.smoothing)

    def next(self):

        self.lines.ifisher[0] = (np.exp(2*self.l.smoothed[0])-1)/(np.exp(2*self.l.smoothed[0])+1)

class iTrend(bt.indicators.PeriodN):

    lines = ('itrend','trigger',)

    params = (('period', 20),)

    plotinfo = dict(
        plot=True,
        plotname='iTrend',
        subplot=False,
        plotlinelabels=True)

    def __init__(self):
        self.alpha = 2.0/(1+self.p.period)
        self.addminperiod(self.p.period)

    def prenext(self):
        self.l.itrend[0] = (self.data[0] + 2*self.data[-1] + self.data[-2])/4

    def next(self):

        it1 = self.lines.itrend[-1]
        it2 = self.lines.itrend[-2]
        p = self.data[0]
        p1 = self.data[-1]
        p2 = self.data[-2]
        a = self.alpha

        self.lines.itrend[0] = (a - (a/2)**2)*p + (a**2/2)*p1 - (a - 3*a**2/4)*p2 \
            + 2*(1-a)*it1 - ((1-a)**2)*it2

        self.lines.trigger[0] = 2*self.l.itrend[0] - self.l.itrend[-2]

class CyberCycle(bt.indicators.PeriodN):

    lines = ('cycle',
             'smooth',
             'trigger',
             )

    plotlines = dict(smooth=dict(_plotskip=True, ))

    plotinfo = dict(
        plot=True,
        plotname='Cyber Cycle',
        subplot=True,
        plotlinelabels=True)

    params = (('period',30),
              )

    def __init__(self):

        self.addminperiod(self.p.period)
        self.alpha = 2.0/(1.0 + self.p.period)

    def prenext(self):

        self.l.cycle[0] = (self.data[0] - 2*self.data[-1] + self.data[-2])/4
        self.l.smooth[0] = (self.data[0] + 2*self.data[-1] \
                            + 2*self.data[-2] + self.data[-3])/6

    def next(self):
        a = self.alpha
        self.l.smooth[0] = (self.data[0] + 2*self.data[-1] \
                            + 2*self.data[-2] + self.data[-3])/6

        self.l.cycle[0] = ((1 - 0.5*a)**2)*(self.l.smooth[0] - 2*self.l.smooth[-1] + self.l.smooth[-2]) \
            + 2*(1-a)*self.l.cycle[-1] - ((1-a)**2)*self.l.cycle[-2]
        self.l.trigger[0] = self.l.cycle[-1]

class AdaptiveCyberCycle(bt.indicators.PeriodN):

    lines = ('cycle',
             'smooth',
             'signal',
             'trigger',
             )

    plotlines = dict(smooth=dict(_plotskip=True, ),
                     cycle=dict(_plotskip=True, ))

    params = (('period',30),
              ('lag', 9),
              )

    plotinfo = dict(
        plot=True,
        plotname='Adaptive Cyber Cycle',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):

        self.addminperiod(self.p.period)
        self.alpha = 2.0/(1.0 + self.p.period)
        self.alpha2 = 1.0/(self.p.lag + 1)

    def prenext(self):

        self.l.cycle[0] = (self.data[0] - 2*self.data[-1] + self.data[-2])/4
        self.l.smooth[0] = (self.data[0] + 2*self.data[-1] \
                            + 2*self.data[-2] + self.data[-3])/6
        self.l.signal[0] = self.alpha2*self.l.cycle[0]

    def next(self):
        a = self.alpha
        a2 = self.alpha2
        self.l.smooth[0] = (self.data[0] + 2*self.data[-1] \
                            + 2*self.data[-2] + self.data[-3])/6

        self.l.cycle[0] = ((1 - 0.5*a)**2)*(self.l.smooth[0] - 2*self.l.smooth[-1] + self.l.smooth[-2]) \
            + 2*(1-a)*self.l.cycle[-1] - ((1-a)**2)*self.l.cycle[-2]

        self.l.signal[0] = a2*self.l.cycle[0] + (1 - a2)*self.l.signal[-1]
        self.l.trigger[0] = self.l.signal[-1]

class HeikenAshi(bt.Indicator):

    lines=('open','high','low','close','signal')

    plotlines = dict(open=dict(_plotskip=True, ),
                     high=dict(_plotskip=True,),
                     low=dict(_plotskip=True,),
                     close=dict(_plotskip=True,))
    plotinfo = dict(
        plot=True,
        plotname='Hieken Ashi Candles',
        subplot=False,
        plotlinelabels=True)


    def __init__(self):
        self.addminperiod=2

    def next(self):
        self.l.open[0] = o = (self.data.open[-1] + self.data.close[-1])/2.0
        self.l.close[0] = c = (self.data.open[0]+self.data.close[0]+self.data.high[0]+self.data.close[0])/4
        self.l.high[0] = max(self.data.high[0], self.data.open[0], self.data.close[0])
        self.l.low[0] = min(self.data.low[0], self.data.open[0], self.data.close[0])
        self.l.signal[0] = -1.0 if c < o else 1.0

class ChaikinVolatility(bt.Indicator):
    params=dict(ema_period=10,
                roc_period=10)
    lines=('cvi',)
    plotinfo = dict(
        plot=True,
        plotname='Chaikin Volatility Index',
        subplot=True,
        plotlinelabels=True)


    def __init__(self):
        price = self.data.high - self.data.low
        ema = bt.indicators.EMA(price,period=self.p.ema_period)
        self.l.cvi = bt.indicators.RateOfChange(ema.ema,period=self.p.roc_period)

class ChaikinMoneyFlow(bt.Indicator):
    lines = ('money_flow',)
    params = (
        ('period', 20),
    )

    plotlines = dict(
        money_flow=dict(
            _name='CMF',
            color='green',
            alpha=0.50
        )
    )

    def __init__(self):
        # Let the indicator get enough data
        self.addminperiod(self.p.period)

        # Plot horizontal Line
        self.plotinfo.plotyhlines = [0]

        # Aliases to avoid long lines
        c = self.data.close
        h = self.data.high
        l = self.data.low
        v = self.data.volume

        self.data.ad = bt.If(bt.Or(bt.And(c == h, c == l), h == l), 0, ((2 * c - l - h) / (h - l)) * v)
        self.lines.money_flow = bt.indicators.SumN(self.data.ad, period=self.p.period) / bt.indicators.SumN(
            self.data.volume, period=self.p.period)

class SSLChannel(bt.Indicator):
    lines = ('ssld', 'sslu')
    params = (('period', 30),)
    plotinfo = dict(
        plot=True,
        plotname='SSL Channel',
        subplot=False,
        plotlinelabels=True)

    def _plotlabel(self):
        return [self.p.period]

    def __init__(self):
        self.addminperiod(self.p.period)
        self.hma_lo = bt.indicators.SmoothedMovingAverage(self.data.low, period=self.p.period)
        self.hma_hi = bt.indicators.SmoothedMovingAverage(self.data.high, period=self.p.period)

    def next(self):
        hlv = 1 if self.data.close > self.hma_hi[0] else -1
        if hlv == -1:
            self.lines.ssld[0] = self.hma_hi[0]
            self.lines.sslu[0] = self.hma_lo[0]

        elif hlv == 1:
            self.lines.ssld[0] = self.hma_lo[0]
            self.lines.sslu[0] = self.hma_hi[0]

class KlingerOscillator(bt.Indicator):

    lines = ('sig', 'kvo')

    params = (('fast', 34), ('slow', 55), ('signal', 13))

    plotinfo = dict(
        plot=True,
        plotname='Klinger Oscillator',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):
        self.plotinfo.plotyhlines = [0]
        self.addminperiod(55)

        self.data.hlc3 = (self.data.high + self.data.low + self.data.close) / 3
        # This works - Note indexing should be () rather than []
        # See: https://www.backtrader.com/docu/concepts.html#lines-delayed-indexing
        self.data.sv = bt.If((self.data.hlc3(0) - self.data.hlc3(-1)) / self.data.hlc3(-1) >= 0, self.data.volume,
                             -self.data.volume)
        self.lines.kvo = bt.indicators.EMA(self.data.sv, period=self.p.fast) - bt.indicators.EMA(self.data.sv,
                                                                                                    period=self.p.slow)
        self.lines.sig = bt.indicators.EMA(self.lines.kvo, period=self.p.signal)

class TrendTriggerFactor(bt.Indicator):

    lines = ('ttf',)
    params = (
        ('period', 20),
    )

    plotinfo = dict(
        plot=True,
        plotname='Trend Trigger Factor',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):
        self.addminperiod(2*self.p.period+1)

    def next(self):
        p = self.p.period+1
        Hi = self.data.high.get(ago=0,size=self.p.period)
        Lo = self.data.low.get(ago=0,size=self.p.period)
        lagHi = self.data.high.get(ago=-p,size=self.p.period)
        lagLo = self.data.low.get(ago=-p,size=self.p.period)

        bp = max(Hi) - min(lagLo)
        sp = max(lagHi) - min(Lo)
        self.l.ttf[0] = 100*(bp-sp)/(0.5*(bp+sp))

class TrendDirectionForceIndex(bt.Indicator):

    lines=('mma','smma','tdf','ntdf')

    params = (
        ('period', 13),
    )

    plotlines = dict(mma=dict(_plotskip=True, ),
                     smma=dict(_plotskip=True,),
                     tdf=dict(_plotskip=True,)
                     )

    plotinfo = dict(
        plot=True,
        plotname='Trend Force and Direction Index',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):

        self.addminperiod(self.p.period*3)
        self.l.mma = bt.indicators.EMA(self.data.close*1000,period=self.p.period)
        self.l.smma = bt.indicators.EMA(self.l.mma,period=self.p.period)

    def prenext(self):

        impetmma = self.l.mma[0] - self.l.mma[-1]
        impetsmma = self.l.smma[0] - self.l.smma[-1]
        divma = abs(self.l.mma[0] - self.l.smma[0])
        averimpet = (impetmma+impetsmma)/2
        pow = averimpet**3
        self.l.tdf[0] = divma * pow

    def next(self):

        impetmma = self.l.mma[0] - self.l.mma[-1]
        impetsmma = self.l.smma[0] - self.l.smma[-1]
        divma = abs(self.l.mma[0] - self.l.smma[0])
        averimpet = (impetmma+impetsmma)/2
        pow = averimpet**3

        self.l.tdf[0] = divma * pow
        self.l.ntdf[0] = self.l.tdf[0]/(max(np.absolute(self.l.tdf.get(size=self.p.period*3))))

class WaddahAttarExplosion(bt.Indicator):
    lines = ('macd', 'utrend', 'dtrend', 'exp', 'dead')

    params = (
        ('sensitivity', 150),
        ('fast', 20),
        ('slow', 40),
        ('channel', 20),
        ('mult', 2.0),
        ('dead', 3.7)

    )

    plotlines = dict(macd=dict(_plotskip=True, ),
                     )

    plotinfo = dict(
        plot=True,
        plotname='Waddah Attar Explosion',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):
        # Plot horizontal Line

        self.l.macd = bt.indicators.MACD(self.data,period_me1=self.p.fast,period_me2=self.p.slow).macd
        boll = bt.indicators.BollingerBands(self.data,period=self.p.channel, devfactor=self.p.mult)

        t1 = (self.l.macd(0)-self.l.macd(-1))*self.p.sensitivity
        self.l.exp = boll.top - boll.bot

        self.l.utrend = bt.If(t1 >= 0, t1, 0.0)
        self.l.dtrend = bt.If(t1 < 0, -1.0*t1, 0.0)
        self.l.dead = bt.indicators.AverageTrueRange(self.data,period=50).atr*self.p.dead

class ASH(bt.Indicator):
    alias = ('AbsoluteStrengthOscilator',)

    lines = ('ash', 'bulls', 'bears',)  # output lines

    # customize the plotting of the *ash* line
    plotlines = dict(ash=dict(_method='bar', alpha=0.33, width=0.66))

    RSI, STOCH = range(0, 2)  # enum values for the parameter mode

    params = dict(
        period=9,
        smoothing=2,
        mode=RSI,
        rsifactor=0.5,
        movav=bt.ind.WMA,  # WeightedMovingAverage
        smoothav=None,  # use movav if not specified
        pointsize=None,  # use only if specified
    )

    def __init__(self):
        # Start calcs according to selected mode
        if self.p.mode == self.RSI:
            p0p1 = self.data - self.data(-1)  # used twice below
            half_abs_p0p1 = self.p.rsifactor * abs(p0p1)  # used twice below

            bulls = half_abs_p0p1 + p0p1
            bears = half_abs_p0p1 - p0p1
        else:
            bulls = self.data - bt.ind.Lowest(self.data, period=self.p.period)
            bears = bt.ind.Highest(self.data, period=self.p.period) - self.data

        avbulls = self.p.movav(bulls, period=self.p.period)
        avbears = self.p.movav(bears, period=self.p.period)

        # choose smoothing average and smooth the already averaged values
        smoothav = self.p.smoothav or self.p.movav  # choose smoothav
        smoothbulls = smoothav(avbulls, period=self.p.smoothing)
        smoothbears = smoothav(avbears, period=self.p.smoothing)

        if self.p.pointsize:  # apply only if it makes sense
            smoothbulls /= self.p.pointsize
            smoothbears /= self.p.pointsize

        # Assign the final values to the output lines
        self.l.bulls = smoothbulls
        self.l.bears = smoothbears
        self.l.ash = smoothbulls - smoothbears

class StandarizedATR(bt.Indicator):

    lines = ('natr',)

    params = (
        ('atr_period', 14),
        ('std_period', 20),
        ('movav', bt.ind.SMA),
    )

    plotinfo = dict(
        plot=True,
        plotname='Standardized ATR',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):

        atr = bt.indicators.ATR(self.data,period=self.p.atr_period)
        satr = self.p.movav(atr,period=self.p.std_period)
        self.stdev = bt.indicators.StandardDeviation(self.data,period=self.p.std_period,movav=self.p.movav)

        self.l.natr = satr/self.stdev

class SuperSmoothFilter(bt.Indicator):

    lines = ('filter',)

    params = (
        ('period', 10),
    )

    plotinfo = dict(
        plot=True,
        plotname='Super Smooth Filter',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):
        self.addminperiod(10)

    def prenext(self):

        self.l.filter[0] = (self.data[0]+self.data[-1])/2

    def next(self):

        a1 = np.exp(-1.414*3.14159/self.p.period)
        b1 = 2*a1*np.cos(np.deg2rad(1.414*180/self.p.period))
        c2 = b1
        c3 = -a1*a1
        c1 = 1 - c2 - c3
        self.l.filter[0] = c1*(self.data[0]+self.data[-1])/2 + c2*self.l.filter[-1] + c3*self.l.filter[-2]

class ElhersHighPass(bt.Indicator):

    lines = ('hp',)

    params = (
        ('period',48),
    )

    plotinfo = dict(
        plot=True,
        plotname='Elhers High Pass',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):
        self.addminperiod(10)

    def deg(self,arg):

        return np.deg2rad(arg)

    def prenext(self):
        c = self.data[0]
        c1 = self.data[-1]
        c2 = self.data[-2]
        a1 = (np.cos(self.deg(.707*360/self.p.period)) + np.sin(self.deg(.707*360/self.p.period))-1)/np.cos(self.deg(.707*360/self.p.period))
        self.l.hp[0] = ((1 - a1/2)**2)*(c - 2*c1 + c2)

    def next(self):
        c = self.data.close[0]
        c1 = self.data.close[-1]
        c2 = self.data.close[-2]
        a1 = (np.cos(self.deg(.707*360/self.p.period)) + np.sin(self.deg(.707*360/self.p.period))-1)/np.cos(self.deg(.707*360/self.p.period))
        self.l.hp[0] = ((1 - a1/2)**2)*(c - 2*c1 + c2) + 2*(1-a1)*self.l.hp[-1] - ((1-a1)**2)*self.l.hp[-2]

class RoofingFilter(bt.Indicator):

    lines = ('roof','iroof')

    params = (
        ('hp_period', 48),
        ('ss_period', 10),
        ('smooth', 2)
    )

    plotinfo = dict(
        plot=True,
        plotname='Elhers Roofing Filter',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):
        self.addminperiod(10)

        hp = ElhersHighPass(self.data,period=self.p.hp_period)
        self.l.roof = SuperSmoothFilter(hp,period=self.p.ss_period)
        self.l.iroof = iFisher(self.l.roof, smoothing=self.p.smooth)

class MAMA(bt.Indicator):

    lines = ('p', 'S', 'D', 'mp', 'Q1', 'I1', 'Q2', 'I2', 'jI', 'jQ', 'Re', 'Im', 'phi', 'smoothPeriod',
             'MAMA','FAMA')

    params = (
        ('fast', 20),
        ('slow', 50),
    )

    plotlines = dict(p=dict(_plotskip=True, ),
                     S=dict(_plotskip=True, ),
                     D=dict(_plotskip=True, ),
                     mp=dict(_plotskip=True, ),
                     Q1=dict(_plotskip=True, ),
                     I1=dict(_plotskip=True, ),
                     Q2=dict(_plotskip=True, ),
                     I2=dict(_plotskip=True, ),
                     jI=dict(_plotskip=True, ),
                     jQ=dict(_plotskip=True, ),
                     Re=dict(_plotskip=True, ),
                     Im=dict(_plotskip=True, ),
                     phi=dict(_plotskip=True, ),
                     smoothPeriod=dict(_plotskip=True, )
                     )

    plotinfo = dict(
        plot=True,
        plotname='Mesa Adaptive Moving Average',
        subplot=False,
        plotlinelabels=True)

    def hilbertTransform(self,data):

        a, b, c, d = [0.0962, 0.5769, 0.075, 0.54]
        d0 = data[0]
        d2 = data[-2]
        d4 = data[-4]
        d6 = data[-6]
        hilbert = a*d0 + b*d2 - b*d4 - a*d6
        return hilbert*(c*self.l.mp[0] + d)

    def smoother(self,data):

        return 0.2*data[0] + 0.8*data[-1]

    def deg(self,arg):
        return np.rad2deg(arg)

    def __init__(self):
        self.fast = 2/(self.p.fast+1)
        self.slow = 2/(self.p.slow+1)
        self.addminperiod(40)
        self.l.p = (self.data.high + self.data.low)/2

    def prenext(self):
        # Variable Initialization
        self.l.Q1[0] = 0.0
        self.l.Q2[0] = 0.0
        self.l.I1[0] = 0.0
        self.l.I2[0] = 0.0
        self.l.jQ[0] = 0.0
        self.l.jI[0] = 0.0
        self.l.Im[0] = 0.0
        self.l.Re[0] = 0.0
        self.l.phi[0] = 0.0
        self.l.smoothPeriod[0] = 0.0
        self.l.mp[0] = 1.0
        self.l.MAMA[0] = 0.0
        self.l.FAMA[0] = 0.0
        self.l.S[0] = (4 * self.l.p[0] + 3 * self.l.p[-1] + 2 * self.l.p[-2] + 3 * self.l.p[-3])/10
        self.l.D[0] = self.hilbertTransform(self.l.S)

    def next(self):
        self.l.mp[0] = 0.0

        self.l.S[0] = (4*self.l.p[0] + 3*self.l.p[-1] + 2*self.l.p[-2]+ 3*self.l.p[-3])/10

        # Smooth and Detrend
        self.l.D[0] = self.hilbertTransform(self.l.S)

        # Inphase and Quadrature
        self.l.Q1[0] = self.hilbertTransform(self.l.D)
        self.l.I1[0] = self.l.D[-3]

        # Phase Advancement of Inphase and Quadrature by 90 degrees
        self.l.jI[0] = self.hilbertTransform(self.l.I1)
        self.l.jQ[0] = self.hilbertTransform(self.l.Q1)

        # Phasor Addition - 3 Bar Averaging
        self.l.I2[0] = self.l.I1[0] - self.l.jQ[0]
        self.l.Q2[0] = self.l.Q1[0] - self.l.jI[0]

        # Smoothing of I and Q
        self.l.I2[0] = self.smoother(self.l.I2)
        self.l.Q2[0] = self.smoother(self.l.Q2)

        # Hemodyne Discriminator
        self.l.Re[0] = self.l.I2[0]*self.l.I2[-1] + self.l.Q2[0]*self.l.Q2[-1]
        self.l.Im[0] = self.l.I2[0]*self.l.Q2[-1] + self.l.Q2[0]*self.l.I2[-1]

        self.l.Re[0] = self.smoother(self.l.Re)
        self.l.Im[0] = self.smoother(self.l.Im)

        if self.l.Im[0] != 0.0 and self.l.Re[0] != 0.0:
            self.l.mp[0] = 360/(self.deg(np.arctan(self.l.Im[0]/self.l.Re[0])))
        if self.l.mp[0] > 1.5*self.l.mp[-1]:
            self.l.mp[0] = 1.5*self.l.mp[-1]
        if self.l.mp[0] < (2.0/3)*self.l.mp[-1]:
            self.l.mp[0] = (2.0/3)*self.l.mp[-1]
        if self.l.mp[0] < 6:
            self.l.mp[0] = 6.0
        if self.l.mp[0] > 50:
            self.l.mp[0] = 50.0
        self.l.mp[0] = self.smoother(self.l.mp)
        self.l.smoothPeriod[0] = (1.0/3)*self.l.mp[0] + (2.0/3)*self.l.smoothPeriod[-1]

        if self.l.I1[0] != 0.0:
            self.l.phi[0] = self.deg(np.arctan(self.l.Q1[0]/self.l.I1[0]))
        dphi = self.l.phi[-1] - self.l.phi[0]

        if dphi < 1:
            dphi = 1.0

        alpha = self.p.fast/dphi

        if alpha < self.slow:
            alpha = self.slow
        if alpha > self.fast:
            alpha = self.fast

        self.l.MAMA[0] = alpha*self.l.p[0] + (1-alpha)*self.l.MAMA[-1]
        self.l.FAMA[0] = 0.5*alpha*self.l.MAMA[0] + (1-0.5*alpha)*self.l.FAMA[-1]

class DecyclerOscillator(bt.Indicator):

    lines = ('osc','decycle', 'hp')

    params = (
        ('hp_period', 48),
    )

    plotlines = dict(decycle=dict(_plotskip=True, ),
                     hp=dict(_plotskip=True, ),
                     )

    plotinfo = dict(
        plot=True,
        plotname='Elhers Decycler Oscillator',
        subplot=True,
        plotlinelabels=True)

    def filter(self,a,set1,set2):

        filt = ((1-a)**2)*(set1[0]-2*set1[-1]+set1[-2])+2*(1-a)*set2[-1] - ((1-a)**2)*set2[-2]
        return filt

    def __init__(self):
        self.addminperiod(20)
        self.b = np.deg2rad(0.707*360/self.p.hp_period)
        self.a1 = (np.cos(self.b)+np.sin(self.b)-1)/np.cos(self.b)
        self.a2 = (np.cos(self.b/2)+np.sin(self.b/2)-1)/np.cos(self.b)

    def prenext(self):

        self.l.hp[0] = 0.0
        self.l.osc[0] = 0.0
        self.l.decycle[0] = self.data.close[-1]

    def next(self):

        self.l.hp[0] = self.filter(self.a1, self.data.close, self.l.hp)
        self.l.decycle[0] = self.data.close[0] - self.l.hp[0]

        self.l.osc[0] = self.filter(self.a2, self.l.decycle, self.l.osc)

class iDecycler(bt.Indicator):

    lines = ('idosc',)

    params = (
        ('hp_period', 48),
        ('smooth', 2)
    )

    plotlines = dict(decycle=dict(_plotskip=True, ),
                     hp=dict(_plotskip=True, ),
                     )

    plotinfo = dict(
        plot=True,
        plotname='iDecycler',
        subplot=True,
        plotlinelabels=True)

    def __init__(self):

        osc = DecyclerOscillator(self.data,hp_period=self.p.hp_period)
        self.l.idosc = iFisher(osc.osc,smoothing=self.p.smooth)

class Butterworth(bt.Indicator):

    lines = ('butter', 'p')

    params = (
        ('period', 48),
        ('poles', 2)
    )

    plotlines = dict(p=dict(_plotskip=True, ),
                     )

    plotinfo = dict(
        plot=True,
        plotname='Butterworth Filter',
        subplot=False,
        plotlinelabels=True)

    def __init__(self):

        self.addminperiod(10)

        if self.p.poles == 2:
            self.a1 = np.exp(-1.414*3.14159/self.p.period)
            self.b1 = 2*self.a1*np.cos(np.deg2rad(1.414*180/self.p.period))
            self.c2 = self.b1
            self.c3 = -self.a1**2
            self.c1 = (1-self.b1+self.a1**2)/4

        elif self.p.poles == 3:
            self.a1 = np.exp(-3.14159 / self.p.period)
            self.b1 = 2 * self.a1 * np.cos(np.deg2rad(1.738 * 180 / self.p.period))
            self.c1 = self.a1 ** 2
            self.c2 = self.b1 + self.c1
            self.c3 = -(self.c1 + self.b1 * self.c1)
            self.c4 = self.c1 ** 2
            self.c1 = (1 - self.b1 + self.c1) * (1 - self.c1) / 8

        else:
            raise ValueError()

        self.l.p = (self.data.high + self.data.low)/2

    def prenext(self):

        self.l.butter[0] = self.l.p[0]

    def next(self):
        p = self.l.p
        if self.p.poles == 2:
            self.l.butter[0] = self.c1*(p[0]+2*p[-1]+p[-2]) + \
                                self.c2*self.l.butter[-1] + \
                                self.c3*self.l.butter[-2]
        elif self.p.poles == 3:
            self.l.butter[0] = self.c1 * (p[0] + 3 * p[-1] + 3 * p[-2] + p[-3]) + \
                                self.c2 * self.l.butter[-1] + \
                                self.c3 * self.l.butter[-2] + \
                                self.c4 * self.l.butter[-3]

class LaguerreFilter(bt.Indicator):

    lines = ('filter', 'p', 'L0', 'L1', 'L2', 'L3')

    params = (
        ('period', 48),
    )

    plotinfo = dict(
        plot=True,
        plotname='Laguerre Filter',
        subplot=False,
        plotlinelabels=True)

    plotlines = dict(p=dict(_plotskip=True, ),
                     L0=dict(_plotskip=True, ),
                     L1=dict(_plotskip=True, ),
                     L2=dict(_plotskip=True, ),
                     L3=dict(_plotskip=True, ),
                     )

    def __init__(self):
        self.addminperiod(30)
        self.alpha = 2/(self.p.period+1)
        self.l.p = (self.data.high + self.data.low)/2

    def prenext(self):

        self.l.L0[0] = self.l.p[0]
        self.l.L1[0] = self.l.p[-1]
        self.l.L2[0] = self.l.p[-2]
        self.l.L3[0] = self.l.p[-2]

    def next(self):
        a = self.alpha
        p = self.l.p
        self.l.L0[0] = a*p[0] + (1-a)*self.l.L0[-1]
        self.l.L1[0] = -(1 - a) * self.l.L0[0] + self.l.L0[-1] + (1 - a) * self.l.L1[-1]
        self.l.L2[0] = -(1 - a) * self.l.L1[0] + self.l.L1[-1] + (1 - a) * self.l.L2[-1]
        self.l.L3[0] = -(1 - a) * self.l.L2[0] + self.l.L2[-1] + (1 - a) * self.l.L3[-1]
        self.l.filter[0] = (self.l.L0[0] + 2*self.l.L1[0] + 2*self.l.L2[0] + self.l.L3[0])/6

class AdaptiveLaguerreFilter(bt.Indicator):

    lines = ('filter', 'p', 'L0', 'L1', 'L2', 'L3')

    params = (
        ('length', 20),
    )

    plotinfo = dict(
        plot=True,
        plotname='Laguerre Filter',
        subplot=False,
        plotlinelabels=True)

    plotlines = dict(p=dict(_plotskip=True, ),
                     L0=dict(_plotskip=True, ),
                     L1=dict(_plotskip=True, ),
                     L2=dict(_plotskip=True, ),
                     L3=dict(_plotskip=True, ),
                     )

    def __init__(self):
        self.addminperiod(60)
        self.l.p = (self.data.high + self.data.low) / 2

    def prenext(self):

        self.l.filter[0] = self.l.p[0]
        self.l.L0[0] = self.l.p[0]
        self.l.L1[0] = self.l.p[-1]
        self.l.L2[0] = self.l.p[-2]
        self.l.L3[0] = self.l.p[-2]

    def next(self):
        p = self.l.p
        diff = [abs(self.l.p[-i]-self.l.filter[-(i+1)]) for i in range(self.p.length)]
        HH = diff[0]
        LL = diff[0]
        for i in range(self.p.length):
            if diff[i] > HH:
                HH = diff[i]
            if diff[i] < LL:
                LL = diff[i]
        data = [(i - LL)/(HH - LL) for i in diff]
        if HH - LL != 0.0:
            a = np.median(data)

        self.l.L0[0] = a*p[0] + (1-a)*self.l.L0[-1]
        self.l.L1[0] = -(1 - a) * self.l.L0[0] + self.l.L0[-1] + (1 - a) * self.l.L1[-1]
        self.l.L2[0] = -(1 - a) * self.l.L1[0] + self.l.L1[-1] + (1 - a) * self.l.L2[-1]
        self.l.L3[0] = -(1 - a) * self.l.L2[0] + self.l.L2[-1] + (1 - a) * self.l.L3[-1]
        self.l.filter[0] = (self.l.L0[0] + 2*self.l.L1[0] + 2*self.l.L2[0] + self.l.L3[0])/6

class SqueezeVolatility(bt.Indicator):
    # Clone of the TradingBear Squeeze Volatility Indicator

    lines = ('hist', 'sqz', 'y', 'ma')

    params = (
        ('period', 10),
        ('mult', 2),
        ('period_kc', 10),
        ('mult_kc', 1.5),
        ('movav', bt.ind.SMA)
    )

    plotinfo = dict(
        plot=True,
        plotname='Squeeze Volatility',
        subplot=True,
        plotlinelabels=True)

    plotlines = dict(sqz=dict(_plotskip=False, ),
                     y=dict(_plotskip=True, ),
                     ma=dict(_plotskip=True, ),
                     )

    def __init__(self):

        self.addminperiod(self.p.period_kc*2)
        bands = bt.indicators.BollingerBands(self.data, period=self.p.period, devfactor=self.p.mult)
        self.l.ma = ma = self.p.movav(self.data,period=self.p.period_kc)
        atr = bt.indicators.ATR(self.data,period=self.p.period_kc)
        rma = self.p.movav(atr.atr, period=self.p.period_kc)
        uKC = ma + rma*self.p.mult_kc
        lKC = ma - rma*self.p.mult_kc

        bool = bt.And(bands.bot>lKC, bands.top<uKC)

        self.l.sqz = bt.If(bool,0.0,1.0)

    def prenext(self):

        self.l.y[0] = 0.0#self.data.close[0]

    def next(self):

        h = max(self.data.high.get(size=self.p.period_kc))
        l = min(self.data.low.get(size=self.p.period_kc))
        av1 = (h+l)/2
        av2 = (av1 + self.l.ma[0])/2
        self.l.y[0] = self.data.close[0] - av2

        # Perform Linear Regression
        x = np.arange(0,self.p.period_kc,1)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, self.l.y.get(size=self.p.period_kc))
        self.l.hist[0] = intercept + slope*(self.p.period_kc - 1.0).as_integer_ratio()

class SchaffTrendCycle(bt.Indicator):

    lines = ('schaff','macd','f1','f2','pf')

    params = (
        ('fast', 23),
        ('slow', 50),
        ('cycle', 10),
        ('factor', 0.5)
    )

    plotinfo = dict(
        plot=True,
        plotname='Schaff Trend Cycle',
        subplot=True,
        plotlinelabels=True)

    plotlines = dict(macd=dict(_plotskip=True, ),
                     f1=dict(_plotskip=True, ),
                     f2=dict(_plotskip=True, ),
                     pf=dict(_plotskip=True, ),
                     )

    def __init__(self):
        # Plot horizontal Line
        self.plotinfo.plotyhlines = [25,75]

        self.addminperiod(self.p.slow)
        self.l.macd = bt.indicators.MACD(self.data,period_me1=self.p.fast,period_me2=self.p.slow)

    def prenext(self):

        self.l.f1[0] = self.data.close[0]
        self.l.pf[0] = self.data.open[0]
        self.l.f2[0] = self.data.high[0]
        self.l.schaff[0] = self.data.low[0]

    def next(self):

        v1 = min(self.l.macd.get(size=self.p.cycle))
        v2 = max(self.l.macd.get(size=self.p.cycle))-v1

        self.l.f1[0] = 100*(self.l.macd[0]-v1)/v2 if v2 > 0 else self.l.f1[-1]
        self.l.pf[0] = self.l.pf[-1] + (self.p.factor*(self.l.f1[0]-self.l.pf[-1]))

        v3 = min(self.l.pf.get(size=self.p.cycle))
        v4 = max(self.l.pf.get(size=self.p.cycle))-v3

        self.l.f2[0] = 100*(self.l.pf[0]-v3)/v4 if v4 > 0 else self.l.f2[-1]
        self.l.schaff[0] = self.l.schaff[-1] + (self.p.factor*(self.l.f2[0]-self.l.schaff[-1]))

class SignalFiller(bt.Indicator):

    lines = ('signal',)

    def nexstart(self):
        self.l.signal[0] = 0.0

    def next(self):

        if self.data[0] != 0:
            self.l.signal[0] = self.data[0]
        else:
            self.l.signal[0] = self.l.signal[-1]

class NormalizedVolume(bt.Indicator):

    lines = ('ma','nv')

    params = (
        ('movav', bt.ind.SMA),
        ('period', 5),
    )

    plotinfo = dict(
        plot=True,
        plotname='Normalized Volume',
        subplot=True,
        plotlinelabels=True)

    plotlines = dict(ma=dict(_plotskip=True, ),
                     )

    def __init__(self):

        self.l.ma = self.p.movav(self.data.volume,period=self.p.period)
        #self.l.nv = 100*(self.data.volume/self.l.ma)

    def next(self):

        self.l.nv[0] = 100*self.data.volume[0]/self.l.ma[0]

class DamianiVolatmeter(bt.Indicator):

    lines = ('v','t','aF','sS','aS','sS')

    params = (
        ('atr_fast', 13),
        ('std_fast', 20),
        ('atr_slow', 40),
        ('std_slow', 100),
        ('thresh', 1.4),
        ('lag_supress', True)
    )

    plotinfo = dict(
        plot=True,
        plotname='Damiani Volatmeter',
        subplot=True,
        plotlinelabels=True)

    plotlines = dict(aF=dict(_plotskip=True, ),
                     aS=dict(_plotskip=True, ),
                     sF=dict(_plotskip=True, ),
                     sS=dict(_plotskip=True, ),
                     )

    def __init__(self):

        self.lag_s = 0.5
        self.l.aF = bt.indicators.AverageTrueRange(self.data,period=self.p.atr_fast)
        self.l.sF = bt.indicators.StandardDeviation(self.data.close,period=self.p.std_fast)

        self.l.aS = bt.indicators.AverageTrueRange(self.data, period=self.p.atr_slow)
        self.l.sS = bt.indicators.StandardDeviation(self.data.close, period=self.p.std_slow)

    def prenext(self):

        self.l.v[0] = 0.0050

    def next(self):

        s1 = self.l.v[-1]
        s3 = self.l.v[-3]

        self.l.v[0] = self.l.aF[0]/self.l.aS[0] + self.lag_s*(s1-s3) if self.p.lag_supress else self.l.aF[0]/self.l.aS[0]
        anti_thresh = self.l.sF[0]/self.l.sS[0]
        self.l.t[0] = self.p.thresh - anti_thresh
