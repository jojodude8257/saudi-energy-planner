from dataclasses import dataclass
import numpy as np
from sklearn.linear_model import LinearRegression

DEMAND_CAGR_ASSUMPTION = 0.038
RENEWABLE_TARGET_YEAR = 2030
RENEWABLE_TARGET_GW = 130
SOLAR_CAPACITY_FACTOR = 0.26
WIND_CAPACITY_FACTOR = 0.32

@dataclass
class Forecast:
    years: list
    demand_twh: list
    peak_load_gw: list
    renewable_capacity_gw: list
    solar_generation_twh: list
    wind_generation_twh: list

def _fit_demand_model(base_year: int, base_demand_twh: float) -> LinearRegression:
    anchor_years = np.array([[base_year], [base_year + 10]])
    anchor_values = np.array([
        np.log(base_demand_twh),
        np.log(base_demand_twh * (1 + DEMAND_CAGR_ASSUMPTION) ** 10),
    ])
    model = LinearRegression()
    model.fit(anchor_years, anchor_values)
    return model

def build_forecast(saudi_data: dict, start_year: int = 2025, end_year: int = 2050, step: int = 5) -> Forecast:
    base_year = 2024
    base_demand = saudi_data["Electricity Consumption (Total)"]
    base_peak = saudi_data["Peak Load"]
    base_renewable_gw = saudi_data["Renewable Installed Capacity"]

    peak_to_demand_ratio = base_peak / base_demand
    demand_model = _fit_demand_model(base_year, base_demand)

    years = list(range(start_year, end_year + 1, step))
    demand_twh, peak_load_gw = [], []
    renewable_capacity_gw, solar_gen_twh, wind_gen_twh = [], [], []

    for y in years:
        d = float(np.exp(demand_model.predict([[y]])[0]))
        demand_twh.append(round(d, 1))
        peak_load_gw.append(round(d * peak_to_demand_ratio, 1))

        t_to_target = RENEWABLE_TARGET_YEAR - base_year
        if y <= RENEWABLE_TARGET_YEAR:
            frac = (y - base_year) / t_to_target
            frac = frac ** 1.3
            cap = base_renewable_gw + frac * (RENEWABLE_TARGET_GW - base_renewable_gw)
        else:
            post_target_slope = 38.0
            cap = RENEWABLE_TARGET_GW + post_target_slope * np.sqrt(y - RENEWABLE_TARGET_YEAR)

        renewable_capacity_gw.append(round(cap, 1))

        solar_share, wind_share = 0.94, 0.06
        solar_cap = cap * solar_share
        wind_cap = cap * wind_share
        solar_gen_twh.append(round(solar_cap * SOLAR_CAPACITY_FACTOR * 8.76, 1))
        wind_gen_twh.append(round(wind_cap * WIND_CAPACITY_FACTOR * 8.76, 1))

    return Forecast(
        years=years,
        demand_twh=demand_twh,
        peak_load_gw=peak_load_gw,
        renewable_capacity_gw=renewable_capacity_gw,
        solar_generation_twh=solar_gen_twh,
        wind_generation_twh=wind_gen_twh,
    )

if __name__ == "__main__":
    from data_loader import load_workbook
    data = load_workbook()
    fc = build_forecast(data.saudi_data)
    for i, y in enumerate(fc.years):
        print(f"{y}: demand={fc.demand_twh[i]} TWh | peak={fc.peak_load_gw[i]} GW | renew.cap={fc.renewable_capacity_gw[i]} GW")
