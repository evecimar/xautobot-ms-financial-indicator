from src.Indicator import Indicator
from iqoptionapi.stable_api import IQ_Option

email = ''
passord = ''
symbol = 'EURUSD'
time_frame = 5

iqoption = IQ_Option(email, passord)
indicators = Indicator(iqoption, symbol, time_frame)

rsi = indicators.get_rsi(14)