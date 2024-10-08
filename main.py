import streamlit as st
import pandas as pd

import utils.indicator_evaluator as ie
from datetime import datetime, timedelta
# import streamlit_analytics
import utils.telegram_controller as tc
import utils.ticker_getter as tg

dow_jones_tickers = tg.get_dow_jones()
sp500_tickers = tg.get_snp_500()
all_tickers = tg.get_all_tickers()

ticker_selection_options = all_tickers + ["Everything", "S&P 500", "Dow Jones"]
# get url parameters
show_params = st.query_params.get("show")


# Function to display ticker input with autocomplete and multi-select
def ticker_input(key="ticker_input", default=None):
    selected_tickers = st.multiselect(
        "Step 1: Select stock tickers",
        options=ticker_selection_options,
        key=key,
        default=default,
        placeholder="'Everything', 'S&P 500', 'Dow Jones' or add individual stock tickers",
    )
    return selected_tickers


# Updated indicators multiselect box and expander settings
def get_user_inputs(settings=None):
    if settings is None:
        settings = {
            "tickers": [],
            "indicator_settings": {
                "golden_cross_sma": {
                    "is_enabled": False,
                    "short_sma": 50,
                    "long_sma": 200,
                },
                "death_cross_sma": {
                    "is_enabled": False,
                    "short_sma": 50,
                    "long_sma": 200,
                },
                "rsi_overbought": {
                    "is_enabled": False,
                    "threshold": 70,
                },
                "rsi_oversold": {
                    "is_enabled": False,
                    "threshold": 30,
                },
                "macd_bullish": {
                    "is_enabled": False,
                    "short_ema": 12,
                    "long_ema": 26,
                    "signal_window": 9,
                },
                "macd_bearish": {
                    "is_enabled": False,
                    "short_ema": 12,
                    "long_ema": 26,
                    "signal_window": 9,
                },
                "bollinger_squeeze": {
                    "is_enabled": False,
                    "window": 20,
                    "num_std_dev": 2,
                },
                "bollinger_expansion": {
                    "is_enabled": False,
                    "window": 20,
                    "num_std_dev": 2,
                },
                "bollinger_breakout": {
                    "is_enabled": False,
                    "window": 20,
                    "num_std_dev": 2,
                },
                "bollinger_pullback": {
                    "is_enabled": False,
                    "window": 20,
                    "num_std_dev": 2,
                },
                "volume_spike": {
                    "is_enabled": False,
                    "window": 20,
                    "num_std_dev": 2,
                },
            },
            "show_win_rate": False,
            "show_only_if_all_signals_met": True,
            "show_only_close_price_above": 20,
            "show_only_volume_above": 100000,
            "recency": 2,
            "min_num_instances": 0,
            "show_only_earnings_within_days": 30,
            "x": 20,
        }

    if show_params == "apex":
        settings["indicator_settings"]["apex_bear_raging"] = {
            "is_enabled": False,
        }
        settings["tickers"] = ["Everything"]
        settings["indicator_settings"]["apex_bull_raging"] = {
            "is_enabled": False,
        }
        settings["indicator_settings"]["apex_uptrend"] = {
            "is_enabled": False,
        }
        # settings["indicator_settings"]["apex_downtrend"] = {
        # "is_enabled": True,
        # }
        settings["indicator_settings"]["apex_bull_appear"] = {
            "is_enabled": False,
        }
        settings["indicator_settings"]["apex_bear_appear"] = {
            "is_enabled": False,
        }

    # Use the ticker_input function for adding tickers
    settings["tickers"] = ticker_input(default=settings.get("tickers", []))
    if "Everything" in settings["tickers"]:
        # TODO: remove all other tickers from the list if "Everything" is chosen
        settings["tickers"] = (
            all_tickers  # Select all tickers if "Everything" is chosen
        )
    if "S&P 500" in settings["tickers"]:
        settings["tickers"] = sp500_tickers
    if "Dow Jones" in settings["tickers"]:
        settings["tickers"] = dow_jones_tickers

    # Dropdown for selecting indicators
    selected_indicators = st.multiselect(
        "Step 2: Select technical indicators",
        options=list(settings["indicator_settings"].keys()),
        default=[
            k for k, v in settings["indicator_settings"].items() if v["is_enabled"]
        ],
    )

    for indicator in selected_indicators:
        settings["indicator_settings"][indicator]["is_enabled"] = True

        if indicator == "golden_cross_sma":
            with st.expander("Golden Cross Settings", expanded=False):
                st.caption(
                    "Golden Cross is a bullish signal that occurs when the short-term moving average crosses above the long-term moving average."
                )
                settings["indicator_settings"]["golden_cross_sma"]["short_sma"] = (
                    st.number_input(
                        "Short SMA window for Golden Cross:",
                        min_value=1,
                        value=settings["indicator_settings"]["golden_cross_sma"][
                            "short_sma"
                        ],
                    )
                )
                settings["indicator_settings"]["golden_cross_sma"]["long_sma"] = (
                    st.number_input(
                        "Long SMA window for Golden Cross:",
                        min_value=1,
                        value=settings["indicator_settings"]["golden_cross_sma"][
                            "long_sma"
                        ],
                    )
                )

        if indicator == "death_cross_sma":
            with st.expander("Death Cross Settings", expanded=False):
                st.caption(
                    "Death Cross is a bearish signal that occurs when the short-term moving average crosses below the long-term moving average."
                )
                settings["indicator_settings"]["death_cross_sma"]["short_sma"] = (
                    st.number_input(
                        "Short SMA window for Death Cross:",
                        min_value=1,
                        value=settings["indicator_settings"]["death_cross_sma"][
                            "short_sma"
                        ],
                    )
                )
                settings["indicator_settings"]["death_cross_sma"]["long_sma"] = (
                    st.number_input(
                        "Long SMA window for Death Cross:",
                        min_value=1,
                        value=settings["indicator_settings"]["death_cross_sma"][
                            "long_sma"
                        ],
                    )
                )

        if indicator == "rsi_overbought":
            with st.expander("RSI Overbought Settings", expanded=False):
                st.caption(
                    "RSI Overbought is a bearish signal that occurs when the Relative Strength Index (RSI) is above a certain threshold."
                )
                settings["indicator_settings"]["rsi_overbought"]["threshold"] = (
                    st.number_input(
                        "RSI Overbought threshold:",
                        min_value=1,
                        max_value=100,
                        value=settings["indicator_settings"]["rsi_overbought"][
                            "threshold"
                        ],
                    )
                )

        if indicator == "rsi_oversold":
            with st.expander("RSI Oversold Settings", expanded=False):
                st.caption(
                    "RSI Oversold is a bullish signal that occurs when the Relative Strength Index (RSI) is below a certain threshold."
                )
                settings["indicator_settings"]["rsi_oversold"]["threshold"] = (
                    st.number_input(
                        "RSI Oversold threshold:",
                        min_value=1,
                        max_value=100,
                        value=settings["indicator_settings"]["rsi_oversold"][
                            "threshold"
                        ],
                    )
                )

        if indicator == "macd_bullish":
            with st.expander("MACD Bullish Settings", expanded=False):
                st.caption(
                    "MACD Bullish is a bullish signal that occurs when the MACD line crosses above the signal line."
                )
                settings["indicator_settings"]["macd_bullish"]["short_ema"] = (
                    st.number_input(
                        "Short EMA for MACD Bullish:",
                        min_value=1,
                        value=settings["indicator_settings"]["macd_bullish"][
                            "short_ema"
                        ],
                    )
                )
                settings["indicator_settings"]["macd_bullish"]["long_ema"] = (
                    st.number_input(
                        "Long EMA for MACD Bullish:",
                        min_value=1,
                        value=settings["indicator_settings"]["macd_bullish"][
                            "long_ema"
                        ],
                    )
                )
                settings["indicator_settings"]["macd_bullish"]["signal_window"] = (
                    st.number_input(
                        "Signal line window for MACD Bullish:",
                        min_value=1,
                        value=settings["indicator_settings"]["macd_bullish"][
                            "signal_window"
                        ],
                    )
                )

        if indicator == "macd_bearish":
            with st.expander("MACD Bearish Settings", expanded=False):
                st.caption(
                    "MACD Bearish is a bearish signal that occurs when the MACD line crosses below the signal line."
                )
                settings["indicator_settings"]["macd_bearish"]["short_ema"] = (
                    st.number_input(
                        "Short EMA for MACD Bearish:",
                        min_value=1,
                        value=settings["indicator_settings"]["macd_bearish"][
                            "short_ema"
                        ],
                    )
                )
                settings["indicator_settings"]["macd_bearish"]["long_ema"] = (
                    st.number_input(
                        "Long EMA for MACD Bearish:",
                        min_value=1,
                        value=settings["indicator_settings"]["macd_bearish"][
                            "long_ema"
                        ],
                    )
                )
                settings["indicator_settings"]["macd_bearish"]["signal_window"] = (
                    st.number_input(
                        "Signal line window for MACD Bearish:",
                        min_value=1,
                        value=settings["indicator_settings"]["macd_bearish"][
                            "signal_window"
                        ],
                    )
                )

        if indicator == "bollinger_squeeze":
            with st.expander("Bollinger Squeeze Settings", expanded=False):
                st.caption(
                    "Bollinger Squeeze is a signal that occurs when the Bollinger Bands narrow, indicating lower volatility."
                )
                settings["indicator_settings"]["bollinger_squeeze"]["window"] = (
                    st.number_input(
                        "Bollinger Squeeze window:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_squeeze"][
                            "window"
                        ],
                    )
                )
                settings["indicator_settings"]["bollinger_squeeze"]["num_std_dev"] = (
                    st.number_input(
                        "Number of standard deviations for Bollinger Squeeze:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_squeeze"][
                            "num_std_dev"
                        ],
                    )
                )

        if indicator == "bollinger_expansion":
            with st.expander("Bollinger Expansion Settings", expanded=False):
                st.caption(
                    "Bollinger Expansion is a signal that occurs when the Bollinger Bands widen, indicating higher volatility."
                )
                settings["indicator_settings"]["bollinger_expansion"]["window"] = (
                    st.number_input(
                        "Bollinger Expansion window:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_expansion"][
                            "window"
                        ],
                    )
                )
                settings["indicator_settings"]["bollinger_expansion"]["num_std_dev"] = (
                    st.number_input(
                        "Number of standard deviations for Bollinger Expansion:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_expansion"][
                            "num_std_dev"
                        ],
                    )
                )

        if indicator == "bollinger_breakout":
            with st.expander("Bollinger Breakout Settings", expanded=False):
                st.caption(
                    "Bollinger Breakout is a signal that occurs when the price breaks out above the upper Bollinger Band."
                )
                settings["indicator_settings"]["bollinger_breakout"]["window"] = (
                    st.number_input(
                        "Bollinger Breakout window:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_breakout"][
                            "window"
                        ],
                    )
                )
                settings["indicator_settings"]["bollinger_breakout"]["num_std_dev"] = (
                    st.number_input(
                        "Number of standard deviations for Bollinger Breakout:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_breakout"][
                            "num_std_dev"
                        ],
                    )
                )

        if indicator == "bollinger_pullback":
            with st.expander("Bollinger Pullback Settings", expanded=False):
                st.caption(
                    "Bollinger Pullback is a signal that occurs when the price pulls back to the middle Bollinger Band after a breakout."
                )
                settings["indicator_settings"]["bollinger_pullback"]["window"] = (
                    st.number_input(
                        "Bollinger Pullback window:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_pullback"][
                            "window"
                        ],
                    )
                )
                settings["indicator_settings"]["bollinger_pullback"]["num_std_dev"] = (
                    st.number_input(
                        "Number of standard deviations for Bollinger Pullback:",
                        min_value=1,
                        value=settings["indicator_settings"]["bollinger_pullback"][
                            "num_std_dev"
                        ],
                    )
                )

        if indicator == "volume_spike":
            with st.expander("Volume Spike Settings", expanded=False):
                st.caption(
                    "Volume Spike is a signal that occurs when trading volume spikes significantly above average."
                )
                settings["indicator_settings"]["volume_spike"]["window"] = (
                    st.number_input(
                        "Volume Spike window:",
                        min_value=1,
                        value=settings["indicator_settings"]["volume_spike"]["window"],
                    )
                )
                settings["indicator_settings"]["volume_spike"]["num_std_dev"] = (
                    st.number_input(
                        "Number of standard deviations for Volume Spike:",
                        min_value=1,
                        value=settings["indicator_settings"]["volume_spike"][
                            "num_std_dev"
                        ],
                    )
                )

    # recency of data to look at (int)
    settings["recency"] = st.number_input(
        "Step 3: Select recency of signal (# trading days) to include in results ",
        min_value=1,
        value=settings.get("recency", 5),
    )

    with st.expander("Advanced Settings", expanded=False):
        settings["min_num_instances"] = st.number_input(
            "Minimum number of past signals for the ticker to be included in results",
            min_value=0,
            value=settings.get("min_num_instances", 0),
        )

        settings["show_only_close_price_above"] = st.number_input(
            "Only screen stocks where latest closing price is above",
            min_value=0,
            value=settings.get("show_only_close_price_above", 0),
        )

        settings["show_only_if_all_signals_met"] = st.checkbox(
            "Show only if all indicator signals are met",
            value=settings.get("show_only_if_all_signals_met", True),
        )

        settings["show_only_volume_above"] = st.number_input(
            "Only show stocks where volume is above",
            min_value=0,
            value=settings.get("show_only_volume_above", 100000),
        )

        settings["show_only_earnings_within_days"] = st.number_input(
            "Only show stocks where earnings report is within the next # days",
            min_value=0,
            value=settings.get("show_only_earnings_within_days", 30),
        )


    return settings


# with streamlit_analytics.track(unsafe_password="test123"):
st.title("Optilens Stock Screener 📈")
st.subheader("Find stocks using technical indicators")

st.sidebar.subheader("Any feedback/ feature requests?")

feedback = st.sidebar.text_area("", height=100)
submit_feedback = st.sidebar.button("Submit")
if submit_feedback:
    tc.send_message(message="User feedback received: \n" + feedback)
    st.sidebar.success(
        f"Feedback '{feedback}' submitted successfully. Thank you for your feedback!"
    )


# Get user inputs
settings = get_user_inputs()
screen_button_placeholder = st.empty()
screen_button = screen_button_placeholder.button("🔎 Screen")


if screen_button:
    if settings["tickers"]:
        # check if there is any indicators enabled in settings['indicator_settings']
        if (
            len(
                [
                    k
                    for k, v in settings["indicator_settings"].items()
                    if v["is_enabled"]
                ]
            )
            == 0
        ):
            st.error("Please enable at least one technical indicator.")
            st.stop()

        screen_button_placeholder.empty()
        stop_screening = screen_button_placeholder.button(
            "Stop screening", key="stop_screening"
        )
        if stop_screening:
            st.rerun()

        st.divider()
        st.header("Screening Results")
        # progress_bar = st.progress(0)
        total_tickers = len(settings["tickers"])

        # progress_text_placeholder = st.empty()
        screening_results = pd.DataFrame(columns=["Ticker"])

        # Placeholder for overall probability calc
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        overall_success_rate_1D_placeholder = col1.empty()
        overall_change_percent_1D_placeholder = col4.empty()
        overall_success_rate_5D_placeholder = col2.empty()
        overall_change_percent_5D_placeholder = col5.empty()
        overall_success_rate_20D_placeholder = col3.empty()
        overall_change_percent_20D_placeholder = col6.empty()

        overall_num_instances = 0

        overall_num_instances_rise_1D = 0
        overall_change_percent_1D = 0
        overall_num_instances_rise_5D = 0
        overall_change_percent_5D = 0
        overall_num_instances_rise_20D = 0
        overall_change_percent_20D = 0

        # Placeholder for the DataFrame that will be updated
        dataframe_placeholder = st.empty()

        with st.status(label="Screening ...", expanded=True) as status:
            result = ie.analyze_everything(settings)
            
            # print result as dataframe
            if result is not None:
                # change result to dataframe
                result = pd.DataFrame(result)
                # Calculate the date 'settings.recency' days ago from today
                recency_date = datetime.now() - timedelta(days=settings["recency"])

                # Filter results to only include data where the last common_date is after 'recency_date'
                result = result[
                    result["common_dates"].apply(
                        lambda x: len(x) > 0
                        and datetime.strptime(x[-1], "%Y-%m-%d") >= recency_date
                    )
                ]
                # Filter results to only include data where the total_instances >= settings["min_num_instances"]
                result = result[
                    result["total_instances"] >= settings["min_num_instances"]
                ]

                 # get the next earnings report date for each ticker
                result["next_earnings_date"] = result["ticker"].apply(
                    lambda x: tg.fetch_next_earnings_date(x)
                )

               
                # filter out next earnings date that is more than 1 month away
                # Convert 'next_earnings_date' to a timezone-aware datetime in UTC
                result["next_earnings_date"] = pd.to_datetime(result["next_earnings_date"], errors='coerce')

                # Convert to UTC if not already timezone-aware
                if result["next_earnings_date"].dt.tz is None:
                    result["next_earnings_date"] = result["next_earnings_date"].dt.tz_localize('UTC')
                else:
                    result["next_earnings_date"] = result["next_earnings_date"].dt.tz_convert('UTC')

                # Filter for dates less than the current time plus the given days in the 'settings'
                result = result[
                    result["next_earnings_date"]
                    < (pd.Timestamp.now(tz='UTC') + timedelta(days=settings["show_only_earnings_within_days"]))
                ]

                # Calculate overall success rate and change percent
                overall_num_instances = result["total_instances"].sum()
                overall_num_instances_rise_1D = result["total_success_count_1D"].sum()
                overall_change_percent_1D = result["total_percentage_change_1D"].sum()
                overall_num_instances_rise_5D = result["total_success_count_5D"].sum()
                overall_change_percent_5D = result["total_percentage_change_5D"].sum()
                overall_num_instances_rise_20D = result["total_success_count_20D"].sum()
                overall_change_percent_20D = result["total_percentage_change_20D"].sum()

                overall_success_rate_1D_placeholder.metric(
                    "1D Success Rate",
                    f"{round(overall_num_instances_rise_1D/overall_num_instances*100, 2)}%",
                )
                overall_change_percent_1D_placeholder.metric(
                    "1D Change %",
                    f"{round(overall_change_percent_1D/overall_num_instances, 2)}%",
                )
                overall_success_rate_5D_placeholder.metric(
                    "5D Success Rate",
                    f"{round(overall_num_instances_rise_5D/overall_num_instances*100, 2)}%",
                )
                overall_change_percent_5D_placeholder.metric(
                    "5D Change %",
                    f"{round(overall_change_percent_5D/overall_num_instances, 2)}%",
                )
                overall_success_rate_20D_placeholder.metric(
                    "20D Success Rate",
                    f"{round(overall_num_instances_rise_20D/overall_num_instances*100, 2)}%",
                )
                overall_change_percent_20D_placeholder.metric(
                    "20D Change %",
                    f"{round(overall_change_percent_20D/overall_num_instances, 2)}%",
                )

                # Only show the latest common_date
                result["common_dates"] = result["common_dates"].apply(
                    lambda x: x[-1] if len(x) > 0 else ""
                )

                # rename common_dates to latest_signal_entry_date
                result.rename(
                    columns={"common_dates": "latest_signal_entry_date"}, inplace=True
                )

               

                dataframe_placeholder.dataframe(result, width=1000, hide_index=True)

                # stop screening and remove the progress bar
                # progress_bar.empty()
                # progress_text_placeholder.empty()

                # recreate screen button after complete
                screen_button_placeholder.empty()
                screen_button_placeholder.button("Reset", key="reset_btn")
                status.update(label="Screening completed! ", state="complete", expanded=False)


    else:
        st.error("Please select at least one stock ticker symbol.")
