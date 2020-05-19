import pandas as pd
import numpy as np
import time
import ta

class Indicator:
    data_frame = None

    def __init__(self, iqoption_api, symbol, time_frame ):
        dataIQ= iqoption_api.get_candles(symbol.upper(),time_frame*60,100,time.time())
        self.data_frame = pd.DataFrame(dataIQ).sort_values(by=["id"], ascending=True)

    def get_moving_average(self, period, candle_number = 0):
        
        if (candle_number <= 0):
            candle_number = None
            start = period
        else:
            start = candle_number + period -1
            candle_number = (candle_number - 1) * -1
        
        start = start * -1
        values = self.data_frame['close'][start:candle_number]
        weigths = np.repeat(1.0, period)/period
        smas = np.convolve(values, weigths, 'valid')

        return smas[0] # as a numpy array

    def get_exponential_moving_average(self, period):
        
        values = self.data_frame['close'][-period:]
        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()
        a =  np.convolve(values, weights, mode='full')[:len(values)]
       
        return a[-1:][0]

    def get_relative_strength_index(self, period):

        values = self.data_frame['close'][-period:]

        deltas = np.diff(values)
        seed = deltas[:period+1]
        up = seed[seed>=0].sum()/period
        down = -seed[seed<0].sum()/period
        rs = up/down
        rsi = np.zeros_like(values)
        rsi[:period] = 100. - 100./(1.+rs)

        for i in range(period, len(values)):
            delta = deltas[i-1] # cause the diff is 1 shorter

            if delta>0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period

            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)

        return rsi[-1:][0]

    def get_rsi(self, period):

        return self.get_relative_strength_index(period)
    
    def get_adx(self, period):

        try:
            
            df = ta.utils.dropna(self.data_frame)
            adx = ta.trend.adx(df['max'], df['min'], df['close'], period, True)

            return adx.tolist()[-1]
        except:
            return 0.0

    def get_trend(self):
    
        adx = self.get_adx(14)
        smaPrevious = self.get_moving_average(14,3)
        smaNow = self.get_moving_average(14)

        diff_sma = round(round(smaNow, 6) - round(smaPrevious, 6), 6)
        
        response = {}
        response["up"] = False
        response["down"] = False
        response['is_strong'] = False

        if adx > 25:
            response['is_strong'] = True

        if diff_sma > 0:
            response['up'] = True
        else:
            response['down'] = True

        return response