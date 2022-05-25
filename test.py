import pandas as pd
from requests import head

RATINGS_PATH = "dummy_ICML.xls"

df = pd.read_excel(RATINGS_PATH, header=2)

print(df.columns)