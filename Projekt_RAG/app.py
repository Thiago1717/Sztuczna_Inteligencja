import streamlit as st
import requests
import json
import urllib.request

st.set_page_config(page_title="Ekspert NBA", page_icon="🏀", layout="wide")
st.title("🏀 Lokalny Asystent NBA")
st.markdown("Zadaj mi pytanie o zasady NBA, CBA lub wyniki Draft Combine!")

# Sprawdzanie dostępnych modeli z API lokalnej Ollamy
try:
    req = urllib.request.urlopen('http://localhost:11434/api/tags')
    data = json.loads(req.read())
    available_models = [model['name'] for model in data['models']]
except Exception as e:
    available_models = ["llama3.1:latest"]

with st.sidebar:
    st.header("⚙️ Ustawienia")
    selected_model = st.selectbox("Wybierz model językowy:", available_models)
    temperature = st.slider("Kreatywność (Temperatura):", min_value=0.0, max_value=1.0, value=0.1, step=0.1)
    
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Napisz swoje pytanie tutaj..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Serwer AI myśli..."):
            try:
                # Wysyłanie zapytania do naszego Backend'u
                res = requests.post("http://localhost:5000/ask", json={
                    "query": prompt,
                    "model": selected_model,
                    "temperature": temperature
                })
                
                if res.status_code == 200:
                    answer = res.json().get("response")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = res.json().get("error", "Nieznany błąd serwera.")
                    st.error(f"Błąd: {error_msg}")
            
            except requests.exceptions.ConnectionError:
                st.error("Nie można połączyć się z serwerem AI. Upewnij się, że uruchomiłeś `backend.py` w innej konsoli!")