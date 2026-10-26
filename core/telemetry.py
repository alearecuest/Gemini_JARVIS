import sqlite3
import datetime
from memory.local_memory import DB_PATH, inicializar_db

class TelemetryLogger:
    """Registra métricas de inferencia (latencia, modelo, tokens y estado) al estilo OpenJarvis Traces."""

    @staticmethod
    def _asegurar_tabla():
        inicializar_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                modelo TEXT,
                latencia_ms INTEGER,
                tokens_total INTEGER,
                consulta TEXT
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_traza(modelo: str, latencia_ms: int, tokens_total: int, consulta: str):
        try:
            TelemetryLogger._asegurar_tabla()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO agent_traces (fecha, modelo, latencia_ms, tokens_total, consulta) VALUES (?, ?, ?, ?, ?)",
                (ahora, modelo, latencia_ms, tokens_total, consulta[:120])
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    @staticmethod
    def obtener_resumen() -> dict:
        try:
            TelemetryLogger._asegurar_tabla()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), AVG(latencia_ms), SUM(tokens_total) FROM agent_traces")
            total_calls, avg_lat, sum_tokens = cursor.fetchone()
            cursor.execute("SELECT modelo, latencia_ms, tokens_total, fecha FROM agent_traces ORDER BY id DESC LIMIT 5")
            ultimas = cursor.fetchall()
            conn.close()
            return {
                "total_consultas": total_calls or 0,
                "latencia_promedio_ms": int(avg_lat or 0),
                "tokens_acumulados": int(sum_tokens or 0),
                "ultimas": ultimas
            }
        except Exception:
            return {"total_consultas": 0, "latencia_promedio_ms": 0, "tokens_acumulados": 0, "ultimas": []}
