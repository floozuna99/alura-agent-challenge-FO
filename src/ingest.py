"""
ingest.py

Etapa 1 del proyecto: lectura y procesamiento del documento.

Este script:
1. Carga un documento PDF.
2. Lo divide en fragmentos (chunks) manejables.
3. Genera embeddings de cada fragmento usando Cohere.
4. Guarda los embeddings en un índice vectorial FAISS local.

Ejecutar UNA vez (o cada vez que cambie el PDF):
    python src/ingest.py
"""

import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings

load_dotenv()

# --- Configuración ---
PDF_PATH = os.getenv("PDF_PATH", "data/documento.pdf")
INDEX_PATH = os.getenv("INDEX_PATH", "data/faiss_index")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
COHERE_API_KEY = os.getenv("COHERE_API_KEY")


def validar_configuracion():
    if not COHERE_API_KEY:
        print("ERROR: No se encontró COHERE_API_KEY en el archivo .env")
        print("Creá un archivo .env basado en .env.example y agregá tu API key.")
        sys.exit(1)

    if not os.path.exists(PDF_PATH):
        print(f"ERROR: No se encontró el archivo PDF en '{PDF_PATH}'")
        print("Colocá tu documento PDF en la carpeta 'data/' o ajustá PDF_PATH en .env")
        sys.exit(1)


def cargar_y_dividir_documento(ruta_pdf: str):
    """Carga el PDF y lo divide en fragmentos de texto."""
    print(f"Cargando documento: {ruta_pdf}")
    loader = PyPDFLoader(ruta_pdf)
    paginas = loader.load()
    print(f"  -> {len(paginas)} página(s) cargada(s)")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(paginas)
    print(f"  -> Documento dividido en {len(chunks)} fragmento(s)")
    return chunks


def crear_indice_vectorial(chunks):
    """Genera embeddings con Cohere y construye el índice FAISS."""
    print("Generando embeddings con Cohere (modelo multilingüe)...")
    embeddings = CohereEmbeddings(
        cohere_api_key=COHERE_API_KEY,
        model="embed-multilingual-v3.0",
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_PATH)
    print(f"  -> Índice vectorial guardado en '{INDEX_PATH}'")


def main():
    validar_configuracion()
    chunks = cargar_y_dividir_documento(PDF_PATH)
    crear_indice_vectorial(chunks)
    print("\n✅ Ingesta completada. Ya podés ejecutar el agente (src/agent.py o src/app.py)")


if __name__ == "__main__":
    main()
