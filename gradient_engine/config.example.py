"""
Copia este archivo como config.py y completa los valores para tu entorno.
  cp config.example.py config.py
"""

# ── Wazuh Manager ────────────────────────────────────────────────────────────
# Si usas Docker local: "localhost" o "127.0.0.1"
WAZUH_API_URL  = "https://<MANAGER_IP>:55000"
WAZUH_USER     = "wazuh-wui"
WAZUH_PASSWORD = "<WAZUH_API_PASSWORD>"

# ── Nodos de la red (nombre → metadatos) ────────────────────────────────────
# pos: coordenadas lógicas en R² (no físicas)
# agent_id: ID del agente Wazuh con zero-padding ("000", "001", "003")
NODES = {
    "wazuh-manager": {
        "ip":       "<MANAGER_IP>",
        "agent_id": "000",
        "pos":      (0.0, 0.0),
        "label":    "A: wazuh-mgr",
    },
    "victim-c": {
        "ip":       "<VICTIM_C_IP>",
        "agent_id": "003",
        "pos":      (3.0, 3.0),
        "label":    "B: victim-c",
    },
    "capstone": {
        "ip":       "<CAPSTONE_IP>",
        "agent_id": "001",
        "pos":      (7.0, 3.0),
        "label":    "C: capstone",
    },
}

# ── Parámetros del motor ─────────────────────────────────────────────────────
SIGMA           = 1.5    # radio de influencia gaussiana (unidades lógicas)
POLL_INTERVAL   = 5      # segundos entre actualizaciones del campo
ALERT_WINDOW    = 3      # minutos de alertas a considerar
DECAY_LAMBDA    = 0.1    # tasa de decaimiento temporal de alertas antiguas
GRID_SIZE       = 120    # resolución de la malla (GRID_SIZE × GRID_SIZE)
EXTENT          = (-1, 9, -2, 6)   # dominio espacial (x_min, x_max, y_min, y_max)
ENTRY_NODE      = "wazuh-manager"  # nodo de entrada del atacante
ENTRY_OFFSET    = (0.5, 0.5)       # desplazamiento desde el centro del nodo de entrada
