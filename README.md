[🎥 VÍDEO (até 3 min)](https://drive.google.com/file/d/1M5QGBR6hAUMCnZPsSH8DhVqhEU17rW9J/view?usp=sharing)

# Jovens Talentos AI Builder 2026 — Recomendação de Investimento (Itapema/SC)

**Candidato:** Guilherme Ximenes
**Desafio:** [enunciado completo](https://seazone-tech.github.io/jovens-talentos-2026-hackathon-data/) (Seazone)

## 👉 A recomendação final está em [`relatorio.md`](relatorio.md)

Lá estão as respostas às 4 perguntas do desafio, o que construir e onde construir (em duas
camadas: tipologia e localização), o veredito sobre a tese "studio/1 quarto no Centro", o retorno
estimado, a metodologia usada e as limitações dos dados — leia antes de assistir ao vídeo, que
resume esse conteúdo.

Para uma leitura mais visual (gráficos embutidos, mesmo conteúdo), abra
[`resultados.html`](resultados.html) no navegador.

## Como rodar a análise

Requer Python 3.11+ com `pandas`, `numpy`, `matplotlib`, `scikit-learn` (já usados no
desenvolvimento; instale com `pip install pandas numpy matplotlib scikit-learn` se necessário).

```bash
python analysis/run_all.py
```

Isso roda a pipeline completa (`analysis/01_data_prep.py` a `analysis/05_investment_recommendation.py`)
e regenera:
- `outputs/processed/` — datasets unificados (Airbnb + VivaReal limpos e joinados) e o ranking
  final de retorno (`q4_r_m2_grid.csv`, `q4_terrenos.csv`)
- `outputs/figures/` — os gráficos referenciados em `relatorio.md` e `resultados.html`

Cada script também pode ser rodado individualmente (ex.: `python analysis/03_location_analysis.py`)
e imprime no terminal os números por trás de cada resposta.

## Estrutura do repositório

```
data/                              # dados originais fornecidos (não alterados)
analysis/
  utils.py                         # carga/limpeza/junção dos 5 CSVs
  01_data_prep.py                  # dataset unificado + checagem de cobertura/viés
  02_profile_analysis.py           # Pergunta 1 — melhor perfil de imóvel
  03_location_analysis.py          # Pergunta 2 — melhor localização
  04_features_analysis.py          # Pergunta 3 — o que explica melhor receita
  05_investment_recommendation.py  # Pergunta 4 — onde investir/construir e retorno estimado
  run_all.py                       # roda tudo em sequência
outputs/
  figures/                         # gráficos gerados (usados no relatorio.md)
  processed/                       # datasets intermediários e ranking final
ai-log/                            # transcrição completa das conversas com a IA
relatorio.md                       # recomendação final (leia primeiro)
resultados.html                    # mesma recomendação, versão visual (abrir no navegador)
```

## Sobre os dados

Snapshot estático do mercado imobiliário de **Itapema (SC)**, com anúncios de Airbnb e de venda
(VivaReal). Mesma base para todos os candidatos.

| Arquivo | O que tem | Como conecta |
|---|---|---|
| `Details_Itapema.csv` | Cada anúncio de Airbnb: título, reviews, star rating, descrição, host_id, nº de quartos, tipo de imóvel | Base principal dos listings |
| `Hosts_ids_Itapema.csv` | Dados do anfitrião: nº de reviews, anos como host, superhost, taxa de resposta | Liga com Details pelo `owner_id` |
| `Mesh_Ids_Data_Itapema.csv` | Latitude/longitude + bairro de cada anúncio | Liga por listing |
| `Price_AV_Itapema.csv` | Preço por anúncio, por data de estadia e por data de captura | Liga por listing |
| `VivaReal_Itapema.csv` | Anúncios de venda: preço, condomínio, área, vendedor | Mercado de compra |

## Uso de IA

Trabalhei com o Claude Code (Anthropic) durante toda a análise — do fork do repositório ao
desenho da metodologia, escrita dos scripts e pesquisa externa. A transcrição completa da sessão,
em texto puro, está em [`ai-log/`](ai-log/).

---

*Seazone — Jovens Talentos AI Builder 2026*
