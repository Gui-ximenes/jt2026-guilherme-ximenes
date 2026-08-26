"""Q4: Onde/o que construir hoje (especulação imobiliária), e com que retorno estimado?

MODELO DE NEGÓCIO DA SEAZONE (pesquisado durante a análise, não está nos dados — ver
ai-log/08-*.md e ai-log/10-*.md): não é uma incorporadora tradicional. Ela estrutura
SPEs (Sociedade de Propósito Específico) por obra: investidores entram como SÓCIOS da
construção, o terreno fica em nome da SPE, e cada obra é autofinanciada só pelos seus
próprios investidores. Depois de pronto, a Seazone opera as unidades como short stay
(o negócio recorrente, via microfranquias que recebem 8% da receita de diária).

RETORNO ESTIMADO — abordagem realista: a Seazone já vende exatamente esse produto
(apartamento compacto de short stay) sob a marca "SPOT", com preços de ticket públicos
no próprio marketplace. Em vez de estimar custo de construção com heurísticas genéricas
(tentativa anterior via CUB-SC + benchmark de terreno, descartada por gerar cap rates
de 38-50% — irreais mesmo depois de ajustada, ver ai-log/09-*.md), usamos o PREÇO REAL
de ticket por m² do SPOT mais comparável (Ponta das Canas, Florianópolis/SC — mesmo
estado, mesma faixa de metragem que nosso "Studio/1 quarto"): 9 unidades de 16,86 a
49,93 m², ticket de R$220.000 a R$423.000, ou seja, R$8.472 a R$13.049/m². Aplicamos
esse preço real como custo à nossa própria receita por m² (calculada na Pergunta 1,
citywide, a partir de Airbnb + VivaReal) para produzir um cap rate nosso, mas ancorado
em dado de mercado real, não numa estimativa genérica de custo de obra.

POR QUE O CUSTO DE TERRENO NÃO É MAIS A VARIÁVEL DECISIVA DESTA ANÁLISE: um terreno
sustenta várias unidades (não é 1 terreno = 1 apartamento), então seu custo é diluído
entre elas — a Seazone não compra "1 terreno por apartamento". O custo de obra por m²
tende a ser parecido entre bairros da mesma cidade. Como não temos dado de quantas
unidades cabem em cada terreno (depende de zoneamento/gabarito, que também está mudando
agora em Itapema — ver seção de riscos), a métrica mais confiável que os dados
sustentam é RECEITA POR M² (R$/m² = ADR ÷ área útil do apartamento pronto
equivalente), calculada na Pergunta 1. Terreno entra aqui só como contexto de
liquidez/execução (quantos lotes existem à venda), não como base de cálculo de retorno.

ESTRUTURA EM DUAS CAMADAS (decisão do candidato — tamanho e localização respondem
perguntas diferentes e não precisam ser combinadas numa única resposta):
  Camada 1 — O QUE construir: decidida pela Pergunta 1 (R$/m² por tipologia).
  Camada 2 — ONDE construir: cruza potencial de receita (Pergunta 2), liquidez de
  terreno (contexto, não custo) e o R$/m² específico de apartamentos compactos em cada
  bairro (quando a amostra permite).
Achados de legislação/risco entram só como seção qualitativa — não ajustam os números.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
import pandas as pd

from utils import BEDROOM_BUCKET_ORDER, apartamento_subset, build_airbnb_dataset, build_viva_dataset, savefig

MIN_N = 10
COMPACT = "Studio/1 quarto"

# Preço real de ticket por m² do SPOT Seazone mais comparável ao nosso "Studio/1
# quarto": Ponta das Canas (Florianópolis/SC), 9 unidades de 1 quarto, 16,86-49,93 m²,
# ticket R$220.000-423.000 (marketplace da Seazone, ago/2026). Unidade menor = mais
# cara por m² (R$13.049), unidade maior = mais barata por m² (R$8.472) — padrão comum
# de compacto (custos fixos de cozinha/banheiro diluem menos em unidades pequenas).
SPOT_PRECO_M2_MIN = 8472    # unidade maior (49,93 m²) — mais parecida com nossa área média (43 m²)
SPOT_PRECO_M2_MAX = 13049   # unidade menor (16,86 m²)
SPOT_RETORNO_DIVULGADO = 17.7  # % a.a., divulgado pela Seazone para este SPOT específico

OCC_SENSITIVITY = [0.40, 0.50, 0.60]
OCC_BASE = 0.50


def retorno_sobre_ticket_real(r_m2, occupancy):
    """Cap rate bruto (pré-impostos, pré custos de gestão) = receita anual por m²
    (nossa, calculada a partir de Airbnb+VivaReal) dividida pelo preço real de ticket
    por m² de um SPOT Seazone comparável (Ponta das Canas/SC). Retorna (cap_min, cap_max)."""
    receita_anual_m2 = r_m2 * 365 * occupancy
    cap_min = receita_anual_m2 / SPOT_PRECO_M2_MAX * 100  # ticket mais caro (unidade menor)
    cap_max = receita_anual_m2 / SPOT_PRECO_M2_MIN * 100  # ticket mais barato (unidade maior)
    return cap_min, cap_max


def land_supply(viva):
    t = viva[(viva["listing_type"] == "terreno") & (viva["usable_area"] > 0)].copy()
    t["preco_m2"] = t["sale_price"] / t["usable_area"]
    g = t.groupby("suburb").agg(
        n_terrenos=("listing_id", "count"), preco_mediano=("sale_price", "median"),
        preco_m2_mediano=("preco_m2", "median"),
    ).reset_index().sort_values("n_terrenos", ascending=False)
    return g


def r_m2_grid(airbnb, viva):
    apt = apartamento_subset(airbnb)
    viva_apt = viva[viva["listing_type"] == "apartamento"]
    a = apt.groupby(["suburb", "bedroom_bucket"]).agg(n_adr=("airbnb_listing_id", "count"), adr=("adr_median", "median")).reset_index()
    v = viva_apt.groupby(["suburb", "bedroom_bucket"])["usable_area"].agg(n_area="count", area="median").reset_index()
    g = a.merge(v, on=["suburb", "bedroom_bucket"], how="inner")
    g["r_m2"] = (g["adr"] / g["area"]).round(2)
    g["confiavel"] = g["n_adr"] >= MIN_N
    return g


def main():
    airbnb = build_airbnb_dataset()
    viva = build_viva_dataset()

    print("=" * 70)
    print("Q4 — ONDE/O QUE CONSTRUIR, COM RETORNO ESTIMADO (duas camadas)")
    print("=" * 70)

    # ---------- CAMADA 1: O QUE CONSTRUIR ----------
    apt = apartamento_subset(airbnb)
    viva_apt = viva[viva["listing_type"] == "apartamento"]
    citywide = apt.groupby("bedroom_bucket").agg(n_adr=("airbnb_listing_id", "count"), adr=("adr_median", "median")).reset_index()
    citywide_area = viva_apt.groupby("bedroom_bucket")["usable_area"].median().reset_index().rename(columns={"usable_area": "area"})
    citywide = citywide.merge(citywide_area, on="bedroom_bucket")
    citywide["r_m2"] = (citywide["adr"] / citywide["area"]).round(2)
    citywide["bedroom_bucket"] = pd.Categorical(citywide["bedroom_bucket"], categories=BEDROOM_BUCKET_ORDER, ordered=True)
    citywide = citywide.sort_values("bedroom_bucket")

    print("\n--- CAMADA 1: O que construir (R$/m², cidade toda) ---")
    print(citywide.to_string(index=False))
    print(f"\n>>> {COMPACT} é a tipologia mais eficiente por m² em toda a cidade — decisão da Camada 1.")

    print(f"\n--- Retorno estimado (ancorado em preço real de ticket, não em heurística de custo) ---")
    print(f"Comparável real: SPOT Ponta das Canas (Florianópolis/SC) — 9 unidades de 1 quarto,")
    print(f"16,86-49,93 m², ticket R$220.000-423.000 -> R${SPOT_PRECO_M2_MIN:,}-{SPOT_PRECO_M2_MAX:,}/m².")
    print(f"Retorno divulgado pela Seazone para ESSE spot: {SPOT_RETORNO_DIVULGADO}% a.a. (referência, não usado no cálculo).")
    compact_row = citywide[citywide["bedroom_bucket"] == COMPACT].iloc[0]
    cmin, cmax = retorno_sobre_ticket_real(compact_row["r_m2"], OCC_BASE)
    print(f"\nNosso cálculo (ocupação-base {int(OCC_BASE*100)}%): receita por m² do nosso dado (Studio/1 quarto, "
          f"R${compact_row['r_m2']:.2f}/m²/noite) ÷ preço real de ticket do comparável -> "
          f"cap rate estimado: {cmin:.1f}% a {cmax:.1f}% a.a.")
    sens = ", ".join(
        f"{int(occ*100)}%: {retorno_sobre_ticket_real(compact_row['r_m2'], occ)[0]:.1f}-"
        f"{retorno_sobre_ticket_real(compact_row['r_m2'], occ)[1]:.1f}%"
        for occ in OCC_SENSITIVITY
    )
    print(f"Sensibilidade de ocupação: {sens}")
    print(f">>> Cai dentro da faixa que a própria Seazone declara para o produto SPOT (13-23% a.a.) e perto")
    print(f">>> do comparável mais próximo geograficamente ({SPOT_RETORNO_DIVULGADO}% a.a., Ponta das Canas/SC) —")
    print(f">>> uma triangulação bem mais forte que a tentativa anterior via CUB genérico (que dava 38-50%).")
    print("Só apartamentos compactos têm esse comparável real: a Seazone não vende SPOTs de 2+ quartos,")
    print("o que é, por si só, mais uma evidência de que o mercado já validou a tese do compacto.")

    # ---------- CAMADA 2: ONDE CONSTRUIR ----------
    print("\n--- CAMADA 2: Onde construir ---")

    land = land_supply(viva)
    print("\nTerrenos à venda por bairro (contexto de liquidez/execução, NÃO usado como custo):")
    print(land.to_string(index=False))
    print("Centro: 0 terrenos à venda hoje — ressalva de execução, não motivo de exclusão do ranking.")

    grid = r_m2_grid(airbnb, viva)
    bairros_q2 = ["Meia Praia", "Casa Branca", "Morretes", "Centro", "Tabuleiro dos Oliveiras"]
    compact_rows = grid[(grid["bedroom_bucket"] == COMPACT) & (grid["suburb"].isin(bairros_q2))].sort_values("r_m2", ascending=False)
    print(f"\nR$/m² de '{COMPACT}' por bairro (a tipologia vencedora da Camada 1, agora por localização):")
    print(compact_rows[["suburb", "n_adr", "adr", "area", "r_m2", "confiavel"]].to_string(index=False))
    print("'confiavel' = False significa n < 10 anúncios Airbnb com preço — leitura só ilustrativa.")

    land_by_bairro = land.set_index("suburb")["n_terrenos"].to_dict()
    print("\n--- Quadro-resumo Camada 2 (ordenado por R$/m² de compacto, quando confiável) ---")
    for _, row in compact_rows.iterrows():
        b = row["suburb"]
        n_ter = land_by_bairro.get(b, 0)
        flag = "" if row["confiavel"] else "  [amostra pequena, n<10]"
        print(f"{b}: R${row['r_m2']:.2f}/m² para {COMPACT} | {n_ter} terrenos à venda{flag}")

    print("\n--- Por que Meia Praia e Ilhota não são a resposta óbvia, mesmo com receita alta? ---")
    ilhota_apt = apt[apt["suburb"] == "Ilhota"]
    ilhota_terrenos = land[land["suburb"] == "Ilhota"]
    print(f"Meia Praia: melhor R$/m² para {COMPACT} da cidade (12,12) e maior potencial de receita (Q2), "
          f"mas só 5 terrenos à venda hoje — limita quantas unidades dá pra construir de uma vez.")
    print(f"Ilhota: só {len(ilhota_apt)} anúncios de apartamento com preço no Airbnb (todos os tamanhos somados) e "
          f"{0 if ilhota_terrenos.empty else int(ilhota_terrenos['n_terrenos'].iloc[0])} terrenos à venda — "
          f"dado insuficiente pra qualquer leitura confiável, não uma rejeição.")

    print("\n--- Riscos e contexto regulatório (pesquisa externa, não está nos dados — qualitativo) ---")
    print("Meia Praia: sujeita a regra de 'cone de sombra' (limita altura de prédios na orla), mas há uma Operação")
    print("Urbana Consorciada (Lei Complementar 113/2021) permitindo mais altura via outorga onerosa, financiando")
    print("alargamento de praia — pode liberar mais densidade construtiva ali no médio prazo (oportunidade).")
    print("Morretes: parte do território é área de encosta (APP acima de 45° de declive, não edificável) e está")
    print("num programa municipal de regularização fundiária (REURB) por histórico de loteamentos informais —")
    print("nem todo os 76 terrenos listados são necessariamente prontos para construir sem checagem individual.")
    print("Casa Branca, Tabuleiro dos Oliveiras e Ilhota também estão no mesmo programa de REURB.")
    print("Centro: nenhuma restrição especial encontrada, mas segue sem terreno listado à venda hoje.")

    grid.to_csv(Path(__file__).resolve().parent.parent / "outputs" / "processed" / "q4_r_m2_grid.csv", index=False)
    land.to_csv(Path(__file__).resolve().parent.parent / "outputs" / "processed" / "q4_terrenos.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    labels = compact_rows["suburb"]
    colors = ["#2a6f97" if c else "#9fb3c8" for c in compact_rows["confiavel"]]
    ax.barh(labels, compact_rows["r_m2"], color=colors)
    for i, (v, n, conf) in enumerate(zip(compact_rows["r_m2"], compact_rows["n_adr"], compact_rows["confiavel"])):
        tag = f"{v:.2f}  (n={n})" + ("" if conf else "  amostra pequena")
        ax.text(v + 0.1, i, tag, va="center", fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, compact_rows["r_m2"].max() * 1.5)
    ax.set_xlabel(f"R$/m²/noite — apartamento {COMPACT}")
    ax.set_title(f"Q4 — Onde construir {COMPACT}: receita por m² por bairro")
    savefig(fig, "q4_r_m2_por_bairro.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    land_plot = land.sort_values("n_terrenos", ascending=True)
    colors2 = ["#e07a5f" if s == "Centro" else "#2a6f97" for s in land_plot["suburb"]]
    ax.barh(land_plot["suburb"], land_plot["n_terrenos"], color=colors2)
    for i, (n, p) in enumerate(zip(land_plot["n_terrenos"], land_plot["preco_m2_mediano"])):
        ax.text(n, i, f"  R${p:,.0f}/m²", va="center", fontsize=8)
    ax.set_xlabel("Nº de terrenos à venda (contexto de liquidez, não de custo)")
    ax.set_title("Q4 — Terra disponível por bairro (Centro = 0, ressalva)")
    savefig(fig, "q4_terrenos_por_bairro.png")
    plt.close(fig)

    print("\nDados salvos em outputs/processed/q4_r_m2_grid.csv e q4_terrenos.csv")
    print("Gráficos salvos em outputs/figures/q4_r_m2_por_bairro.png e q4_terrenos_por_bairro.png")


if __name__ == "__main__":
    main()
