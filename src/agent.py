"""
agent.py

Etapa 2 del proyecto: el agente inteligente que responde preguntas
en lenguaje natural sobre el documento cargado.

Uso como script (modo consola, para probar localmente):
    python src/agent.py

Uso como módulo (lo importa app.py para el servidor web):
    from agent import responder_pregunta
"""

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

INDEX_PATH = os.getenv("INDEX_PATH", "data/faiss_index")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

PROMPT_TEMPLATE = """Sos un asistente que responde preguntas basándote ÚNICAMENTE en el
contexto del documento proporcionado. Si la respuesta no está en el contexto,
decí claramente que no encontraste esa información en el documento. No inventes datos.

Contexto:
{context}

Pregunta: {question}

Respuesta (en español, clara y concisa):"""

_qa_chain = None  # cache para no recrear la cadena en cada request


def _cargar_cadena():
    """Carga el índice FAISS y arma la cadena de RetrievalQA con Cohere."""
    global _qa_chain
    if _qa_chain is not None:
        return _qa_chain

    if not COHERE_API_KEY:
        raise RuntimeError(
            "No se encontró COHERE_API_KEY. Configurá el archivo .env "
            "(ver .env.example)."
        )

    if not os.path.exists(INDEX_PATH):
        raise RuntimeError(
            f"No se encontró el índice vectorial en '{INDEX_PATH}'. "
            "Corré primero: python src/ingest.py"
        )

    embeddings = CohereEmbeddings(
        cohere_api_key=COHERE_API_KEY,
        model="embed-multilingual-v3.0",
    )
    vectorstore = FAISS.load_local(
        INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatCohere(
        cohere_api_key=COHERE_API_KEY,
        model="command-a-03-2025",
        temperature=0.2,
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE, input_variables=["context", "question"]
    )

    _qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return _qa_chain


def responder_pregunta(pregunta: str) -> dict:
    """
    Recibe una pregunta en lenguaje natural y devuelve un dict con:
      - respuesta: texto generado por el modelo
      - fuentes: lista de fragmentos del documento usados como contexto
    """
    chain = _cargar_cadena()
    resultado = chain.invoke({"query": pregunta})

    fuentes = [
        {
            "pagina": doc.metadata.get("page", "N/D"),
            "fragmento": doc.page_content[:200] + "..."
            if len(doc.page_content) > 200
            else doc.page_content,
        }
        for doc in resultado.get("source_documents", [])
    ]

    return {"respuesta": resultado["result"], "fuentes": fuentes}


def main():
    """Modo consola para probar el agente localmente antes de exponerlo como API."""
    print("=== Agente Alura — modo consola ===")
    print("Escribí tu pregunta (o 'salir' para terminar)\n")
    while True:
        pregunta = input("Pregunta: ").strip()
        if pregunta.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break
        if not pregunta:
            continue
        try:
            resultado = responder_pregunta(pregunta)
            print(f"\nRespuesta: {resultado['respuesta']}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
