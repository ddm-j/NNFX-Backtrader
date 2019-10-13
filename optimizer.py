from opt_utilities import *
from itertools import product
from custom_functions import *
from nnfx import NNFX
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
from deap import base, creator, tools
import random

class Optimization(object):

    def __init__(self,mode,selections,density,lower,upper):
        self.master = MasterParameters()
        self.ingest = dict()
        self.selections = selections
        self.density = density
        self.mode = mode
        self.lower = lower
        self.upper = upper
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
                0: (int, [lower, upper]),
                1: ('custom', [0.05])
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
                0: (int, [lower, upper]),
                1: ('custom', [0.05])
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

    def filter_indicators(self):

        for typ, ind in self.ingest.items():
            for name, args in ind.items():
                if name not in self.selections[typ]:
                    continue
                if self.mode == 'brute':
                    self.master.add_indicator(typ,name,args['input'],args['conds'],self.density)
                elif self.mode == 'genetic':
                    self.key[name] = args

    def load_indicators(self):

        self.baseline(self.lower,self.upper)
        self.confirmation(self.lower,self.upper)
        self.volume(self.lower,self.upper)
        self.exit(self.lower,self.upper)
        self.filter_indicators()

    def generate_combinations(self):

        baseline = [item for sublist in self.master.parameter_sets['baseline'] for item in sublist]
        confirmation = [item for sublist in self.master.parameter_sets['confirmation'] for item in sublist]
        volume = [item for sublist in self.master.parameter_sets['volume'] for item in sublist]
        exit = [item for sublist in self.master.parameter_sets['exit'] for item in sublist]

        combinations = list(product(baseline,confirmation,confirmation,volume,exit))
        combinations  = [x for x in combinations if x[1][0]!=x[2][0]]
        self.combinations = combinations

    def brute(self):

        # Parameter Initialization

        print('Loading Indicators')
        self.load_indicators(5)
        print('Generating Combinations')
        self.generate_combinations()
        print('%i Combinations generated for testing' % len(self.combinations))

        # Create a cerebro entity
        cerebro = bt.Cerebro(stdstats=False)

        # Enable Slippage on Open Price (Approximately %0.01 percent)
        cerebro.broker = bt.brokers.BackBroker(slip_perc=0.0001, slip_open=True)

        # Add our strategy

        cerebro.optstrategy(NNFX,optim=self.combinations[0:30])

        # Get Data Files from Data Folder
        paths, names = file_browser()

        dpath = 'Data/'
        datasets = [
            (dpath + path, name) for path, name in zip(paths, names)
        ]

        trade_pairs = ['EURUSD','GBPUSD','USDCHF','USDJPY']
        datasets = [i for i in datasets if i[1] in trade_pairs]

        # Create a Data Feeds and Add to Cerebro

        for i in range(len(datasets)):
            data = bt.feeds.GenericCSVData(dataname=datasets[i][0],
                                           openinterest=-1,
                                           dtformat='%d.%m.%Y %H:%M:%S.000')
            cerebro.adddata(data, name=datasets[i][1])

        # Set our desired cash start
        cerebro.broker.setcash(1000.0)

        # Add Analyzers
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

        #opt_count_total = len(self.combinations[0:10])
        #pbar = tqdm(smoothing=0.05, desc='Optimization', total=opt_count_total)
        #def optimization_step(NNFX):
        #    pbar.update()

        #cerebro.optcallback(optimization_step)
        t0 = time.time()
        res = cerebro.run()
        t1 = time.time()

        print('Time Elapsed: %.2f'% (t1-t0))

        return_opt = pd.DataFrame({r[0].params.optim: r[0].analyzers.sqn.get_analysis() for r in res}).T.loc[:,['sqn']]
        return_opt.to_csv('opt_results.csv')
        print(return_opt)

    def encode_chromosome(self):

        self.key = dict()
        self.load_indicators()
        chromo_map = []
        chromo_range = []
        chromo_conds = []
        for i, (ind, args) in enumerate(self.key.items()):
            for j, (input, params) in enumerate(args.items()):
                if input == 'input':
                    for k, param in params.items():
                        chromo_map.append(param[0])
                        chromo_range.append(param[1])
                elif input == 'conds':
                    if params:
                        re_index = []
                        for cond_set in params:
                            re_index.append([cond_set[0]+i,cond_set[1],cond_set[2]+i])
                        chromo_conds.append(re_index)

        return chromo_map, chromo_conds, chromo_range

    def decode_chromosome(self,chromo):
        decoded = []
        i = 0
        for j, (ind,args) in enumerate(self.key.items()):
            params = []
            for k, (name, gene) in enumerate(args['input'].items()):
                params.append(chromo[i])
                i += 1
            decoded.append([ind,params])
        return decoded

    def evaluate_pop(self,pop,metric):

        # Create a cerebro entity
        cerebro = bt.Cerebro(stdstats=False)

        # Enable Slippage on Open Price (Approximately %0.01 percent)
        cerebro.broker = bt.brokers.BackBroker(slip_perc=0.0001, slip_open=True)

        # Add our strategy
        cerebro.optstrategy(NNFX, optim=pop)

        # Get Data Files from Data Folder
        paths, names = file_browser()

        dpath = 'Data/'
        datasets = [
            (dpath + path, name) for path, name in zip(paths, names)
        ]

        trade_pairs = ['EURUSD', 'GBPUSD', 'USDCHF', 'USDJPY']
        datasets = [i for i in datasets if i[1] in trade_pairs]

        # Create a Data Feeds and Add to Cerebro
        for i in range(len(datasets)):
            data = bt.feeds.GenericCSVData(dataname=datasets[i][0],
                                           openinterest=-1,
                                           dtformat='%d.%m.%Y %H:%M:%S.000')
            cerebro.adddata(data, name=datasets[i][1])

        # Set our desired cash start
        cerebro.broker.setcash(1000.0)

        # Add Analyzers
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(bt.analyzers.Returns, _name='ret')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')

        res = cerebro.run()

        return_opt = dict()
        return_opt['params'] = []
        return_opt['ret'] = []
        return_opt['sqn'] = []
        return_opt['dd'] = []
        return_opt['cal'] = []
        for r in res:
            params = r[0].params.optim
            ret = r[0].analyzers.ret.get_analysis()['rnorm']
            sqn = r[0].analyzers.sqn.get_analysis()['sqn']
            dd = r[0].analyzers.dd.get_analysis().max.drawdown
            try:
                cal = ret / (dd / 100)
            except:
                cal = 'nan'
            return_opt['params'].append(params)
            return_opt['ret'].append(ret)
            return_opt['sqn'].append(sqn)
            return_opt['dd'].append(dd)
            return_opt['cal'].append(cal)
        return return_opt[metric]

    def get_truth(self, inp, relate, cut):
        ops = {'>': operator.gt,
               '<': operator.lt,
               '>=': operator.ge,
               '<=': operator.le,
               '=': operator.eq}
        return ops[relate](inp, cut)

    def checkBounds(self, ranges):
        def decorator(func):
            def wrapper(*args, **kargs):
                offspring = func(*args, **kargs)
                for child in offspring:
                    for i in range(len(child)):
                        if ranges[i] and child[i] > ranges[i][1]:
                            child[i] = ranges[i][1]
                        elif ranges[i] and child[i] < ranges[i][0]:
                            child[i] = ranges[i][0]
                return offspring
            return wrapper
        return decorator

    def genetic(self):

        # Fitness Definition
        creator.create('FitnessMax', base.Fitness, weights=(1.0,))

        # Individual Definition
        creator.create('Individual', list, fitness=creator.FitnessMax)

        # Genetic Toolbox
        toolbox = base.Toolbox()

        # Register the Attributes
        types, conds, ranges = self.encode_chromosome()
        attributes = []
        for i, (t, r) in enumerate(zip(types,ranges)):
            attributes.append(i)
            if t == int:
                toolbox.register(str(i), random.randint, r[0], r[1])
            elif t == bool:
                toolbox.register(str(i), random.randint, 0, 1)
            elif t == float:
                toolbox.register(str(i), random.uniform, r[0], r[1])
            elif t == 'custom':
                toolbox.register(str(i), random.choice, r)
            else:
                print('ERROR - NO TYPE DETECTION SETUP')
        attributes = [getattr(toolbox,str(i)) for i in attributes]

        # Register the Individual
        toolbox.register("individual", tools.initCycle, creator.Individual, tuple(attributes), n=1)

        # Register the Population
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # Register Evalutation
        toolbox.register("evaluate", self.evaluate_pop)

        # Register Mating
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.decorate("mate", self.checkBounds(ranges))

        # Register Mutation
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.decorate("mutate", self.checkBounds(ranges))

        # Register Selection
        toolbox.register("select", tools.selTournament, tournsize=3)

        # MAIN ALGORITHM
        pop = toolbox.population(n=3000)
        fitnesses = self.evaluate_pop([self.decode_chromosome(i) for i in pop],'ret')
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = (fit,)

        CXPB, MUTPB = 0.5, 0.2

        # Extracting all the fitnesses
        fits = [ind.fitness.values[0] for ind in pop]

        # Begin the evolution
        NGEN = 20
        for i in tqdm(range(NGEN)):
            # A new generation
            print("-- Generation %i --" % i)

            # Select the next generation individuals
            offspring = toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = list(map(toolbox.clone, offspring))

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < CXPB:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            for ind in invalid_ind[:]:
                for i, r in zip(ind,ranges):
                    if r and (i < r[0] or i > r[1]):
                        invalid_ind.remove(ind)

            print('Popluation Size: %i'%len(invalid_ind))

            fitnesses = self.evaluate_pop([self.decode_chromosome(i) for i in invalid_ind],'ret')
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = (fit,)

            pop[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in pop]

            print('Best Individual')
            print(self.decode_chromosome(invalid_ind[np.argmax(fitnesses)]))

            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean ** 2) ** 0.5

            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)

    def optimize(self):
        if self.mode == 'brute':
            self.brute()
        elif self.mode == 'genetic':
            self.genetic()

if __name__ == '__main__':

    #freeze_support()
    # Selection Tests
    selections = {
        'baseline': ['alaguerre'],
        'confirmation': ['itrend','mama'],
        'volume': ['damiani'],
        'exit': ['dosc']
    }


    opt = Optimization(mode='genetic',selections=selections,density=5,lower=8,upper=60)
    opt.optimize()



