"""Inject a visible fallback INSIDE the plotly graph div.

Verified in a browser with cdn.plot.ly blocked: without this the div renders 0 children
and the reader gets a 640px blank box under a caption describing content that is not there.

Plotly APPENDS its chart rather than replacing the div's contents -- a first version of
this shipped the fallback text alongside a working chart, caught by testing the CDN-OK
case as well as the CDN-blocked one. Plotly stamps `js-plotly-plot` onto the container
on successful render (confirmed in-browser), so that class is the hide signal.
"""
import re

CSS = (
    "<style>.plotly-fallback{font:14px/1.5 system-ui,-apple-system,sans-serif;color:#7a7a7a;"
    "padding:1.1rem 1.2rem;margin:0;border:1px dashed rgba(122,122,122,.45);border-radius:8px;"
    "max-width:46rem}.js-plotly-plot>.plotly-fallback{display:none!important}</style>"
)

def inject(path, text):
    s = open(path, encoding="utf-8").read()
    m = re.search(r'(<div id="[0-9a-f-]+" class="plotly-graph-div"[^>]*>)(</div>)', s)
    if not m:
        raise SystemExit(f"FAIL: graph div not found in {path} -- fallback NOT injected")
    if "</head>" not in s:
        raise SystemExit(f"FAIL: no <head> in {path} -- stylesheet NOT injected")
    s = s.replace("</head>", CSS + "</head>", 1)
    m = re.search(r'(<div id="[0-9a-f-]+" class="plotly-graph-div"[^>]*>)(</div>)', s)
    fb = '<p class="plotly-fallback">' + text + "</p>"
    s = s[: m.end(1)] + fb + s[m.end(1):]
    open(path, "w", encoding="utf-8").write(s)
