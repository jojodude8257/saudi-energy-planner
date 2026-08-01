import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data_loader import load_workbook, DEFAULT_WORKBOOK
from forecasting import build_forecast
from scenario_engine import apply_scenarios
from recommender import recommend

st.set_page_config(page_title="Saudi Nuclear & Renewable Energy Planner", layout="wide")
st.title("AI-Driven Saudi Energy Planning & Decision Support")
st.caption("Live Python implementation reading national data, weights, and scenario parameters directly from energy_model.xlsx.")

with st.sidebar:
    st.header("Data source")
    workbook_path = st.text_input("Workbook path", value=str(DEFAULT_WORKBOOK))
    if st.button("Reload from Excel"):
        st.cache_data.clear()

    @st.cache_data
    def load(path):
        return load_workbook(path)

    try:
        data = load(workbook_path)
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    st.success(f"Loaded {len(data.saudi_data)} national variables, {len(data.scenarios)} scenarios from the workbook.")

    st.header("Scenario & horizon")
    scenario_name = st.selectbox("Scenario", data.scenarios["Scenario"].tolist(), index=len(data.scenarios) - 1)
    target_year = st.select_slider("Target year", options=[2025, 2030, 2035, 2040, 2045, 2050], value=2035)

    st.header("Decision weights (%)")
    st.caption("Defaults come from the Decision Engine sheet.")
    weights = {}
    default_weights = data.weights
    cols_sum = 0
    for crit, default in default_weights.items():
        w = st.slider(crit, 0, 100, int(default))
        weights[crit] = w
        cols_sum += w

    if cols_sum != 100:
        st.warning(f"Weights sum to {cols_sum}%, not 100%. Consider adjusting so they total 100%.")

forecast = build_forecast(data.saudi_data)
scenario_states = apply_scenarios(forecast, data.scenarios, target_year)
scenario = next(s for s in scenario_states if s.name == scenario_name)
rec = recommend(scenario, data.carbon, weights)

st.subheader(f"Recommendation: {scenario.name}, {scenario.year}")
k1, k2, k3, k4, k5, k6 = st.columns(6)
best = rec.full_ranking[0]
k1.metric("Recommended Mix", best.mix_name)
k2.metric("Decision Score", f"{best.weighted_total:.1f}/100")
k3.metric("Cost", f"{best.cost:.0f}")
k4.metric("Reliability", f"{best.reliability:.0f}")
k5.metric("Energy Security", f"{best.energy_security:.0f}")
k6.metric("CO2 Score", f"{best.co2:.0f}")

st.info(f"**Why:** Driven mainly by {', '.join(rec.top_reasons)}. Confidence: {rec.confidence_pct:.0f}% margin over runner-up.")

st.markdown(
    f"**Scenario inputs:** Demand **{scenario.demand_twh:,.0f} TWh** (x{scenario.demand_multiplier:.2f} vs baseline) | "
    f"Peak load **{scenario.peak_load_gw:,.0f} GW** | Water stress **{scenario.water_index:.2f}** | "
    f"Renewable output **{scenario.renewable_output_twh:,.0f} TWh** (x{scenario.renewable_multiplier:.2f} vs baseline)"
)

st.subheader("All candidate mixes ranked")
ranking_df = pd.DataFrame([{
    "Mix": m.mix_name,
    "Decision Score": m.weighted_total,
    "Cost": m.cost,
    "Reliability": m.reliability,
    "Energy Security": m.energy_security,
    "CO2": m.co2,
    "Water": m.water,
} for m in rec.full_ranking])

st.dataframe(ranking_df, use_container_width=True, hide_index=True)

fig_bar = go.Figure()
for crit in ["Cost", "Reliability", "Energy Security", "CO2", "Water"]:
    fig_bar.add_trace(go.Bar(name=crit, x=ranking_df["Mix"], y=ranking_df[crit]))
fig_bar.update_layout(barmode="group", title="Criterion scores by mix", height=400)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Recommendation across all scenarios")
compare_rows = []
for s in scenario_states:
    r = recommend(s, data.carbon, weights)
    compare_rows.append({
        "Scenario": s.name,
        "Recommended Mix": r.recommended_mix,
        "Decision Score": r.decision_score,
        "Demand (TWh)": s.demand_twh,
        "Peak Load (GW)": s.peak_load_gw,
    })
st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

st.subheader("AI Forecast demand & renewable output to 2050")
fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(x=forecast.years, y=forecast.demand_twh, name="Demand (TWh)", mode="lines+markers"))
fig_fc.add_trace(go.Scatter(
    x=forecast.years,
    y=[s + w for s, w in zip(forecast.solar_generation_twh, forecast.wind_generation_twh)],
    name="Solar + Wind generation (TWh)",
    mode="lines+markers"
))
fig_fc.update_layout(height=400, xaxis_title="Year", yaxis_title="TWh")
st.plotly_chart(fig_fc, use_container_width=True)
