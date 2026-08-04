"""Long-tail figure: specimen images retained per Lobelia species.

Form choice: DOT PLOT, not a bar chart. The data spans three orders of magnitude
(811 -> 1), so the axis has to be log; but bar length encodes value from a zero
baseline and a log axis has no zero, which would make bar length arbitrary.
A dot encodes value by POSITION, which is legitimate on a log axis.

Colour: #2e7d32 validated with the dataviz skill's validator against BOTH the light
(#fcfcfb) and dark (#1a1a19) surfaces - chroma floor, lightness band and >=3:1
contrast all pass on each. Axis ink #7a7a7a is 4.18:1 on light, 4.06:1 on dark.
"""

import os
import sys

import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fallback_util import inject
from _paths import fig as fig_path  # noqa: E402

# From the project's own GBIFDataaquisitionMASTER.xlsx ledger (20 complete species tabs).
ROWS = [
    ("cardinalis", 899, 811),
    ("spicata", 484, 468),
    ("kalmii", 334, 315),
    ("glandulosa", 230, 230),
    ("puberula", 211, 206),
    ("paludosa", 129, 127),
    ("feayana", 123, 122),
    ("nuttallii", 116, 115),
    ("dortmanna", 151, 111),
    ("homophylla", 51, 51),
    ("appendiculata", 44, 44),
    ("elongata", 26, 26),
    ("floridana", 24, 23),
    ("brevifolia", 23, 23),
    ("georgiana", 20, 20),
    ("canbyi", 18, 18),
    ("flaccidifolia", 11, 11),
    ("rogersii", 9, 9),
    ("gattingeri", 2, 2),
    ("apalachicolensis", 1, 1),
]
ROWS.sort(key=lambda r: r[2])  # ascending -> largest lands at the top

DOT = "#2e7d32"
INK = "#7a7a7a"
GRID = "rgba(122,122,122,0.30)"

species = [f"<i>L. {r[0]}</i>" for r in ROWS]
screened = [r[1] for r in ROWS]
retained = [r[2] for r in ROWS]
kept_pct = [100.0 * r[2] / r[1] for r in ROWS]

fig = go.Figure()

# Leader lines are a reading aid across 20 rows, drawn in the recessive grid colour
# so they never read as magnitude.
for sp, ret in zip(species, retained):
    fig.add_shape(
        type="line",
        x0=0.86,
        x1=ret,
        y0=sp,
        y1=sp,
        line=dict(color=GRID, width=1),
        layer="below",
    )

fig.add_trace(
    go.Scatter(
        x=retained,
        y=species,
        mode="markers",
        marker=dict(
            color=DOT, size=11, line=dict(color="rgba(252,252,251,0.85)", width=1.5)
        ),
        customdata=list(zip(screened, kept_pct)),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "retained images <b>%{x}</b><br>"
            "occurrence records screened %{customdata[0]}<br>"
            "kept %{customdata[1]:.0f}%<extra></extra>"
        ),
        name="",
    )
)

fig.update_layout(
    height=560,
    margin=dict(l=8, r=30, t=12, b=54),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=INK, size=13),
    showlegend=False,  # single series - the axis title names it
    xaxis=dict(
        type="log",
        range=[-0.09, 3.05],
        title=dict(text="specimen images retained (log scale)", font=dict(size=12)),
        gridcolor=GRID,
        zeroline=False,
        showline=False,
        tickvals=[1, 3, 10, 30, 100, 300, 1000],
        ticktext=["1", "3", "10", "30", "100", "300", "1000"],
        tickfont=dict(color=INK),
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont=dict(color=INK, size=12),
    ),
    hoverlabel=dict(
        bgcolor=DOT, font=dict(color="#ffffff", size=12), bordercolor="rgba(0,0,0,0)"
    ),
)

out = fig_path("lobelia_species_counts.html")
fig.write_html(
    out,
    include_plotlyjs="cdn",
    full_html=True,
    config={"displayModeBar": False, "responsive": True},
)
# Without this the reader gets a blank 580px box when cdn.plot.ly is unreachable.
# It carries the numbers because the 20-row table that used to back this chart up
# was removed as a duplicate -- there is no longer a fallback elsewhere on the page.
inject(
    out,
    "Specimen images retained per species, after de-duplication: "
    "<b>811</b> for <i>L. cardinalis</i> down to a single usable sheet for "
    "<i>L. apalachicolensis</i> &mdash; three orders of magnitude across "
    "<b>20</b> species, from <b>2,906</b> occurrence records screened to "
    "<b>2,733</b> images retained. This chart needs JavaScript and the Plotly library.",
)

print("wrote", out, os.path.getsize(out), "bytes")
print("species:", len(ROWS), "| max", max(retained), "| min", min(retained))
