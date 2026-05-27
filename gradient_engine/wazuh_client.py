import json
import subprocess
from datetime import datetime, timedelta, timezone

# SSH config para el Wazuh manager
SSH_HOST = "165.227.109.227"
SSH_USER = "root"
ALERTS_FILE = "/var/ossec/logs/alerts/alerts.json"


def get_token(url: str, user: str, password: str) -> str:
    """Compatibilidad con main.py — ya no usamos JWT, retorna string vacío."""
    return ""


def get_alerts_for_agent(
    url: str,
    token: str,
    agent_id: str,
    last_n_minutes: int = 10,
) -> list:
    """
    Lee alertas del agente desde /var/ossec/logs/alerts/alerts.json via SSH.
    Filtra por agent.id y por ventana temporal de los últimos last_n_minutes.
    """
    since = datetime.now(timezone.utc) - timedelta(minutes=last_n_minutes)

    try:
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no",
             "-o", "ConnectTimeout=8",
             "-o", "BatchMode=yes",
             f"{SSH_USER}@{SSH_HOST}",
             f"tail -n 5000 {ALERTS_FILE} 2>/dev/null || echo ''"],
            capture_output=True,
            text=True,
            timeout=12,
        )
        lines = result.stdout.strip().splitlines()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    alerts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            alert = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Filtrar por agente
        alert_agent_id = str(alert.get("agent", {}).get("id", "")).zfill(3)
        if alert_agent_id != agent_id.zfill(3):
            continue

        # Filtrar por ventana temporal
        ts_str = alert.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if ts < since:
                continue
        except (ValueError, TypeError):
            continue

        alerts.append({
            "rule": alert.get("rule", {}),
            "timestamp": ts_str,
            "agent": alert.get("agent", {}),
        })

    return alerts


def score_from_alerts(alerts: list, decay_lambda: float = 0.1) -> float:
    """
    Calcula v_i aplicando decaimiento temporal:
        v_i = Σ level_j * exp(-λ * Δt_j)

    Solo cuenta alertas de nivel >= 5 para filtrar ruido de sistema.
    Normalizado a [0, 10] usando escala logarítmica para evitar saturación.
    """
    if not alerts:
        return 0.0

    now = datetime.now(timezone.utc)
    total = 0.0

    for alert in alerts:
        level = alert.get("rule", {}).get("level", 0)
        if level < 5:          # ignorar ruido de nivel bajo (syscollector, heartbeat, etc.)
            continue
        ts_str = alert.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            delta_minutes = (now - ts).total_seconds() / 60
            weight = level * (2.718281828 ** (-decay_lambda * delta_minutes))
            total += weight
        except (ValueError, TypeError):
            total += level

    if total == 0.0:
        return 0.0

    # log1p evita saturación: log1p(x) crece rápido al inicio y se aplana
    import math
    score = math.log1p(total) / math.log1p(50) * 10.0
    return min(score, 10.0)
