import streamlit as st

from toml import load as toml_load
import numpy as np
import pandas as pd
import altair as alt
import json
from config import Config

st.set_page_config(
    page_title="Model Performance",
    layout="wide",
    initial_sidebar_state="expanded",
)

def kaplan_meier(s_true, t_true, t_new=None):

    t, d, n = hazard_components(s_true, t_true)

    m = np.cumprod(1 - np.divide(
        d, n,
        out=np.zeros(len(d)),
        where=n > 0
    ))
    
    v = (m ** 2) * np.cumsum(np.divide(
        d, n * (n - d),
        out=np.zeros(len(d)),
        where=n * (n - d) > 0
    ))

    if t_new is not None:
        return interpolate(t, m, t_new)
    else:
        return t, m, v

def interpolate(x, y, new_x, method='pad'):
    
    # s = pd.Series(data=y, index=x)
    # new_y = (s
    #     .reindex(s.index.union(new_x).unique())
    #     .interpolate(method=method)[new_x]
    #     .values
    # )
    
    # return new_y

    return np.interp(new_x, x, y)

def hazard_components(s_true, t_true):

    df = (
        pd.DataFrame({'event': s_true, 'time': t_true})
        .groupby('time')
        .agg(['count', 'sum'])
    )

    t = df.index.values
    d = df[('event', 'sum')].values
    c = df[('event', 'count')].values
    n = np.sum(c) - np.cumsum(c) + c

    return t, d, n

def auct_curve(auct, auct_low, auct_high, times):
    data = pd.DataFrame(
        {"Years (t)": times, "AUCₜ": auct, "AUC_low": auct_low, "AUC_high": auct_high}
    )

    line = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Years (t)",
            y=alt.Y("AUCₜ", title="AUCₜ", scale=alt.Scale(domain=[0.4, 1])),
        )
    )
    band = (
        alt.Chart(data)
        .mark_errorband(extent="ci")
        .encode(
            x="Years (t)",
            y=alt.Y("AUC_low", title=""),
            y2=alt.Y2("AUC_high", title=""),
        )
    )
    rule = (
        alt.Chart(pd.DataFrame({"y": [0.5]}))
        .mark_rule(strokeDash=[3, 3], color="black")
        .encode(y="y")
    )
    combined_chart = (line + band + rule).properties(title="AUCₜ Curve")
    st.altair_chart(combined_chart, use_container_width=True)


def apt_curve(apt, apt_low, apt_high, prevt, times):
    data = pd.DataFrame(
        {
            "Years (t)": times,
            "APₜ": apt,
            "AP_low": apt_low,
            "AP_high": apt_high,
            "prevt": prevt,
        }
    )
    line = (
        alt.Chart(data).mark_line().encode(x="Years (t)", y=alt.Y("APₜ", title="APₜ"))
    )

    band = (
        alt.Chart(data)
        .mark_errorband(extent="ci")
        .encode(
            x="Years (t)",
            y=alt.Y("AP_low", title=""),
            y2=alt.Y2("AP_high", title=""),
        )
    )

    ref = (
        alt.Chart(data)
        .mark_line(strokeDash=[3, 3], color="black")
        .encode(x="Years (t)", y="prevt")
    )

    combined_chart = (line + band + ref).properties(title="APₜ Curve")
    st.altair_chart(combined_chart, use_container_width=True)


def cum_predicted_probability(test_s, test_t, test_predictions, times):
    cumulative_predicted_risk = np.cumsum(test_predictions, axis=1)[:, :-1]

    cp_mean = [0] + list(cumulative_predicted_risk.mean(axis=0))
    cp_std = [0] + list(cumulative_predicted_risk.std(axis=0))

    pred_data = pd.DataFrame(
        {
            "Years (t)": [0] + list(times),
            "cp_mean": cp_mean,
            "cp_low": np.array(cp_mean) - np.array(cp_std),
            "cp_high": np.array(cp_mean) + np.array(cp_std),
        }
    )
    pred_line = (
        alt.Chart(pred_data)
        .mark_line()
        .encode(x=alt.X("Years (t)", title="Years (t)"), y="cp_mean")
    )
    pred_band = (
        alt.Chart(pred_data)
        .mark_errorband(extent="ci")
        .encode(
            x=alt.X("Years (t)", title="Years (t)"),
            y=alt.Y("cp_low", title="Probability"),
            y2=alt.Y2("cp_high", title=""),
        )
    )

    km_times, km_mean, km_var = kaplan_meier(test_s, test_t)
    km_data = pd.DataFrame(
        {
            "km_times": km_times,
            "1 - km_mean": 1 - km_mean,
            "1 - km_low": 1 - km_mean - np.sqrt(km_var),
            "1 - km_high": 1 - km_mean + np.sqrt(km_var),
        }
    )
    km_line = (
        alt.Chart(km_data)
        .mark_line(color="black")
        .encode(x="km_times", y="1 - km_mean")
    )
    km_band = (
        alt.Chart(km_data)
        .mark_errorband(extent="ci", color="black")
        .encode(
            x="km_times",
            y=alt.Y("1 - km_low", title=""),
            y2=alt.Y2("1 - km_high", title=""),
        )
    )

    combined_chart = (pred_line + pred_band + km_line + km_band).properties(
        title="Cumulative Predicted Probability Curve"
    )
    st.altair_chart(combined_chart, use_container_width=True)


st.header("Model Performance 📈")
labels = ["autism", "adhd"]

config = Config(**toml_load("config.toml"))

for label, tab in zip(labels, st.tabs(["Autism", "ADHD"])):
    config_diagnosis = getattr(config, label)
    with open(config_diagnosis.testset_results, 'r') as f:
        testset_results = json.load(f)
    test_s = testset_results["test_s"]
    test_t = testset_results["test_t"]
    test_predictions = testset_results["test_predictions"]
    auct = testset_results["auct"]
    auct_low = testset_results["auct_low"]
    auct_high = testset_results["auct_high"]
    apt = testset_results["apt"]
    apt_low = testset_results["apt_low"]
    apt_high = testset_results["apt_high"]
    prevt = testset_results["prevt"]

    times = config_diagnosis.bin_boundaries[1:]
    with tab:
        auct_curve(auct, auct_low, auct_high, times)
        apt_curve(apt, apt_low, apt_high, prevt, times)
        cum_predicted_probability(test_s, test_t, test_predictions, times)
