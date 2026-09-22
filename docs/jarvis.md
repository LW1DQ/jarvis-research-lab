# CHATGPT

La máquina será un **Ubuntu Server 26.04** y el objetivo es terminar
con:

TU SERVIDOR

│

┌───────────────────┼───────────────────┐

│ │ │

Ollama OpenHands Khoj

modelos locales agente/SDK memoria

│ │ │

└───────────────────┼───────────────────┘

│

MCP

│

┌─────────────┼─────────────┐

│ │ │

PaperQA2 Python NS-3

papers datos experimentos

La arquitectura se apoya en capacidades que los proyectos actuales ya
ofrecen: OpenHands tiene SDK, herramientas, MCP, persistencia,
seguridad/confirmación y workspaces locales o efímeros; PaperQA2 tiene
RAG agentic para papers con citas; Khoj es self-hostable y puede usar
Ollama; y Open Interpreter actual funciona en Linux, soporta MCP y
sandboxing.

# 1. Antes de instalar: hacer un inventario

Conectate por SSH:

ssh usuario@IP_DEL_SERVIDOR

Ejecutá:

hostnamectl

uname -a

lsb_release -a

Luego:

lscpu

free -h

lsblk

df -h

Y GPU:

lspci \| grep -Ei \'vga\|3d\|nvidia\|amd\'

Si NVIDIA:

nvidia-smi

Guardá la salida.

Esto no es un detalle menor: **la elección de modelos Ollama depende
muchísimo de RAM/VRAM**.

# 2. Actualizar Ubuntu

sudo apt update

sudo apt full-upgrade -y

Instalá herramientas:

sudo apt install -y \\

git \\

curl \\

wget \\

unzip \\

jq \\

tree \\

htop \\

tmux \\

build-essential \\

pkg-config \\

ca-certificates \\

gnupg \\

lsb-release \\

python3 \\

python3-pip \\

python3-venv

Comprobá:

python3 \--version

git \--version

curl \--version

# 3. Docker

Ubuntu 26.04 tiene actualmente soporte oficial para Docker mediante los
paquetes de Ubuntu; además, la documentación de Ubuntu 26.04 ya
contempla Docker rootless como opción de seguridad.

Para nuestro primer despliegue yo usaría el Docker de Ubuntu, que es más
sencillo:

sudo apt install -y docker.io docker-compose

Activar:

sudo systemctl enable \--now docker

Comprobar:

sudo systemctl status docker \--no-pager

Agregar tu usuario:

sudo usermod -aG docker \"\$USER\"

Ahora cerrá la sesión SSH:

exit

Volvé a entrar.

Comprobar:

docker run \--rm hello-world

Tiene que funcionar **sin** sudo.

# 4. Crear nuestro directorio de trabajo

mkdir -p \~/research-jarvis

cd \~/research-jarvis

Crearemos:

mkdir -p \\

projects \\

papers \\

thesis \\

datasets \\

experiments \\

notebooks \\

agents \\

mcp \\

config \\

logs \\

backups

Comprobar:

tree -L 2 \~/research-jarvis

# 5. Crear un archivo de configuración central

nano \~/research-jarvis/config/.env

Por ahora:

TZ=America/Argentina/Rio_Gallegos

RESEARCH_ROOT=/home/TU_USUARIO/research-jarvis

OLLAMA_HOST=http://127.0.0.1:11434

KHOJ_PORT=42110

OPENHANDS_PORT=3000

Cambiá:

TU_USUARIO

por tu usuario real.

Protección:

chmod 600 \~/research-jarvis/config/.env

# 6. Instalar Ollama

La instalación oficial actual para Linux sigue siendo:

curl -fsSL https://ollama.com/install.sh \| sh

Comprobar:

ollama \--version

Y:

systemctl status ollama \--no-pager

Comprobar API:

curl http://127.0.0.1:11434/api/tags

Deberías recibir JSON.

# 7. No descarguemos todavía 20 modelos

Primero probemos que funciona.

ollama pull qwen3

Después:

ollama run qwen3

Probá:

Explica qué es ARFIMA-GARCH en términos académicos.

Salir:

/bye

### Importantísimo {#importantísimo .unnumbered}

**No voy a fijar todavía el modelo definitivo.**

Primero necesitamos saber tu hardware.

La configuración puede terminar usando:

modelo general

modelo de coding

modelo rápido

embedding

pero no quiero hacerte descargar 50--100 GB innecesariamente.

# 8. Instalar uv

OpenHands actualmente recomienda uv y Python 3.12 para su instalación
CLI.

Instalar:

curl -LsSf https://astral.sh/uv/install.sh \| sh

Recargar:

source \~/.bashrc

Comprobar:

uv \--version

Y:

uv python install 3.12

Comprobar:

uv python list

# 9. Instalar OpenHands

Esta será nuestra primera pieza importante.

La documentación actual recomienda:

uv tool install openhands \--python 3.12

Ejecutamos:

uv tool install openhands \--python 3.12

Comprobar:

openhands \--version

# 10. Levantar OpenHands

Probemos primero:

openhands serve

La documentación actual indica que el comando comprueba los requisitos
de Docker, descarga las imágenes necesarias y levanta el servidor GUI.

Desde otra máquina podés hacer SSH tunneling:

ssh -L 3000:127.0.0.1:3000 usuario@IP_DEL_SERVIDOR

Y abrir:

http://localhost:3000

### No publiques el puerto 3000 directamente a Internet. {#no-publiques-el-puerto-3000-directamente-a-internet. .unnumbered}

Primera prueba:

Analiza el directorio actual y describe los archivos. No modifiques
nada.

# 11. Configurar OpenHands para trabajar SOLO en nuestro workspace

Nuestro objetivo:

/home/TU_USUARIO/research-jarvis/

No:

/home/TU_USUARIO/

y muchísimo menos:

/

OpenHands tiene herramientas de terminal, edición, navegador y MCP, y
soporta ejecución mediante workspaces Docker/efímeros.

La primera regla de nuestro sistema va a ser:

**El agente trabaja dentro de un workspace controlado.**

# 12. Instalar el SDK de OpenHands

Creamos el proyecto:

cd \~/research-jarvis

mkdir -p agents/core

cd agents/core

Inicializamos:

uv init

Instalar SDK:

uv add openhands-sdk

El SDK actual ofrece APIs Python/REST, agentes, herramientas,
workspaces, MCP, persistencia, seguridad y servidores remotos.

Crear prueba:

nano hello_agent.py

Con:

from openhands.sdk import LLM, Agent, Conversation, Tool

from openhands.tools.terminal import TerminalTool

from openhands.tools.file_editor import FileEditorTool

from openhands.tools.task_tracker import TaskTrackerTool

llm = LLM(

model=\"qwen3\",

)

agent = Agent(

llm=llm,

tools=\[

Tool(name=TerminalTool.name),

Tool(name=FileEditorTool.name),

Tool(name=TaskTrackerTool.name),

\],

)

conversation = Conversation(

agent=agent,

workspace=\"\~/research-jarvis/projects\",

)

conversation.send_message(

\"Describe la estructura del proyecto. No modifiques archivos.\"

)

conversation.run()

**Acá puede ser necesario adaptar la configuración del proveedor/modelo
a la interfaz Ollama concreta del SDK actual.** No quiero inventarte
parámetros que no aparecen en la versión instalada; lo vamos a comprobar
contra la versión exacta una vez instalada.

# 13. PaperQA2

Ahora creamos un entorno separado.

cd \~/research-jarvis

uv venv \--python 3.12 .venv-paperqa

Activar:

source .venv-paperqa/bin/activate

Instalar:

uv pip install \"paper-qa\>=5\"

PaperQA2 actual requiere Python ≥3.11, tiene CLI pqa, workflows agentic
para búsqueda/evidencia/respuesta y soporte de múltiples proveedores
mediante LiteLLM.

Comprobar:

pqa \--help

# 14. Preparar tu biblioteca

Yo organizaría tus papers:

mkdir -p
\~/research-jarvis/papers/{traffic,arfima,garch,foundation-models,ns3,networking}

Por ejemplo:

papers/

├── traffic/

├── arfima/

├── garch/

├── foundation-models/

├── ns3/

└── networking/

Copiá ahí tus PDFs.

# 15. PaperQA2: primera prueba

Probá primero con uno o unos pocos documentos.

La función que queremos validar es:

PDF

↓

PaperQA2

↓

recuperación

↓

evidencia

↓

respuesta

↓

citas

No pasaría todavía toda tu biblioteca.

PaperQA2 actualmente incorpora búsqueda textual local, awareness de
metadata, reranking, contextualización y RAG agentic.

### Punto importante {#punto-importante .unnumbered}

PaperQA2 llama a Semantic Scholar, Crossref y Unpaywall para metadata
cuando corresponde, por lo que **no debemos asumir que todo el pipeline
sea offline solamente porque el LLM sea local**.

Para investigación esto es bueno, porque metadata y citas mejoran; pero
hay que tenerlo presente.

# 16. Khoj

Ahora levantamos la memoria/knowledge base.

Crear:

mkdir -p \~/.khoj

cd \~/.khoj

Descargar compose oficial:

wget
https://raw.githubusercontent.com/khoj-ai/khoj/master/docker-compose.yml

Es exactamente el método documentado actualmente por Khoj.

Editar:

nano docker-compose.yml

### Cambiar obligatoriamente {#cambiar-obligatoriamente .unnumbered}

Buscá:

KHOJ_ADMIN_PASSWORD

y:

KHOJ_DJANGO_SECRET_KEY

Poné valores fuertes y aleatorios.

Podés generar uno:

openssl rand -hex 32

Khoj exige esos valores para una instalación self-hosted correctamente
configurada.

# 17. Conectar Khoj con Ollama

Khoj documenta explícitamente el uso de Ollama mediante OPENAI_BASE_URL.

Como Ollama está en el host y Khoj estará dentro de Docker, **no vamos a
asumir que** 127.0.0.1:11434 **dentro del contenedor apunta al host**.

En Linux agregaremos una ruta del host al compose, normalmente:

extra_hosts:

\- \"host.docker.internal:host-gateway\"

y utilizaremos:

http://host.docker.internal:11434/v1

La URL exacta dependerá de cómo quede el compose actual.

# 18. Arrancar Khoj

cd \~/.khoj

docker compose up -d

Comprobar:

docker compose ps

Logs:

docker compose logs -f

Buscamos:

Khoj is ready to engage

La documentación oficial indica ese mensaje como señal de que el
servidor está listo.

Desde SSH tunnel:

ssh -L 42110:127.0.0.1:42110 usuario@IP_DEL_SERVIDOR

Abrir:

http://localhost:42110

# 19. Conectar tus documentos a Khoj

La idea es que Khoj conozca:

\~/research-jarvis/thesis

\~/research-jarvis/papers

\~/research-jarvis/projects

No todo tu \$HOME.

Khoj está pensado precisamente como sistema self-hosted de knowledge
base, con búsqueda sobre documentos y web, agentes y modelos
configurables.

# 20. Open Interpreter

Acá hay una corrección respecto a nuestra conversación anterior.

**El repositorio oficial actual** openinterpreter/openinterpreter **ya
no es simplemente el viejo paquete Python.**

Actualmente es un agente de coding basado en Rust/Codex, con:

-   Linux;

-   sandbox;

-   MCP;

-   skills;

-   permisos;

-   ACP;

-   AGENTS.md;

-   múltiples harnesses;

-   compatibilidad Codex.

La instalación actual indicada por el proyecto es:

curl -fsSL https://www.openinterpreter.com/install \| sh

Después:

interpreter \--help

Y:

interpreter

# 21. No darle acceso total a Open Interpreter

Éste es un punto crítico.

El servidor contiene:

tesis

papers

datasets

credenciales

Docker

código

Por lo tanto vamos a utilizar:

sandbox

\+

permissions

\+

AGENTS.md

\+

workspace delimitado

El Open Interpreter actual tiene explícitamente capacidades de sandbox,
permisos, hooks, MCP y directorios .agents/skills.

# 22. Crear AGENTS.md

Esto será muy importante.

nano \~/research-jarvis/AGENTS.md

Contenido inicial:

\# Research JARVIS

\## Purpose

This workspace is dedicated to scientific research,

thesis development, academic papers, experiments,

data analysis and reproducible computational work.

\## Rules

1\. Never invent scientific results.

2\. Never invent citations, DOIs or bibliographic metadata.

3\. Never delete research data.

4\. Never overwrite raw datasets.

5\. Never modify experimental results.

6\. Preserve reproducibility.

7\. Keep generated files separate from raw inputs.

8\. Before modifying code, inspect the repository.

9\. Before running expensive experiments, request confirmation.

10\. Cite sources used for scientific claims.

11\. Distinguish evidence, inference and speculation.

12\. Do not publish or upload material without explicit confirmation.

\## Directory rules

raw data:

datasets/

experiments:

experiments/

source code:

projects/

papers:

papers/

thesis:

thesis/

generated notebooks:

notebooks/

Esto es una de las ventajas de la arquitectura actual de Open
Interpreter: utiliza AGENTS.md y .agents/skills como mecanismos
compartidos.

# 23. Crear Skills

mkdir -p \~/research-jarvis/.agents/skills

Primera:

mkdir -p \~/research-jarvis/.agents/skills/research

nano \~/research-jarvis/.agents/skills/research/SKILL.md

Segunda:

mkdir -p \~/research-jarvis/.agents/skills/ns3

Tercera:

mkdir -p \~/research-jarvis/.agents/skills/timeseries

Cuarta:

mkdir -p \~/research-jarvis/.agents/skills/papers

Esto nos permite que distintos agentes sepan cómo trabajar
específicamente con:

papers

NS-3

series temporales

estadística

sin meter todo en un prompt gigantesco.

# 24. Instalar Python científico

Crearía un entorno:

cd \~/research-jarvis

uv venv \--python 3.12 .venv-science

source .venv-science/bin/activate

Instalar:

uv pip install \\

numpy \\

pandas \\

scipy \\

matplotlib \\

statsmodels \\

scikit-learn \\

jupyter \\

openpyxl \\

pyarrow \\

seaborn

Para tu trabajo particular:

uv pip install \\

arch \\

hurst

Después incorporaremos:

tshark

pyshark

scapy

y las herramientas específicas de NS-3.

# 25. Preparar NS-3

No instalaría todavía una segunda versión de NS-3.

Primero detectamos si ya tenés:

which ns3

y:

find \~ -maxdepth 3 -type d -name \"ns-3.45\" 2\>/dev/null

Como tu investigación ya está en NS-3.45, **vamos a conectar tu
instalación existente**, si está disponible, en lugar de duplicarla.

# 26. PostgreSQL / vector DB

Acá cambiaría ligeramente el plan anterior.

**No instalaría PostgreSQL y Qdrant manualmente todavía.**

Khoj ya utiliza una arquitectura de persistencia propia y su deployment
Docker incluye sus componentes correspondientes.

Agregaremos una base aparte solamente cuando descubramos que realmente
necesitamos:

memoria estructurada

\+

metadatos de experimentos

\+

knowledge graph

Eso mantiene la primera versión mucho más simple.

# 27. Crear el Research MCP

Ésta será nuestra primera integración propia.

mkdir -p \~/research-jarvis/mcp/research

cd \~/research-jarvis/mcp/research

uv init

Este MCP tendrá inicialmente solamente:

search_papers

read_paper

search_library

save_research_note

No tendrá:

delete

publish

upload

# 28. Crear el Data MCP

mkdir -p \~/research-jarvis/mcp/data

Herramientas:

analyze_csv

describe_dataset

run_statistics

create_plot

compare_experiments

# 29. Crear NS-3 MCP

mkdir -p \~/research-jarvis/mcp/ns3

Y nuestra interfaz:

list_simulations

run_simulation

read_flowmonitor

parse_logs

extract_pcap

compare_runs

Pero:

run_simulation

debe requerir confirmación.

# 30. Research Agent

Ahora sí:

Research Agent

│

┌─────────────┼─────────────┐

▼ ▼ ▼

PaperQA2 Khoj Web

│ │ │

└─────────────┼─────────────┘

▼

Evidence

La regla:

**ninguna afirmación científica sin trazabilidad a evidencia o
indicación explícita de que es inferencia.**

PaperQA2 es especialmente útil aquí porque sus respuestas están
diseñadas para incorporar citas y su workflow puede iterar sobre
búsqueda y evidencia.

# 31. Data Agent

Después:

Data Agent

│

├── Python

├── pandas

├── scipy

├── statsmodels

├── arch

└── matplotlib

Y algo fundamental para vos:

raw/

↓

analysis/

↓

results/

↓

figures/

Nunca:

raw → agente modifica directamente

# 32. NS-3 Agent

Después:

NS3 Agent

│

├── ns-3.45

├── FlowMonitor

├── PCAP

├── logs

└── Python

Podremos darle órdenes como:

Analizá las 30 repeticiones.

Y deberá generar:

experiments/

└── experiment_001/

├── metadata.json

├── raw/

├── analysis/

├── figures/

└── report.md

# 33. Reviewer Agent

Después:

Reviewer

│

├── tesis

├── papers

├── resultados

├── metodología

└── bibliografía

Tiene que encontrar:

afirmaciones sin evidencia

referencias dudosas

contradicciones

errores metodológicos

repeticiones

resultados mal interpretados

Este agente va a ser especialmente útil para vos.

# 34. Writer Agent

El Writer **no debería buscar libremente**.

Recibe:

evidence package

y produce:

sección

Esto reduce muchísimo las alucinaciones.

# 35. Finalmente: voz

No empezaría con voz.

Cuando todo funcione por texto:

Whisper

↓

Research JARVIS

↓

OpenHands

↓

agent/tool

↓

resultado

↓

TTS

Ahí recién podemos incorporar el concepto JARVIS que veníamos hablando.

# 36. Lo que tendremos después de esta instalación

Tu servidor quedará conceptualmente:

Ubuntu Server 26.04

│

├── Ollama

│

├── OpenHands

│ └── SDK

│

├── Open Interpreter

│

├── Khoj

│

├── PaperQA2

│

├── Python scientific stack

│

├── Docker

│

├── MCP

│ ├── research

│ ├── papers

│ ├── data

│ └── ns3

│

└── \~/research-jarvis

├── thesis

├── papers

├── datasets

├── experiments

└── projects

## Y hay tres cosas que NO haría todavía {#y-hay-tres-cosas-que-no-haría-todavía .unnumbered}

**No instalaría LangGraph.**

OpenHands ya tiene agent state, herramientas, persistencia, MCP y
control suficiente para nuestra primera arquitectura.

**No instalaría STORM todavía.**

PaperQA2 ya nos da una capa científica mucho más específica para papers.
STORM lo podemos integrar después para investigación exploratoria.

**No instalaría 10 agentes.**

Primero:

Research

Data

NS-3

Reviewer

Writer

Eso es suficiente.

# Una corrección importante respecto de lo que te dije antes

**Open Interpreter actual es considerablemente distinto del Open
Interpreter Python clásico.** El repositorio oficial ahora es un agente
Rust/Codex, con sandbox, MCP, skills, ACP y múltiples harnesses. El
propio proyecto aclara que el viejo proyecto Python continúa como fork
mantenido por la comunidad.

Por eso, **en esta instalación usaría el Open Interpreter actual**, no
el viejo pip install open-interpreter que aparece en muchos tutoriales.

También corregiría otra cosa: **no instalaría a ciegas PaperQA2 + Ollama
esperando que todo sea 100 % local**; PaperQA2 puede trabajar con
modelos alternativos/locales, pero su sistema de metadata integra
fuentes externas como Semantic Scholar, Crossref y Unpaywall.

## El orden de ejecución que te recomiendo {#el-orden-de-ejecución-que-te-recomiendo .unnumbered}

No ejecutes todo de una vez.

### BLOQUE A --- infraestructura {#bloque-a-infraestructura .unnumbered}

Ubuntu

↓

Docker

↓

uv

↓

Ollama

### BLOQUE B --- agentes {#bloque-b-agentes .unnumbered}

OpenHands

↓

OpenHands SDK

↓

Open Interpreter

### BLOQUE C --- conocimiento {#bloque-c-conocimiento .unnumbered}

PaperQA2

↓

Khoj

### BLOQUE D --- ciencia {#bloque-d-ciencia .unnumbered}

Python

↓

Data Agent

↓

NS-3 Agent

### BLOQUE E --- integración {#bloque-e-integración .unnumbered}

MCP

↓

Research Agent

↓

Reviewer

↓

Writer

### BLOQUE F --- JARVIS {#bloque-f-jarvis .unnumbered}

voz

↓

orquestador

↓

agentes

↓

herramientas

↓

memoria

**Yo empezaría exactamente por A y no pasaría a B hasta que Ollama,
Docker y los permisos del usuario estén funcionando correctamente.**
Esto además es especialmente relevante porque ya habías tenido problemas
de permisos con /var/run/docker.sock; en Ubuntu 26.04 tenemos incluso la
opción de Docker rootless si después queremos endurecer la seguridad.

Cuando tengas acceso a esa máquina, el primer comando útil es
simplemente:

echo \"=== SISTEMA ===\" && hostnamectl && echo \"=== CPU ===\" && lscpu
\| grep -E \'Model name\|CPU\\(s\\)\' && echo \"=== RAM ===\" && free -h
&& echo \"=== GPU ===\" && lspci \| grep -Ei \'vga\|3d\|nvidia\|amd\'
\|\| true && echo \"=== DISCO ===\" && df -h /

Con esa salida podemos fijar **el modelo Ollama, la configuración Docker
y los límites de memoria del stack**, y después seguir el procedimiento
exactamente sin instalar componentes innecesarios.

# 

# GROK 

**Plan completo y definitivo para Ubuntu Server 26.04**\
\
Todo lo que te recomendé, en orden, listo para ejecutar.

### Resumen de lo que vas a tener {#resumen-de-lo-que-vas-a-tener .unnumbered}

  -------------------------------------------------------------------------------------
  Prioridad   Proyecto             Puerto   Función principal           Tipo
  ----------- -------------------- -------- --------------------------- ---------------
  1           **OpenJarvis**       8000     Cerebro principal + deep    Local-first
                                            research                    

  2           **GPT Researcher**   8001     Investigación profunda con  Investigación
                                            citas                       

  3           **PersonalJarvis**   47821    Interfaz web + voz          Headless
                                            (opcional)                  

  Extra       Ollama               11434    Modelos locales             Motor
  -------------------------------------------------------------------------------------

### Fase 0 -- Preparación del servidor (haz esto primero) {#fase-0-preparación-del-servidor-haz-esto-primero .unnumbered}

Bash

\# Actualizar sistema

sudo apt update && sudo apt upgrade -y

\# Herramientas básicas

sudo apt install -y git curl python3 python3-venv python3-pip
build-essential ufw tmux

\# Verificar

python3 \--version

**Crea tu carpeta de trabajo de tesis:**

Bash

mkdir -p \~/Tesis/{papers,borradores,notas,outputs,scripts}

### Fase 1 -- OpenJarvis (el núcleo) {#fase-1-openjarvis-el-núcleo .unnumbered}

Bash

\# Instalación

curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh \| bash

\# Recargar PATH

source \~/.bashrc

\# Activar modo investigación

jarvis init \--preset deep-research \--force

\# Descargar modelos recomendados

ollama pull qwen3.5:9b

\# Si tienes más de 32 GB de RAM:

\# ollama pull qwen3.5:14b

**Crear servicio systemd:**

Bash

\# Generar API key (cópiala y guárdala)

jarvis auth generate-key

Bash

sudo nano /etc/systemd/system/openjarvis.service

Pega esto (cambia TU_USUARIO):

ini

\[Unit\]

Description=OpenJarvis AI Assistant

After=network.target

Wants=network-online.target

\[Service\]

Type=simple

User=TU_USUARIO

Group=TU_USUARIO

WorkingDirectory=/home/TU_USUARIO

Environment=\"PATH=/home/TU_USUARIO/.local/bin:/usr/local/bin:/usr/bin:/bin\"

Environment=\"HOME=/home/TU_USUARIO\"

ExecStart=/home/TU_USUARIO/.local/bin/jarvis serve \--host 0.0.0.0
\--port 8000

Restart=always

RestartSec=8

StandardOutput=journal

StandardError=journal

\[Install\]

WantedBy=multi-user.target

Bash

sudo systemctl daemon-reload

sudo systemctl enable \--now openjarvis

sudo systemctl status openjarvis

### Fase 2 -- GPT Researcher {#fase-2-gpt-researcher .unnumbered}

Bash

cd \~

git clone https://github.com/assafelovic/gpt-researcher.git

cd gpt-researcher

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

Crea el archivo .env:

Bash

nano .env

Contenido recomendado (elige una opción):

**Opción A -- Con API (mejor calidad):**

env

OPENAI_API_KEY=tu_clave_openai

TAVILY_API_KEY=tu_clave_tavily

**Opción B -- 100% local (usando Ollama):**

env

OPENAI_BASE_URL=http://localhost:11434/v1

OPENAI_API_KEY=ollama

FAST_LLM=ollama:qwen3.5:9b

SMART_LLM=ollama:qwen3.5:9b

**Crear servicio systemd:**

Bash

sudo nano /etc/systemd/system/gpt-researcher.service

ini

\[Unit\]

Description=GPT Researcher

After=network.target openjarvis.service

\[Service\]

Type=simple

User=TU_USUARIO

Group=TU_USUARIO

WorkingDirectory=/home/TU_USUARIO/gpt-researcher

Environment=\"PATH=/home/TU_USUARIO/gpt-researcher/.venv/bin:/usr/local/bin:/usr/bin:/bin\"

ExecStart=/home/TU_USUARIO/gpt-researcher/.venv/bin/uvicorn main:app
\--host 0.0.0.0 \--port 8001

Restart=always

RestartSec=8

StandardOutput=journal

StandardError=journal

\[Install\]

WantedBy=multi-user.target

Bash

sudo systemctl daemon-reload

sudo systemctl enable \--now gpt-researcher

sudo systemctl status gpt-researcher

### Fase 3 -- PersonalJarvis (opcional pero recomendado) {#fase-3-personaljarvis-opcional-pero-recomendado .unnumbered}

Bash

curl -fsSL
https://raw.githubusercontent.com/PersonalJarvis/PersonalJarvis/main/install/install.sh
\| bash -s \-- \--headless

**Crear servicio:**

Bash

sudo nano /etc/systemd/system/personal-jarvis.service

ini

\[Unit\]

Description=PersonalJarvis Headless

After=network.target

\[Service\]

Type=simple

User=TU_USUARIO

Group=TU_USUARIO

WorkingDirectory=/home/TU_USUARIO/.personal-jarvis

Environment=\"PATH=/home/TU_USUARIO/.personal-jarvis/.venv/bin:/usr/local/bin:/usr/bin:/bin\"

ExecStart=/home/TU_USUARIO/.personal-jarvis/.venv/bin/jarvis serve

Restart=always

RestartSec=8

\[Install\]

WantedBy=multi-user.target

Bash

sudo systemctl daemon-reload

sudo systemctl enable \--now personal-jarvis

### Fase 4 -- Seguridad y acceso {#fase-4-seguridad-y-acceso .unnumbered}

Bash

\# Firewall

sudo ufw default deny incoming

sudo ufw default allow outgoing

sudo ufw allow OpenSSH

sudo ufw allow 8000/tcp \# OpenJarvis

sudo ufw allow 8001/tcp \# GPT Researcher

sudo ufw allow 47821/tcp \# PersonalJarvis

sudo ufw enable

sudo ufw status

**Recomendación fuerte de seguridad:**

-   No expongas los puertos directamente a internet.

-   Usa **SSH tunnel** o un reverse proxy con Nginx + HTTPS (Cloudflare
    > Tunnel o Let's Encrypt).

### Fase 5 -- Comandos de administración diarios {#fase-5-comandos-de-administración-diarios .unnumbered}

Bash

\# Ver estado de todo

sudo systemctl status openjarvis gpt-researcher personal-jarvis

\# Reiniciar uno

sudo systemctl restart openjarvis

\# Ver logs en vivo

journalctl -u openjarvis -f

journalctl -u gpt-researcher -f

\# Detener temporalmente

sudo systemctl stop openjarvis

### Cómo usar todo para tu tesis {#cómo-usar-todo-para-tu-tesis .unnumbered}

1.  **OpenJarvis** → investigación diaria, resumir papers, generar
    > esquemas, responder preguntas sobre tu tema.

2.  **GPT Researcher** → literature review larga y bien citada.

3.  **PersonalJarvis** → interfaz web más amigable + voz desde el
    > navegador.

4.  Guarda siempre los resultados en \~/Tesis/outputs/.

### Orden final de ejecución (cópialo y ve paso a paso) {#orden-final-de-ejecución-cópialo-y-ve-paso-a-paso .unnumbered}

1.  Fase 0 (preparación)

2.  Fase 1 (OpenJarvis + systemd)

3.  Fase 2 (GPT Researcher + systemd)

4.  Fase 3 (PersonalJarvis -- opcional)

5.  Fase 4 (firewall)

6.  Probar todo desde el navegador o con curl

# DEEPSEEK

### Plan de Instalación y Configuración {#plan-de-instalación-y-configuración .unnumbered}

Este plan está diseñado para ser modular. Puedes empezar con el **Núcleo
Esencial** y luego añadir herramientas según tus necesidades.

#### Fase 0: Preparación del Entorno (Requisitos Previos) {#fase-0-preparación-del-entorno-requisitos-previos .unnumbered}

Antes de empezar, asegúrate de tener instalado lo siguiente:

1.  **Python 3.11 o superior**: Casi todas las herramientas lo
    > requieren.

2.  **Git**: Para clonar los repositorios.

3.  **Node.js y npm**: Necesario para algunas herramientas y la gestión
    > de paquetes.

4.  **Un gestor de paquetes**: pip (para Python) y, opcionalmente, uv
    > (para Hypo-Research).

5.  **VS Code**: Especialmente si planeas usar el *Research Workflow
    > Assistant*.

#### Fase 1: El Núcleo Esencial (Recomendación Principal) {#fase-1-el-núcleo-esencial-recomendación-principal .unnumbered}

Este es el combo que te recomiendo instalar primero para cubrir el flujo
de trabajo principal de tu tesis.

##### 1. JARVIS Research OS (Para Revisiones Sistemáticas) {#jarvis-research-os-para-revisiones-sistemáticas .unnumbered}

Esta herramienta es tu \"cerebro\" principal para automatizar la
revisión de literatura.

-   **Clonar el repositorio**:

    bash

    git clone https://github.com/kaneko-ai/jarvis-ml-pipeline.git

    cd jarvis-ml-pipeline

-   **Crear y activar un entorno virtual** (recomendado):

    -   **Windows**:

        bash

        python -m venv .venv

        .\\.venv\\Scripts\\Activate.ps1

    -   **Linux/macOS**:

        bash

        python -m venv .venv

        source .venv/bin/activate

-   **Instalar la herramienta**:

    bash

    pip install -e .

    Esto instalará el paquete jarvis-research-os en modo editable.

-   **Configuración de LLMs**: JARVIS usa LiteLLM para acceder a
    > múltiples modelos (Gemini, OpenAI, DeepSeek, etc.). Necesitarás
    > configurar tus claves API. Revisa la documentación del proyecto
    > para más detalles.

-   **Verificar la instalación**:

    bash

    jarvis \--version

    Deberías ver algo como v2.0.0.

##### 2. OpenWorkers (Para Verificación de Citas y Afirmaciones) {#openworkers-para-verificación-de-citas-y-afirmaciones .unnumbered}

Esta herramienta te ayudará a auditar la veracidad de tus afirmaciones y
citas, asegurando que todo esté respaldado.

-   **Descarga e instalación**: La forma más sencilla es descargar el
    > instalador para tu sistema operativo desde la página de [GitHub
    > Releases](https://github.com/different-ai/openwork/releases) o
    > desde el sitio oficial
    > [openworklabs.com/download](https://openworklabs.com/download).

-   **Integración con otros agentes**: Una vez instalado, puedes
    > añadirlo como un servidor MCP a otros agentes como Codex o Claude
    > Code.

    -   **Para Codex**:

        bash

        codex mcp add openwork \--url
        https://api.openworklabs.com/mcp/agent

    -   **Para Claude Code**:

        bash

        claude mcp add \--transport http openwork
        https://api.openworklabs.com/mcp/agent

#### Fase 2: Herramientas de Exploración y Redacción (Opcional pero Recomendado) {#fase-2-herramientas-de-exploración-y-redacción-opcional-pero-recomendado .unnumbered}

Añade estas herramientas para tareas más específicas.

##### 3. Orca (Para Investigación Conversacional) {#orca-para-investigación-conversacional .unnumbered}

Ideal para consultas rápidas y exploración de temas de forma
conversacional.

-   **Instalación**:

    -   **Windows**: Descarga el instalador .exe desde GitHub Releases.

    -   **macOS**: Puedes usar Homebrew: brew install \--cask
        > stablyai/orca/orca o descargar el .dmg.

    -   **Linux**: Descarga el .deb o el AppImage desde GitHub Releases.

-   **Configuración**: Después de instalar, necesitarás configurar las
    > claves API para las fuentes de datos (Semantic Scholar, arXiv,
    > etc.) en un archivo de configuración.

##### 4. Hypo-Research (Para Habilidades Específicas de Redacción y Revisión) {#hypo-research-para-habilidades-específicas-de-redacción-y-revisión .unnumbered}

Excelente para tareas concretas como simular el proceso de revisión por
pares o generar respuestas a los revisores.

-   **Requisito**: Esta herramienta **requiere** uv para la gestión de
    > dependencias. Instálalo primero: pip install uv.

-   **Clonar e instalar**:

    bash

    git clone https://github.com/HypoxanthineOvO/Hypo-Research.git

    cd Hypo-Research

    uv sync

-   **Verificar**:

    bash

    uv run hypo-research \--help

-   **Instalar Skills (para Codex/Claude)**: Si usas Codex o Claude,
    > puedes instalar los skills para integrarlos directamente:

    bash

    bash install-skills.sh

#### Fase 3: Herramientas de Flujo de Trabajo Integral (Para un Enfoque Más Estructurado) {#fase-3-herramientas-de-flujo-de-trabajo-integral-para-un-enfoque-más-estructurado .unnumbered}

Si prefieres un entorno más integrado, considera estas opciones.

##### 5. Research Workflow Assistant (Para VS Code) {#research-workflow-assistant-para-vs-code .unnumbered}

Perfecto si tu flujo de trabajo está centrado en VS Code y GitHub
Copilot.

-   **Clonar el repositorio**:

    bash

    git clone
    https://github.com/Intersect-Collaborations-LLC/research-workflow-assistant.git

    cd research-workflow-assistant

-   **Instalar dependencias**:

    bash

    pip install -e mcp-servers/\_shared

-   **Configuración interactiva**: Abre el proyecto en VS Code, abre el
    > chat de Copilot y escribe \@setup para seguir una guía de
    > configuración interactiva. Si algo falla, usa \@troubleshooter.

##### 6. AcadClaw (Para el Ciclo de Vida Completo de la Investigación) {#acadclaw-para-el-ciclo-de-vida-completo-de-la-investigación .unnumbered}

Cubre todo el espectro, desde la búsqueda de literatura hasta la
revisión del paper.

-   **Clonar e instalar**:

    bash

    git clone \<repo-url\> \# Reemplaza con la URL del repo

    cd acadclaw

    python -m venv venv

    source venv/bin/activate \# En Windows:
    .\\venv\\Scripts\\activate.ps1

    pip install -e \".\[academic\]\"

-   **Verificar**:

    bash

    acadclaw \--version

-   **Configurar modelos**:

    bash

    acadclaw provider setup \--provider deepseek \--api-key
    \<TU_API_KEY\> \--model deepseek-V4-pro

    Puedes configurar otros proveedores como OpenAI, Anthropic u Ollama.

### 💡 Recomendación Final de Implementación {#recomendación-final-de-implementación .unnumbered}

1.  **Comienza con el Núcleo**: Instala **JARVIS Research OS** y
    > **OpenWorkers**. Esto te dará una base sólida para la revisión de
    > literatura y la verificación de hechos.

2.  **Añade Orca** para la exploración inicial y consultas rápidas.

3.  **Incorpora Hypo-Research** cuando necesites funciones específicas
    > como la simulación de revisión por pares o la generación de
    > respuestas.

4.  **Evalúa las herramientas de flujo de trabajo** (Research Workflow
    > Assistant y AcadClaw) si necesitas una integración más profunda
    > con tu entorno de desarrollo o un enfoque más estructurado.

# CHATGPT

# 1. Preparar Ubuntu

Primero:

sudo apt update

sudo apt upgrade -y

Instalar herramientas base:

sudo apt install -y \\

git \\

curl \\

wget \\

unzip \\

build-essential \\

python3 \\

python3-venv \\

python3-pip \\

jq \\

tree \\

htop \\

tmux

Comprobar:

python3 \--version

git \--version

docker \--version

docker compose version

Para OpenHands, la documentación actual recomienda **Python 3.12** y uv.

# 2. Primero arreglar Docker

Esto es particularmente importante en tu caso porque ya habías tenido el
problema:

permission denied while trying to connect to Docker

unix:///var/run/docker.sock

Comprobamos:

sudo systemctl status docker

Después:

sudo usermod -aG docker \$USER

Y verificamos:

getent group docker

Después hay que **cerrar completamente la sesión y volver a entrar**
para que el grupo se aplique.

Luego:

docker run hello-world

Tiene que funcionar **sin** sudo.

No continuaría con OpenHands hasta que esto funcione.

# 3. Crear la estructura de Research JARVIS

mkdir -p \~/research-jarvis

cd \~/research-jarvis

Crear:

mkdir -p \\

projects \\

papers \\

thesis \\

datasets \\

experiments \\

notebooks \\

memory \\

agents \\

mcp \\

logs \\

config \\

backups

Quedará:

\~/research-jarvis/

projects/

papers/

thesis/

datasets/

experiments/

notebooks/

memory/

agents/

mcp/

logs/

config/

backups/

Yo pondría acá tus proyectos existentes, **no directamente en** \$HOME.

Por ejemplo:

projects/

├── tfi/

├── ns3/

├── traffic-timeseries/

└── papers/

# 4. Instalar Ollama

Ollama será el proveedor local de modelos.

Instalación oficial:

curl -fsSL https://ollama.com/install.sh \| sh

Comprobar:

ollama \--version

Y:

systemctl status ollama

Probar:

ollama run qwen3

No descargues todavía 10 modelos.

**Primero probamos uno.**

Después elegiremos:

general

coding

embeddings

small/fast

dependiendo del hardware.

Ollama puede actuar como servidor local para los componentes que acepten
APIs compatibles. PaperQA2, por ejemplo, documenta el uso de modelos
locales mediante servidores compatibles.

# 5. Crear entorno Python general

Instalamos uv:

curl -LsSf https://astral.sh/uv/install.sh \| sh

Cerrar/abrir terminal o cargar:

source \~/.bashrc

Comprobar:

uv \--version

Crear entorno:

cd \~/research-jarvis

uv venv \--python 3.12

Activar:

source .venv/bin/activate

Pero **no meteremos todo en este mismo entorno**.

Esto es importante.

Tendremos:

OpenHands → entorno propio

PaperQA2 → entorno propio

Open Interpreter → entorno propio

Así evitamos el infierno de dependencias.

# 6. Instalar OpenHands

Éste será nuestro primer agente.

La documentación actual recomienda:

uv tool install openhands \--python 3.12

Luego:

openhands serve

OpenHands también permite:

openhands serve \--mount-cwd

y:

openhands serve \--gpu

cuando corresponde.

Yo **empezaría con Docker/sandbox**, no con acceso completo a tu Ubuntu.

La arquitectura de OpenHands permite utilizar el equipo local como
workspace o ejecutar agentes dentro de workspaces efímeros, por ejemplo
Docker/Kubernetes.

Abrimos:

http://localhost:3000

La documentación oficial indica ese puerto para la instalación Docker.

### Primera prueba {#primera-prueba .unnumbered}

Darle acceso solamente a:

\~/research-jarvis/projects/

y pedir:

Analiza este proyecto y explícame su estructura. No modifiques ningún
archivo.

Si eso funciona, tenemos el **primer componente operativo**.

# 7. Instalar OpenHands SDK

Además del servidor GUI, nos interesa el SDK porque después vamos a
crear **nuestro propio Research Agent**.

El repositorio actual muestra una API basada en:

from openhands.sdk import LLM, Agent, Conversation, Tool

y herramientas para terminal, edición de archivos y seguimiento de
tareas.

Creamos:

cd \~/research-jarvis

mkdir -p agents/openhands

cd agents/openhands

uv init

Luego:

uv add openhands-sdk

y hacemos nuestro primer agente de prueba.

Todavía no vamos a construir el JARVIS completo.

# 8. Instalar PaperQA2

Creamos un entorno separado:

cd \~/research-jarvis

uv venv \--python 3.12 .venv-paperqa

source .venv-paperqa/bin/activate

Instalar:

uv pip install \"paper-qa\>=5\"

PaperQA2 versión 5 requiere Python 3.11 o superior y su instalación
básica es pip install paper-qa.

Para embeddings locales:

uv pip install \"paper-qa\[local\]\"

La documentación actual recomienda paper-qa\[local\] para utilizar
embeddings locales.

# 9. Primera biblioteca científica

Crear:

mkdir -p \~/research-jarvis/papers

Podés copiar algunos de tus papers:

papers/

├── traffic/

├── arfima/

├── garch/

├── foundation-models/

├── sundial/

└── ns3/

Probar PaperQA2:

cd \~/research-jarvis/papers/traffic

pqa ask \"¿Qué evidencia existe de dependencia de largo alcance en
tráfico de redes?\"

PaperQA2 utiliza un índice de documentos y recupera pasajes para
construir respuestas basadas en las fuentes.

### Esto es importante {#esto-es-importante .unnumbered}

Primero quiero que funcione **con tus PDFs reales**.

Antes de integrar agentes.

# 10. Conectar PaperQA2 a modelos locales

Acá no recomiendo inventar una configuración todavía.

PaperQA2 ha cambiado bastante en los últimos años y existen diferentes
vías para conectar modelos locales. La documentación actual permite
utilizar servidores OpenAI-compatible/LiteLLM y Ollama aparece entre los
escenarios documentados por el proyecto/comunidad.

La estrategia será:

PaperQA2

↓

LiteLLM / compatible endpoint

↓

Ollama

↓

modelo local

Pero primero hacemos funcionar:

PaperQA2 + configuración estándar

y luego sustituimos el LLM.

Eso nos da una instalación fácil de depurar.

# 11. Instalar Khoj

Acá utilizaría **Docker**, no Python.

La documentación actual de Khoj recomienda exactamente este método de
self-hosting:

mkdir \~/.khoj

cd \~/.khoj

wget
https://raw.githubusercontent.com/khoj-ai/khoj/master/docker-compose.yml

Luego:

docker compose up

Khoj documenta que puede conectarse a Ollama mediante una URL compatible
con OpenAI, y que su búsqueda puede utilizar modelos locales.

El docker-compose.yml actual incluye:

PostgreSQL/pgvector

sandbox

SearXNG

computer

Khoj server

y publica Khoj en:

42110

según el compose actual.

Accedemos:

http://localhost:42110

# 12. Configurar Khoj como memoria

Acá vamos a tener:

\~/research-jarvis/thesis

\~/research-jarvis/papers

\~/research-jarvis/projects

\~/research-jarvis/experiments

y Khoj va a indexar esos contenidos.

Khoj tiene integración específica con Obsidian y permite consultas sobre
notas privadas y web.

Yo convertiría:

Obsidian

↓

Knowledge Base

↓

Khoj

en tu **memoria humana + conocimiento del proyecto**.

# 13. Instalar Open Interpreter

Ahora agregamos la parte de ejecución.

El instalador Linux oficial actual existe:

curl -sL
https://raw.githubusercontent.com/openinterpreter/open-interpreter/main/installers/oi-linux-installer.sh
\| bash

El proyecto también documenta instalación mediante Python/pip.

Pero acá **prefiero no darle acceso total al sistema**.

Primero:

Open Interpreter

↓

Docker sandbox

↓

\~/research-jarvis/projects

Porque estamos creando un agente que puede ejecutar código y comandos.

# 14. MCP

Una vez funcionando:

OpenHands

PaperQA2

Khoj

Open Interpreter

recién ahí introducimos MCP.

La arquitectura:

JARVIS

│

MCP Client

│

┌─────────────┼─────────────┐

▼ ▼ ▼

Papers Python NS3

│ │ │

PaperQA2 scipy ns-3

Nuestro primer MCP server sería:

### research-mcp {#research-mcp .unnumbered}

con:

search_papers()

read_paper()

save_note()

search_knowledge()

Después:

### python-mcp {#python-mcp .unnumbered}

run_python()

run_notebook()

analyze_csv()

plot_data()

Después:

### ns3-mcp {#ns3-mcp .unnumbered}

run_simulation()

list_runs()

read_flowmonitor()

analyze_pcap()

compare_runs()

# 15. Crear tu primer Research Agent

Acá recién aparece realmente tu JARVIS.

ResearchAgent

│

├── PaperQA2

├── Khoj

├── Web

├── MCP

└── OpenHands

Podrías decir:

"Investiga el estado del arte sobre predicción probabilística del
tráfico de red y encuentra evidencia sobre ARFIMA-GARCH y foundation
models."

Y tendría que:

1\. buscar

2\. recuperar

3\. leer

4\. contrastar

5\. citar

6\. guardar

7\. responder

No queremos todavía voz.

# 16. Segundo agente: Data Agent

Este será especialmente importante para vos.

DataAgent

│

├── Python

├── pandas

├── numpy

├── scipy

├── statsmodels

├── arch

├── matplotlib

└── NS-3

Ejemplo:

"Tomá los resultados de las 30 repeticiones y buscá diferencias entre
protocolos."

El agente:

CSV

↓

Python

↓

estadística

↓

test

↓

gráficos

↓

informe

# 17. Tercer agente: Paper Reviewer

Este lo considero obligatorio.

Le damos:

ReviewerAgent

y reglas:

NO inventar citas

NO inventar resultados

NO modificar resultados

NO asumir que algo es verdadero

SEÑALAR evidencia faltante

SEÑALAR contradicciones

Podrías darle:

"Revisá este capítulo como jurado de una maestría."

Y el sistema usaría:

tesis

\+

bibliografía

\+

PaperQA2

\+

criterios de revisión

# 18. Writer Agent

Último agente de la primera versión:

WriterAgent

Su regla fundamental:

Evidence → Writer

Nunca:

LLM → Writer → inventar

Ejemplo:

"Redactá la sección de resultados usando exclusivamente estos
resultados."

El agente genera texto, pero el origen queda identificado.

# 19. Recién entonces agregamos voz

Cuando todo lo anterior funcione:

Whisper

↓

JARVIS

↓

Research Agent

↓

PaperQA2 / OpenHands / Python

↓

TTS

Y podés decir:

"JARVIS, ¿qué papers nuevos hay sobre foundation models para series
temporales?"

o:

"JARVIS, analizá la simulación número 27."

Ahí sí empieza a parecerse al JARVIS que tenés en mente.

# 20. Estructura final

Al final quiero que tu máquina tenga algo así:

\~/research-jarvis/

├── agents/

│ ├── researcher/

│ ├── data/

│ ├── reviewer/

│ ├── writer/

│ └── ns3/

│

├── papers/

│ ├── traffic/

│ ├── arfima/

│ ├── garch/

│ └── foundation-models/

│

├── thesis/

│

├── projects/

│ ├── tfi/

│ ├── ns3/

│ └── experiments/

│

├── datasets/

│

├── experiments/

│

├── notebooks/

│

├── mcp/

│ ├── research/

│ ├── python/

│ └── ns3/

│

├── memory/

│

├── logs/

│

└── backups/

Y los servicios:

localhost:3000 OpenHands

localhost:42110 Khoj

localhost:11434 Ollama

más los MCP servers y los procesos Python.

# Lo que NO haría

No instalaría inicialmente:

STORM

Robin

Finch

LangGraph

AutoGen

CrewAI

14 agentes

voz

avatar

camera

smart-home

No porque sean malos.

Sino porque **ahora mismo no los necesitamos**.

Primero:

Ollama

↓

OpenHands

↓

PaperQA2

↓

Khoj

↓

Open Interpreter

↓

MCP

↓

Research Agent

Cuando eso esté sólido, incorporamos las mejores ideas de STORM, Finch y
Microsoft JARVIS.

## Y hay una mejora que haría desde el principio {#y-hay-una-mejora-que-haría-desde-el-principio .unnumbered}

No pondría todos los programas directamente sobre tu Ubuntu.

Usaría:

Ubuntu

│

┌──────┴──────┐

│ Docker │

└──────┬──────┘

│

┌───────────────┼────────────────┐

▼ ▼ ▼

OpenHands Khoj Sandboxes

│ │

└───────┬───────┘

▼

Ollama

y conservaría tus datos reales fuera de los contenedores, montando
**solo los directorios necesarios**. OpenHands y Khoj tienen
soporte/documentación actual para este tipo de despliegue en
Linux/Docker.

### Orden práctico {#orden-práctico .unnumbered}

**Paso 1:** arreglar Docker.\
**Paso 2:** instalar Ollama.\
**Paso 3:** levantar OpenHands.\
**Paso 4:** levantar PaperQA2.\
**Paso 5:** levantar Khoj.\
**Paso 6:** instalar Open Interpreter.\
**Paso 7:** conectar Ollama.\
**Paso 8:** MCP.\
**Paso 9:** Research Agent.\
**Paso 10:** Data/NS-3 Agent.\
**Paso 11:** Reviewer + Writer.\
**Paso 12:** voz y automatización.

Y yo lo haría **de manera interactiva, comando por comando**,
comprobando cada etapa antes de pasar a la siguiente. Así, si algo
falla, sabemos exactamente qué componente lo produjo en lugar de
terminar con ocho servicios instalados y sin saber cuál está roto.

**Podemos empezar directamente por el Paso 1 en tu Ubuntu: Docker +
estructura base + Ollama**, y te voy dando los comandos exactos y qué
resultado deberías obtener después de cada uno.
