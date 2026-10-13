# Claude — projectinstructies (Open Parafrase Vertaling)

Deze repo is de site van de Open Parafrase Vertaling (OPV). Ze is op
2026-10-08 afgesplitst van de Open Vertaling; zie
`docs/superpowers/specs/2026-10-08-splitsing-drie-sites-design.md`.

## Drie sites, drie repo's

- **OPV** (deze repo): de parafrase. Standaardeditie `nl-opv`; de OV is
  alleen kiesbaar als vergelijking (`js/teksteditie.js`).
- **OV** (`../website-open-bijbelvertaling`): de herziene Statenvertaling.
- **OGW** (`../website-open-gods-woord`): wiki, achtergrond en broninformatie.

Links naar de andere sites lopen altijd via `js/sites.js`
(`KASites.url('ogw', pad)` of `data-ogw-href` / `data-ov-href` in HTML).
Lokaal: OV :8000, OGW :8001, OPV :8002.

## Parafrase bewerken

- Bewerk alleen de werkbron `data/edities/opv/chapters/`; bouw daarna de
  leeseditie met `scripts/opv_leeseditie.py` en controleer met
  `scripts/validate_opv.py`.
- De SV1888-hoofdstukken in `data/{boek}/` zijn de bron en komen uit de OV.
  Wijzig ze hier niet; tekstwijzigingen aan de OV gebeuren in de OV-repo.
- Leg redactionele keuzes vast in `docs/opv/besluitregister.md`.

## Werkstijl

- Een push naar `main` publiceert via `.github/workflows/deploy.yml` op
  `https://open-parafrase-weergave.nl`. Push of publiceer alleen wanneer de
  gebruiker daarvoor opdracht heeft gegeven.
