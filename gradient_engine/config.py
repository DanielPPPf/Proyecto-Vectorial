WAZUH_API_URL  = "https://165.227.109.227:55000"
WAZUH_USER     = "wazuh-wui"
WAZUH_PASSWORD = "el8pgwMlv49?Nh3A0xvKsaCXEfgFent*"

# Nodos del laboratorio: nombre → {ip, agent_id, pos en R²}
NODES = {
    "wazuh-manager": {
        "ip":       "165.227.109.227",
        "agent_id": "000",
        "pos":      (0.0, 0.0),   # Entry point — Nodo A
        "label":    "A: wazuh-mgr",
    },
    "victim-c": {
        "ip":       "165.227.122.79",
        "agent_id": "003",
        "pos":      (3.0, 3.0),   # Nodo intermedio — Nodo B
        "label":    "B: victim-c",
    },
    "capstone": {
        "ip":       "198.199.71.219",
        "agent_id": "001",
        "pos":      (7.0, 3.0),   # Crown jewel — Nodo C
        "label":    "C: capstone",
    },
}

SIGMA           = 1.5    # radio de influencia gaussiana de cada nodo
POLL_INTERVAL   = 5      # segundos entre actualizaciones
ALERT_WINDOW    = 3      # minutos de alertas a considerar
DECAY_LAMBDA    = 0.1    # decaimiento temporal de alertas antiguas
GRID_SIZE       = 120    # resolución de la malla
EXTENT          = (-1, 9, -2, 6)   # (x_min, x_max, y_min, y_max)
ENTRY_NODE      = "wazuh-manager"  # nodo desde donde parte el atacante
ENTRY_OFFSET    = (0.5, 0.5)      # offset dentro de la red, donde el gradiente apunta hacia los nodos víctima
