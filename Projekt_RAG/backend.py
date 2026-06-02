import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import faiss
import json
import numpy as np
import ollama
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify

app = Flask(__name__)

print("Ładowanie wektoryzatora (CPU)...")
embedder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2', device='cpu')

print("Ładowanie bazy wiedzy...")
if os.path.exists("vec_db/vector_database.index"):
    index = faiss.read_index("vec_db/vector_database.index")
    with open("vec_db/metadata.json", "r") as f:
        metadata = json.load(f)
    print("Baza gotowa!")
else:
    index = None
    metadata = []
    print("OSTRZEŻENIE: Brak bazy wektorowej.")

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query')
    selected_model = data.get('model', 'llama3.1:latest')
    temperature = data.get('temperature', 0.1)

    if not index:
        return jsonify({"error": "Baza wiedzy nie jest gotowa."}), 500

    try:
        question_embedding = embedder.encode(query, show_progress_bar=False)
        D, I = index.search(np.array([question_embedding]), k=5)
        chunks = [metadata[i] for i in I[0]]

        context = ""
        for i, chunk in enumerate(chunks):
            context += f"{i+1}. {chunk['chunk']}\n"

        prompt_template = f"""Based on the following context items, please answer the query.
Give yourself room to think by extracting relevant passages from the context before answering the query.
Don't return the thinking, only return the answer. Answer in Polish language only.
Context:
{context}
Main User Query: {query}
Answer:"""

        response = ollama.chat(
            model=selected_model,
            messages=[
                {"role": "system", "content": "Be helpful, straight to the point. Use only context. Do not hallucinate."},
                {"role": "user", "content": prompt_template}
            ],
            options={"temperature": temperature, "num_predict": 512}
        )
        
        answer = response['message']['content']
        
        sources_text = "\n\n---\n**Źródła z PDF:**\n"
        for i, chunk in enumerate(chunks):
            sources_text += f"- *{chunk['filename']}* (str. {chunk['page_number'] + 1})\n"

        return jsonify({"response": answer + sources_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, threaded=False)