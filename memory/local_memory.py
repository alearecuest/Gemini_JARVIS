import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "jarvis_memory.db")

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recuerdos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            contenido TEXT,
            fecha TEXT
        )
    """)
    conn.commit()
    conn.close()

def guardar_recuerdo_db(contenido: str, categoria: str = "general") -> str:
    inicializar_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO recuerdos (categoria, contenido, fecha) VALUES (?, ?, ?)", (categoria.lower(), contenido, ahora))
    conn.commit()
    conn.close()
    return f"Nota guardada en memoria permanente bajo la categoría '{categoria}'."

def buscar_recuerdos_db(consulta: str = "") -> str:
    inicializar_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if consulta.strip():
        cursor.execute("SELECT categoria, contenido, fecha FROM recuerdos WHERE contenido LIKE ? OR categoria LIKE ? ORDER BY id DESC LIMIT 10", (f"%{consulta}%", f"%{consulta}%"))
    else:
        cursor.execute("SELECT categoria, contenido, fecha FROM recuerdos ORDER BY id DESC LIMIT 10")
    filas = cursor.fetchall()
    conn.close()
    
    if not filas:
        return "No encontré notas guardadas en la memoria permanente que coincidan."
    return "Recuerdos almacenados:\n" + "\n".join([f"- [{cat.upper()}] ({fecha}): {cont}" for cat, cont, fecha in filas])
