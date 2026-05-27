# Movimiento Lateral de un Atacante como Flujo Gradiente
**Curso:** Cálculo Vectorial  
**Modalidad:** Grupos de máximo 4 estudiantes  
**Proyecto:** Cálculo Vectorial en Lugares Inesperados

---

## 1. Título del proyecto
**Movimiento lateral de un atacante como flujo gradiente: una perspectiva vectorial de la ciberseguridad ofensiva**

---

## 2. Integrantes
> _Por definir_

---

## 3. Campo no tradicional elegido
**Ciberseguridad ofensiva** — específicamente la etapa de _movimiento lateral_ en un ataque dirigido (APT).

Este campo es no tradicional para el cálculo vectorial porque normalmente se estudia desde la informática, la ingeniería de redes o la ciencia forense digital — no desde el análisis vectorial. Sin embargo, la dinámica de un atacante navegando una red tiene una estructura matemática que el cálculo vectorial describe con precisión.

---

## 4. Descripción del fenómeno

### ¿Qué es el movimiento lateral?
En un ataque informático dirigido, el atacante rara vez compromete directamente su objetivo final. Primero obtiene acceso a un nodo de baja seguridad (punto de entrada), y luego se **mueve lateralmente** por la red — saltando de equipo en equipo — hasta alcanzar el activo de mayor valor: una base de datos, un servidor de control, credenciales administrativas.

Este proceso no es aleatorio. Un atacante con información sobre la red elige en cada paso el nodo que maximiza su acceso futuro con el menor riesgo de detección. Esa toma de decisiones tiene una estructura matemática precisa.

### El problema concreto
Dada una red corporativa con $k$ nodos, cada uno con un nivel de vulnerabilidad medible, ¿cuál es la trayectoria que un atacante racional seguiría desde el punto de entrada hasta el activo crítico?

---

## 5. Pregunta central del proyecto

> **¿Puede el gradiente de un campo escalar de vulnerabilidad modelar la trayectoria óptima de un atacante en movimiento lateral, y qué revela ese modelo sobre dónde concentrar las defensas?**

---

## 6. Conceptos de cálculo vectorial utilizados

| Concepto | Rol en el modelo |
|----------|-----------------|
| Campo escalar $V(\mathbf{x})$ | Función de vulnerabilidad definida sobre la red |
| Gradiente $\nabla V$ | Dirección de mayor vulnerabilidad — guía el ataque |
| Curva parametrizada $\mathbf{r}(t)$ | Trayectoria del atacante en el tiempo |
| Integral de línea $\int_C \nabla V \cdot d\mathbf{r}$ | Vulnerabilidad acumulada a lo largo de un recorrido |
| Campo conservativo | El campo $\nabla V$ es conservativo — el camino no importa, solo el destino |
| Puntos críticos de $V$ | Máximos = activos críticos; puntos de silla = cuellos de botella |
| Rotacional $\nabla \times \nabla V = 0$ | El campo gradiente es siempre irrotacional |

---

## 7. Construcción del modelo matemático

El modelo se desarrolla en dos fases complementarias. La **Fase 1** establece un modelo analítico con una función cerrada, lo que permite calcular el gradiente, la trayectoria y la integral de línea de forma exacta. La **Fase 2** extiende el modelo a un entorno dinámico donde $V$ se alimenta de datos reales del laboratorio (Wazuh + Suricata), haciendo que el campo evolucione en tiempo real durante el ataque.

---

### Fase 1 — Modelo analítico (caso base)

#### 7.1 El espacio de la red

Se modela una red corporativa ficticia con 6 activos. Las coordenadas no son físicas sino abstractas: representan la cercanía lógica de cada nodo al núcleo de la red y su nivel de privilegio.

| Nodo | Activo | Coordenadas $(x, y)$ |
|------|--------|----------------------|
| A | Equipo de usuario | $(0, 0)$ |
| B | Servidor de archivos | $(2, 1)$ |
| C | Servidor de aplicaciones | $(3, 3)$ |
| D | Controlador de dominio | $(5, 2)$ |
| E | Base de datos de clientes | $(7, 3)$ |
| F | Servidor de respaldo | $(4, -1)$ |

El atacante entra por el nodo A y busca alcanzar el nodo E (crown jewel).

#### 7.2 Campo escalar de vulnerabilidad

Se define $V: \mathbb{R}^2 \to \mathbb{R}$ como:

$$V(x, y) = 60 - (x - 7)^2 - (y - 3)^2 + 0.8x + 0.5y$$

La parte cuadrática negativa hace que $V$ sea mayor cerca del nodo E en $(7, 3)$. Los términos lineales $0.8x + 0.5y$ introducen una inclinación que modela el aumento gradual de exposición a medida que el atacante avanza hacia zonas más internas de la red.

#### 7.3 Campo gradiente

Las derivadas parciales de $V$ son:

$$\frac{\partial V}{\partial x} = -2(x - 7) + 0.8 = 14.8 - 2x$$

$$\frac{\partial V}{\partial y} = -2(y - 3) + 0.5 = 6.5 - 2y$$

Por tanto, el campo vectorial gradiente es:

$$\vec{F}(x, y) = \nabla V(x, y) = (14.8 - 2x,\; 6.5 - 2y)$$

Este campo indica, en cada punto de la red, la dirección hacia la cual crece más rápidamente la vulnerabilidad.

#### 7.4 Trayectoria parametrizada del atacante

Si el atacante sigue exactamente el campo gradiente, su posición $\vec{r}(t) = (x(t), y(t))$ satisface:

$$\vec{r}'(t) = \nabla V(\vec{r}(t))$$

Lo que produce el sistema de EDOs:

$$x'(t) = 14.8 - 2x(t), \qquad y'(t) = 6.5 - 2y(t)$$

Con condición inicial $\vec{r}(0) = (0, 0)$ (nodo A), la solución es:

$$x(t) = 7.4\left(1 - e^{-2t}\right), \qquad y(t) = 3.25\left(1 - e^{-2t}\right)$$

$$\boxed{\vec{r}(t) = \left(7.4\left(1 - e^{-2t}\right),\; 3.25\left(1 - e^{-2t}\right)\right)}$$

Cuando $t \to \infty$, la trayectoria converge a $(7.4, 3.25)$, muy cerca del nodo E $(7, 3)$ — el activo más crítico.

#### 7.5 Punto crítico y clasificación

Los puntos críticos ocurren cuando $\nabla V = \mathbf{0}$:

$$14.8 - 2x = 0 \implies x = 7.4$$
$$6.5 - 2y = 0 \implies y = 3.25$$

Para clasificar el punto crítico $(7.4, 3.25)$ se usa la matriz Hessiana de $V$:

$$H_V = \begin{pmatrix} -2 & 0 \\ 0 & -2 \end{pmatrix}$$

Como $H_V$ es negativa definida ($\det H_V = 4 > 0$ y $\frac{\partial^2 V}{\partial x^2} = -2 < 0$), el punto crítico es un **máximo local** — la zona de mayor vulnerabilidad del modelo, ubicada junto al nodo E.

#### 7.6 Conservatividad del campo

El campo $\vec{F}(x,y) = (P, Q) = (14.8 - 2x,\; 6.5 - 2y)$ es conservativo si:

$$\frac{\partial P}{\partial y} = \frac{\partial Q}{\partial x}$$

Verificando:

$$\frac{\partial P}{\partial y} = 0, \qquad \frac{\partial Q}{\partial x} = 0$$

Como $\frac{\partial P}{\partial y} = \frac{\partial Q}{\partial x}$, el campo es **conservativo**. Esto significa que la ganancia de vulnerabilidad acumulada entre dos nodos depende únicamente del punto de origen y del punto de destino, no de la ruta tomada.

#### 7.7 Integral de línea

Por el Teorema Fundamental de las Integrales de Línea:

$$\int_C \nabla V \cdot d\vec{r} = V(\vec{r}(T)) - V(\vec{r}(0))$$

Para la trayectoria A → E:

$$V(7, 3) = 60 - 0 - 0 + 0.8(7) + 0.5(3) = 67.1$$

$$V(0, 0) = 60 - 49 - 9 + 0 + 0 = 2.0$$

$$\int_C \nabla V \cdot d\vec{r} = 67.1 - 2.0 = 65.1$$

**Interpretación:** la ganancia acumulada de exposición desde el equipo de usuario hasta la base de datos de clientes es 65.1 unidades de vulnerabilidad, independientemente del camino que tome el atacante.

#### 7.8 Irrotacionalidad del campo

Como $\nabla V$ es el gradiente de una función escalar, su rotacional es idénticamente cero:

$$\nabla \times (\nabla V) = \mathbf{0}$$

**Interpretación:** no existen "remolinos" de vulnerabilidad. Un atacante que recorre un camino cerrado y regresa al punto de partida no gana ni pierde exposición neta.

---

### Fase 2 — Modelo dinámico con Wazuh + Suricata

En el laboratorio, $V$ no se construye manualmente sino que emerge de datos reales. Cada nodo de la red tiene un agente Wazuh y está monitorizado por Suricata a nivel de red. Los scores $v_i$ se actualizan cada 5 segundos según las alertas recibidas:

$$V(\mathbf{x}, t) = \sum_{i=1}^{k} v_i(t) \cdot \exp\!\left(-\frac{\|\mathbf{x} - \mathbf{x}_i\|^2}{2\sigma^2}\right)$$

donde $v_i(t)$ incorpora un factor de decaimiento temporal para que alertas recientes pesen más que alertas antiguas:

$$v_i(t) = \sum_j \text{level}_j \cdot e^{-\lambda(t - t_j)}$$

A medida que el atacante se mueve, $V(\mathbf{x}, t)$ se deforma — los nodos comprometidos aumentan su score y el gradiente reorienta la trayectoria predicha en tiempo real. Esto permite comparar la trayectoria predicha por el modelo $\vec{r}(t)$ con la trayectoria real visible en los logs.

---

## 8. Interpretación del modelo en el contexto de ciberseguridad

### 8.1 Valores de vulnerabilidad en los nodos

Evaluando $V(x, y)$ en cada activo de la red:

| Nodo | Activo | Coordenadas | $V(x, y)$ |
|------|--------|-------------|-----------|
| A | Equipo de usuario | $(0, 0)$ | 2.0 |
| B | Servidor de archivos | $(2, 1)$ | 33.1 |
| C | Servidor de aplicaciones | $(3, 3)$ | 47.9 |
| D | Controlador de dominio | $(5, 2)$ | 60.0 |
| E | Base de datos de clientes | $(7, 3)$ | 67.1 |
| F | Servidor de respaldo | $(4, -1)$ | 37.7 |

Los valores crecen a lo largo de la ruta $A \to B \to C \to D \to E$, confirmando que el modelo representa una trayectoria coherente: el atacante parte de un nodo de baja exposición y se acerca progresivamente al activo más valioso.

### 8.2 Dirección del ataque en cada nodo

Evaluando $\nabla V$ en los nodos intermedios:

| Nodo | Coordenadas | $\nabla V = (14.8 - 2x,\; 6.5 - 2y)$ | Interpretación |
|------|-------------|---------------------------------------|----------------|
| A | $(0, 0)$ | $(14.8,\; 6.5)$ | Fuerte impulso hacia el interior de la red |
| B | $(2, 1)$ | $(10.8,\; 4.5)$ | Sigue avanzando hacia zonas de mayor privilegio |
| C | $(3, 3)$ | $(8.8,\; 0.5)$ | Movimiento principalmente horizontal |
| D | $(5, 2)$ | $(4.8,\; 2.5)$ | Se acerca al crown jewel |
| E | $(7, 3)$ | $(0.8,\; 0.5)$ | Gradiente casi nulo — zona de máxima vulnerabilidad |

### 8.3 Trayectoria predicha vs. ruta discreta

El modelo continuo predice que el atacante converge a $(7.4, 3.25)$. En el grafo discreto, la ruta que sigue el crecimiento de $V$ es:

$$A \to B \to C \to D \to E$$

La correspondencia entre la trayectoria continua $\vec{r}(t)$ y la ruta discreta valida que el modelo captura correctamente la lógica del movimiento lateral.

### 8.4 Implicaciones defensivas

El modelo sugiere que **defender únicamente la base de datos no es suficiente**. Lo que debe reducirse es la *pendiente* del campo $\nabla V$ a lo largo de la ruta de ataque. Esto se traduce en medidas concretas:

- **Segmentación de red** entre nodos B–C y C–D: interrumpe la continuidad del campo, forzando al atacante a superar barreras donde $V$ no crece suavemente.
- **Reducción de privilegios en D** (Controlador de dominio): bajar $V(5, 2)$ de 60.0 reduce el gradiente que apunta hacia E.
- **Honeypots en puntos de silla**: zonas donde $|\nabla V|$ es pequeño pero no nulo son candidatas naturales para colocar activos señuelo.
- **Monitoreo intensivo en la ruta de gradiente**: los nodos por donde $\vec{r}(t)$ pasa en los primeros valores de $t$ son los más probables de ser comprometidos primero.

### 8.5 Validación en el laboratorio (Fase 2)

El laboratorio ejecutó un ataque SSH brute force progresivo desde Kali Linux contra los nodos victim-c (B) y capstone (C), mientras el motor Python monitoreaba el campo en tiempo real. A continuación se documentan las observaciones obtenidas durante 53 iteraciones de monitoreo (265 segundos de ejecución con `POLL_INTERVAL = 5s`).

#### Configuración del experimento

| Parámetro | Valor |
|-----------|-------|
| Nodo A (entry) | wazuh-manager — `165.227.109.227`, pos $(0.0, 0.0)$ |
| Nodo B | victim-c — `165.227.122.79`, pos $(3.0, 3.0)$ |
| Nodo C (crown jewel) | capstone — `198.199.71.219`, pos $(7.0, 3.0)$ |
| $\sigma$ (radio gaussiano) | 1.5 |
| Ventana temporal | 3 minutos |
| Decaimiento $\lambda$ | 0.1 min⁻¹ |
| Punto de entrada efectivo | $(0.5, 0.5)$ — offset del nodo A |

#### Observación 1 — El campo V responde en tiempo real al ataque

A medida que el simulador enviaba intentos de autenticación SSH a victim-c y capstone, los scores de esos nodos crecieron proporcionalmente:

| Iteración | $v_A$ | $v_B$ | $v_C$ | $\int\nabla V \cdot d\mathbf{r}$ |
|-----------|--------|--------|--------|----------------------------------|
| 1  | 0.00 | 5.88 | 9.82 | +5.86 |
| 9  | 0.00 | 7.39 | 8.90 | +7.22 |
| 37 | 0.00 | 8.23 | 9.89 | +8.04 |
| 53 | 0.00 | 8.38 | 10.00 | +8.18 |

La validación empírica del Teorema Fundamental de Integrales de Línea es directa: $\int_C \nabla V \cdot d\mathbf{r} = V(\mathbf{r}(T)) - V(\mathbf{r}(0))$. En todas las iteraciones, la integral creció de forma monotónica con los scores, confirmando que la ganancia de vulnerabilidad del atacante está determinada únicamente por los valores en el origen y el destino — no por la trayectoria intermedia.

#### Observación 2 — La silla de montar entre B y C es el hallazgo topológico central

En todas las figuras con dos nodos activos, el panel del gradiente $\nabla V$ muestra una región donde las flechas se "abren" en dos conjuntos opuestos. Esa región corresponde a un **punto de silla** del campo escalar — un punto crítico donde el Hessiano tiene eigenvalores de signo opuesto. Matemáticamente separa las dos cuencas de atracción del campo: puntos a la izquierda del saddle convergen hacia B, puntos a la derecha convergen hacia C.

Esta observación tiene una interpretación defensiva directa: el saddle point es el **cuello de botella topológico** de la red. Colocar controles de acceso o honeypots en esa zona (aproximadamente en $(5, 3)$ entre B y C) maximiza la probabilidad de detección del atacante en tránsito.

#### Observación 3 — Los puntos críticos detectados correlacionan con la estructura del campo

| Estado del campo | Puntos críticos detectados | Interpretación |
|-----------------|---------------------------|----------------|
| 1 nodo activo | 46–94 | Campo casi plano fuera del pico — muchos artefactos numéricos |
| 2 nodos activos | 13–21 | Campo bien estructurado con silla definida |
| 3 nodos activos | 5–8 | Campo muy estructurado — mínimos y máximos bien separados |

Con dos nodos activos el campo tiene la estructura más informativa: un máximo en B, un máximo en C y un punto de silla entre ellos. Este es el escenario que el modelo analítico de la Fase 1 describe con mayor precisión.

#### Observación 4 — Tres nodos activos simultáneos colapsan la integral de línea

En las iteraciones 23–35, el wazuh-manager (nodo A) generó sus propias alertas de nivel ≥ 5, elevando su score a $v_A \approx 4$. En esas iteraciones, la integral cayó a $\int \nabla V \cdot d\mathbf{r} \approx 0.08$–$0.16$:

| Iter | $v_A$ | $v_B$ | $v_C$ | $\int\nabla V \cdot d\mathbf{r}$ |
|------|--------|--------|--------|----------------------------------|
| 26 | 4.41 | 8.10 | 8.03 | +0.13 |
| 33 | 4.09 | 9.04 | 9.56 | +0.07 |
| 35 | 4.01 | 8.33 | 10.00 | +0.09 |

La explicación geométrica: el pico gaussiano de A crea un gradiente local que "empuja" al atacante de vuelta desde el punto de entrada $(0.5, 0.5)$ — el punto de partida queda atrapado en la ladera ascendente del gaussiano de A, donde el flujo gradiente apunta en dirección contraria a B y C. La integral es casi nula porque el atacante "no sabe hacia dónde ir" cuando el nodo de entrada tiene alta actividad propia.

Esto es una **limitación identificada del modelo**: un SIEM muy activo en el nodo de entrada genera ruido que distorsiona la predicción. En producción, se requeriría un filtrado más selectivo por tipo de alerta (solo alertas de intrusión, no alertas operacionales).

#### Observación 5 — La trayectoria en dos etapas (A→B→C) valida la estructura del movimiento lateral

La integración en dos etapas muestra claramente el patrón A→B→C:
- **Etapa A→B** (línea azul sólida): el flujo gradiente desde $(0.5, 0.5)$ converge hacia victim-c, el primer máximo local accesible desde el punto de entrada. Este comportamiento replica la fase de "pivote inicial" del movimiento lateral.
- **Etapa B→C** (línea naranja punteada): desde el pivote en B, el flujo reanuda hacia capstone — el crown jewel — validando que una vez comprometido B, el gradiente orienta al atacante hacia el activo de mayor valor.

La observación confirma la interpretación del modelo: **cada máximo local del campo es un nodo comprometido potencial**, y la secuencia de máximos visitados por el flujo gradiente predice el orden del movimiento lateral.

### 8.6 Evidencia visual del laboratorio

A continuación se clasifica el registro fotográfico obtenido durante la sesión de laboratorio del 26 de mayo de 2026. Las capturas se agrupan por origen y contenido; los identificadores corresponden a los archivos de referencia.

#### Grupo A — Kali Linux: motor en ejecución

| Identificador | Archivo fuente | Descripción |
|---|---|---|
| `fig_kali_attack_sim` | `19-02-07.png` | Terminal con `attack_sim.py` corriendo en loop continuo. Se observan los ciclos victim-c → pausa → capstone con sus contadores de intentos SSH. |
| `fig_kali_gradient_engine` | `19-02-20.png` | Terminal con `main.py` mostrando scores en tiempo real por iteración: `victim-c: v=X.XX`, `capstone: v=X.XX` y la integral de línea $\int\nabla V \cdot d\mathbf{r}$. |

#### Grupo B — Wazuh: vista global del SIEM

| Identificador | Archivo fuente | Descripción |
|---|---|---|
| `fig_wazuh_events_global` | `19-05-46.png` | Pestaña Events de Security events — 17,153 hits en 24 h. Los tres agentes (capstone-campusshield, victim-b, victim-c) aparecen mezclados. Se distinguen alertas Rule 5710 (sshd) y Suricata (86601). |
| `fig_wazuh_dashboard_global` | `19-06-02.png` | Dashboard de Security events — totales: 17,163 alertas, **2,971 fallos de autenticación**, 1,318 éxitos. Pie chart de top 5 agentes y resumen de tácticas MITRE ATT&CK. |

#### Grupo C — Wazuh: inventario de agentes

| Identificador | Archivo fuente | Descripción |
|---|---|---|
| `fig_wazuh_agents` | `19-06-22.png` | Vista Agents con 2 agentes activos, 0 desconectados, 100% de cobertura. Muestra: capstone-campusshield (ID 001, `198.199.71.219`, Ubuntu 24.04, v4.7.5) y victim-c (ID 003, `165.227.122.79`, Ubuntu 22.04, v4.7.5). |

#### Grupo D — Wazuh: Security Events por nodo

| Identificador | Archivo fuente | Descripción |
|---|---|---|
| `fig_wazuh_events_victimc` | `19-07-10.png` | Security Events filtrado a victim-c. Pico de alertas sshd en la evolución temporal. Top 5 alerts dominado por "sshd: Attempt to login using a non-existent user". Tácticas visibles: Credential Access + **Lateral Movement** (T1110.001, T1021.004, Rule 5710). |
| `fig_wazuh_events_capstone` | `19-07-26.png` | Security Events filtrado a capstone-campusshield (agent 001). Totales: 9,458 alertas, **1,164 fallos de autenticación**, 37 autenticaciones exitosas. Mezcla de alertas Suricata IDS y sshd activas. |

#### Grupo E — Wazuh: MITRE ATT&CK

| Identificador | Archivo fuente | Descripción |
|---|---|---|
| `fig_mitre_dashboard` | `19-07-49.png` | MITRE ATT&CK Dashboard para capstone (agent 001). Top tactics: **Credential Access** y **Lateral Movement** dominan con ~2,000 eventos cada uno. Bar chart de ataques por táctica confirma la alineación con TA0008. |
| `fig_mitre_events` | `19-07-57.png` | MITRE ATT&CK Events para capstone — **1,250 hits** en las últimas 24 h. Todas las entradas clasificadas como T1110.001 (Brute Force: Password Guessing) + T1021.004 (Remote Services: SSH), nivel 5, Rule 5710. |

#### Grupo F — Wazuh: Integrity Monitoring

| Identificador | Archivo fuente | Descripción |
|---|---|---|
| `fig_wazuh_fim` | `19-08-26.png` | Integrity Monitoring Events para capstone — 5 modificaciones detectadas en `/usr/bin/vim.basic`, `/usr/bin/helpztags`, `/usr/bin/vimtutor`, `/usr/bin/vim.tiny`, `/usr/bin/xxd`. Rule 550 "Integrity checksum changed", nivel 7. Evidencia de actividad de post-explotación sobre el sistema de archivos del nodo comprometido. |

> **Nota:** Las capturas de las 18:21 (`18-21-29.png`, `18-21-46.png`) corresponden a una fase anterior de la sesión en la que el motor no estaba funcionando correctamente y no se incluyen como evidencia del experimento.

---

## 9. Discusión: alcances, limitaciones y posibles mejoras

### 9.1 Alcances del modelo

El modelo logra representar mediante objetos matemáticos precisos una situación de ciberseguridad que usualmente se describe de forma cualitativa:

- $V(x, y)$ convierte la noción abstracta de "vulnerabilidad" en un campo escalar operable
- $\nabla V$ formaliza la dirección óptima del ataque
- $\vec{r}(t)$ describe la trayectoria como una curva parametrizada con solución analítica
- La integral de línea cuantifica la exposición acumulada entre dos puntos de la red
- El punto crítico identifica matemáticamente el activo más expuesto
- La conservatividad revela que la ruta específica no altera el riesgo total acumulado

### 9.2 Limitaciones

**Del modelo analítico (Fase 1):**
- La función $V(x, y)$ fue construida para satisfacer las propiedades matemáticas deseadas, no derivada de datos empíricos
- Una red real no es un plano continuo sino un grafo discreto con reglas de firewall, credenciales y segmentos
- Un atacante real no siempre tiene información completa para seguir el gradiente óptimo
- El campo perfectamente conservativo es una idealización: barreras y controles de acceso rompen esta propiedad

**Del modelo dinámico (Fase 2):**
- El score $v_i$ basado en niveles de alerta de Wazuh puede ser ruidoso — una alerta de nivel alto no implica necesariamente compromiso
- El parámetro $\sigma$ (radio de influencia de cada nodo) requiere calibración
- La interpolación gaussiana no respeta la topología real de la red

### 9.3 Posibles mejoras

- **Grafo discreto ponderado**: reemplazar el plano continuo por un grafo donde las aristas tienen peso según la dificultad real de moverse entre nodos (controles de acceso, autenticación, segmentación)
- **Superficie 3D**: modelar $z = V(x, y)$ como superficie tridimensional para visualizar el "relieve de vulnerabilidad" de la red
- **Barreras defensivas como restricciones**: incorporar firewalls y MFA como zonas donde $V$ tiene un salto discontinuo o una barrera de potencial
- **Comparación de rutas**: calcular $\int_C \nabla V \cdot d\vec{r}$ para múltiples rutas hacia el mismo destino y verificar numéricamente la independencia de camino
- **Integración con OpenCTI**: usar los TTPs de MITRE ATT&CK (TA0008) para asignar pesos de vulnerabilidad más fundamentados por técnica de movimiento lateral

---

## 10. Bitácora de uso de IA

> _Por completar durante el proceso de trabajo_

---

## 11. Conclusiones

El proyecto demuestra que el cálculo vectorial puede aplicarse de manera rigurosa y no decorativa a un fenómeno de ciberseguridad. El movimiento lateral de un atacante dentro de una red informática tiene una estructura matemática precisa: un campo escalar de vulnerabilidad $V$, cuyo gradiente $\nabla V$ orienta la trayectoria del atacante hacia los activos de mayor exposición.

Los conceptos del curso utilizados —campo escalar, gradiente, curva parametrizada, integral de línea, campo conservativo, puntos críticos y rotacional— no fueron mencionados superficialmente sino que cada uno cumplió una función interpretativa dentro del modelo:

- El **gradiente** formalizó la dirección óptima del ataque
- La **curva parametrizada** $\vec{r}(t) = (7.4(1-e^{-2t}),\; 3.25(1-e^{-2t}))$ describió analíticamente el recorrido del atacante
- La **integral de línea** (= 65.1) cuantificó la exposición acumulada entre el punto de entrada y el activo crítico
- La **conservatividad** reveló que la ruta específica no altera el riesgo total — solo importan el origen y el destino
- El **punto crítico** con Hessiana negativa definida identificó matemáticamente la zona de mayor vulnerabilidad

La principal contribución del trabajo no es predecir exactamente un ataque real, sino ofrecer una forma geométrica y vectorial de pensar la seguridad de redes. Desde esta perspectiva, defender la red significa **reducir las pendientes del campo $\nabla V$** que conducen hacia los activos críticos — una idea que el cálculo vectorial hace precisa y cuantificable.

La extensión al laboratorio con Wazuh y Suricata convierte el modelo teórico en un experimento verificable, donde los datos reales de alertas alimentan $V$ dinámicamente y permiten contrastar la trayectoria predicha con la trayectoria real del atacante.

---

## 12. Referencias bibliográficas

- Marsden, J. E., & Tromba, A. (2012). *Vector Calculus* (6th ed.). W. H. Freeman.
- MITRE ATT&CK. *Lateral Movement, Tactic TA0008*. https://attack.mitre.org/tactics/TA0008/
- MITRE ATT&CK. *Enterprise Mitigations: Network Segmentation*. https://attack.mitre.org/mitigations/enterprise/
- Cybersecurity and Infrastructure Security Agency (CISA). *StopRansomware Guide*. https://www.cisa.gov/stopransomware/ransomware-guide
- Verizon. *Data Breach Investigations Report*. https://www.verizon.com/business/resources/reports/dbir/
- Common Vulnerability Scoring System (CVSS) v3.1. NIST NVD. https://nvd.nist.gov/vuln-metrics/cvss
