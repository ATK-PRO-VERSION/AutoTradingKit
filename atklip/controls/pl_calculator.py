import streamlit as st


def calculate_pl_with_fees(entry_price: float, exit_price: float, 
                           capital=1000, proportion_closed=100, 
                           leverage: int=1, taker_fee: float=0, 
                           maker_fee: float=0, order_type: str="market",
                           is_stop_loss=False):
    """_summary_
    Args:
        entry_price (float): _description_
        exit_price (float): _description_
        capital (int, optional): _description_. Defaults to 1000.
        leverage (int, optional): _description_. Defaults to 5.
        proportion_closed (int, optional): _description_. Defaults to 100.
        taker_fee (float, optional): fee for market order. Defaults to 0.05.
        maker_fee (float, optional): fee for litmit order. Defaults to 0.02.
        order_type (str, optional): limit or market. Defaults to "market".
        is_stop_loss (bool, optional): order has stoped or not. Defaults to False.
    Returns:
        _type_: _description_
    """
    taker_fee = taker_fee/100
    maker_fee = maker_fee/100
    total_position_value = capital * leverage
    close_fee = 0
    if order_type == "market":
        open_fee = total_position_value * taker_fee
        if is_stop_loss:
            close_fee = total_position_value *taker_fee* proportion_closed
    else:
        open_fee = total_position_value * maker_fee
        if is_stop_loss:
            close_fee = total_position_value *maker_fee* proportion_closed

    price_difference = abs(entry_price - exit_price)
        
    percent_change = price_difference / entry_price
    leverage_gain = percent_change * leverage
    capital_gain = leverage_gain * capital * proportion_closed
    pl = capital_gain - open_fee * proportion_closed - close_fee
    return round(pl, 4)

def calculate_recommended_capital(entry_price: float, stop_loss_price: float, 
                                  total_capital: float=1000, risk_percentage: float=2, 
                                  leverage: int=1, taker_fee: float=0, maker_fee: float=0, 
                                  order_type: str="market"):
    """_summary_

    Args:
        entry_price (float): _description_
        stop_loss_price (float): _description_
        total_capital (float, optional): _description_. Defaults to 1000.
        risk_percentage (float, optional): _description_. Defaults to 2.
        leverage (int, optional): _description_. Defaults to 5.
        taker_fee (float, optional): _description_. Defaults to 0.05.
        maker_fee (float, optional): _description_. Defaults to 0.02.
        order_type (str, optional): _description_. Defaults to "market".

    Returns:
        _type_: _description_
    """
    taker_fee = taker_fee/100
    maker_fee = maker_fee/100
    capital_to_risk = total_capital * (risk_percentage / 100)
    price_difference = abs(entry_price - stop_loss_price)
    percent_change_sl = price_difference / entry_price
    leveraged_loss_per_unit = percent_change_sl * leverage
    
    if order_type == "market":
        total_taker_fee = entry_price * leverage * taker_fee * 2
    else:
        total_taker_fee = entry_price * leverage * maker_fee * 2
    
    effective_loss_per_unit = leveraged_loss_per_unit + (total_taker_fee / (entry_price * leverage))
    recommended_capital = capital_to_risk / effective_loss_per_unit
    return round(recommended_capital, 4)


def calculate_recommended_capital_base_on_loss_capital(entry_price: float, stop_loss_price: float, 
                                                        loss_capital: float=1000, 
                                                        leverage: int=5, taker_fee: float=0, 
                                                        maker_fee: float=0, order_type: str="market"):
    """_summary_

    Args:
        entry_price (float): _description_
        stop_loss_price (float): _description_
        loss_capital (float, optional): _description_. Defaults to 1000.
        leverage (int, optional): _description_. Defaults to 5.
        taker_fee (float, optional): _description_. Defaults to 0.05.
        maker_fee (float, optional): _description_. Defaults to 0.02.
        order_type (str, optional): _description_. Defaults to "market".

    Returns:
        _type_: _description_
    """
    taker_fee = taker_fee/100
    maker_fee = maker_fee/100
    price_difference = abs(entry_price - stop_loss_price)
    percent_change_sl = price_difference / entry_price
    leveraged_loss_per_unit = percent_change_sl * leverage
    
    if order_type == "market":
        total_taker_fee = entry_price * leverage * taker_fee * 2
    else:
        total_taker_fee = entry_price * leverage * maker_fee * 2
    
    effective_loss_per_unit = leveraged_loss_per_unit + (total_taker_fee / (entry_price * leverage))
    
    # Tính số vốn khuyến nghị dựa trên số vốn có thể mất
    recommended_capital = loss_capital / effective_loss_per_unit
    return round(recommended_capital, 4)

# CSS for background color and author note
st.markdown(
    """
    <style>
    .reportview-container {
        background: #0052cc;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #0052cc;
        color: white;
    }
    .stButton>button {
        background: #ffffff;
        color: #0052cc;
        font-weight: bold;
    }
    .stNumberInput>div>input {
        background: #ffffff;
        color: #0052cc;
    }
    .author-note, .donation-note {
        font-size: 0.8em;
        color: #ffffff;
        text-align: center;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Risk Management Calculator")
st.header("Calculate Profit/Loss and Recommended Capital")

# Adding a space before General settings
st.markdown("<br>", unsafe_allow_html=True)

# Dividing into sections
st.subheader("General Settings")
total_capital = st.number_input("Total Capital - _The total amount of capital available for trading._", value=10000.0, format="%.2f")
capital = st.number_input("Capital - _The amount of money you are investing in this position._", value=1000.0, format="%.2f")
leverage = st.number_input("Leverage", value=10)
risk_percentage = st.number_input("Risk Percentage - _The percentage of your total trading capital that you are willing to risk on this trade._", value=5.0, format="%.1f")
taker_fee = st.number_input("Taker Fee (%)", value=0.055, format="%.3f")
maker_fee = st.number_input("Maker Fee (%)", value=0.02, format="%.3f") 

st.subheader("Price Settings")
entry_price = st.number_input("Entry Price ($)", value=60000.00, format="%.2f")
stop_loss_price = st.number_input("Stop Loss Price ($)", value=59000.00, format="%.2f")

# Select position type
position_type = st.selectbox("Position Type", ["LONG", "SHORT"])
is_long = position_type == "LONG"

st.subheader("Take Profit Settings")
# Creating columns for individual TPs
col1, col2, col3 = st.columns(3)

with col1:
    exit_price_tp1 = st.number_input("Exit Price TP1 ($)", value=61000.00, format="%.2f")
    proportion_closed_tp1 = st.number_input("Proportion Closed TP1 (%)", value=0.5)

with col2:
    exit_price_tp2 = st.number_input("Exit Price TP2 ($)", value=62000.00, format="%.2f")
    proportion_closed_tp2 = st.number_input("Proportion Closed TP2 (%)", value=0.3)

with col3:
    exit_price_tp3 = st.number_input("Exit Price TP3 ($)", value=63000.00, format="%.2f")
    proportion_closed_tp3 = st.number_input("Proportion Closed TP3 (%)", value=0.2)

# Adding a space before the Calculate button
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Calculate"):
    valid_input = True
    if is_long:
        if stop_loss_price >= entry_price:
            st.error("For LONG positions, the stop loss price must be lower than the entry price.")
            valid_input = False
        if exit_price_tp1 <= entry_price or exit_price_tp2 <= entry_price or exit_price_tp3 <= entry_price:
            st.error("For LONG positions, the take profit prices must be higher than the entry price.")
            valid_input = False
    else:
        if stop_loss_price <= entry_price:
            st.error("For SHORT positions, the stop loss price must be higher than the entry price.")
            valid_input = False
        if exit_price_tp1 >= entry_price or exit_price_tp2 >= entry_price or exit_price_tp3 >= entry_price:
            st.error("For SHORT positions, the take profit prices must be lower than the entry price.")
            valid_input = False

    if valid_input:
        total_pl = 0
        total_proportion = 0
        
        if proportion_closed_tp1 > 0:
            pl_tp1 = calculate_pl_with_fees(entry_price, exit_price_tp1, capital, leverage, proportion_closed_tp1, taker_fee, maker_fee)
            total_pl += pl_tp1
            total_proportion += proportion_closed_tp1
        else:
            pl_tp1 = 0

        if proportion_closed_tp2 > 0 and total_proportion < 1.0:
            pl_tp2 = calculate_pl_with_fees(entry_price, exit_price_tp2, capital, leverage, proportion_closed_tp2, taker_fee, maker_fee, is_stop_loss=False)
            total_pl += pl_tp2
            total_proportion += proportion_closed_tp2
        else:
            pl_tp2 = 0

        if proportion_closed_tp3 > 0 and total_proportion < 1.0:
            pl_tp3 = calculate_pl_with_fees(entry_price, exit_price_tp3, capital, leverage, proportion_closed_tp3, taker_fee, maker_fee, is_stop_loss=False)
            total_pl += pl_tp3
            total_proportion += proportion_closed_tp3
        else:
            pl_tp3 = 0

        if total_proportion < 1.0:
            pl_remaining = calculate_pl_with_fees(entry_price, entry_price, capital, leverage, 1.0 - total_proportion, taker_fee, maker_fee, is_stop_loss=False)
            total_pl += pl_remaining
        else:
            pl_remaining = 0

        pl_stop_loss = calculate_pl_with_fees(entry_price, stop_loss_price, capital, leverage, 1, taker_fee, maker_fee, is_stop_loss=True)
        recommended_capital = calculate_recommended_capital(entry_price, stop_loss_price, total_capital, risk_percentage, leverage, taker_fee,maker_fee)
        recommended_capital_loss_capital = calculate_recommended_capital_base_on_loss_capital(entry_price, stop_loss_price,50, leverage, taker_fee)

        
        st.markdown("---")
        st.subheader("Results")
        
        st.markdown(f"**Recommended capital to risk {risk_percentage}% of total capital:** :green[${recommended_capital}]")
        st.markdown(f"**Recommended capital base on loss_capital:** :green[${recommended_capital_loss_capital}]")
        st.markdown(f"**Total P/L if all TPs are hit:** :green[${total_pl}]")
        st.markdown(f"**P/L for TP1:** :green[${pl_tp1}]")
        if proportion_closed_tp2 > 0:
            st.markdown(f"**P/L for TP2:** :green[${pl_tp2}]")
        if proportion_closed_tp3 > 0:
            st.markdown(f"**P/L for TP3:** :green[${pl_tp3}]")
        if total_proportion < 1.0:
            st.markdown(f"**P/L for remaining position (if SL is hit at entry price):** :green[${pl_remaining}]")
        st.markdown(f"**P/L if Stop Loss is hit directly:** :red[${pl_stop_loss}]")

        # Check that the total proportion is 100%
        if (proportion_closed_tp1 + proportion_closed_tp2 + proportion_closed_tp3) != 1.0:
            st.warning("Warning: The total proportion of closed positions does not equal 100%. Please check the proportions.")

# Adding author and crypto addresses for donations
st.markdown(
    """
         <br>
        <br>
        <br>
        <br>
    <div class="author-note">
        Developed by adrian-13
    </div>
    <div class="donation-note">
        If you find this tool useful and want to support the development of more applications, consider donating:
        <br>
        <br>
        BTC: bc1q4qhsf0ch743c0fr9uqwxdfhpdtgnqt4cj4rj3u
        <br>
        ETH: 0xe3DF6a179DC2D77f86FbE3e58F4Baa265b336AfE
        <br>
        SOL: CsH93X5xRENDsJtxVbsVdew8rLiZ8v4iQPd2NkhA319R
        <br>
        DOGE: DRxhFxSoLNHSBcUbSyoXqT6oGWfNcmHVjQ
        <br>
        LTC: ltc1q4uc4celdsxxh4g0u2pjvdfvnrf9wa5nc0ge0gj
    </div>
    """,
    unsafe_allow_html=True
)
