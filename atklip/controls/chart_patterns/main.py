import pandas as pd
import numpy as np

from tradingpatterns import detect_head_shoulder

from hard_data import generate_sample_df_with_pattern
# Have price data (OCHLV dataframe)

df = pd.read_pickle("data_indicator_oanda_xau_usd_m15_full.pkl")

df = pd.DataFrame(df)

# Apply pattern indicator screener
df = detect_head_shoulder(df)


df.loc[df['head_shoulder_pattern'] == pd.NA, 'high_roll_max'] = pd.NA

#df = df.loc[df['head_shoulder_pattern'] == np.nan, 'low_roll_min'] = np.nan

print(df.iloc[-30:])