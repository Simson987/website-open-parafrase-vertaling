"""Zinsregels behouden tekst, citaatopmaak en verwijzingen."""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def test_zinnen_krijgen_regels_met_behoud_van_inline_opmaak():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.add_script_tag(path=str(ROOT / "js/chapter-renderer.js"))
        result = page.evaluate("""() => {
            const html = 'Hij zei: <span class="god-speaks"><i>Kom kijken. '
                + 'Blijf bij mij!</i></span> Daarna gingen ze naar '
                + '<a href="#bethanie">Bethanië</a>.';
            const el = document.createElement('div');
            el.innerHTML = ChapterRenderer._opvZinsregels(html);
            return {
                text: el.textContent,
                breaks: el.querySelectorAll('br').length,
                speech: el.querySelector('.god-speaks i').textContent,
                href: el.querySelector('a').getAttribute('href'),
                unfinished: ChapterRenderer._opvZinsregels('Hij ging naar'),
                decimal: ChapterRenderer._opvZinsregels('Het was 3.5 meter. Toen stopte hij.'),
            };
        }""")
        assert result["text"] == "Hij zei: Kom kijken. Blijf bij mij! Daarna gingen ze naar Bethanië."
        assert result["breaks"] == 3
        assert result["speech"] == "Kom kijken. Blijf bij mij!"
        assert result["href"] == "#bethanie"
        assert "<br" not in result["unfinished"]
        assert result["decimal"].count("<br") == 2
        browser.close()
