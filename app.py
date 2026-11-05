
import streamlit as st
from datetime import time

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

    st.title("🔍 Campus Resource Availability")

    st.write(
        "Search for campus resources based on your "
        "requirements, date, time and capacity."
    )

    st.divider()

    st.subheader("📋 Search Requirements")

    with st.form("availability_form"):

        resource_type = st.selectbox(
            "Select Resource Type",
            [
                "Classroom",
                "Amphitheatre",
                "Lab",
                "Guest House",
                "Parking"
            ]
        )

        col1, col2 = st.columns(2)

        with col1:
            booking_date = st.date_input("Required Date")

            start_time = st.time_input(
                "Start Time",
                value=time(14, 0)
            )

        with col2:
            capacity = st.number_input(
                "Number of People / Vehicles",
                min_value=1,
                max_value=500,
                value=50
            )

            end_time = st.time_input(
                "End Time",
                value=time(16, 0)
            )

        purpose = st.text_area(
            "Purpose of Booking",
            placeholder="Example: Faculty workshop"
        )

        submitted = st.form_submit_button(
            "🔍 Search Availability",
            use_container_width=True
        )

    if submitted:

        if start_time >= end_time:
            st.error("End time must be later than start time.")

        elif not purpose.strip():
            st.warning("Please enter the purpose of booking.")

        else:
            request = {
                "resource_type": resource_type,
                "date": str(booking_date),
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "capacity": int(capacity),
                "purpose": purpose.strip()
            }

            st.session_state["availability_request"] = request

            st.success("Your search request has been captured!")

            st.subheader("📌 Your Search Request")

            st.write(f"**Resource:** {resource_type}")
            st.write(f"**Date:** {booking_date}")
            st.write(
                f"**Time:** {request['start_time']} - "
                f"{request['end_time']}"
            )
            st.write(f"**Capacity:** {capacity}")
            st.write(f"**Purpose:** {purpose}")

            st.info(
                "The real availability engine will be "
                "connected by Member 1."
            )



elif page == "My Bookings":

    st.title("📅 My Campus Bookings")

    st.write(
        "View and track your classroom, event venue, "
        "guest house and parking booking requests."
    )

    st.divider()

    # Sample bookings for frontend demonstration only
    bookings = [
        {
            "Booking ID": "BK-1001",
            "Resource": "Classroom EB1-101",
            "Type": "Classroom",
            "Date": "2026-11-12",
            "Time": "14:00 - 16:00",
            "Status": "Approved"
        },
        {
            "Booking ID": "BK-1002",
            "Resource": "Amphitheatre 1",
            "Type": "Amphitheatre",
            "Date": "2026-11-14",
            "Time": "10:00 - 12:00",
            "Status": "Pending"
        },
        {
            "Booking ID": "BK-1003",
            "Resource": "Guest House Room 2",
            "Type": "Guest House",
            "Date": "2026-11-16",
            "Time": "Check-in",
            "Status": "Rejected"
        }
    ]

    # Summary metrics
    total = len(bookings)
    approved = sum(
        1 for b in bookings if b["Status"] == "Approved"
    )
    pending = sum(
        1 for b in bookings if b["Status"] == "Pending"
    )
    rejected = sum(
        1 for b in bookings if b["Status"] == "Rejected"
    )

    st.subheader("📊 Booking Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Requests", total)
    col2.metric("Approved", approved)
    col3.metric("Pending", pending)
    col4.metric("Rejected", rejected)

    st.divider()

    # Booking filters
    st.subheader("📋 Booking History")

    selected_status = st.selectbox(
        "Filter by Status",
        ["All", "Approved", "Pending", "Rejected"]
    )

    if selected_status == "All":
        filtered_bookings = bookings
    else:
        filtered_bookings = [
            b for b in bookings
            if b["Status"] == selected_status
        ]

    if filtered_bookings:

        for booking in filtered_bookings:

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(
                        f"### {booking['Resource']}"
                    )
                    st.write(
                        f"**Booking ID:** {booking['Booking ID']}"
                    )
                    st.write(
                        f"**Date:** {booking['Date']}"
                    )
                    st.write(
                        f"**Time:** {booking['Time']}"
                    )

                with col2:
                    st.write("**Status**")

                    if booking["Status"] == "Approved":
                        st.success("Approved")

                    elif booking["Status"] == "Pending":
                        st.warning("Pending")

                    else:
                        st.error("Rejected")

    else:
        st.info("No bookings found for this status.")

    st.divider()

    st.caption(
        "Demo records only. Member 2 will connect this page "
        "to actual booking records from the database."
    )


elif page == "Admin Panel":
    st.title("🛡️ Admin Panel")
    st.info("Admin controls and approvals will be integrated here.")

st.divider()
st.caption("CampusPilot AI | JKLU AI Buildathon 2026")
