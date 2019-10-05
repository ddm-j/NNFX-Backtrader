from opt_utilities import *
from itertools import product

class Optimization(object):

    def __init__(self,selections):
        self.master = MasterParameters()
        self.ingest = dict()
        self.selections = selections
        # Define The Indicators for Optimization

    def baseline(self,lower,upper):
        typ = 'baseline'
        self.ingest[typ] = dict()

        # Kijun Sen
        self.ingest[typ]['kijun'] = {
            'input':{
                0:(int,[lower,upper])
            },
            'conds':None,
        }

        # General Moving Average
        self.ingest[typ]['ma'] = {
            'input':{
                0:('mas',None),
                1:(int,[lower,upper])
            },
            'conds':None,
        }

        # iTrend
        self.ingest[typ]['itrend'] = {
            'input': {
                0: (int,[lower, upper])
            },
            'conds': None,
        }

        # FAMA
        self.ingest[typ]['fama'] = {
            'input': {
                0: (int,[lower, upper]),
                1: (int,[lower, upper])
            },
            'conds': [
                [1,'>',0]
            ],
        }

        # MAMA
        self.ingest[typ]['mama'] = {
            'input': {
                0: (int,[lower, upper]),
                1: (int,[lower, upper])
            },
            'conds': [
                [1,'>',0]
            ],
        }

        # Laguerre
        self.ingest[typ]['laguerre'] = {
            'input': {
                0: (int,[lower, upper])
            },
            'conds': None,
        }

        # Adaptive Laguerre
        self.ingest[typ]['alaguerre'] = {
            'input': {
                0: (int,[5, 50])
            },
            'conds': None,
        }

        # Butterworth Filter
        self.ingest[typ]['butter'] = {
            'input': {
                0: (int,[lower, upper]),
                1: ('custom',[2,3])
            },
            'conds': None,
        }

    def confirmation(self,lower,upper):
        typ = 'confirmation'
        self.ingest[typ] = dict()

        # iTrend
        self.ingest[typ]['itrend'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # Cyber Cycle
        self.ingest[typ]['cybercyle'] = {
            'input':{
                0:(int,[lower,upper])
            },
            'conds':None,
        }

        # Adaptive Cyber Cycle
        self.ingest[typ]['adaptivecybercycle'] = {
            'input': {
                0: (int, [lower, upper]),
                1: (int, [5,20])
            },
            'conds': None,
        }

        # SSL
        self.ingest[typ]['ssl'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # Aroon Up & Down
        self.ingest[typ]['aroon'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # Trend Trigger Factor
        self.ingest[typ]['ttf'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # Trend Direction & Force Index
        self.ingest[typ]['tdfi'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # CMF - Chaikin Money Flow
        self.ingest[typ]['cmf'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # ASH - Absolute Strength Index
        self.ingest[typ]['ash'] = {
            'input': {
                0: (int, [lower, upper]),
                1: ('custom',[2,3,4]),
                2: ('custom',[0,1]),
                3: (float,[0.1,1.0]),
                4: ('custom',[bt.ind.SMA,bt.ind.EMA]),
                5: ('custom',[None]),
                6: ('custom',[None])
            },
            'conds': None,
        }

        # Elher's Roofing Filter
        self.ingest[typ]['roof'] = {
            'input': {
                0: (int, [lower, upper]),
                1: (int, [lower, upper]),
                2: ('custom', [2,3,4,5])
            },
            'conds': [
                [0,'>',1]
            ],
        }

        # MAMA
        self.ingest[typ]['mama'] = {
            'input': {
                0: (int, [lower, upper]),
                1: (int, [lower, upper])
            },
            'conds': [
                [1, '>', 0]
            ],
        }

        # Elher's Decycler Oscillator
        self.ingest[typ]['dosc'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # Decycler with inverse Fisher Transform
        self.ingest[typ]['idosc'] = {
            'input': {
                0: (int, [lower, upper]),
                1: ('custom', [2, 3, 4, 5])
            },
            'conds': None,
        }

        # Schaff Trend Cycle
        self.ingest[typ]['schaff'] = {
            'input': {
                0: (int, [lower, upper]),
                1: (int, [lower, upper]),
                2: (int, [5, 20]),
                3: (float, [0.1, 1.0])
            },
            'conds': [
                [1,'>',0]
            ],
        }

    def volume(self,lower,upper):
        typ = 'volume'
        self.ingest[typ] = dict()

        # CVI - Chaikin Volatility Index
        self.ingest[typ]['cvi'] = {
            'input': {
                0: (int, [lower, upper]),
                1: (int, [lower, upper])
            },
            'conds': None,
        }

        # Trend Direction & Force Index
        self.ingest[typ]['tdfi'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # WAE - Waddah Attar Explosion
        self.ingest[typ]['wae'] = {
            'input': {
                0: ('custom', [50,100,150,200,250,300]), # Sensitivity
                1: (int, [lower, upper]), # Fast
                2: (int, [lower, upper]), # Slow
                3: (int, [lower, upper]), # Channel
                4: ('custom', [0.5,1.0,1.5,2.0,2.5,3.0]), # STD Dev
                5: (float, [1.0,5.0]) # Dead Zone Value
            },
            'conds': [
                [2, '>', 1]
            ],
        }

        # TTM Squeeze Volatility
        self.ingest[typ]['squeeze'] = {
            'input': {
                0: (int, [lower, upper]), #period
                1: (float, [0.25, 3.0]), #mult
                2: (int, [lower, upper]), #period_kc
                3: (float, [0.25, 3.0]), #mult_kc
                4: ('mas', None)
            },
            'conds': None,
        }

        # Damiani Volatmeter
        self.ingest[typ]['damiani'] = {
            'input': {
                0: (int, [lower, upper]), # Fast ATR
                1: (int, [lower, upper]), # Fast STD
                2: (int, [lower, upper]), # Slow ATR
                3: (int, [lower, upper]), # Slow STD
                4: (float, [0.5, 3.0]), # Threshold
                5: (bool, None)
            },
            'conds': [
                [2, '>', 0],
                [3, '>', 1]
            ],
        }

    def exit(self,lower, upper):
        typ = 'exit'
        self.ingest[typ] = dict()

        # SSL Channel
        self.ingest[typ]['ssl'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # iTrend
        self.ingest[typ]['itrend'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

        # MAMA
        self.ingest[typ]['mama'] = {
            'input': {
                0: (int, [lower, upper]),
                1: (int, [lower, upper]),
            },
            'conds': [
                [1, '>', 0]
            ],
        }

        # Decylcer Oscillator
        self.ingest[typ]['dosc'] = {
            'input': {
                0: (int, [lower, upper])
            },
            'conds': None,
        }

    def load_indicators(self,density):
        self.baseline(8,40)
        self.confirmation(8,40)
        self.volume(8,40)
        self.exit(8,40)
        for typ, ind in self.ingest.items():
            for name, args in ind.items():
                if name not in self.selections[typ]:
                    continue
                self.master.add_indicator(typ,name,args['input'],args['conds'],density)

    def generate_combinations(self):

        baseline = [item for sublist in self.master.parameter_sets['baseline'] for item in sublist]
        confirmation = [item for sublist in self.master.parameter_sets['confirmation'] for item in sublist]
        volume = [item for sublist in self.master.parameter_sets['volume'] for item in sublist]
        exit = [item for sublist in self.master.parameter_sets['exit'] for item in sublist]

        combinations = list(product(baseline,confirmation,confirmation,volume,exit))
        print(len(combinations))


# Selection Tests
selections = {
    'baseline': ['kijun'],
    'confirmation': ['itrend'],
    'volume': ['cvi'],
    'exit': ['itrend']
}

opt = Optimization(selections)

opt.load_indicators(5)
opt.generate_combinations()

