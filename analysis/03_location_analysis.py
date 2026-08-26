"""Q2: Qual a melhor localização em termos de receita — restrito a apartamentos?

A Seazone só constrói apartamentos, então o ranking de bairros abaixo usa só
listing_type == "apartamento" (a versão anterior deste script somava todos os tipos
de imóvel, o que distorcia o ranking com casas/hotéis/outros que a Seazone nunca
construiria).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt

from utils import apartamento_subset, build_airbnb_dataset, savefig


def main():
    airbnb = build_airbnb_dataset()
    apt = apartamento_subset(airbnb)
    apt = apt[apt["suburb"].notna()]

    print("=" * 70)
    print("Q2 — MELHOR LOCALIZAÇÃO POR RECEITA (apartamentos)")
    print(f"(base: {len(apt)} anúncios de apartamento com dados de preço e bairro identificado)")
    print("=" * 70)

    by_suburb = apt.groupby("suburb").agg(
        n=("airbnb_listing_id", "count"),
        adr_mediano=("adr_median", "median"),
        reviews_mediano=("number_of_reviews", "median"),
        score_mediano=("revenue_potential_score", "median"),
    ).reset_index()
    by_suburb = by_suburb[by_suburb["n"] >= 10].sort_values("score_mediano", ascending=False)

    print("\n--- Ranking de bairros por Revenue Potential Score (mín. 10 anúncios de apartamento) ---")
    print(by_suburb.to_string(index=False))

    print("\n--- Bairros excluídos do ranking por amostra < 10 anúncios de apartamento ---")
    small = apt.groupby("suburb").size()
    small = small[small < 10].sort_values(ascending=False)
    print(small.to_string() if len(small) else "(nenhum)")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(by_suburb["suburb"], by_suburb["score_mediano"], color="#3d5a80")
    for i, (n, v) in enumerate(zip(by_suburb["n"], by_suburb["score_mediano"])):
        ax.text(v, i, f"  n={n}", va="center", fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Revenue Potential Score (mediano)")
    ax.set_title("Q2 — Potencial de receita por bairro (apartamentos, min. 10 anúncios)")
    savefig(fig, "q2_score_por_bairro.png")
    plt.close(fig)

    print("\nGráfico salvo em outputs/figures/q2_score_por_bairro.png")


if __name__ == "__main__":
    main()
