import streamlit as st
import json
from agent.request_parser import parse_user_request
from database.db_manager import save_booking

st.title("CampusPilot AI 🎓")
st.subheader("Smart Campus Venue & Booking Manager")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm CampusPilot. What would you like to book today?"}]

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("E.g., Book a classroom for an AI workshop..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process with your Gemini parser
    with st.spinner("Analyzing booking details..."):
        try:
                #Fetch and forcefully clean Gemini's response
             raw_response = parse_user_request(prompt)
             clean_json = raw_response.strip().replace("```json", "").replace("```", "")
                
                # Load data
             booking_data = json.loads(clean_json)
             missing = booking_data.get("missing_fields", [])
        
             if missing:
                    missing_str = ", ".join(missing).replace("_", " ")
                    bot_reply = f"I still need a few details: {missing_str}"
             else:
                    save_booking(booking_data)
                    bot_reply = "Perfect! Your classroom is officially booked and saved to the database."
                    
        except Exception as e:
                # Expose the exact failure point
                error_type = type(e).__name__
                bot_reply = f"SYSTEM CRASH ({error_type}): {e}"
           
            
        # Display and save bot reply
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        