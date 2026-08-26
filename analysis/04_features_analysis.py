"""Q3: Que características explicam os anúncios com melhor receita (apartamentos)?

Restrito a listing_type == "apartamento" (a Seazone só constrói apartamentos). Usa
uma regressão linear múltipla (features padronizadas) sobre o Revenue Potential
Score, controlando pelo tamanho do imóvel (number_of_bedrooms), para isolar o efeito
de qualidade/host/operação — não apenas correlação bruta, que seria confundida pelo
tamanho (imóveis maiores custam mais e teriam correlação alta com quase tudo).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from utils import apartamento_subset, build_airbnb_dataset, savefig

FEATURES = [
    "number_of_bedrooms",
    "amenities_count",
    "is_superhost",
    "can_instant_book",
    "is_professional",
    "star_rating",
    "number_of_bathrooms",
    "years_host",
]
# guest_satisfaction_overall excluída: colinear com star_rating (r=0.85), causava
# coeficientes instáveis/sinais invertidos. min_nights excluída: constante (sempre 0
# na subamostra com preço), sem informação.

FEATURE_LABELS_PT = {
    "number_of_bedrooms": "nº de quartos (controle de tamanho)",
    "amenities_count": "nº de amenidades listadas",
    "is_superhost": "é superhost",
    "can_instant_book": "reserva instantânea habilitada",
    "is_professional": "anfitrião profissional",
    "star_rating": "nota média (star rating)",
    "guest_satisfaction_overall": "satisfação geral do hóspede",
    "min_nights": "estadia mínima (noites)",
    "number_of_bathrooms": "nº de banheiros",
    "years_host": "anos como anfitrião",
}


def to_binary(series):
    return series.map({True: 1.0, False: 0.0})


def main():
    airbnb = build_airbnb_dataset()
    priced = apartamento_subset(airbnb)

    df = priced.copy()
    for col in ["is_superhost", "can_instant_book", "is_professional"]:
        df[col] = to_binary(df[col])

    model_df = df[FEATURES + ["revenue_potential_score"]].dropna()

    print("=" * 70)
    print("Q3 — CARACTERÍSTICAS QUE EXPLICAM MELHOR RECEITA")
    print(f"(base: {len(model_df)} anúncios de apartamento com preço e todas as features preenchidas)")
    print("=" * 70)

    print("\n--- Correlação bruta (Pearson) com Revenue Potential Score ---")
    corr = model_df[FEATURES].corrwith(model_df["revenue_potential_score"]).sort_values(
        key=abs, ascending=False
    )
    for feat, val in corr.items():
        print(f"{FEATURE_LABELS_PT[feat]:<40} {val:+.3f}")

    X = model_df[FEATURES].values
    y = model_df["revenue_potential_score"].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    reg = LinearRegression().fit(X_scaled, y)
    r2 = reg.score(X_scaled, y)

    coef_df = pd.DataFrame({
        "feature": [FEATURE_LABELS_PT[f] for f in FEATURES],
        "coef_padronizado": reg.coef_,
    }).sort_values("coef_padronizado", key=np.abs, ascending=False)

    print(f"\n--- Regressão linear múltipla (features padronizadas), R²={r2:.3f} ---")
    print("Coeficiente = variação no Revenue Potential Score por +1 desvio-padrão na feature,")
    print("mantendo as demais constantes (controla o efeito de tamanho do imóvel).")
    print(coef_df.to_string(index=False))

    fig, ax = plt.subplots(figsize=(8, 5))
    plot_df = coef_df.sort_values("coef_padronizado")
    colors = ["#e07a5f" if v < 0 else "#2a6f97" for v in plot_df["coef_padronizado"]]
    ax.barh(plot_df["feature"], plot_df["coef_padronizado"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Coeficiente padronizado (efeito no Revenue Potential Score)")
    ax.set_title(f"Q3 — O que explica melhor receita (R²={r2:.2f})")
    savefig(fig, "q3_regressao_features.png")
    plt.close(fig)

    print("\nGráfico salvo em outputs/figures/q3_regressao_features.png")


if __name__ == "__main__":
    main()
