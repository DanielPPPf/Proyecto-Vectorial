# Laboratorio: Modelo de Gradiente en Tiempo Real
**Proyecto:** Movimiento lateral de un atacante como flujo gradiente  
**Componente:** Implementación funcional con Wazuh + Python

---

## Arquitectura general

```
[Kali Linux - Atacante]
        ↓ movimiento lateral (SSH, SMB, Pass-the-Hash, etc.)
[Nodos víctima - VMs con Wazuh Agent]
        ↓ logs y alertas
[Wazuh Manager]
        ↓ REST API
[Python - Motor de gradiente]
        ↓
[Visualización en tiempo real]
  heatmap de V(x) + campo ∇V + trayectoria r(t)
```

---

## Infraestructura del laboratorio

### VMs requeridas

| VM | Rol | OS sugerido |
|----|-----|-------------|
| Wazuh Manager | SIEM central | Ubuntu 22.04 |
| Nodo 1 — Entry point | Acceso inicial del atacante | Ubuntu / Windows 10 |
| Nodo 2 — Workstation | Movimiento lateral intermedio | Windows 10 |
| Nodo 3 — Server | Activo de alto valor (crown jewel) | Ubuntu Server |
| Kali Linux | Atacante | Kali rolling |

> Mínimo viable: **4 VMs** en VirtualBox o VMware con red interna aislada.

### Red interna sugerida

```
Red: 192.168.100.0/24

Wazuh Manager   → 192.168.100.10
Nodo 1 (entry)  → 192.168.100.20
Nodo 2 (ws)     → 192.168.100.30
Nodo 3 (server) → 192.168.100.40
Kali            → 192.168.100.99
```

---

## Wazuh como fuente de datos del modelo

### Cómo alimenta el campo escalar V(x)

Cada agente Wazuh genera alertas con nivel de severidad (escala 1–15). Ese nivel se mapea directamente al score de vulnerabilidad $v_i$ de cada nodo:

```python
def score_from_alerts(alerts: list, max_score: float = 150.0) -> float:
    """
    Suma los niveles de alerta del nodo y normaliza a [0, 10].
    """
    total = sum(alert["rule"]["level"] for alert in alerts)
    return min(total / max_score * 10, 10.0)
```

A medida que el atacante se mueve:
- Los nodos comprometidos generan más alertas
- $v_i$ aumenta en esos nodos
- $V(\mathbf{x})$ se deforma dinámicamente
- $\nabla V$ apunta hacia el siguiente objetivo predicho

### Reglas de Wazuh relevantes para movimiento lateral

| Técnica | OS | Event IDs / logs |
|--------|-----|-----------------|
| Logon remoto | Windows | 4624, 4648 |
| Uso de credenciales especiales | Windows | 4672 |
| PSExec / WMI | Windows | 7045, 4688 |
| SSH lateral | Linux | `auth.log` — `Accepted password/publickey` |
| Pass-the-Hash | Windows | 4624 tipo 3 + NTLM |
| RDP | Windows | 4624 tipo 10 |

---

## Técnicas de movimiento lateral a simular

### Linux → Linux
```bash
# SSH hopping desde Kali
ssh user@192.168.100.20
ssh user@192.168.100.30  # desde nodo 1
```

### Windows (con impacket)
```bash
# Pass-the-Hash
python3 psexec.py -hashes :NTLMHASH administrator@192.168.100.30

# WMI lateral movement
python3 wmiexec.py administrator:password@192.168.100.30
```

### Con crackmapexec
```bash
crackmapexec smb 192.168.100.0/24 -u administrator -H NTLMHASH --local-auth
```

---

## Motor Python del gradiente

### Estructura del proyecto

```
gradient_engine/
├── main.py              # loop principal
├── wazuh_client.py      # polling de la API de Wazuh
├── scalar_field.py      # construcción de V(x) y ∇V
├── gradient_flow.py     # integración de dr/dt = ∇V
├── visualizer.py        # visualización en tiempo real
└── config.py            # IPs, credenciales, parámetros
```

### config.py

```python
WAZUH_API_URL  = "https://192.168.100.10:55000"
WAZUH_USER     = "wazuh-wui"
WAZUH_PASSWORD = "your_password"

NODES = {
    "entry_point": {"ip": "192.168.100.20", "pos": (1.0, 2.0)},
    "workstation":  {"ip": "192.168.100.30", "pos": (3.0, 2.0)},
    "server":       {"ip": "192.168.100.40", "pos": "5.0, 2.0)"},
}

SIGMA          = 1.0   # radio de influencia de cada nodo en el campo
POLL_INTERVAL  = 5     # segundos entre actualizaciones
```

### wazuh_client.py

```python
import requests, urllib3
urllib3.disable_warnings()

def get_token(url, user, password):
    r = requests.post(f"{url}/security/user/authenticate",
                      auth=(user, password), verify=False)
    return r.json()["data"]["token"]

def get_alerts_per_agent(url, token, agent_id, last_n_minutes=5):
    headers = {"Authorization": f"Bearer {token}"}
    params  = {
        "agent_ids": agent_id,
        "limit": 500,
        "sort": "-timestamp",
    }
    r = requests.get(f"{url}/alerts", headers=headers,
                     params=params, verify=False)
    return r.json().get("data", {}).get("affected_items", [])
```

### scalar_field.py

```python
import numpy as np

def build_scalar_field(node_positions: list[tuple],
                       scores: list[float],
                       sigma: float,
                       grid_size: int = 100,
                       extent: tuple = (0, 6, 0, 4)):
    """
    Construye V(x) como superposición de gaussianas centradas en cada nodo.
    Retorna la malla X, Y y la matriz V.
    """
    x_min, x_max, y_min, y_max = extent
    xs = np.linspace(x_min, x_max, grid_size)
    ys = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(xs, ys)
    V = np.zeros_like(X)

    for (px, py), v_i in zip(node_positions, scores):
        dist_sq = (X - px)**2 + (Y - py)**2
        V += v_i * np.exp(-dist_sq / (2 * sigma**2))

    return X, Y, V

def compute_gradient(V, X, Y):
    """Gradiente numérico de V sobre la malla."""
    dVdy, dVdx = np.gradient(V,
                              Y[:, 0],
                              X[0, :])
    return dVdx, dVdy
```

### gradient_flow.py

```python
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import RegularGridInterpolator

def integrate_attacker_path(X, Y, V, start_pos, t_span=(0, 20), n_steps=200):
    """
    Resuelve dr/dt = ∇V(r(t)) con condición inicial start_pos.
    Retorna la trayectoria r(t) como array de puntos.
    """
    dVdy, dVdx = np.gradient(V, Y[:, 0], X[0, :])

    interp_x = RegularGridInterpolator((Y[:, 0], X[0, :]), dVdx,
                                        bounds_error=False, fill_value=0)
    interp_y = RegularGridInterpolator((Y[:, 0], X[0, :]), dVdy,
                                        bounds_error=False, fill_value=0)

    def flow(t, pos):
        p = np.array([[pos[1], pos[0]]])  # (y, x) para el interpolador
        return [float(interp_x(p)), float(interp_y(p))]

    t_eval = np.linspace(*t_span, n_steps)
    sol = solve_ivp(flow, t_span, start_pos, t_eval=t_eval, method="RK45")
    return sol.y  # shape (2, n_steps)
```

### visualizer.py

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def setup_figure():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Modelo de Gradiente — Movimiento Lateral en Tiempo Real")
    axes[0].set_title("Campo escalar V(x)")
    axes[1].set_title("Gradiente ∇V")
    axes[2].set_title("Trayectoria del atacante r(t)")
    return fig, axes

def update_plots(axes, X, Y, V, dVdx, dVdy, path, node_positions, scores):
    for ax in axes:
        ax.cla()

    # Panel 1: heatmap de V
    axes[0].contourf(X, Y, V, levels=30, cmap="YlOrRd")
    axes[0].set_title("Campo escalar $V(\\mathbf{x})$")

    # Panel 2: campo vectorial ∇V
    skip = 5
    axes[1].quiver(X[::skip, ::skip], Y[::skip, ::skip],
                   dVdx[::skip, ::skip], dVdy[::skip, ::skip],
                   alpha=0.7)
    axes[1].contourf(X, Y, V, levels=15, cmap="YlOrRd", alpha=0.3)
    axes[1].set_title("Gradiente $\\nabla V$")

    # Panel 3: trayectoria
    axes[2].contourf(X, Y, V, levels=15, cmap="YlOrRd", alpha=0.5)
    if path is not None:
        axes[2].plot(path[0], path[1], "b-", linewidth=2, label="$\\mathbf{r}(t)$ predicho")
        axes[2].plot(path[0][0], path[1][0], "go", markersize=8, label="Entrada")
        axes[2].plot(path[0][-1], path[1][-1], "r*", markersize=12, label="Destino")

    # Nodos
    for ax in axes:
        for (px, py), s in zip(node_positions, scores):
            ax.plot(px, py, "ks", markersize=8)
            ax.annotate(f"v={s:.1f}", (px, py),
                        textcoords="offset points", xytext=(5, 5), fontsize=7)

    axes[2].legend(fontsize=7)
    plt.tight_layout()
```

### main.py

```python
import time
import matplotlib.pyplot as plt
from config import WAZUH_API_URL, WAZUH_USER, WAZUH_PASSWORD, NODES, SIGMA, POLL_INTERVAL
from wazuh_client import get_token, get_alerts_per_agent
from scalar_field import build_scalar_field, compute_gradient
from gradient_flow import integrate_attacker_path
from visualizer import setup_figure, update_plots

def main():
    token = get_token(WAZUH_API_URL, WAZUH_USER, WAZUH_PASSWORD)
    node_names = list(NODES.keys())
    node_positions = [NODES[n]["pos"] for n in node_names]
    entry_pos = list(NODES["entry_point"]["pos"])

    fig, axes = setup_figure()
    plt.ion()
    plt.show()

    while True:
        # 1. Obtener scores desde Wazuh
        scores = []
        for name in node_names:
            agent_id = NODES[name].get("agent_id", "000")
            alerts = get_alerts_per_agent(WAZUH_API_URL, token, agent_id)
            scores.append(score_from_alerts(alerts))

        # 2. Construir campo escalar y gradiente
        X, Y, V = build_scalar_field(node_positions, scores, SIGMA)
        dVdx, dVdy = compute_gradient(V, X, Y)

        # 3. Integrar trayectoria del atacante
        path = integrate_attacker_path(X, Y, V, entry_pos)

        # 4. Actualizar visualización
        update_plots(axes, X, Y, V, dVdx, dVdy, path, node_positions, scores)
        plt.pause(0.1)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
```

---

## Visualización esperada

Tres paneles actualizándose cada 5 segundos:

| Panel | Contenido | Qué demuestra |
|-------|-----------|---------------|
| Heatmap $V(\mathbf{x})$ | Zonas rojas = alta vulnerabilidad | El campo escalar evoluciona con el ataque |
| Quiver $\nabla V$ | Flechas apuntando hacia zonas de riesgo | Dirección predicha del movimiento lateral |
| Trayectoria $\mathbf{r}(t)$ | Curva azul sobre el mapa de calor | Camino óptimo predicho por el modelo |

---

## Lo que el laboratorio valida matemáticamente

| Pregunta matemática | Cómo se verifica en el lab |
|--------------------|---------------------------|
| ¿Sigue el atacante $\nabla V$? | Comparar trayectoria real (logs) vs. $\mathbf{r}(t)$ predicho |
| ¿Es $\nabla V$ conservativo? | Calcular $\oint_C \nabla V \cdot d\mathbf{r}$ en dos rutas distintas al mismo nodo |
| ¿Coinciden los puntos críticos con el crown jewel? | El máximo de $V$ debe coincidir con el nodo de mayor valor |

---

## Plan de construcción

| Fase | Tarea | Estado |
|------|-------|--------|
| 1 | Montar VMs y red interna | Pendiente |
| 2 | Instalar Wazuh Manager y agentes | Pendiente |
| 3 | Verificar recepción de alertas por nodo | Pendiente |
| 4 | Script básico: leer API → construir $V$ | Pendiente |
| 5 | Simular ataque manual y verificar que $V$ cambia | Pendiente |
| 6 | Agregar visualización del gradiente y trayectoria | Pendiente |
| 7 | Experimento completo + captura de resultados | Pendiente |
| 8 | Documentar para informe y bitácora de IA | Pendiente |

---

## Dependencias Python

```
numpy
scipy
matplotlib
requests
urllib3
```

Instalación:
```bash
pip install numpy scipy matplotlib requests urllib3
```
