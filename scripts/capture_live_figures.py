#!/usr/bin/env python3
"""Capture high-resolution screenshots of the live taxonomy site for the report.

Figure 1 = released taxonomy interface (header, navigation, and the classification
overview panel). Figure 5 = an example expanded L4 risk card. Uses the installed
Google Chrome via Playwright at device_scale_factor=2 for crisp output.
"""
from playwright.sync_api import sync_playwright

FIG = "/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/figures"
URL = "https://deep1003.github.io/Physical-AI-Risk-Taxonomy/"

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)

    # --- Figure 1: interface + classification overview ---
    pg = b.new_page(viewport={"width": 1400, "height": 2200}, device_scale_factor=2)
    pg.goto(URL, wait_until="load", timeout=60000)
    pg.wait_for_timeout(2800)
    bottom = 1250
    el = pg.query_selector("#summary-tbody")
    if el:
        box = el.bounding_box()
        if box:
            bottom = int(box["y"] + box["height"])
    pg.screenshot(path=FIG + "/_shot_fig1.png",
                  clip={"x": 0, "y": 0, "width": 1400, "height": bottom + 24})
    print("fig1 saved, overview bottom =", bottom)
    pg.close()

    # --- Figure 5: one expanded L4 card ---
    pg2 = b.new_page(viewport={"width": 860, "height": 1300}, device_scale_factor=2)
    pg2.goto(URL, wait_until="load", timeout=60000)
    pg2.wait_for_timeout(2500)
    pg2.wait_for_selector(".l3-header", timeout=15000)
    hdr = pg2.locator(".l3-header").first
    hdr.scroll_into_view_if_needed()
    hdr.click()
    pg2.wait_for_timeout(900)
    card = pg2.locator(".cards-grid .card").first
    card.scroll_into_view_if_needed()
    pg2.wait_for_timeout(400)
    card.screenshot(path=FIG + "/_shot_fig5.png")
    print("fig5 saved")
    pg2.close()
    b.close()
print("DONE")
