import backtrader as bt
import glob

# Custome Forex Commission Scheme

class forexSpreadCommisionScheme(bt.CommInfoBase):
    '''
    This commission scheme attempts to calcuate the commission hidden in the
    spread by most forex brokers. It assumes a mid point data is being used.

    *New Params*
    spread: Float, the spread in pips of the instrument
    JPY_pair: Bool, states whether the pair being traded is a JPY pair
    acc_counter_currency: Bool, states whether the account currency is the same
    as the counter currency. If false, it is assumed to be the base currency
    '''
    params = (
        ('spread', 2.0),
        ('stocklike', False),
        ('JPY_pair', False),
        ('method', 0),
        ('exchange_rate', 0.0),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        )

    def _getcommission(self, size, price, pseudoexec):
        '''
        This scheme will apply half the commission when buying and half when selling.
        If JPY pair change the multiplier accordingly.
        If account currency is same as the base currency, change pip value calc.
        '''


        multiplier = 100.0 if self.p.JPY_pair else 1.0

        if self.p.method == 0:
            # Account Currency Same as Counter - Pip Cost $0.0001
            pip_cost = 0.0001
        elif self.p.method == 1:
            # Acoount Currency Same as Base - Pip Cost $0.0001/USDXXX
            pip_cost = 0.0001/price
        elif self.p.method == 2:
            # Account Currency Neither Base or Counter - Pip Cost $0.0001/Exchange_Rate
            # Exchange Rate = AccountCurrency/Counter
            pip_cost = 0.0001/self.p.exchange_rate

        pip_cost = pip_cost*multiplier

        comm = self.p.spread*pip_cost*size

        return comm

def notifier(order,date,sl_list,verbose=True):
    if hasattr(order,'Accepted'):
        # Is an Order Object
        if order.status == order.Accepted:
            if verbose:
                print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
                print('Order Accepted')
                print('{}, {}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                    date,
                    order.data._name,
                    order.status,
                    order.ref,
                    order.size,
                    'NA' if not order.price else round(order.price, 5)
                ))
                print('-' * 80)


        if order.status == order.Completed:
            if verbose:
                print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
                print('Order Completed')
                print('{}, {}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                    date,
                    order.data._name,
                    order.status,
                    order.ref,
                    order.size,
                    'NA' if not order.price else round(order.price, 5)
                ))
                print('Created: {} Price: {} Size: {}'.format(bt.num2date(order.created.dt), order.created.price,
                                                              order.created.size))
                print('-' * 80)

        if order.status == order.Canceled:
            if order.ref == sl_list[-1]:
                textfield = ' - Take Profit Hit, Setting new Stop Level'
            else:
                textfield = ''
            if verbose:
                print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
                print('Order Canceled'+textfield)
                print('{}, {}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                    date,
                    order.data._name,
                    order.status,
                    order.ref,
                    order.size,
                    'NA' if not order.price else round(order.price, 5)
                ))
                print('-' * 80)
            if order.ref == sl_list[-1]:
                return order.size/2, order.price

        if order.status == order.Rejected:
            if verbose:
                print('-' * 32, ' NOTIFY ORDER ', '-' * 32)
                print('WARNING! Order Rejected')
                print('{}, {}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                    date,
                    order.data._name,
                    order.status,
                    order.ref,
                    order.size,
                    'NA' if not order.price else round(order.price, 5)
                ))
                print('-' * 80)

    else:
        # Order is actually a "trade"
        trade = order
        if trade.isclosed:
            if verbose:
                print('-' * 32, ' NOTIFY TRADE ', '-' * 32)
                print('{}, Close Price: {}, Profit, Gross {}, Net {}'.format(
                    date,
                    trade.price,
                    round(trade.pnl, 2),
                    round(trade.pnlcomm, 2)))
                print('-' * 80)


def printTradeAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total,2)
    strike_rate = (total_won / total_closed) * 100
    #Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate','Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed,total_won,total_lost]
    r2 = [round(strike_rate,2), win_streak, lose_streak, pnl_net]
    #Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    #Print the rows
    print_list = [h1,r1,h2,r2]
    row_format ="{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))

def printSQN(analyzer):
    sqn = round(analyzer.sqn,2)
    print('SQN: {}'.format(sqn))

class CSVData(bt.feeds.GenericCSV):

    params = (
        ('openinterest',-1),
        ('dtformat','%d.%m.%Y %H:%M:%S.000'),
    )

def file_browser():
    paths = [f.split('\\')[1] for f in glob.glob('Data/*.csv')]
    names = [f.split('.')[0] for f in paths]
    return paths, names