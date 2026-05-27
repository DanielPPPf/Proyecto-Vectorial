import time
import subprocess
import matplotlib.pyplot as plt

from config import (
    WAZUH_API_URL, WAZUH_USER, WAZUH_PASSWORD,
    NODES, SIGMA, POLL_INTERVAL, ALERT_WINDOW,
    DECAY_LAMBDA, GRID_SIZE, EXTENT, ENTRY_NODE, ENTRY_OFFSET,
)
from wazuh_client import get_token, get_alerts_for_agent, score_from_alerts
from scalar_field import build_scalar_field, compute_gradient, find_critical_points
from gradient_flow import integrate_attacker_path, compute_line_integral
from visualizer import setup_figure, update_plots


def main():
    print("[*] Autenticando con Wazuh...")
    token = get_token(WAZUH_API_URL, WAZUH_USER, WAZUH_PASSWORD)
    print("[+] Token obtenido")

    node_names     = list(NODES.keys())
    node_positions = [NODES[n]["pos"]      for n in node_names]
    node_labels    = [NODES[n]["label"]    for n in node_names]
    agent_ids      = [NODES[n]["agent_id"] for n in node_names]
    base_pos       = NODES[ENTRY_NODE]["pos"]
    entry_pos      = [base_pos[0] + ENTRY_OFFSET[0], base_pos[1] + ENTRY_OFFSET[1]]

    fig, axes, ax_info = setup_figure()
    plt.ion()
    plt.show()

    iteration = 0

    print("[*] Iniciando loop de monitoreo — Ctrl+C para detener\n")

    while True:
        try:
            iteration += 1

            # 1. Renovar token si es necesario y obtener scores
            token = get_token(WAZUH_API_URL, WAZUH_USER, WAZUH_PASSWORD)
            scores = []
            for agent_id in agent_ids:
                alerts = get_alerts_for_agent(
                    WAZUH_API_URL, token, agent_id,
                    last_n_minutes=ALERT_WINDOW,
                )
                s = score_from_alerts(alerts, decay_lambda=DECAY_LAMBDA)
                scores.append(s)

            # 2. Construir V(x,y) y calcular ∇V
            X, Y, V = build_scalar_field(
                node_positions, scores, SIGMA,
                grid_size=GRID_SIZE, extent=EXTENT,
            )
            dVdx, dVdy = compute_gradient(X, Y, V)

            # 3. Integrar trayectoria en dos etapas: entry→B y B→C
            path_ab = integrate_attacker_path(
                X, Y, dVdx, dVdy, entry_pos,
                t_span=(0, 30), n_steps=200,
            )
            # Reiniciar desde el destino de la etapa 1 para ir hacia el siguiente nodo
            pivot = [float(path_ab[0, -1]), float(path_ab[1, -1])]
            path_bc = integrate_attacker_path(
                X, Y, dVdx, dVdy, pivot,
                t_span=(0, 30), n_steps=200,
            )
            import numpy as np
            path = np.concatenate([path_ab, path_bc], axis=1)

            # 4. Integral de línea y puntos críticos
            line_integral     = compute_line_integral(X, Y, V, path)
            critical_points   = find_critical_points(X, Y, dVdx, dVdy)

            # 5. Log en terminal
            print(
                f"[{iteration:04d}] "
                + " | ".join(f"{n}: v={s:.2f}" for n, s in zip(node_names, scores))
                + f" | ∫∇V·dr={line_integral:+.2f}"
                + f" | críticos={len(critical_points)}"
            )

            # 6. Actualizar visualización
            update_plots(
                axes, ax_info, fig,
                X, Y, V, dVdx, dVdy,
                path, node_positions, node_labels, scores,
                line_integral, critical_points,
                iteration,
            )
            plt.pause(0.1)

            # 7. Guardar figura y enviar via scp
            fig_path = f"/tmp/gradient_fig_{iteration:04d}.png"
            fig.savefig(fig_path, dpi=100, bbox_inches="tight",
                        facecolor=fig.get_facecolor())
            subprocess.Popen(
                ["scp", "-o", "StrictHostKeyChecking=no",
                 "-o", "ConnectTimeout=5",
                 fig_path,
                 "daniel@192.168.50.135:/home/daniel/Documents/Vectorial/"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except KeyboardInterrupt:
            print("\n[!] Detenido por el usuario")
            break
        except Exception as e:
            print(f"[!] Error en iteración {iteration}: {e}")

        time.sleep(POLL_INTERVAL)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
