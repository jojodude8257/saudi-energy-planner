from dataclasses import dataclass
from decision_engine import MixScore, evaluate_all_mixes

@dataclass
class Recommendation:
    scenario_name: str
    year: int
    recommended_mix: str
    decision_score: float
    confidence_pct: float
    top_reasons: list
    full_ranking: list

def recommend(scenario, carbon: dict, weights: dict) -> Recommendation:
    ranking = evaluate_all_mixes(scenario, carbon, weights)
    best, runner_up = ranking[0], ranking[1]
    margin = best.weighted_total - runner_up.weighted_total
    confidence = round(min(95.0, 50.0 + margin * 4), 0)

    diffs = {
        "Cost": best.cost - runner_up.cost,
        "Reliability": best.reliability - runner_up.reliability,
        "Energy Security": best.energy_security - runner_up.energy_security,
        "CO2 Performance": best.co2 - runner_up.co2,
        "Water Support": best.water - runner_up.water,
    }

    top_reasons = [k for k, v in sorted(diffs.items(), key=lambda kv: kv[1], reverse=True) if v > 0][:2]
    if not top_reasons:
        top_reasons = ["Balanced performance across all criteria"]

    return Recommendation(
        scenario_name=scenario.name,
        year=scenario.year,
        recommended_mix=best.mix_name,
        decision_score=best.weighted_total,
        confidence_pct=confidence,
        top_reasons=top_reasons,
        full_ranking=ranking,
    )

if __name__ == "__main__":
    from data_loader import load_workbook
    from forecasting import build_forecast
    from scenario_engine import apply_scenarios
    data = load_workbook()
    fc = build_forecast(data.saudi_data)
    states = apply_scenarios(fc, data.scenarios, target_year=2035)
    for scenario in states:
        rec = recommend(scenario, data.carbon, data.weights)
        print(f"{rec.scenario_name:28s} -> {rec.recommended_mix:35s} score={rec.decision_score:5.1f} confidence={rec.confidence_pct:.0f}%")
