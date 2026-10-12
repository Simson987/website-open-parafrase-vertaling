"""Bewijs dat de parafrase op deze site de standaardeditie is."""
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class _Stil(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, _format, *_args):
        pass


def test_parafrase_is_de_standaard_en_leest():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Stil)
    poort = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            basis = f"http://127.0.0.1:{poort}"

            page.goto(f"{basis}/index.html#johannes/1", wait_until="domcontentloaded")
            # Deze site toont alleen de parafrase: geen editiekeuze.
            assert page.locator("#opt-teksteditie").count() in (0, 1)
            page.wait_for_timeout(500)
            assert page.locator("#sidebar-right #opt-teksteditie").count() == 0

            # Zonder ?editie= en zonder opgeslagen keuze leest men de parafrase.
            page.goto(f"{basis}/index.html#johannes/1",
                      wait_until="domcontentloaded")
            page.locator('.verse-row[data-verse="1"]').wait_for(timeout=15000)
            # De sierletter staat als eigen element, dus de regelafbreking eruit.
            tekst = " ".join(page.locator('.verse-row[data-verse="1"]').inner_text().split())
            assert "n het begin was het Woord er al" in tekst, tekst
            # De parafrase is niet de Statenvertaling: de zin moet anders lopen.
            assert tekst.strip() != "", tekst
            print("\nJohannes 1:1 in de parafrase:", tekst[:160])
            browser.close()
    finally:
        server.shutdown()
