"""Bio-Alpha Experiment Runner — Parameter Sweeps & A/B Tests.

Run:  python run_experiments.py
"""
from bioalpha.simulation.model import run_parameter_sweep, run_ab_test

SEVEN_DAYS = 168


def experiment_1():
    """CO2 Cost Sensitivity Sweep."""
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: CO2 Cost Sensitivity Sweep")
    print("=" * 60)
    print("Testing: What if CO2 costs $5, $10, $20, or $40 per burst?")
    print(f"Duration: 7 days x 3 runs per config\n")

    df = run_parameter_sweep(
        sweep_params={"co2_cost": [5, 10, 20, 40]},
        timesteps=SEVEN_DAYS, runs_per_config=3,
    )
    final = df[df["timestep"] == df["timestep"].max()]

    print(f"{'CO2 Cost':>10} | {'Biomass':>8} | {'$ALPHA Left':>12} | {'Health':>8} | {'CO2 Bursts':>11} | {'OPEX':>10}")
    print("-" * 72)
    costs = [5, 10, 20, 40]
    for i in sorted(final["subset"].unique()):
        g = final[final["subset"] == i]
        c = costs[i] if i < len(costs) else "?"
        print(f"    ${c:>3}/burst | {g['biomass_grams'].mean():>6.1f}g | ${g['alpha_balance'].mean():>10,.0f} | {g['health_score'].mean():>6.1f} | {g['co2_bursts'].mean():>9.0f} | ${g['total_opex'].mean():>8,.0f}")


def experiment_2():
    """Conservative vs Aggressive CO2."""
    print("\n\n" + "=" * 60)
    print("EXPERIMENT 2: A/B Test -- Conservative vs Aggressive CO2")
    print("=" * 60)
    print("A (Conservative): CO2 min = 600 ppm")
    print("B (Aggressive):   CO2 min = 1000 ppm")
    print(f"Duration: 7 days x 5 runs each\n")

    df_a, df_b = run_ab_test(
        params_a={"co2_min": [600]}, params_b={"co2_min": [1000]},
        timesteps=SEVEN_DAYS, runs=5,
    )
    _print_ab(df_a, df_b, "Conservative", "Aggressive")


def experiment_3():
    """16h vs 20h Light."""
    print("\n\n" + "=" * 60)
    print("EXPERIMENT 3: A/B Test -- 16h vs 20h Light Schedule")
    print("=" * 60)
    print("A: 16h light (6AM-10PM)")
    print("B: 20h light (4AM-12AM)")
    print(f"Duration: 7 days x 5 runs each\n")

    df_c, df_d = run_ab_test(
        params_a={"light_on_hour": [6], "light_off_hour": [22]},
        params_b={"light_on_hour": [4], "light_off_hour": [24]},
        timesteps=SEVEN_DAYS, runs=5,
    )
    _print_ab(df_c, df_d, "16h Light", "20h Light")


def _print_ab(df_a, df_b, label_a, label_b):
    fa = df_a[df_a["timestep"] == df_a["timestep"].max()]
    fb = df_b[df_b["timestep"] == df_b["timestep"].max()]

    metrics = [
        ("Avg Biomass (g)", "biomass_grams", "max"),
        ("Avg $ALPHA Left", "alpha_balance", "max"),
        ("Avg Health", "health_score", "max"),
        ("CO2 Bursts", "co2_bursts", "min"),
        ("Irrigations", "irrigation_events", "min"),
        ("Dosing Events", "dosing_events", "min"),
        ("Total OPEX", "total_opex", "min"),
    ]

    print(f"{'Metric':<22} | {label_a:>16} | {label_b:>16} | {'Winner':>10}")
    print("-" * 72)
    for label, col, best in metrics:
        va, vb = fa[col].mean(), fb[col].mean()
        sa = f"${va:>12,.0f}" if col in ("alpha_balance", "total_opex") else f"{va:>13.1f}"
        sb = f"${vb:>12,.0f}" if col in ("alpha_balance", "total_opex") else f"{vb:>13.1f}"
        w = "A" if (va > vb if best == "max" else va < vb) else "B" if (vb > va if best == "max" else vb < va) else "TIE"
        print(f"  {label:<20} | {sa:>16} | {sb:>16} | {w:>10}")


if __name__ == "__main__":
    experiment_1()
    experiment_2()
    experiment_3()
    print("\n" + "=" * 60)
    print("All experiments complete!")
    print("=" * 60)
