import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import RegularGridInterpolator


def integrate_attacker_path(
    X: np.ndarray,
    Y: np.ndarray,
    dVdx: np.ndarray,
    dVdy: np.ndarray,
    start_pos: list,
    t_span: tuple = (0, 30),
    n_steps: int = 300,
) -> np.ndarray:
    """
    Resuelve la EDO de flujo gradiente:

        dr/dt = ∇V(r(t)),   r(0) = start_pos

    Recibe el gradiente ya computado (dVdx, dVdy) para no recalcular.
    Retorna la trayectoria r(t) como array shape (2, n_steps).
    """
    interp_x = RegularGridInterpolator(
        (Y[:, 0], X[0, :]), dVdx,
        method="linear",
        bounds_error=False,
        fill_value=0.0,
    )
    interp_y = RegularGridInterpolator(
        (Y[:, 0], X[0, :]), dVdy,
        method="linear",
        bounds_error=False,
        fill_value=0.0,
    )

    def flow(t, pos):
        # RegularGridInterpolator espera (y, x)
        p = np.array([[pos[1], pos[0]]])
        return [float(interp_x(p).item()), float(interp_y(p).item())]

    t_eval = np.linspace(*t_span, n_steps)
    sol = solve_ivp(
        flow,
        t_span,
        start_pos,
        t_eval=t_eval,
        method="RK45",
        rtol=1e-4,
        atol=1e-6,
    )
    return sol.y  # shape (2, n_steps)


def compute_line_integral(
    X: np.ndarray,
    Y: np.ndarray,
    V: np.ndarray,
    path: np.ndarray,
) -> float:
    """
    Calcula ∫_C ∇V · dr a lo largo de la trayectoria predicha.

    Por el Teorema Fundamental de Integrales de Línea:
        ∫_C ∇V · dr = V(r(T)) - V(r(0))

    Lo calcula numéricamente para validar el resultado analítico.
    """
    interp_V = RegularGridInterpolator(
        (Y[:, 0], X[0, :]), V,
        method="linear",
        bounds_error=False,
        fill_value=0.0,
    )

    # Valor de V en inicio y fin de la trayectoria
    start = np.array([[path[1, 0],  path[0, 0]]])
    end   = np.array([[path[1, -1], path[0, -1]]])

    v_start = float(interp_V(start).item())
    v_end   = float(interp_V(end).item())

    return v_end - v_start
