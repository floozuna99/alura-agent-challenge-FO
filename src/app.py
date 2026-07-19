"""
app.py

Etapa 3 (preparación): expone el agente como una aplicación web simple,
lista para desplegar en OCI Compute.

Ejecutar local:
    python src/app.py
Luego abrir: http://localhost:8080
"""

import os
from flask import Flask, request, jsonify, render_template_string
from agent import responder_pregunta

app = Flask(__name__)

PAGINA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Agente Alura - Challenge</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; }
    h1 { color: #2b2d42; }
    #pregunta { width: 100%; padding: 10px; font-size: 16px; }
    button { padding: 10px 20px; font-size: 16px; margin-top: 10px; cursor: pointer; }
    #respuesta { margin-top: 20px; padding: 15px; background: #f0f4f8; border-radius: 8px; white-space: pre-wrap; }
    .fuente { font-size: 12px; color: #555; margin-top: 10px; }
    #loading { display: none; color: #888; }
  </style>
</head>
<body>
  <h1>🤖 Agente Alura</h1>
  <p>Hacé una pregunta sobre el documento cargado:</p>
  <input type="text" id="pregunta" placeholder="Ej: ¿Cuál fue el producto más vendido?">
  <button onclick="preguntar()">Preguntar</button>
  <p id="loading">Pensando...</p>
  <div id="respuesta"></div>

  <script>
    async function preguntar() {
      const pregunta = document.getElementById('pregunta').value;
      if (!pregunta) return;
      document.getElementById('loading').style.display = 'block';
      document.getElementById('respuesta').innerHTML = '';
      try {
        const res = await fetch('/ask', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({question: pregunta})
        });
        const data = await res.json();
        document.getElementById('loading').style.display = 'none';
        if (data.error) {
          document.getElementById('respuesta').innerHTML = 'Error: ' + data.error;
        } else {
          document.getElementById('respuesta').innerText = data.respuesta;
        }
      } catch (e) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('respuesta').innerText = 'Error de conexión: ' + e;
      }
    }
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGINA_HTML)


@app.route("/health")
def health():
    """Endpoint de salud, útil para verificar que el deploy en OCI funciona."""
    return jsonify({"status": "ok"})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    pregunta = data.get("question", "").strip()

    if not pregunta:
        return jsonify({"error": "Falta el parámetro 'question'"}), 400

    try:
        resultado = responder_pregunta(pregunta)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    # host="0.0.0.0" es necesario para que sea accesible cuando esté en OCI
    app.run(host="0.0.0.0", port=port, debug=False)
