
import streamlit as st

st.set_page_config(
    page_title="CampusPilot AI",
    page_icon="🏫",
    layout="wide"
)

# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.title("🏫 CampusPilot AI")
st.sidebar.caption("Smart Campus Management")

role = st.sidebar.selectbox(
    "Login as",
    ["Student", "Faculty", "Admin"]
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "AI Assistant",
        "Availability",
        "My Bookings",
        "Admin Panel"
    ]
)

st.sidebar.divider()
st.sidebar.info(f"Demo role: {role}")

# -------------------------------
# DASHBOARD
# -------------------------------

if page == "Dashboard":

    st.title("🏫 CampusPilot AI")
    st.subheader(f"Welcome to your {role} Dashboard")

    st.write(
        "Manage campus venues, guest house rooms "
        "and parking through one intelligent platform."
    )

    st.divider()

    # Demo metrics — replace with database data later
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Classrooms", "25", "Demo data")
    col2.metric("Available Venues", "12", "Demo data")
    col3.metric("Pending Requests", "5", "Demo data")
    col4.metric("Parking Slots", "40", "Demo data")

    st.divider()

    st.subheader("🚀 Campus Resources")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🏫 Classrooms")
        st.write("Find available classrooms.")
        st.button("Explore Classrooms", key="classrooms")

    with c2:
        st.markdown("### 🎤 Amphitheatres")
        st.write("Check event venue availability.")
        st.button("Explore Amphitheatres", key="amphi")

    with c3:
        st.markdown("### 🅿️ Parking")
        st.write("Check available parking spaces.")
        st.button("Explore Parking", key="parking")

    st.divider()

    st.subheader("🤖 AI Campus Assistant")

    st.write(
        "Ask the AI agent to find venues, "
        "check availability and coordinate bookings."
    )

    if st.button("Open AI Assistant"):
        st.session_state["selected_page"] = "AI Assistant"
        st.rerun()

# -------------------------------
# OTHER PAGES — TEMPORARY PLACEHOLDERS
# -------------------------------


elif page == "AI Assistant":

    st.title("🤖 CampusPilot AI Assistant")

    st.write(
        "Your intelligent assistant for campus "
        "venue, guest house and parking management."
    )

    st.divider()

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Welcome message
    if not st.session_state.chat_history:
        st.info(
            "👋 Hello! I am CampusPilot AI. "
            "Tell me what you need, and I will help "
            "you manage campus resources."
        )

        st.markdown("### 💡 Try asking:")
        st.markdown("""
        - Find a classroom for 50 students.
        - I need an amphitheatre for an event.
        - Check guest house room availability.
        - Find parking for 2 visitor vehicles.
        """)

    # Display conversation history
    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    user_message = st.chat_input(
        "Ask CampusPilot AI anything..."
    )

    if user_message:

        # Save user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })

        # Temporary response until Member 3 connects Gemini
        assistant_message = (
            "Your request has been received! "
            "The Gemini AI agent is not connected yet. "
            "Member 3 will integrate the request "
            "understanding and booking workflow."
        )

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        st.rerun()

    # Clear chat
    if st.button("🗑️ Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()


elif page == "Availability":
    st.title("🔍 Resource Availability")
    st.info("Member 1 will integrate the availability engine here.")

elif page == "My Bookings":
    st.title("📅 My Bookings")
    st.info("Member 2 will integrate booking records here.")

elif page == "Admin Panel":
    st.title("🛡️ Admin Panel")
    st.info("Admin controls and approvals will be integrated here.")

st.divider()
st.caption("CampusPilot AI | JKLU AI Buildathon 2026")
