import numpy as np


def build_scalar_field(
    node_positions: list,
    scores: list,
    sigma: float,
    grid_size: int = 120,
    extent: tuple = (-1, 9, -2, 6),
) -> tuple:
    """
    Construye V(x,y) como superposición de gaussianas:

        V(x,y) = Σ v_i * exp(-||x - x_i||² / 2σ²)

    Retorna (X, Y, V) — mallas numpy.
    """
    x_min, x_max, y_min, y_max = extent
    xs = np.linspace(x_min, x_max, grid_size)
    ys = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(xs, ys)
    V = np.zeros_like(X)

    for (px, py), v_i in zip(node_positions, scores):
        dist_sq = (X - px) ** 2 + (Y - py) ** 2
        V += v_i * np.exp(-dist_sq / (2 * sigma ** 2))

    return X, Y, V


def compute_gradient(X: np.ndarray, Y: np.ndarray, V: np.ndarray) -> tuple:
    """
    Gradiente numérico de V sobre la malla.
    Retorna (dVdx, dVdy).
    """
    dVdy, dVdx = np.gradient(V, Y[:, 0], X[0, :])
    return dVdx, dVdy


def find_critical_points(
    X: np.ndarray,
    Y: np.ndarray,
    dVdx: np.ndarray,
    dVdy: np.ndarray,
    threshold: float = 0.02,
) -> list:
    """
    Detecta puntos donde |∇V| ≈ 0 (candidatos a máximos/sillas).
    Retorna lista de coordenadas (x, y).
    """
    magnitude = np.sqrt(dVdx ** 2 + dVdy ** 2)
    max_mag = magnitude.max()
    if max_mag == 0:
        return []

    normalized = magnitude / max_mag
    rows, cols = np.where(normalized < threshold)

    # Agrupar puntos cercanos — tomar solo el centro de cada cluster
    points = list(zip(X[rows, cols], Y[rows, cols]))
    if not points:
        return []

    clusters = []
    used = [False] * len(points)
    for i, p in enumerate(points):
        if used[i]:
            continue
        cluster = [p]
        used[i] = True
        for j, q in enumerate(points):
            if not used[j]:
                if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 < 0.5:
                    cluster.append(q)
                    used[j] = True
        cx = sum(c[0] for c in cluster) / len(cluster)
        cy = sum(c[1] for c in cluster) / len(cluster)
        clusters.append((cx, cy))

    return clusters
