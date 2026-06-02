import streamlit as st
import requests
import ollama 
st.set_page_config(page_title="Ekspert NBA", page_icon="🏀", layout="wide")
st.title("🏀 Lokalny Asystent NBA")
st.markdown("Zadaj mi pytanie o zasady NBA, CBA lub wyniki Draft Combine!")

with st.sidebar:
    st.header("⚙️ Ustawienia")
    
    try:
        available_models = [m['name'] for m in ollama.list()['models']]
        if not available_models:
            available_models = ["Brak pobranych modeli"]
    except Exception:
        st.warning("Nie udało się połączyć z Ollamą. Czy aplikacja działa w tle?")
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
                st.error("Nie można połączyć się z serwerem AI. Upewnij się, że uruchomiłeś `backend.py` w innej konsoli!")