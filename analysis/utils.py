"""Funções compartilhadas de carga, limpeza e junção dos dados de Itapema/SC."""

import ast
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "outputs" / "processed"
FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"

BEDROOM_BUCKET_ORDER = ["Studio/1 quarto", "2 quartos", "3 quartos", "4+ quartos"]


def bedroom_bucket(n):
    """Studio (0 quartos) e 1 quarto entram na mesma categoria "Studio/1 quarto" — a Seazone
    trata os dois como o mesmo produto compacto, e separá-los deixava a amostra de studio
    (n=8 na cidade inteira) pequena demais para qualquer leitura própria."""
    if pd.isna(n):
        return np.nan
    n = int(n)
    if n <= 1:
        return "Studio/1 quarto"
    if n == 2:
        return "2 quartos"
    if n == 3:
        return "3 quartos"
    return "4+ quartos"


def count_amenities(raw):
    if pd.isna(raw):
        return 0
    try:
        items = ast.literal_eval(raw)
        return len(items) if isinstance(items, list) else 0
    except (ValueError, SyntaxError):
        return 0


def load_details():
    df = pd.read_csv(DATA_DIR / "Details_Itapema.csv")
    df["airbnb_listing_id"] = df["airbnb_listing_id"].astype(str)
    df["owner_id"] = df["owner_id"].astype(str)
    df["amenities_count"] = df["amenities"].apply(count_amenities)
    df["bedroom_bucket"] = df["number_of_bedrooms"].apply(bedroom_bucket)
    return df


def load_hosts():
    """Hosts_ids tem múltiplos snapshots por owner_id (capturas repetidas do scraper).
    Mantemos apenas o snapshot mais recente por host."""
    df = pd.read_csv(DATA_DIR / "Hosts_ids_Itapema.csv")
    df["owner_id"] = df["owner_id"].astype(str)
    df["host_snapshot_date"] = pd.to_datetime(df["host_snapshot_date"])
    df = df.sort_values("host_snapshot_date").drop_duplicates("owner_id", keep="last")
    return df


def load_mesh():
    df = pd.read_csv(DATA_DIR / "Mesh_Ids_Data_Itapema.csv")
    df["airbnb_listing_id"] = df["airbnb_listing_id"].astype(str)
    df["suburb"] = df["suburb"].replace("none", np.nan)
    return df


def load_price():
    df = pd.read_csv(DATA_DIR / "Price_AV_Itapema.csv")
    df["airbnb_listing_id"] = df["airbnb_listing_id"].astype(str)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_viva():
    df = pd.read_csv(DATA_DIR / "VivaReal_Itapema.csv")
    df["listing_id"] = df["listing_id"].astype(str)
    df["bedroom_bucket"] = df["bedrooms"].apply(bedroom_bucket)
    df = df[df["business_types"] == "Venda"].copy()
    return df


def price_agg_by_listing():
    price = load_price()
    agg = price.groupby("airbnb_listing_id")["price"].agg(
        adr_median="median", adr_mean="mean", adr_std="std", n_quotes="count",
        adr_min="min", adr_max="max",
    ).reset_index()
    return agg


def build_airbnb_dataset(save=True):
    """Junta details + mesh + hosts + preço agregado num único dataset por anúncio."""
    details = load_details()
    mesh = load_mesh()
    hosts = load_hosts()
    price_agg = price_agg_by_listing()

    df = details.merge(
        mesh[["airbnb_listing_id", "suburb"]], on="airbnb_listing_id", how="left"
    )
    df = df.merge(hosts, on="owner_id", how="left", suffixes=("", "_host"))
    df = df.merge(price_agg, on="airbnb_listing_id", how="left")
    df["has_price_data"] = df["n_quotes"].notna()

    if save:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(PROCESSED_DIR / "airbnb_unified.csv", index=False)
    return df


def build_viva_dataset(save=True):
    df = load_viva()
    if save:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(PROCESSED_DIR / "viva_clean.csv", index=False)
    return df


def add_revenue_score(df):
    """Revenue Potential Score = ADR mediano x percentil de reviews (demanda relativa),
    calculado DENTRO do próprio subconjunto recebido (ex.: só apartamentos com preço).
    Proxy explícito, não receita real — ver limitações no relatorio.md."""
    df = df.copy()
    df["reviews_percentile"] = df["number_of_reviews"].rank(pct=True)
    df["revenue_potential_score"] = df["adr_median"] * df["reviews_percentile"]
    return df


def apartamento_subset(airbnb_df):
    """Anúncios com preço, restritos a listing_type == 'apartamento' — a Seazone só constrói
    apartamentos, então todas as perguntas 1-4 são respondidas só sobre essa tipologia.
    O percentil de reviews do Revenue Potential Score é recalculado dentro desse subconjunto
    (não herdado do conjunto com todos os tipos de imóvel)."""
    df = airbnb_df[(airbnb_df["has_price_data"]) & (airbnb_df["listing_type"] == "apartamento")].copy()
    return add_revenue_score(df)


def savefig(fig, name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / name, dpi=140, bbox_inches="tight")
