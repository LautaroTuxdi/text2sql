# Agente Text2SQL — Setup rápido

## Consigna elegida

Elegimos la consigna 2: Agente(s) text2SQL de asistencia a clientes - - -
Dada una base de datos de una empresa (por ej., ventas, inventario, clientes, reviews), desarrollar un agente que pueda traducir consultas en lenguaje natural de clientes, a una (o más) consultas SQL/tablas, cuyos resultados luego deben ensamblarse para responder al cliente.
La interfaz puede diseñarse como un chatbot unificado, que internamente puede conectar en forma flexible a más de un agente o fuente de conocimiento. Algunas de estas fuentes de conocimiento podrían incluir búsqueda web.
Se recomienda incluir un agente "ruteador" que direccione las distintas consultas.

## Participantes

- Defelippe Lautaro
- Defelippe Fabricio

Este repositorio monta un flujo multi-agente (router → SQL agent → Web agent) usando `langgraph`.

Requisitos
- Python 3.10+ recomendado

Variables de entorno
- Copia `.env.example` a `.env` y añade tus claves:
  - `DEEPSEEK_API_KEY` — usada por el LLM (endpoint OpenAI-compatible)
  - `TAVILY_API_KEY` — usada por la herramienta de búsqueda Tavily

Pasos de instalación
```powershell
# Crear y activar venv
python -m venv venv

source .venv/bin/activate        # Linux/Mac
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process .\venv\Scripts\Activate.ps1        # Windows

# Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Alternativa en cmd.exe
```cmd
python -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Crear la base de datos de ejemplo
```powershell
python mock_db.py
```
Esto generará `retail.db` con tablas y datos de prueba.

Uso de las claves
- `DEEPSEEK_API_KEY`: se lee desde `load_dotenv()` y se pasa al cliente `ChatOpenAI` en `nodes.py` para conectarse al endpoint de DeepSeek.
- `TAVILY_API_KEY`: se usa internamente por `TavilySearchResults` (inicializada en `main.py`) para autenticar las búsquedas cuando el flujo enrutado llega al agente web.

Ejecutar la aplicación (smoke test)
```powershell
python main.py
```
Escribe una consulta de ejemplo (por ejemplo: "¿Cuáles son los 5 productos más vendidos?") y observa cómo el router envía la petición al agente SQL o al agente web según corresponda.

Notas y debugging
- Si falta una clave, `main.py` imprimirá una advertencia al iniciar.
- Para ver mensajes de debug, revisa los `print()` en `main.py` y `tools.py` (por ejemplo, `run_sql_query` imprime la consulta ejecutada).

Seguridad SQL
- El SQL Agent tiene un filtro que **rechaza automáticamente** sentencias `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`.
- Solo se permiten sentencias `SELECT` (o `WITH` que desemboque en un `SELECT`).
- También se rechazan consultas que contengan múltiples sentencias separadas por `;`.

Archivos importantes
- `main.py` — inicializa herramientas y flujo
- `nodes.py` — definición del LLM y agentes
- `tools.py` — herramientas `run_sql_query`, `get_db_schema`, `tavily_tool`
- `mock_db.py` — crea `retail.db` de prueba
- `.env.example` — ejemplar de variables de entorno
