import matplotlib.pyplot as plt
import networkx as nx
from typing import Tuple

def plot_geom_graph_2d(
    G: nx.Graph,
    *,
    ax: plt.Axes | None = None,
    node_size: float = 30,
    node_color: str = "steelblue",
    edge_color: str = "0.70",
    edge_width: float = 0.8,
    with_labels: bool = False,
    **scatter_kwargs,
) -> plt.Axes:
    """
    Visualise a 2-D Euclidean-threshold graph.

    Parameters
    ----------
    G : nx.Graph
        An undirected graph whose nodes are (x, y) coordinate tuples.
    ax : matplotlib Axes, optional
        Re-use an existing Axes; one is created otherwise.
    node_size, node_color : passed to `Axes.scatter`
    edge_color, edge_width : appearance of edge line segments
    with_labels : draw node indices next to each point
    **scatter_kwargs : any extra keyword arguments forwarded to `scatter`.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes the graph is drawn on (useful for further tweaking).
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    # ----- collect coordinates --------------------------------------------
    pos: dict[int, Tuple[float, float]] = {i: node for i, node in enumerate(G.nodes)}
    xs, ys = zip(*pos.values())

    # ----- draw edges ------------------------------------------------------
    for u, v in G.edges:
        x1, y1 = u
        x2, y2 = v
        ax.plot([x1, x2], [y1, y2], edge_color, linewidth=edge_width, zorder=1)

    # ----- draw nodes ------------------------------------------------------
    ax.scatter(xs, ys, s=node_size, c=node_color, zorder=2, **scatter_kwargs)

    # optional labels (small datasets only)
    if with_labels:
        for i, (x, y) in pos.items():
            ax.text(x, y, str(i), fontsize=8, ha="right", va="bottom")

    # ----- prettify --------------------------------------------------------
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title("Euclidean-threshold graph")
    ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.4)

    fig.tight_layout()
    plt.savefig("graph.pdf", dpi=300, bbox_inches="tight")
    return ax