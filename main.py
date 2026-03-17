import os
import sys
import argparse
import threading
import config
from workflow import app
from dotenv import load_dotenv

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.theme import Theme
from rich import box

load_dotenv()

# ---------------------------------------------------------------------------
# Tema de colores
# ---------------------------------------------------------------------------
tema = Theme({
    "usuario":  "bold cyan",
    "agente":   "bold green",
    "nodo":     "bold yellow",
    "debug":    "dim magenta",
    "error":    "bold red",
    "aviso":    "bold orange1",
    "titulo":   "bold white on blue",
    "keyword":  "bold yellow",
})
console = Console(theme=tema)

# Palabras clave SQL / dominio que se resaltan en la respuesta final
KEYWORDS = [
    "SELECT", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY",
    "AVG", "MAX", "MIN", "COUNT", "SUM",
    "cliente", "clientes", "producto", "productos",
    "venta", "ventas", "reseña", "reseñas", "calificación", "inventario",
]

NOMBRES_NODOS = {
    "router":    "🔀 Router",
    "sql_agent": "🗄️  Agente SQL",
    "web_agent": "🌐 Agente Web",
}


def resaltar(texto: str) -> Text:
    """Devuelve un objeto rich.Text con palabras clave resaltadas."""
    t = Text(texto)
    for kw in KEYWORDS:
        t.highlight_words([kw], style="keyword")
        t.highlight_words([kw.lower()], style="keyword")
        t.highlight_words([kw.capitalize()], style="keyword")
    return t


def verificar_claves():
    for nombre in ("DEEPSEEK_API_KEY", "TAVILY_API_KEY"):
        if not os.environ.get(nombre):
            console.print(
                f"[aviso]⚠  Advertencia:[/aviso] no se encontró "
                f"[bold]{nombre}[/bold] en las variables de entorno."
            )


def ejecutar_debug(initial_state: dict) -> dict:
    """Modo debug: muestra la actividad interna de cada nodo en tiempo real."""
    console.print()
    for event in app.stream(initial_state, stream_mode="updates"):
        for nodo, valor in event.items():
            if nodo == "__end__":
                continue
            nombre = NOMBRES_NODOS.get(nodo, nodo)
            console.print(f"[nodo]▶  Nodo:[/nodo] {nombre}")
            if isinstance(valor, dict) and "messages" in valor:
                for msg in valor["messages"]:
                    contenido = getattr(msg, "content", str(msg))
                    tipo = type(msg).__name__
                    console.print(f"   [debug][{tipo}][/debug] {contenido[:300]}")
    # invoke para obtener el estado final completo
    return app.invoke(initial_state)


def ejecutar_produccion(initial_state: dict) -> dict:
    """Modo producción: spinner mientras el grafo procesa en un hilo."""
    resultado: dict = {}
    excepcion: list = [None]

    def _invocar():
        try:
            resultado.update(app.invoke(initial_state))
        except Exception as e:
            excepcion[0] = e

    hilo = threading.Thread(target=_invocar, daemon=True)
    hilo.start()

    with Live(
        Spinner("dots", text=" [bold cyan]Procesando…[/bold cyan]"),
        console=console,
        refresh_per_second=12,
    ):
        hilo.join()

    if excepcion[0]:
        raise excepcion[0]

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description="Agente Text2SQL — interfaz de línea de comandos"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Activa el modo debug: muestra la actividad interna de cada nodo.",
    )
    args = parser.parse_args()
    config.DEBUG = args.debug  # activa prints internos en nodes/tools/workflow

    console.print(Panel(
        "[titulo]  Agente Text2SQL — Sistema Multi-Agente  [/titulo]\n"
        f"Modo: [bold]{'🐛 DEBUG' if args.debug else '🚀 PRODUCCIÓN'}[/bold]\n"
        "Escribe [bold cyan]salir[/bold cyan] o [bold cyan]exit[/bold cyan] para terminar.",
        box=box.DOUBLE_EDGE,
        border_style="blue",
    ))

    verificar_claves()

    while True:
        try:
            console.print()
            pregunta = console.input("[usuario]Tú:[/usuario] ").strip()
            if not pregunta:
                continue
            if pregunta.lower() in ["salir", "exit", "quit"]:
                console.print("[agente]👋  ¡Hasta luego![/agente]")
                break

            initial_state = {
                "question": pregunta,
                "messages": [],
                "iterations": 0,
            }

            if args.debug:
                final_state = ejecutar_debug(initial_state)
            else:
                final_state = ejecutar_produccion(initial_state)

            respuesta = final_state["messages"][-1]
            contenido = getattr(respuesta, "content", str(respuesta))

            console.print()
            console.print(Panel(
                resaltar(contenido),
                title="[agente]🤖 Agente[/agente]",
                border_style="green",
                box=box.ROUNDED,
            ))

        except KeyboardInterrupt:
            console.print("\n[agente]👋  ¡Hasta luego![/agente]")
            break
        except Exception as e:
            console.print(f"[error]✖  Error:[/error] {e}")


if __name__ == "__main__":
    main()
