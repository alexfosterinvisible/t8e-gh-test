# Short answer: totally doable. Your repo can be turned into a graph and laid out with yFiles’ hierarchical style like the demo you linked. The trick is splitting the job into (1) extract structure, (2) pick node/edge types, (3) feed yFiles either JSON via GraphBuilder or GraphML, (4) tune the layout.
#
# Here’s a crisp plan that works well for Python codebases:
#
# 1. Extract a dependency + call graph
#
# * Imports between modules/packages → use **grimp** to build a precise import graph; it’s actively maintained and just shipped a new release (so: current and fast). You get a queryable graph of module-level edges right away. ([PyPI][1])
# * Function/class call graph → start with **PyCG** (ICSE-evaluated static call graph generator) for better coverage of higher-order functions and class hierarchies; fall back to **pyan3** for quick scans or as a second opinion. Both output GraphViz-friendly edges you can re-map. ([PyPI][2])
#
# 2. Decide what a “node” is (keep it simple first)
#
# * Level 0: packages / modules.
# * Level 1: classes & top-level functions (only for the hotspots).
# * Optional “state” nodes: files or modules that hold global state, config loaders, persistence helpers—flag by heuristics (e.g., frequent reads/writes of JSON/pickle, singletons) and link call sites to them.
#
# 3. Emit data for yFiles
#    Two easy paths, both supported in their current HTML SDK:
#
# * **JSON + GraphBuilder**: produce arrays of `{id, label, group}` nodes and `{source, target, type}` edges; yFiles’ GraphBuilder will ingest JSON and you call `layout = new HierarchicalLayout()` to get the look from the demo. See the GraphBuilder demo and docs. ([yFiles, the diagramming library][3])
# * **GraphML**: emit GraphML (NetworkX/pygraphviz or your own writer); yFiles’ **GraphMLSupport** loads it directly in the browser. Handy if you want to round-trip graphs or style in GraphML. ([yFiles, the diagramming library][4])
#
# 4. Apply the hierarchical layout and tweak it to your taste
#    yFiles’ Hierarchical/Hierarchic layout lets you set orientation, layering, edge routing, and custom layer assignment—useful if you want “entrypoints at the top, leaves at the bottom,” or to pin “state” on one side. All of that is configurable. ([yFiles, the diagramming library][5])
#
# What’s inferable vs. manual?
#
# * Imports: fully inferable with **grimp** (very reliable). ([grimp.readthedocs.io][6])
# * Calls: **PyCG** gets you a strong static approximation, including tricky Python features; you can enrich with your manual “truths” where dynamic dispatch or reflection hides edges. ([PyPI][2])
# * State: semi-inferable (file IO helpers, config modules, caches). Tagging these by heuristic + your manual annotations works well.
#
# A minimal proof-of-concept flow (pseudo-ish):
#
# ```bash
# # 1) Structure
# pip install grimp PyCG networkx

# 2) Imports → edges_import.json
# python -c "
# import grimp, json
# g = grimp.build_graph('your_pkg')
# edges=[{'source':u,'target':v,'type':'imports'} for u,v in g.edges()]
# print(json.dumps(edges))
# " > edges_import.json

# 3) Calls → edges_call.json
# pycg --package your_pkg --max-iter 3 --output callgraph.json
# Convert callgraph.json to [{source,target,type:'calls'}]

# 4) Nodes (modules + hot functions) → nodes.json
# Build from grimp.modules + PyCG symbols

# 5) Feed yFiles (GraphBuilder) and run HierarchicalLayout in the browser
# ```
#
# Why yFiles vs. GraphViz/NetworkX layouts?
#
# * You can absolutely render with GraphViz DOT (`dot` / `sfdp`) via NetworkX wrappers, but you’ll spend more time coaxing hierarchy, routing, and groups. yFiles gives you interactivity, grouping, layering control, and polished routing out of the box—closer to what your demo shows. ([networkx.org][7])
#
# Where you’ll likely want manual overrides (your “control flow relationships”):
#
# * Dynamic plugin registries, reflection, DI/service locators.
# * Meta-programmed decorators that hide real call edges.
# * Cross-cutting “state” access that static tools under-report.
#
# Implementation notes for a satisfying map:
#
# * Use **groups**: group nodes by package or “feature slice”; yFiles’ hierarchic layout handles grouped graphs well. ([yFiles, the diagramming library][5])
# * Add **edge types** and toggle layers: show Imports only, Calls only, or Both; style them differently.
# * Surface **entrypoints**: scripts/CLIs/tests as top layer; pin with custom layer assignment. ([yFiles, the diagramming library][8])
# * Make “state modules” a distinct color/shape so your eyes snap to them.
# * Keep the initial graph sparse: start with module ↔ module imports; then selectively “drill in” to functions for the hottest modules.
#
# Licensing & getting started
#
# * yFiles for HTML is commercial; the **Dev Suite** is the fastest way to bootstrap a local demo project and riff on the hierarchical layout sample. ([yFiles, the diagramming library][9])
#
# If you want, I can sketch the exact JSON schema for GraphBuilder, plus a tiny script to merge **grimp** and **PyCG** output into that schema so you can drop it straight into the yFiles demo scaffold and hit run.
#
# [1]: https://pypi.org/project/grimp/?utm_source=chatgpt.com "grimp · PyPI"
# [2]: https://pypi.org/project/PyCG/?utm_source=chatgpt.com "PyCG · PyPI"
# [3]: https://www.yfiles.com/demos/databinding/graphbuilder/?utm_source=chatgpt.com "Graph Builder Demo [yFiles for HTML]"
# [4]: https://docs.yworks.com/yfiles-html/api/GraphMLSupport.html?utm_source=chatgpt.com "GraphMLSupport Class | yFiles for HTML Documentation"
# [5]: https://docs.yworks.com/yfiles-html/dguide/layout/hierarchical_layout.html?utm_source=chatgpt.com "Hierarchical Layout | Automatic Graph Layout | yFiles for HTML ..."
# [6]: https://grimp.readthedocs.io/en/stable/readme.html?utm_source=chatgpt.com "Grimp — Grimp 3.12 documentation - Read the Docs"
# [7]: https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pydot.graphviz_layout.html?utm_source=chatgpt.com "graphviz_layout — NetworkX 3.5 documentation"
# [8]: https://www.yfiles.com/the-yfiles-sdk/features/automatic-layouts/hierarchical-layout-coding?utm_source=chatgpt.com "Coding: Hierarchical Layout - yfiles.com"
# [9]: https://www.yfiles.com/the-yfiles-sdk/web/yfiles-for-html/getting-started?utm_source=chatgpt.com "Getting started with yFiles for HTML"
