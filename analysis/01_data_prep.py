"""Prepara o dataset analítico unificado e reporta cobertura/viés dos dados de preço."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd

from utils import BEDROOM_BUCKET_ORDER, build_airbnb_dataset, build_viva_dataset


def pct_table(df, col):
    return (df[col].value_counts(normalize=True, dropna=False) * 100).round(1)


def main():
    airbnb = build_airbnb_dataset()
    viva = build_viva_dataset()

    print("=" * 70)
    print("PREPARAÇÃO DE DADOS — Itapema/SC")
    print("=" * 70)

    print(f"\nAnúncios Airbnb únicos: {len(airbnb)}")
    print(f"Imóveis à venda (VivaReal): {len(viva)}")

    n_with_price = airbnb["has_price_data"].sum()
    print(f"\nAnúncios com cotação de preço (Price_AV): {n_with_price} "
          f"({n_with_price / len(airbnb) * 100:.1f}% do total)")
    print("-> Price_AV é uma amostra de cotações de diária (ADR) para datas futuras, "
          "capturada em 3 rodadas de scrape (jan/2025), NÃO um histórico real de reservas.")

    print("\n--- Checagem de viés: bairro (suburb) ---")
    full = pct_table(airbnb, "suburb")
    priced = pct_table(airbnb[airbnb["has_price_data"]], "suburb")
    comp = pd.DataFrame({"pct_populacao_total": full, "pct_com_preco": priced}).fillna(0)
    print(comp.head(10))

    print("\n--- Checagem de viés: tipologia (bedroom_bucket) ---")
    full_b = pct_table(airbnb, "bedroom_bucket").reindex(BEDROOM_BUCKET_ORDER)
    priced_b = pct_table(airbnb[airbnb["has_price_data"]], "bedroom_bucket").reindex(BEDROOM_BUCKET_ORDER)
    comp_b = pd.DataFrame({"pct_populacao_total": full_b, "pct_com_preco": priced_b}).fillna(0)
    print(comp_b)

    print("\n--- Checagem de viés: listing_type ---")
    full_t = pct_table(airbnb, "listing_type")
    priced_t = pct_table(airbnb[airbnb["has_price_data"]], "listing_type")
    comp_t = pd.DataFrame({"pct_populacao_total": full_t, "pct_com_preco": priced_t}).fillna(0)
    print(comp_t)

    print("\n--- VivaReal: tipologia (bedroom_bucket) ---")
    print(pct_table(viva, "bedroom_bucket").reindex(BEDROOM_BUCKET_ORDER))

    print("\nDatasets salvos em outputs/processed/airbnb_unified.csv e viva_clean.csv")


if __name__ == "__main__":
    main()
