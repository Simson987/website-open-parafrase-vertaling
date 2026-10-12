# Open Parafrase Vertaling (OPV)

De Bijbel in eenvoudig, hedendaags Nederlands, naverteld vanuit de
Statenvertaling. **Proef**: alle verzen hebben de status *concept*.

🌐 **openparafrase.nl** (definitief domein)

## Drie sites

| Site | Repo | Inhoud |
|---|---|---|
| Open Parafrase Vertaling | deze repo | de parafrase |
| Open Vertaling | `website-open-bijbelvertaling` | de herziene Statenvertaling met alle opties |
| Open Gods Woord | `website-open-gods-woord` | wiki, Bijbelachtergrond en broninformatie |

De adressen van de drie sites staan op één plek: `js/sites.js`.

## Werken aan de parafrase

- Werkbron: `data/edities/opv/chapters/{boek}/{hoofdstuk}.json`
  (met `data/edities/opv/manifest.json` en `concepten.json`).
- Leeseditie bouwen: `python3 scripts/opv_leeseditie.py` schrijft
  `data/vertalingen/nl-opv/` en werkt `data/vertalingen/manifest.json` bij.
- Controleren: `python3 scripts/validate_opv.py`.
- Zoekindex: `python3 scripts/build_search_index.py --editie nl-opv`.
- Redactionele besluiten: `docs/opv/besluitregister.md`.

De directe bron is SV1888 in `data/{boek}/{hoofdstuk}.json` (veld
`textSV1888`). Die hoofdstukken komen uit de Open Vertaling en dienen ook als
vergelijkingskolom in de lezer.

## Lokaal draaien

```
python3 -m http.server 8002 --bind 127.0.0.1
```

Open http://127.0.0.1:8002/. Draaien de OV (:8000) en OGW (:8001) ook, dan
werken de kruislinks lokaal.

## Tests

```
python3 -m unittest discover -s tests
```

## Licentie

De tekst van de parafrase is publiek domein.
