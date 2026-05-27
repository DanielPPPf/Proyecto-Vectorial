# Motor de Gradiente — Modelado de Movimiento Lateral

Proyecto final de Cálculo Vectorial — Universidad de La Sabana

Modela la trayectoria de un atacante dentro de una red como flujo gradiente de un
campo escalar de vulnerabilidad V(x,y), construido en tiempo real a partir de
alertas del SIEM Wazuh.

```
r'(t) = ∇V(r(t)),   r(0) = punto de entrada
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│  Infraestructura (Docker / VMs)                     │
│                                                     │
│  ┌──────────────┐    alertas     ┌───────────────┐  │
│  │ victim-c (B) │ ─────────────► │               │  │
│  └──────────────┘                │ wazuh-manager │  │
│                                  │  (Nodo A)     │  │
│  ┌──────────────┐    alertas     │               │  │
│  │ capstone (C) │ ─────────────► │               │  │
│  └──────────────┘                └───────┬───────┘  │
└────────────────────────────────────────  │  ────────┘
                                           │ SSH (lee alerts.json)
                              ┌────────────▼────────────┐
                              │    gradient_engine/     │
                              │                         │
                              │  wazuh_client.py  →     │
                              │  scalar_field.py  →     │
                              │  gradient_flow.py →     │
                              │  visualizer.py          │
                              └─────────────────────────┘
```

**Nodos en el espacio lógico R²:**

| Nodo | Coordenadas | Rol |
|------|-------------|-----|
| A: wazuh-manager | (0, 0) | Punto de entrada del atacante |
| B: victim-c      | (3, 3) | Nodo intermedio |
| C: capstone      | (7, 3) | Crown jewel |

---

## Requisitos

- Docker Engine 24+ y Docker Compose v2
- Python 3.10+
- `sshpass` (para `attack_sim.py`)
- Acceso SSH al manager como root (para lectura de `alerts.json`)

---

## Replicar el laboratorio

### 1. Clonar el repositorio

```bash
git clone git@github.com:DanielPPPf/Proyecto-Vectorial.git
cd Proyecto-Vectorial
```

### 2. Levantar la infraestructura con Docker

```bash
cd infra
cp .env.example .env          # editar contraseñas si se desea
```

El stack de Wazuh requiere certificados SSL antes del primer arranque.
Usar el generador oficial:

```bash
# Descargar herramienta de certificados de Wazuh
curl -sO https://packages.wazuh.com/4.7/wazuh-certs-tool.sh
curl -sO https://packages.wazuh.com/4.7/config.yml

# Editar config.yml con los nombres de los servicios:
# nodes.indexer[0].name:   wazuh.indexer
# nodes.server[0].name:    wazuh.manager
# nodes.dashboard[0].name: wazuh.dashboard

bash wazuh-certs-tool.sh -A
mkdir -p certs
tar -xf ./wazuh-certificates.tar -C certs/ --strip-components=1
```

Levantar el stack:

```bash
docker compose up -d
```

Verificar que los tres servicios están en pie:

```bash
docker compose ps
# wazuh-indexer    → healthy
# wazuh-manager    → running
# wazuh-dashboard  → running
```

Los agentes (victim-c y capstone) se registran automáticamente al iniciar.
Verificar en el dashboard: `https://localhost` → Agents.

### 3. Habilitar SSH al manager (para el motor)

El motor lee `alerts.json` vía SSH. En el manager, habilitar acceso root:

```bash
docker exec -it wazuh-manager bash
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
service ssh start   # si no está corriendo
passwd root         # establecer contraseña
```

O preferiblemente, copiar la clave pública:

```bash
ssh-copy-id -p 2222 root@localhost
```

### 4. Configurar el motor de gradiente

```bash
cd gradient_engine
cp config.example.py config.py
```

Editar `config.py` con:
- `WAZUH_API_URL`: IP del manager (o `https://localhost:55000` en Docker)
- IPs y `agent_id` de cada nodo según el dashboard de Wazuh

Instalar dependencias:

```bash
pip install -r requirements.txt
```

### 5. Generar alertas con el simulador

En una terminal separada:

```bash
# Editar attack_sim.py: ajustar VICTIM_C y CAPSTONE con las IPs de los contenedores
docker inspect victim-c | grep IPAddress
docker inspect capstone | grep IPAddress

python attack_sim.py
```

El simulador genera intentos de autenticación SSH fallidos contra los nodos,
que Wazuh captura como Rule 5710 (level 5: "SSH Authentication Failed").

### 6. Ejecutar el motor

```bash
cd gradient_engine
python main.py
```

El motor abre una ventana matplotlib con 4 paneles actualizados cada 5 segundos:
- **Panel 1**: Heatmap de V(x,y)
- **Panel 2**: Campo vectorial ∇V
- **Panel 3**: Trayectoria r(t) en dos segmentos (A→B azul, B→C naranja)
- **Panel 4**: Métricas numéricas (scores, integral de línea, iteración)

Las figuras se guardan automáticamente en `/tmp/gradient_fig_NNNN.png`.

---

## Estructura del repositorio

```
Proyecto-Vectorial/
├── gradient_engine/          # Motor Python
│   ├── config.example.py     # Plantilla de configuración
│   ├── wazuh_client.py       # Lectura de alertas y scoring
│   ├── scalar_field.py       # Campo escalar gaussiano y gradiente
│   ├── gradient_flow.py      # Integración RK45 y integral de línea
│   ├── visualizer.py         # Visualizador matplotlib 4 paneles
│   ├── main.py               # Loop principal
│   └── requirements.txt
├── infra/                    # Infraestructura Docker
│   ├── docker-compose.yml    # Wazuh stack + agentes
│   ├── agent.Dockerfile      # Imagen Ubuntu con Wazuh agent + sshd
│   ├── agent-entrypoint.sh   # Registro y arranque del agente
│   └── .env.example          # Plantilla de variables de entorno
├── attack_sim.py             # Simulador de movimiento lateral
└── proyecto/                 # Informe del proyecto
    ├── proyecto_vectorial.tex
    ├── proyecto_vectorial.pdf
    └── imgs/
```

---

## Modelo matemático (resumen)

**Fase 1 — Analítica:**

```
V(x,y) = 60 − (x−7)² − (y−3)² + 0.8x + 0.5y

∇V = (14.8 − 2x,  6.5 − 2y)

r(t) = (7.4(1 − e^{−2t}),  3.25(1 − e^{−2t}))
```

**Fase 2 — Dinámica:**

```
V(x,y,t) = Σᵢ vᵢ(t) · exp(−‖x − xᵢ‖² / 2σ²)

vᵢ = log1p(Σⱼ levelⱼ · e^{−λΔtⱼ}) / log1p(50) × 10

∇V calculado numéricamente (numpy.gradient)
Integración con RK45 (scipy.integrate.solve_ivp)
```

Ver `proyecto/proyecto_vectorial.pdf` para el desarrollo completo.
