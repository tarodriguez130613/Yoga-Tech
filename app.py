"""
Yoga-Tech
Universidad El Bosque - Biomecánica Aplicada
Autores: Tatiana Rodríguez & David Castro
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
DATA_FILE = "resultados.json"
MAX_PARTICIPANTES = 20

def cargar():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/organizadores")
def organizadores():
    return render_template("organizadores.html")

@app.route("/api/guardar", methods=["POST"])
def api_guardar():
    data = request.json
    nombre = (data.get("nombre") or "Anónimo").strip() or "Anónimo"
    puntuacion = int(data.get("puntuacion", 0))
    nivel = data.get("nivel", "Bajo")

    resultados = cargar()
    nombres_unicos = {r["nombre"].lower() for r in resultados}
    if nombre.lower() not in nombres_unicos and len(nombres_unicos) >= MAX_PARTICIPANTES:
        return jsonify({"ok": False, "mensaje": "Ya se alcanzó el máximo de 20 participantes"}), 400

    resultados.append({
        "id": len(resultados) + 1,
        "nombre": nombre,
        "puntuacion": puntuacion,
        "nivel": nivel,
        "hora": datetime.now().strftime("%H:%M:%S")
    })
    guardar(resultados)
    return jsonify({"ok": True})

@app.route("/api/resultados")
def api_resultados():
    resultados = cargar()
    scores = [r["puntuacion"] for r in resultados]
    stats = {
        "max": max(scores) if scores else None,
        "min": min(scores) if scores else None,
        "promedio": round(sum(scores)/len(scores), 1) if scores else None,
        "cantidad": len(resultados),
        "participantes": len({r["nombre"].lower() for r in resultados})
    }
    return jsonify({"resultados": resultados, "stats": stats})

@app.route("/api/limpiar", methods=["POST"])
def api_limpiar():
    guardar([])
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
