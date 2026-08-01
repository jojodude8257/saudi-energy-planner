from dataclasses import dataclass, field

CANDIDATE_MIXES = {
    "Solar + Grid (gas backup)": {"nuclear": 0.00, "battery": 0.00},
    "Solar + SMR": {"nuclear": 0.25, "battery": 0.00},
    "Solar + Nuclear (large)": {"nuclear": 0.40, "battery": 0.00},
    "Nuclear + Battery": {"nuclear": 0.35, "battery": 0.15},
    "Nuclear + Desalination-focused": {"nuclear": 0.45, "battery": 0.05},
}

NUCLEAR_CAPEX_PENALTY = 35
BATTERY_COST_BONUS = 10
NUCLEAR_RELIABILITY_BONUS = 55
BATTERY_RELIABILITY_BONUS = 30
DEMAND_STRESS_RELIABILITY_PENALTY = 25
RENEWABLE_SHORTFALL_RELIABILITY_PENALTY = 20
WATER_STRESS_PENALTY_NO_NUCLEAR = 25
IMPORT_DEPENDENCE_BASE_SCORE = 70
NUCLEAR_SECURITY_BONUS = 25

@dataclass
class MixScore:
    mix_name: str
    cost: float
    reliability: float
    energy_security: float
    co2: float
    water: float
    weighted_total: float
    breakdown: dict = field(default_factory=dict)

def _clip(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def score_mix(mix_name: str, shares: dict, scenario, carbon: dict, weights: dict) -> MixScore:
    nuclear_share = shares["nuclear"]
    battery_share = shares["battery"]

    cost = 90 - NUCLEAR_CAPEX_PENALTY * nuclear_share + BATTERY_COST_BONUS * battery_share
    cost = _clip(cost)

    firm_share = nuclear_share + battery_share
    demand_stress = max(0.0, scenario.demand_multiplier - 1.0)
    renewable_shortfall = max(0.0, 1.0 - scenario.renewable_multiplier)

    reliability = 60
    reliability += NUCLEAR_RELIABILITY_BONUS * nuclear_share
    reliability += BATTERY_RELIABILITY_BONUS * battery_share
    reliability -= DEMAND_STRESS_RELIABILITY_PENALTY * demand_stress * (1 - firm_share)
    reliability -= RENEWABLE_SHORTFALL_RELIABILITY_PENALTY * renewable_shortfall * (1 - firm_share)
    reliability = _clip(reliability)

    energy_security = IMPORT_DEPENDENCE_BASE_SCORE + NUCLEAR_SECURITY_BONUS * nuclear_share
    energy_security = _clip(energy_security)

    gas_intensity = carbon.get("Natural Gas (CCGT)", 490)
    nuclear_intensity = carbon.get("Nuclear", 12)
    gas_share = max(0.0, 1.0 - nuclear_share - battery_share)
    blended_intensity = gas_share * gas_intensity + nuclear_share * nuclear_intensity
    co2 = _clip(100 * (1 - blended_intensity / gas_intensity))

    water = 70 + 20 * nuclear_share - WATER_STRESS_PENALTY_NO_NUCLEAR * scenario.water_index * (1 - nuclear_share)
    water = _clip(water)

    breakdown = {
        "nuclear_share": nuclear_share,
        "battery_share": battery_share,
        "blended_carbon_intensity_gCO2_kWh": round(blended_intensity, 1),
        "water_index": scenario.water_index,
    }

    weighted_total = (
        weights.get("Cost", 30) * cost
        + weights.get("Reliability", 25) * reliability
        + weights.get("Energy Security", 20) * energy_security
        + weights.get("CO2 Emissions", 15) * co2
        + weights.get("Water Support", 10) * water
    ) / 100

    return MixScore(
        mix_name=mix_name,
        cost=round(cost, 1),
        reliability=round(reliability, 1),
        energy_security=round(energy_security, 1),
        co2=round(co2, 1),
        water=round(water, 1),
        weighted_total=round(weighted_total, 1),
        breakdown=breakdown,
    )

def evaluate_all_mixes(scenario, carbon: dict, weights: dict) -> list[MixScore]:
    return sorted(
        (score_mix(name, shares, scenario, carbon, weights) for name, shares in CANDIDATE_MIXES.items()),
        key=lambda m: m.weighted_total,
        reverse=True,
    )

if __name__ == "__main__":
    from data_loader import load_workbook
    from forecasting import build_forecast
    from scenario_engine import apply_scenarios
    data = load_workbook()
    fc = build_forecast(data.saudi_data)
    states = apply_scenarios(fc, data.scenarios, target_year=2035)
    for scenario in states:
        print(f"\n=== {scenario.name} ({scenario.year}) ===")
        results = evaluate_all_mixes(scenario, data.carbon, data.weights)
        for r in results:
            print(f"  {r.mix_name:35s} score={r.weighted_total:5.1f}")
        print(f"  --> Recommended: {results[0].mix_name}")
