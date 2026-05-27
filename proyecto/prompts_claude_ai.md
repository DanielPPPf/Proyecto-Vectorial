# Prompts para reconstruir la sesión en claude.ai

Estos prompts replican el proceso de trabajo descrito en la bitácora de IA
del proyecto. Pégalos en orden en una nueva conversación de claude.ai.
El hilo muestra cómo el conocimiento de dominio en ciberseguridad se contrastó
con la formalización matemática de Claude para llegar al modelo final.

---

## PROMPT 1 — Contexto inicial y búsqueda de enfoque

> Estoy en un curso de Cálculo Vectorial y necesito hacer un proyecto aplicando
> cálculo vectorial a un campo no tradicional. Tengo conocimientos de
> ciberseguridad — tengo experiencia con el framework MITRE ATT&CK, he trabajado
> con SIEMs como Wazuh y conozco bien la kill chain de ataques APT.
>
> Una etapa que me parece interesante es el movimiento lateral (MITRE TA0008):
> cuando un atacante ya está dentro de la red y se mueve de equipo en equipo
> buscando el activo más valioso. Intuitivamente, el atacante siempre se mueve
> hacia donde "más le conviene", que depende de qué tan vulnerables están los
> nodos vecinos.
>
> ¿Tiene sentido modelar eso con cálculo vectorial? ¿Qué conceptos del curso
> (gradiente, campo escalar, integral de línea) podrían aplicar aquí de forma
> no forzada?

---

## PROMPT 2 — Formalización del campo escalar

> Me convence la idea del campo escalar de vulnerabilidad V(x,y). Quiero
> entender bien cómo construirlo.
>
> En la red tengo k nodos, cada uno con un nivel de vulnerabilidad v_i medible
> (por ejemplo, derivado de las alertas de seguridad que genera). Las
> coordenadas (x,y) de cada nodo no son físicas sino lógicas: representan
> qué tan cerca está el nodo del núcleo de la red y qué nivel de privilegio
> tiene.
>
> ¿Cómo construiría V(x,y) a partir de esos scores? Necesito que sea una
> función continua y diferenciable para poder calcularle el gradiente.
> También necesito que tenga máximos en los nodos más vulnerables y que
> decaiga suavemente entre nodos.

---

## PROMPT 3 — Modelo analítico con función cerrada

> Para la Fase 1 del proyecto quiero un modelo analítico puro con una función
> V(x,y) de forma cerrada, no gaussianas, para poder calcular todo exactamente.
>
> La red tiene 6 nodos:
> - A (equipo usuario): (0,0) — punto de entrada del atacante
> - B (servidor archivos): (2,1)
> - C (servidor aplicaciones): (3,3)
> - D (controlador dominio): (5,2)
> - E (base de datos): (7,3) — crown jewel, activo más crítico
> - F (respaldo): (4,-1)
>
> Necesito una función V(x,y) que:
> 1. Tenga su máximo en E (7,3)
> 2. Sea cuadrática con coeficientes α = β = 1 en los términos cuadráticos,
>    es decir, de la forma V(x,y) = C − (x−7)² − (y−3)² + términos lineales.
>    Esto garantiza que el gradiente sea lineal y la EDO tenga solución exacta
>    con separación de variables.
> 3. Tenga términos lineales +0.8x + 0.5y que modelen el aumento de exposición
>    al avanzar hacia el interior de la red (mayor x = más cerca del núcleo,
>    mayor y = mayor privilegio).
> 4. Usa C = 60 para que V(E) sea el valor máximo de referencia.
>
> Construye V(x,y) expandida en forma estándar, calcula su gradiente ∇V,
> evalúa V en cada uno de los 6 nodos y clasifica el punto crítico con el Hessiano.

---

## PROMPT 4 — Trayectoria del atacante como EDO

> Perfecto. Ahora quiero modelar la trayectoria del atacante.
>
> Si el atacante sigue siempre la dirección de mayor vulnerabilidad, su
> posición r(t) = (x(t), y(t)) satisface r'(t) = ∇V(r(t)). Eso me da un
> sistema de EDOs.
>
> Con el gradiente que calculaste (∇V = (14.8 - 2x, 6.5 - 2y)) y condición
> inicial r(0) = (0,0):
> 1. Resuelve el sistema por separación de variables, mostrando el desarrollo
>    completo paso a paso
> 2. Verifica que cuando t→∞ la trayectoria converge al punto crítico
> 3. Evalúa r(t) en t = 0.5, 1, 2 y 5 para ver la progresión

---

## PROMPT 5 — Integral de línea y conservatividad

> Ahora necesito dos cosas más para completar el modelo analítico:
>
> 1. **Conservatividad**: verifica si el campo F = ∇V = (14.8 - 2x, 6.5 - 2y)
>    es conservativo. Si lo es, ¿qué implica eso para el atacante? ¿Importa
>    qué camino tome entre A y E?
>
> 2. **Integral de línea**: calcula ∫_C ∇V·dr a lo largo de la trayectoria
>    A→E usando el Teorema Fundamental de Integrales de Línea. Interpreta el
>    resultado en términos de ciberseguridad: ¿qué representa esa ganancia
>    acumulada de 65.1?
>
> 3. **Rotacional**: verifica que ∇×(∇V) = 0 e interpreta qué significa
>    en el contexto del modelo.

---

## PROMPT 6 — Arquitectura del sistema Python

> Ahora quiero construir una Fase 2 donde V(x,y) no sea fija sino que se
> construya en tiempo real a partir de alertas de Wazuh. Tengo una
> infraestructura en DigitalOcean con 3 VMs Ubuntu y Wazuh 4.7.5 instalado.
>
> El sistema debe:
> - Consultar las alertas de cada agente Wazuh cada 5 segundos
> - Calcular un score v_i para cada nodo basado en las alertas recientes
> - Construir V(x,y) como superposición de gaussianas centradas en los nodos
> - Calcular ∇V numéricamente e integrar la trayectoria del atacante
> - Visualizar todo en tiempo real con matplotlib
>
> ¿Cómo estructurarías el proyecto en módulos Python? Dame la arquitectura
> antes de escribir código.

---

## PROMPT 7 — Cliente Wazuh y scoring

> La API REST de Wazuh 4.7.5 no tiene el endpoint /alerts (fue eliminado en
> versiones recientes). Sin embargo tengo acceso SSH al manager como root y
> puedo leer directamente /var/ossec/logs/alerts/alerts.json que tiene las
> alertas en formato JSON, una por línea.
>
> Necesito un módulo wazuh_client.py que:
> 1. Lea las últimas 5000 líneas del archivo vía SSH usando subprocess
> 2. Filtre las alertas por agent.id (campo de 3 dígitos con zero-padding)
>    y por ventana temporal (últimos N minutos)
> 3. Calcule un score v_i con decaimiento temporal exponencial:
>    score = Σ level_j * exp(-λ * Δt_j)
>    donde Δt es el tiempo en minutos desde la alerta
> 4. Normalice el score con log1p para evitar saturación cuando hay muchas alertas
> 5. Solo cuente alertas de nivel >= 5 (filtrar ruido operacional como
>    heartbeats, syscollector, etc.)
>
> Host del manager: <WAZUH_MANAGER_IP>, usuario: root

---

## PROMPT 8 — Campo escalar con gaussianas

> Ahora el módulo scalar_field.py. Necesita tres funciones:
>   
> 1. **build_scalar_field(node_positions, scores, sigma, grid_size)**:
>    construye V(x,y) en una malla 200x200 como superposición gaussiana.
>    Cada nodo i contribuye: v_i * exp(-||x - x_i||² / (2σ²)).
>    El dominio espacial va de (-2,10) en x y (-2,7) en y.
>
> 2. **compute_gradient(X, Y, V)**: calcula ∂V/∂x y ∂V/∂y numéricamente
>    usando numpy.gradient con diferencias finitas.
>
> 3. **find_critical_points(X, Y, dVdx, dVdy, threshold)**: detecta puntos
>    donde |∇V| < threshold, los agrupa por contigüidad y retorna sus
>    coordenadas. Usar scipy.ndimage.label para agrupar.
>
> El parámetro sigma controla el radio de influencia de cada nodo.
> Con sigma=1.5, ¿cómo decae la contribución gaussiana a distancia σ y 2σ?

---

## PROMPT 9 — Integración del flujo gradiente con RK45

> El módulo gradient_flow.py necesita:
>
> 1. **integrate_attacker_path(X, Y, dVdx, dVdy, start, t_span, n_steps)**:
>    integra la EDO r'(t) = ∇V(r(t)) usando scipy.integrate.solve_ivp con
>    método RK45. El gradiente en puntos arbitrarios se obtiene por
>    interpolación bilineal con RegularGridInterpolator.
>
> 2. **compute_line_integral(X, Y, V, path)**: calcula la integral de línea
>    usando el Teorema Fundamental: V(destino) - V(origen), con interpolación
>    del campo V en los extremos de la trayectoria.
>
> Pregunta importante: si victim-c y capstone tienen ambos scores altos,
> el flujo gradiente desde el punto de entrada convergerá al máximo local
> más cercano y se detendrá ahí. ¿Cómo modelarías el salto completo
> A→B→C (B=victim-c, C=capstone) dado que el gradiente se detiene en B?

---

## PROMPT 10 — Visualizador de 4 paneles

> El módulo visualizer.py genera una figura matplotlib con fondo oscuro
> (#0d1117) compuesta por 4 paneles en proporción 3:3:3:1:
>
> 1. **Panel 1** — Heatmap de V(x,y): contourf con colormap YlOrRd,
>    40 niveles, con isolíneas blancas semitransparentes
>
> 2. **Panel 2** — Campo vectorial ∇V: quiver con flechas cyan sobre
>    el heatmap con alpha=0.4. Si el gradiente es casi cero (sin alertas
>    activas), mostrar texto "∇V ≈ 0" en lugar de quiver para evitar
>    división por cero
>
> 3. **Panel 3** — Trayectoria r(t) en dos segmentos:
>    - A→B: línea azul sólida (dodgerblue)
>    - B→C: línea naranja punteada
>    - Marcadores: círculo verde (entrada), triángulo amarillo (pivote B),
>      estrella roja (destino C)
>
> 4. **Panel 4** — Info numérica: iteración, integral de línea, puntos
>    críticos, scores por nodo, max/min V. Sin ejes, texto sobre fondo oscuro.
>
> Los nodos de la red se muestran en los 3 paneles principales con colores
> verde/naranja/rojo según su rol.

---

## PROMPT 11 — Loop principal y auto-save

> El main.py debe orquestar todo en un loop infinito con estas etapas
> por iteración:
>
> 1. Obtener token Wazuh (ahora un stub vacío ya que usamos SSH)
> 2. Consultar alertas de los 3 agentes y calcular scores
> 3. Construir V(x,y) y calcular ∇V
> 4. Integrar trayectoria en DOS etapas:
>    - Etapa 1: desde entry_pos hasta que converja → path_ab
>    - Etapa 2: desde el último punto de path_ab → path_bc
>    - Concatenar: path = concatenar(path_ab, path_bc)
> 5. Calcular integral de línea y detectar puntos críticos
> 6. Imprimir en consola: iteración | score por nodo | integral | críticos
> 7. Actualizar figura en pantalla con plt.pause(0.1)
> 8. Guardar figura en /tmp/gradient_fig_{iter:04d}.png
> 9. Transferir vía SCP a daniel@192.168.50.135:/home/daniel/Documents/Vectorial/
>    (no bloqueante: usar subprocess.Popen)
>
> Configuración:
> - NODES: wazuh-manager en (0,0), victim-c (agent_id=003) en (3,3), capstone (agent_id=001) en (7,3)
> - ENTRY_NODE = "wazuh-manager", ENTRY_OFFSET = (0.5, 0.5)
> - SIGMA=1.5, POLL_INTERVAL=5, ALERT_WINDOW=3, DECAY_LAMBDA=0.1

---

## PROMPT 12 — Simulador de tráfico SSH para el laboratorio

> Necesito un script attack_sim.py que genere intentos de autenticación SSH
> fallidos de forma controlada contra dos VMs de mi laboratorio privado,
> para que Wazuh registre alertas y el motor de gradiente tenga datos reales.
>
> Contexto: las VMs (victim-c y capstone) son instancias que yo administro
> en un entorno de laboratorio aislado para esta materia. El script no sale
> de ese entorno. Las IPs destino son variables configurables, no están
> hardcodeadas.
>
> El script necesita:
> - Intentar conexiones SSH con credenciales inválidas usando subprocess
>   (no importa el resultado, el rechazo es el objetivo: genera el log)
> - Opciones SSH: -o PasswordAuthentication=yes -o PubkeyAuthentication=no
>   -o ConnectTimeout=3 -o StrictHostKeyChecking=no
>   (necesarias para que sshd intente la autenticación y genere el evento
>   que Wazuh captura como Rule 5710, level 5)
> - Ciclo: N intentos → TARGET_B, pausa SLEEP_S segundos,
>           N intentos → TARGET_C, pausa SLEEP_S segundos, repetir
> - Configuración al inicio del archivo: TARGET_B, TARGET_C, N=20,
>   SLEEP_S=30, DELAY=0.15 (tiempo entre intentos para no saturar)
> - Imprimir en consola qué intento va y el código de retorno SSH
>
> Las credenciales a probar pueden ser cualquier lista corta de strings
> obviamente inválidas (el objetivo es el rechazo, no el acceso).

---

## PROMPT 13 — Problema: scores todos en 0.00

> El motor está corriendo pero todos los scores son 0.00 en todas las
> iteraciones, aunque attack_sim.py dice que está enviando intentos.
>
> Output del motor:
> [0001] wazuh-mgr: v=0.00 | victim-c: v=0.00 | capstone: v=0.00 | ∫∇V·dr=+0.00
>
> He verificado que:
> - La conexión SSH al manager funciona manualmente
> - El archivo /var/ossec/logs/alerts/alerts.json existe y tiene contenido
> - Los intentos SSH de attack_sim.py sí llegan a los nodos (puedo verlos
>   en /var/log/auth.log de victim-c)
>
> ¿Qué puede estar fallando en el filtrado de alertas?

---

## PROMPT 14 — Problema: scores saturados en 10.00

> Ahora el problema opuesto: todos los scores son exactamente 10.00 desde
> la primera iteración y el campo V es completamente plano (todos los nodos
> en el máximo). Las figuras generadas son en blanco.
>
> Creo que el problema es que hay demasiadas alertas operacionales en la
> ventana temporal. El manager genera constantemente alertas de syscollector,
> FIM, heartbeat que tienen nivel >= 5 pero no son de intrusión.
>
> Dos posibles soluciones que se me ocurren:
> 1. Reducir la ventana temporal de 10 a 3 minutos
> 2. Cambiar la normalización del score para que no sature
>
> ¿Cómo implementarías ambos cambios? Para la normalización quiero algo que
> crezca rápido al inicio pero se aplane con volúmenes altos de alertas.

---

## PROMPT 15 — Problema: trayectoria invisible / integral ≈ 0

> Los scores ahora se ven bien (victim-c ~6, capstone ~8) pero la trayectoria
> en el panel 3 no aparece, o aparece como un punto. La integral de línea
> es siempre ≈ 0.
>
> El punto de entrada está en (0,0) porque ENTRY_NODE es "wazuh-manager"
> que tiene posición (0,0). Estoy pensando que el problema es que (0,0) es
> el centro de la gaussiana del manager, así que si el manager tiene cualquier
> score, ese punto es un máximo local y el gradiente ahí es ~0. La trayectoria
> no va a ningún lado porque empieza exactamente en un extremo del campo.
>
> ¿Cómo soluciono esto? El atacante no viene del propio manager sino que
> entra a la red desde fuera.

---

## PROMPT 16 — Problema: capstone siempre en 0 pese al ataque

> victim-c sube a ~7-8 con el simulador pero capstone siempre se queda en 0.00.
> He verificado que los intentos SSH llegan a capstone (veo los paquetes en
> tcpdump) pero Wazuh no genera alertas de nivel >= 5 para ese nodo.
>
> Revisando la configuración de capstone, veo que tiene:
> PasswordAuthentication no
> en /etc/ssh/sshd_config
>
> Cuando SSH rechaza la conexión sin ni siquiera intentar la contraseña,
> ¿genera Wazuh una alerta de nivel 5 (Rule 5710)? ¿O necesita que el
> intento de autenticación llegue al PAM para que sshd lo loguee como
> "Failed password" o "Invalid user"?

---

## PROMPT 17 — Análisis de resultados: iteración 1

> El motor lleva 53 iteraciones corriendo con attack_sim.py activo.
> En la iteración 1:
> - victim-c (B): v = 5.88
> - capstone (C): v = 9.82
> - wazuh-manager (A): v = 0.00
> - Integral de línea: +5.86
> - Puntos críticos detectados: 21
>
> La trayectoria muestra el segmento A→B (azul) llegando a victim-c.
> En el panel del gradiente hay una zona entre B y C donde las flechas
> cyan parecen divergir en dos direcciones opuestas.
>
> ¿Qué es matemáticamente esa zona de divergencia del gradiente?
> ¿Cómo se llama ese tipo de punto crítico y cómo se clasifica con el Hessiano?
> ¿Qué implicación defensiva tiene para la red?

---

## PROMPT 18 — Análisis: colapso de la integral con 3 nodos activos

> En las iteraciones 26-35, el wazuh-manager empezó a generar alertas propias
> (actualizaciones del sistema, FIM events) y su score subió a ~4.
> En esas iteraciones la integral de línea colapsó de ~8 a valores de 0.07-0.13:
>
> Iter 26: vA=4.41, vB=8.10, vC=8.03, ∫=+0.13
> Iter 33: vA=4.09, vB=9.04, vC=9.56, ∫=+0.07
> Iter 35: vA=4.01, vB=8.33, vC=10.00, ∫=+0.09
>
> El punto de entrada está en (0.5, 0.5), desplazado del manager en (0,0).
> ¿Por qué el score del manager afecta tanto la integral si el punto de entrada
> no está en el centro de su gaussiana? ¿Cuál es la explicación geométrica
> de lo que le pasa a la trayectoria cuando el nodo A tiene score alto?

---

## PROMPT 19 — Preparar el informe: estructura y conexión entre fases

> Quiero preparar el informe final del proyecto. Necesito que me ayudes a
> articular claramente la conexión entre la Fase 1 (modelo analítico) y la
> Fase 2 (laboratorio real).
>
> La Fase 1 tiene una función V(x,y) exacta con solución analítica cerrada.
> La Fase 2 usa gaussianas con scores dinámicos y RK45 numérico.
>
> Preguntas para estructurar la sección de resultados:
> 1. ¿Qué propiedades de la Fase 1 (conservatividad, irrotacionalidad) siguen
>    siendo válidas en la Fase 2 aunque el campo sea gaussiano y no cuadrático?
> 2. El Teorema Fundamental se valida empíricamente en la Fase 2: la integral
>    de línea ≈ V(destino) - V(origen) en cada iteración. ¿Cómo debería
>    presentarse eso como validación experimental?
> 3. El saddle point observado en el panel del gradiente: ¿es el mismo tipo
>    de punto crítico que en la Fase 1, o tiene diferencias en un campo
>    gaussiano?

---

## PROMPT 20 — Reflexión final sobre el modelo

> Para cerrar el informe: ¿cuál es, en tu opinión, el aporte genuino de usar
> cálculo vectorial aquí versus simplemente decir "el atacante va al nodo más
> vulnerable"?
>
> Específicamente me interesa si el modelo hace predicciones que la intuición
> informal no haría:
> - El saddle point como cuello de botella: ¿es algo que surge del modelo
>   matemático y no sería obvio sin él?
> - La conservatividad y su implicación defensiva: ¿qué revela que no revelaría
>   un análisis cualitativo?
> - La irrotacionalidad: ¿tiene alguna implicación práctica o es solo una
>   propiedad matemática sin consecuencia operativa?
>
> Quiero que el informe argumente que el cálculo vectorial añade precisión
> real, no solo vocabulario técnico.
