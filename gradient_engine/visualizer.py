import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


def setup_figure():
    fig = plt.figure(figsize=(18, 6))
    fig.patch.set_facecolor("#0d1117")
    gs = gridspec.GridSpec(1, 4, figure=fig, width_ratios=[3, 3, 3, 1])

    axes = [fig.add_subplot(gs[i]) for i in range(3)]
    ax_info = fig.add_subplot(gs[3])

    for ax in axes:
        ax.set_facecolor("#0d1117")

    ax_info.set_facecolor("#0d1117")
    ax_info.axis("off")

    fig.suptitle(
        "Motor de Gradiente — Movimiento Lateral en Tiempo Real",
        color="white", fontsize=13, y=1.01
    )
    return fig, axes, ax_info


def update_plots(
    axes, ax_info, fig,
    X, Y, V,
    dVdx, dVdy,
    path,
    node_positions, node_labels, scores,
    line_integral, critical_points,
    iteration,
):
    for ax in axes:
        ax.cla()
        ax.set_facecolor("#0d1117")
    ax_info.cla()
    ax_info.set_facecolor("#0d1117")
    ax_info.axis("off")

    cmap = "YlOrRd"
    norm = Normalize(vmin=V.min(), vmax=max(V.max(), 0.01))

    # ── Panel 1: Heatmap V(x,y) ──────────────────────────────────────
    cf = axes[0].contourf(X, Y, V, levels=40, cmap=cmap, norm=norm)
    axes[0].contour(X, Y, V, levels=10, colors="white", alpha=0.15, linewidths=0.5)
    axes[0].set_title("Campo escalar $V(\\mathbf{x})$", color="white", fontsize=10)

    # ── Panel 2: Campo vectorial ∇V ──────────────────────────────────
    skip = 8
    axes[1].contourf(X, Y, V, levels=30, cmap=cmap, norm=norm, alpha=0.4)
    gx = dVdx[::skip, ::skip]
    gy = dVdy[::skip, ::skip]
    mag = np.sqrt(gx**2 + gy**2).max()
    if mag > 1e-9:
        axes[1].quiver(
            X[::skip, ::skip], Y[::skip, ::skip],
            gx, gy,
            color="cyan", alpha=0.8, scale=mag * 10, width=0.004,
        )
    else:
        axes[1].text(0.5, 0.5, "∇V ≈ 0\n(sin alertas activas)",
                     transform=axes[1].transAxes, color="cyan",
                     ha="center", va="center", fontsize=9)
    axes[1].set_title("Gradiente $\\nabla V$", color="white", fontsize=10)

    # ── Panel 3: Trayectoria r(t) ─────────────────────────────────────
    axes[2].contourf(X, Y, V, levels=30, cmap=cmap, norm=norm, alpha=0.5)
    if path is not None and path.shape[1] > 1:
        mid = path.shape[1] // 2
        # Etapa A→B
        axes[2].plot(
            path[0, :mid], path[1, :mid],
            color="dodgerblue", linewidth=2.5,
            label="$\\mathbf{r}(t)$ A→B", zorder=5,
        )
        # Etapa B→C
        axes[2].plot(
            path[0, mid:], path[1, mid:],
            color="orange", linewidth=2.5, linestyle="--",
            label="$\\mathbf{r}(t)$ B→C", zorder=5,
        )
        axes[2].plot(path[0, 0],   path[1, 0],   "go", markersize=10,
                     label="Entrada", zorder=6)
        axes[2].plot(path[0, mid], path[1, mid], "y^", markersize=12,
                     label="Pivote B", zorder=6)
        axes[2].plot(path[0, -1],  path[1, -1],  "r*", markersize=14,
                     label="Destino C", zorder=6)

    # Puntos críticos
    for (cx, cy) in critical_points:
        for ax in axes:
            ax.plot(cx, cy, "w^", markersize=7, alpha=0.7, zorder=7)

    # Nodos en los 3 paneles
    colors_nodes = ["#00ff88", "#ffaa00", "#ff4444"]
    for ax in axes:
        for (px, py), label, score, color in zip(
            node_positions, node_labels, scores, colors_nodes
        ):
            ax.plot(px, py, "s", color=color, markersize=10, zorder=8)
            ax.annotate(
                f"{label}\nv={score:.1f}",
                (px, py),
                textcoords="offset points", xytext=(6, 6),
                fontsize=7, color=color,
            )
        ax.tick_params(colors="gray")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333")

    axes[2].legend(fontsize=7, facecolor="#1a1a2e", labelcolor="white",
                   loc="upper left")
    axes[2].set_title("Trayectoria $\\mathbf{r}(t)$", color="white", fontsize=10)

    # ── Panel 4: Info numérica ────────────────────────────────────────
    info_lines = [
        ("Iteración",      f"{iteration}"),
        ("", ""),
        ("Integral de línea", ""),
        ("∫∇V·dr",         f"{line_integral:+.2f}"),
        ("", ""),
        ("Puntos críticos", f"{len(critical_points)}"),
        ("", ""),
        ("Scores actuales", ""),
    ]
    for label, score, color in zip(node_labels, scores, colors_nodes):
        info_lines.append((label, f"{score:.2f}"))

    info_lines += [
        ("", ""),
        ("Max V",  f"{V.max():.2f}"),
        ("Min V",  f"{V.min():.2f}"),
    ]

    y_pos = 0.97
    for key, val in info_lines:
        if key == "":
            y_pos -= 0.025
            continue
        color = "white" if val else "#888888"
        ax_info.text(0.05, y_pos, key, transform=ax_info.transAxes,
                     fontsize=8, color="#888888", va="top")
        if val:
            ax_info.text(0.95, y_pos, val, transform=ax_info.transAxes,
                         fontsize=8, color=color, va="top", ha="right")
        y_pos -= 0.06

    plt.tight_layout()
