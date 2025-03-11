import numpy as np
import pandas as pd
import pandas_ta as ta


"""_summary_
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © TZack88

//@version=5
indicator('RSI Momentum Trend', overlay=true)

// ** ---> Inputs ------------- {
var bool positive       = false
var bool negative       = false
string RSI_group        = "RSI Settings"
string mom_group        = "Momentum Vales"
string visual           = "Visuals" 
int Len2                = input(14,"RSI 1️⃣",inline = "rsi",group = RSI_group)
int pmom                = input(65," Positive above",inline = "rsi1",group =RSI_group )
int nmom                = input(32,"Negative below",inline = "rsi1",group =RSI_group )
bool showlabels         = input(true,"Show Momentum ❓",inline = "001",group =visual )
color p                 = input(color.rgb(76, 175, 79, 62),"Positive",inline = "001",group =visual )
color n                 = input(color.rgb(255, 82, 82, 66),"Negative",inline = "001",group =visual )
bool filleshow          = input(true,"Show highlighter ❓",inline = "002",group =visual )
color bull              = input(color.rgb(76, 175, 79, 62),"Bull",inline = "002",group =visual )
color bear              = input(color.rgb(255, 82, 82, 66),"Bear",inline = "002",group =visual )
rsi                     = ta.rsi(close, Len2)
//------------------- }

// ** ---> Momentums ------------- {

p_mom               = rsi[1] < pmom and rsi > pmom and rsi > nmom and ta.change(ta.ema(close,5)) > 0
n_mom               = rsi < nmom and ta.change(ta.ema(close,5)) < 0
if p_mom
    positive:= true
    negative:= false

if n_mom
    positive:= false
    negative:= true     

// ** ---> Entry Conditions ------------- {

a = plot(filleshow ? ta.ema(high,5) : na,display = display.none,editable = false)
b = plot(filleshow ? ta.ema(low,10) : na,style = plot.style_stepline,color = color.red,display = display.none,editable = false)

// fill(a,b,color = color.from_gradient(rsi14,35,pmom,color.rgb(255, 82, 82, 66),color.rgb(76, 175, 79, 64)) )
fill(a,b,color = positive ? bull :bear ,editable = false)

//plotting 
pcondition = positive and not positive[1]
ncondition2 = negative and not negative[1]
plotshape(showlabels ? pcondition: na , title="Positive Signal",style=shape.labelup, color=p, location= location.belowbar , size=size.tiny,text= "Positive",textcolor = color.white)
plotshape(showlabels ? ncondition2: na , title="Negative Signal",style=shape.labeldown, color=n, location= location.abovebar , size=size.tiny,text = "Negative",textcolor = color.white)
// Alerts //
alertcondition(pcondition,"Positive Trend")
alertcondition(ncondition2,"Negative Trend")
//
"""


# Input parameters
Len2 = 14  # RSI period
pmom = 65  # Positive momentum threshold
nmom = 32  # Negative momentum threshold

def calculate_rsi_momentum_trend(df: pd.DataFrame,Len2:int = 14,pmom:int = 65 ,nmom: int = 32):
    """
    Converts the RSI Momentum Trend from PineScript to Python.
    :param df: DataFrame with columns ['open', 'high', 'low', 'close']
    :return: DataFrame with calculated RSI, momentum conditions, and signals.
    """
    # Calculate RSI
    df['rsi'] = ta.rsi(df['close'], length=Len2)
    
    # Calculate EMA changes
    df['ema_5'] = ta.ema(df['close'], length=5)
    df['ema_5_change'] = df['ema_5'].diff()

    # Momentum conditions
    df['p_mom'] = (df['rsi'].shift(1) < pmom) & (df['rsi'] > pmom) & (df['rsi'] > nmom) & (df['ema_5_change'] > 0)
    df['n_mom'] = (df['rsi'] < nmom) & (df['ema_5_change'] < 0)

    # Flags for positive and negative conditions
    df['positive'] = False
    df['negative'] = False

    df.loc[df['p_mom'], 'positive'] = True
    df.loc[df['n_mom'], 'negative'] = True

    # Entry conditions
    df['pcondition'] = (df['positive'] & ~df['positive'].shift(1).fillna(False))
    df['ncondition'] = (df['negative'] & ~df['negative'].shift(1).fillna(False))

    # Output signals
    df['signal'] = np.where(df['pcondition'], 'Positive', np.where(df['ncondition'], 'Negative', None))

    return df[['rsi', 'ema_5', 'p_mom', 'n_mom', 'positive', 'negative', 'pcondition', 'ncondition', 'signal']]

# Example usage
# Create a sample DataFrame with OHLC data
data = pd.DataFrame({
    'open': np.random.random(500),
    'high': np.random.random(500),
    'low': np.random.random(500),
    'close': np.random.random(500)
})
df = pd.DataFrame(data)

# Calculate RSI Momentum Trend
result = calculate_rsi_momentum_trend(df)

print(result)
