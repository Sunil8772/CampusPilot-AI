import streamlit as st
from agent.orchestrator import process_message

st.title("CampusPilot AI 🎓")
st.subheader("Smart Campus Venue & Booking Manager")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm CampusPilot. What would you like to do?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("E.g., Book a classroom for an AI workshop..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Analyzing booking details..."):
        bot_reply = process_message(prompt)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})