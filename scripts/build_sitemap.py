#!/usr/bin/env python3
"""Bouw de sitemap samen met de leespagina's uit dezelfde leeseditie."""
from build_leespaginas import build_site

if __name__ == "__main__":
    result = build_site()
    print("Sitemap en leespagina's gebouwd:", result)
