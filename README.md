# 🤖 Agente Alura — Challenge Cloud Computing

Agente de inteligencia artificial capaz de responder preguntas en lenguaje natural
sobre un documento PDF, utilizando una arquitectura RAG (Retrieval-Augmented
Generation) y desplegado en Oracle Cloud Infrastructure (OCI).

> Proyecto desarrollado como parte del Challenge Alura Agente (Cloud Computing).

---

## 📐 Arquitectura

```
┌─────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   PDF/CSV   │───▶│  PyPDFLoader +    │───▶│  Cohere Embeddings  │
│ (documento) │    │  Text Splitter    │    │  (multilingual-v3)  │
└─────────────┘    └──────────────────┘    └──────────┬──────────┘
                                                        ▼
                                              ┌──────────────────┐
                                              │   FAISS Index     │
                                              │ (base vectorial)   │
                                              └──────────┬──────────┘
                                                        ▼
┌─────────────┐    ┌──────────────────┐    ┌────────────────────┐
│  Pregunta   │───▶│  Búsqueda de      │───▶│  Cohere Command-R   │
│  (usuario)  │    │  contexto (top-k) │    │  (genera respuesta)  │
└─────────────┘    └──────────────────┘    └──────────┬──────────┘
                                                        ▼
                                              ┌──────────────────┐
                                              │  Respuesta final  │
                                              │  (Flask API/Web)  │
                                              └──────────────────┘
```

**Stack utilizado:**
- **Python 3.11**
- **LangChain** — orquestación del pipeline RAG
- **PyPDF** — lectura del documento PDF
- **Cohere** (`embed-multilingual-v3.0` + `command-r`) — embeddings y generación de lenguaje natural
- **FAISS** — base de datos vectorial local
- **Flask** — servidor web para exponer el agente
- **Oracle Cloud Infrastructure (OCI Compute)** — despliegue en la nube

---

## 📁 Estructura del repositorio

```
alura-agent-challenge/
├── src/
│   ├── ingest.py      # Etapa 1: lee y procesa el documento
│   ├── agent.py        # Etapa 2: agente RAG que responde preguntas
│   └── app.py           # Etapa 3: servidor web (deploy en OCI)
├── data/
│   └── documento.pdf   # Documento base de conocimiento (agregar el propio)
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## ⚙️ Instrucciones para ejecutar el proyecto localmente

### 1. Clonar el repositorio
```bash
git clone https://github.com/<tu-usuario>/alura-agent-challenge.git
cd alura-agent-challenge
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
```
Editar `.env` y agregar tu API key gratuita de Cohere (se obtiene en
https://dashboard.cohere.com/api-keys).

### 4. Agregar el documento PDF
Colocar el archivo PDF en `data/documento.pdf` (o ajustar `PDF_PATH` en `.env`).

### 5. Procesar el documento (Etapa 1)
```bash
python src/ingest.py
```

### 6. Probar el agente en consola (Etapa 2)
```bash
python src/agent.py
```

### 7. Levantar el servidor web
```bash
python src/app.py
```
Abrir en el navegador: http://localhost:8080

---

## 💬 Ejemplos de preguntas y respuestas (evidencia real)

Estas son respuestas reales generadas por el agente, ejecutado en Google Colab:

**Pregunta:** ¿Cuál es el precio desde de un departamento en Altavida Luque?
**Respuesta:** El precio inicial de un departamento en Altavida Luque es desde USD 914/m².

**Pregunta:** ¿Cuántas unidades tiene Altamira Surubi'i?
**Respuesta:** Según el documento, Altamira Surubi'i tiene 350 departamentos terminados.

**Pregunta:** ¿En dónde queda Alzara Plaza?
**Respuesta:** Alzara Plaza está situado en un barrio tranquilo de Asunción, ofreciendo comodidad y exclusividad sin estar alejado de la ciudad.

> **Nota sobre precisión:** en algunas consultas sobre amenities de proyectos con
> nombres o características similares, el agente puede mezclar información de
> distintos proyectos debido al tamaño de los fragmentos (chunks) usados en la
> búsqueda semántica. Una mejora futura es aumentar el `chunk_size` en `ingest.py`
> para mantener cada sección de proyecto más completa y reducir este solapamiento.

---

## ☁️ Deploy en Oracle Cloud Infrastructure (OCI)

> _Pendiente — se agregará el enlace público y/o captura de pantalla de la
> aplicación corriendo en OCI una vez completado el despliegue._

**Resumen del proceso de deploy:**
1. Creación de una instancia Compute (VM.Standard.E2.1.Micro — free tier).
2. Configuración de reglas de seguridad (Ingress) para el puerto 8080.
3. Instalación de Docker en la instancia.
4. Build y ejecución del contenedor con las variables de entorno configuradas.
5. Verificación de acceso público vía IP pública de la instancia.

---

## ✅ Estado del proyecto

- [x] Etapa 1: Lectura y procesamiento del documento
- [x] Etapa 2: Agente de IA respondiendo preguntas
- [ ] Etapa 3: Deploy en OCI
- [ ] README completo con evidencias

---

## 👤 Autor

Proyecto desarrollado por Flor — Challenge Alura Agente (Cloud Computing).
