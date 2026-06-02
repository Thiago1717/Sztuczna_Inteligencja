import streamlit as st
import requests

st.set_page_config(page_title="Ekspert NBA", page_icon="🏀", layout="wide")
st.title("🏀 Asystent NBA")
st.markdown("Zadaj mi pytanie o zasady NBA, CBA lub wyniki Draft Combine!")

with st.sidebar:
    st.header("⚙️ Ustawienia")
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            data = response.json()
            available_models = [model['name'] for model in data.get('models', [])]
            if not available_models:
                available_models = ["Brak pobranych modeli"]
        else:
            available_models = ["llama3.1:latest"]
    except requests.exceptions.RequestException:
        st.warning("Nie udało się połączyć z Ollamą (port 11434).")
        available_models = ["llama3.1:latest"]
        
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
        with st.spinner(f"Serwer AI myśli (używa modelu: {selected_model})..."):
            try:
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
                    st.error(f"Błąd backendu: {error_msg}")
            
            except requests.exceptions.ConnectionError:
                st.error("BŁĄD KRYTYCZNY: Nie działa serwer `backend.py`! Uruchom go w drugiej konsoli.")