# Data provenance

Both inputs are **real, public extracts of Swiggy's own restaurant listings**. No synthetic,
simulated or imputed data is used anywhere in this project.

| File | Rows | Source |
|---|---|---|
| `raw/swiggy_national.csv` | 148,541 | `huggingface.co/datasets/GowthamD03/Swiggy` → `swiggy.csv` |
| `raw/swiggy_metro_sla.csv` | 8,680 | `huggingface.co/datasets/jason1966/abhijitdahatonde_swiggy-restuarant-dataset` → `swiggy.csv` |

## Columns — national

`id, name, city, rating, rating_count, cost, cuisine, lic_no, link, address, menu`

- `city` is `"Locality,City"` for most rows (`"Indirapuram,Delhi"`) and a bare city name for others,
  so it is split into `locality` + `city_name` in the clean step.
- `rating` is `"--"` when Swiggy suppresses the rating.
- `rating_count` is a band: `"Too Few Ratings"`, `"20+ ratings"`, `"1K+ ratings"`.
- `cost` is `"₹ 200"`.
- `cuisine` holds up to two comma-separated tags.
- `menu` is a filename reference, not menu content — there is **no item-level price data**, which is
  why this project is supply-side and not revenue-side.

## Columns — metro SLA

`ID, Area, City, Restaurant, Price, Avg ratings, Total ratings, Food type, Address, Delivery time`

`Delivery time` is Swiggy's **quoted** delivery estimate in minutes, not a measured delivery.

## Re-download

```bash
python scripts/00_download_data.py
```

The raw CSVs are git-ignored (45 MB) — the download script fetches and row-count-verifies them, and
the cleaned outputs in `data/clean/` are committed so the analysis is reproducible without the fetch.

## Licensing note

Scraped listing data of this kind is used here for non-commercial portfolio analysis. The published
artefacts contain aggregate statistics and a partial listing sample, not a redistribution of the full
scrape.
