from opt_utilities import *

class Optimization(object):

    def __init__(self):
        self.master = MasterParameters()
        self.ingest = dict()
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


    def load_indicators(self,density):
        self.baseline(8,60)
        self.confirmation(8,60)
        for typ, ind in self.ingest.items():
            for name, args in ind.items():
                self.master.add_indicator(typ,name,args['input'],args['conds'],density)

opt = Optimization()
opt.load_indicators(10)

for i in opt.master.parameter_sets['confirmation']:
    print(i)