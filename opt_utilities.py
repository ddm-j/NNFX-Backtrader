import backtrader as bt
from collections import OrderedDict
import numpy as np
from itertools import product
import operator


class IndicatorParameters(object):

    """
    Class that controls indicator parameters for optimization
    """

    def __init__(self, name, input, conditions, density):

        self.mas = [bt.ind.SMA,
                    bt.ind.EMA,
                    bt.ind.HMA,
                    bt.ind.WMA,
                    bt.ind.DEMA]

        self.input = input
        self.conditions = conditions
        self.name = name
        self.density = density

    def get_truth(self, inp, relate, cut):
        ops = {'>': operator.gt,
               '<': operator.lt,
               '>=': operator.ge,
               '<=': operator.le,
               '=': operator.eq}
        return ops[relate](inp, cut)

    def get_ranges(self):

        # Loop through types and range bounds
        self.ranges = OrderedDict()

        for i, p in self.input.items():
            typ = p[0]
            bounds = p[1]
            if typ not in [int, float]:
                if typ == 'custom':
                    self.ranges[i] = bounds
                else:
                    # Type of Parameter is Non-numeric
                    self.ranges[i] = [True, False] if typ == bool else self.mas
            else:
                # Type of Parameter is an integer or float
                if typ == int:
                    step = int((bounds[1]-bounds[0])/self.density) if len(bounds)>1 else None
                    self.ranges[i] = np.arange(bounds[0],bounds[1],step) if len(bounds)>1 else bounds
                if typ == float:
                    self.ranges[i] = np.linspace(bounds[0],bounds[1],self.density) if len(bounds)>1 else bounds

    def test_conditions(self,params):
        test = [not self.get_truth(params[i[0]],i[1],params[i[2]]) for i in self.conditions]
        if any(test):
            return True
        else:
            return False

    def generate_combinations(self):
        if self.ranges:
            ranges = [i for key,i in self.ranges.items()]
            combinations = list(product(*ranges))

            # Remove parameter sets that conflict with conditions
            for i in combinations[:]:
                if self.conditions:
                    if self.test_conditions(i):
                        combinations.remove(i)

            self.combinations =  [(self.name, i) for i in combinations]

    def get(self):

        self.get_ranges()
        self.generate_combinations()

class MasterParameters(object):

    def __init__(self):
        self.parameter_sets = {
            'baseline':[],
            'confirmation':[],
            'volume':[],
            'exit':[]
        }

    def add_indicator(self,ind_type,name,input,conditions,density):
        ind = IndicatorParameters(name,input,conditions,density)
        ind.get()
        param_set = ind.combinations
        self.parameter_sets[ind_type].append(param_set)


