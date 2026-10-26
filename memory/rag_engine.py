import os
import json
import sqlite3
import datetime
import numpy as np
from google import genai
from memory.local_memory import DB_PATH, inicializar_db

class RAGEngine:
    """Motor de Memoria Vectorial Semántica (Embeddings + Cosine Similarity) estilo OpenJarvis."""

    def __init__(self):
        inicializar_db()
        self._migrar_tabla_vectorial()
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def _migrar_tabla_vectorial(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Tabla para fragmentos de documentos y recuerdos con su vector de embedding
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memoria_vectorial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origen TEXT,
                contenido TEXT,
                vector_json TEXT,
                fecha TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _obtener_embedding(self, texto: str) -> list:
        if not self.client:
            return []
        for modelo_emb in ["text-embedding-004", "embedding-001"]:
            try:
                res = self.client.models.embed_content(
                    model=modelo_emb,
                    contents=texto
                )
                return res.embeddings[0].values
            except Exception:
                continue
        return []

    def indexar_texto(self, contenido: str, origen: str = "memoria_usuario") -> str:
        vector = self._obtener_embedding(contenido)
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memoria_vectorial (origen, contenido, vector_json, fecha) VALUES (?, ?, ?, ?)",
            (origen, contenido, json.dumps(vector), ahora)
        )
        conn.commit()
        conn.close()
        tipo = "semántico (vectorizado)" if vector else "léxico"
        return f"Conocimiento indexado en modo {tipo} bajo '{origen}'."

    def indexar_archivo(self, ruta_archivo: str) -> str:
        if not os.path.exists(ruta_archivo):
            return f"No se encontró el archivo '{ruta_archivo}'."
        try:
            with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                texto = f.read()
        except Exception as e:
            return f"Error leyendo archivo: {e}"

        # Dividir en fragmentos (chunks) de ~800 caracteres para RAG preciso
        parrafos = [p.strip() for p in texto.split("\n\n") if len(p.strip()) > 20]
        chunks = []
        actual = ""
        for p in parrafos:
            if len(actual) + len(p) < 800:
                actual += "\n" + p
            else:
                if actual:
                    chunks.append(actual.strip())
                actual = p
        if actual:
            chunks.append(actual.strip())

        nombre = os.path.basename(ruta_archivo)
        for idx, chunk in enumerate(chunks[:20]):  # Límite seguro por archivo
            self.indexar_texto(chunk, origen=f"archivo:{nombre}#parte{idx+1}")

        return f"Archivo '{nombre}' procesado e indexado en la base vectorial ({len(chunks[:20])} fragmentos)."

    def buscar_semantico(self, consulta: str, top_k: int = 4) -> str:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT origen, contenido, vector_json, fecha FROM memoria_vectorial")
        filas = cursor.fetchall()
        conn.close()

        if not filas:
            return "La base de conocimiento vectorial aún está vacía."

        vec_consulta = self._obtener_embedding(consulta)
        resultados = []

        if vec_consulta:
            q_np = np.array(vec_consulta, dtype=np.float32)
            q_norm = np.linalg.norm(q_np)
            for origen, contenido, vec_json, fecha in filas:
                vec_doc = json.loads(vec_json) if vec_json else []
                if vec_doc and len(vec_doc) == len(vec_consulta):
                    d_np = np.array(vec_doc, dtype=np.float32)
                    sim = float(np.dot(q_np, d_np) / (q_norm * np.linalg.norm(d_np) + 1e-9))
                else:
                    sim = 0.3 if consulta.lower() in contenido.lower() else 0.0
                resultados.append((sim, origen, contenido, fecha))
            resultados.sort(key=lambda x: x[0], reverse=True)
        else:
            # Fallback si no hubo vector
            for origen, contenido, _, fecha in filas:
                score = 1.0 if consulta.lower() in contenido.lower() else 0.1
                resultados.append((score, origen, contenido, fecha))
            resultados.sort(key=lambda x: x[0], reverse=True)

        mejores = resultados[:top_k]
        salida = [
            f"- [{origen} | Similitud: {sim:.2f} | {fecha}]: {contenido}"
            for sim, origen, contenido, fecha in mejores if sim > 0.15
        ]
        return "Resultados semánticos (RAG):\n" + ("\n".join(salida) if salida else "Sin coincidencias relevantes.")
