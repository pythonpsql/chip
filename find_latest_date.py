from datetime import datetime
from dateutil.parser import parse
# import pandas as pd
string_ = '20180201'
d=datetime.strptime(string_, '%Y%m%d')
print(d)
string_2 = '20180202'
d2=datetime.strptime(string_2, '%Y%m%d')
print(d>d2)



