"""Q1: Qual o melhor perfil de imóvel (nº de quartos) — restrito a apartamentos?

A Seazone só constrói apartamentos (não casas, hotéis ou outros tipos), então toda a
análise abaixo é restrita a listing_type == "apartamento". Studio e 1 quarto entram
na mesma categoria "Studio/1 quarto" (ver utils.bedroom_bucket) — separados, o studio
tinha só 8 anúncios com preço em toda a cidade, amostra pequena demais para qualquer
leitura própria.

MÉTRICA PRINCIPAL — Receita por m² (R$/m²) = ADR mediano do Airbnb ÷ área útil mediana
do apartamento pronto equivalente (VivaReal). Por quê essa é a métrica decisiva e não a
receita bruta nem o preço de terreno: o custo de terreno é diluído entre as várias
unidades construídas no mesmo prédio (não é 1 terreno = 1 apartamento), e o custo de
obra por m² tende a ser parecido entre bairros da mesma cidade (mesma mão de obra,
mesmos materiais, CUB regional similar). Ou seja, o custo de construção de um
apartamento é aproximadamente proporcional ao seu tamanho, então normalizar a receita
pelo tamanho (m²) aproxima o retorno por real investido melhor do que normalizar pelo
preço de terreno (que não temos como diluir corretamente) ou do que olhar receita bruta
(que favorece unidades grandes só porque custam mais para construir).

Também reportamos a Revenue Potential Score bruta (ADR × percentil de reviews) como
contexto — ela mostra receita absoluta, mas não é a métrica que decide "o que construir".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
import pandas as pd

from utils import BEDROOM_BUCKET_ORDER, apartamento_subset, build_airbnb_dataset, build_viva_dataset, savefig

MIN_N = 10


def main():
    airbnb = build_airbnb_dataset()
    viva = build_viva_dataset()
    apt = apartamento_subset(airbnb)
    viva_apt = viva[viva["listing_type"] == "apartamento"]

    print("=" * 70)
    print("Q1 — MELHOR PERFIL DE IMÓVEL (apartamentos)")
    print(f"(base: {len(apt)} anúncios de apartamento com dados de preço, de {airbnb['has_price_data'].sum()} no total com preço)")
    print("=" * 70)

    by_bedroom = apt.groupby("bedroom_bucket").agg(
        n=("airbnb_listing_id", "count"),
        adr_mediano=("adr_median", "median"),
        reviews_mediano=("number_of_reviews", "median"),
        score_mediano=("revenue_potential_score", "median"),
    ).reset_index()
    area = viva_apt.groupby("bedroom_bucket")["usable_area"].agg(n_area="count", area_mediana="median").reset_index()
    by_bedroom = by_bedroom.merge(area, on="bedroom_bucket")
    by_bedroom["r_m2"] = (by_bedroom["adr_mediano"] / by_bedroom["area_mediana"]).round(2)
    by_bedroom["bedroom_bucket"] = pd.Categorical(
        by_bedroom["bedroom_bucket"], categories=BEDROOM_BUCKET_ORDER, ordered=True
    )
    by_bedroom = by_bedroom.sort_values("bedroom_bucket")

    print("\nScore = ADR mediano x percentil de reviews (receita bruta, contexto). R$/m² = ADR")
    print("mediano / área útil mediana do apartamento pronto (VivaReal) — métrica principal.")
    print("\n--- Por número de quartos (só apartamento) ---")
    print(by_bedroom.to_string(index=False))

    print(f"\n>>> Studio/1 quarto rende R${by_bedroom.set_index('bedroom_bucket').loc['Studio/1 quarto','r_m2']:.2f}/m²/noite — "
          f"quase o dobro de qualquer outra tipologia. Esse é o achado central da Pergunta 1.")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    order = [b for b in BEDROOM_BUCKET_ORDER if b in by_bedroom["bedroom_bucket"].values]
    plot_df = by_bedroom.set_index("bedroom_bucket").loc[order]
    ax.bar(order, plot_df["r_m2"], color="#2a6f97")
    for i, (n, v) in enumerate(zip(plot_df["n"], plot_df["r_m2"])):
        ax.text(i, v, f"n={n}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("R$ de ADR por m² (mediano)")
    ax.set_title("Q1 — Receita por m² construído, por número de quartos (apartamentos)")
    plt.xticks(rotation=10)
    savefig(fig, "q1_receita_por_m2.png")
    plt.close(fig)

    print("\nGráfico salvo em outputs/figures/q1_receita_por_m2.png")


if __name__ == "__main__":
    main()
