from dataclasses import dataclass
import pandas as pd

@dataclass
class ScenarioState:
    name: str
    year: int
    demand_twh: float
    demand_multiplier: float
    water_index: float
    renewable_output_twh: float
    renewable_multiplier: float
    peak_load_gw: float

def apply_scenarios(forecast, scenarios_df: pd.DataFrame, target_year: int) -> list[ScenarioState]:
    if target_year not in forecast.years:
        target_year = min(forecast.years, key=lambda y: abs(y - target_year))
    idx = forecast.years.index(target_year)

    base_demand = forecast.demand_twh[idx]
    base_peak = forecast.peak_load_gw[idx]
    base_renewable = forecast.solar_generation_twh[idx] + forecast.wind_generation_twh[idx]

    states = []
    for _, row in scenarios_df.iterrows():
        demand_mult = float(row["Demand Multiplier"])
        water_mult = float(row["Water"])
        renew_mult = float(row["Renewables"])

        states.append(ScenarioState(
            name=row["Scenario"],
            year=target_year,
            demand_twh=round(base_demand * demand_mult, 1),
            demand_multiplier=demand_mult,
            water_index=round(water_mult, 2),
            renewable_output_twh=round(base_renewable * renew_mult, 1),
            renewable_multiplier=renew_mult,
            peak_load_gw=round(base_peak * demand_mult, 1),
        ))
    return states

if __name__ == "__main__":
    from data_loader import load_workbook
    from forecasting import build_forecast
    data = load_workbook()
    fc = build_forecast(data.saudi_data)
    states = apply_scenarios(fc, data.scenarios, target_year=2035)
    for s in states:
        print(s)
