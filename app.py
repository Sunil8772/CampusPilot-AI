
import os
import streamlit as st
from datetime import datetime, time
from dotenv import load_dotenv

from agent.orchestrator import process_user_request
from agent.tools import check_resource_availability
from services.common import CAMPUS_TZ
from services.permissions import upsert_user
from services.booking import (
    get_user_bookings,
    create_booking_request,
    get_pending_bookings,
    approve_booking,
    reject_booking,
    get_booking_by_id,
)
from services.resources import get_resources, add_resource, update_resource

load_dotenv()

DEMO_PROFILES = {
    "Student": ("demo-student", "CampusPilot Demo Student", "student-demo@example.local", "student"),
    "Faculty": ("demo-faculty", "CampusPilot Demo Faculty", "faculty-demo@example.local", "faculty"),
    "Admin": ("demo-admin", "CampusPilot Demo Admin", "admin@example.local", "admin"),
}


def get_demo_user(selected_role):
    """Return a fixed synthetic profile; this is not production authentication."""
    return upsert_user(*DEMO_PROFILES[selected_role])

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


# ----------------------------------
# ROLE-BASED NAVIGATION
# ----------------------------------

DEMO_MODE = os.getenv("CAMPUSPILOT_DEMO_MODE", "false").strip().lower() == "true"
if not DEMO_MODE:
    st.error(
        "Demo mode is disabled. Set CAMPUSPILOT_DEMO_MODE=true in your local .env "
        "to use synthetic buildathon profiles. Production use requires real authentication."
    )
    st.stop()

role = st.sidebar.selectbox(
    "Demo profile (synthetic only)",
    ["Student", "Faculty", "Admin"]
)
st.sidebar.warning("DEMO MODE — role selection is not authentication.")

# Navigation options according to role
if role == "Student":

    navigation_options = [
        "Dashboard",
        "AI Assistant",
        "Availability",
        "My Bookings"
    ]

elif role == "Faculty":

    navigation_options = [
        "Dashboard",
        "AI Assistant",
        "Availability",
        "My Bookings"
    ]

else:

    navigation_options = [
        "Dashboard",
        "AI Assistant",
        "Availability",
        "My Bookings",
        "Admin Panel"
    ]

page = st.sidebar.radio(
    "Navigation",
    navigation_options,
    key=f"navigation_{role}"
)

st.sidebar.divider()

st.sidebar.info(f"Demo role: {role}")

# Extra protection for Admin Panel
if page == "Admin Panel" and role != "Admin":
    st.error("Access denied! Admin permissions required.")
    st.stop()


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

        # Pass recent user turns so Gemini can resolve follow-up answers
        # such as "next Friday" after it asks for a missing date.
        recent_user_turns = [
            item["content"] for item in st.session_state.chat_history
            if item["role"] == "user"
        ][-5:]
        conversation = "\n".join(f"User: {turn}" for turn in recent_user_turns)
        with st.spinner("Gemini is understanding your request and checking campus systems..."):
            agent_result = process_user_request(conversation, user_id=None)
        st.session_state["last_agent_result"] = agent_result

        assistant_message = agent_result.get("message", "I could not process that request.")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        if agent_result.get("status") == "availability_checked":
            for item in agent_result.get("results", []):
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": item.get("summary", "No availability summary.")
                })
        elif agent_result.get("status") == "error":
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Please check the local Gemini and PostgreSQL configuration. " + assistant_message
            })
        st.rerun()

    # Show real resources returned by the availability tool. For booking intent,
    # require both resource selection and a separate explicit confirmation.
    last_result = st.session_state.get("last_agent_result", {})
    if last_result.get("status") == "availability_checked":
        parsed = last_result.get("parsed_request", {})
        resource_options = []
        for group in last_result.get("results", []):
            tool_result = group.get("result", {})
            if tool_result.get("success"):
                for resource in tool_result.get("available_resources", []):
                    resource_options.append((group["resource_type"], resource))

        if last_result.get("intent") == "book_resources" and resource_options:
            st.divider()
            st.subheader("📨 Submit a booking request")
            with st.form("ai_booking_confirmation_form"):
                selected = st.selectbox(
                    "Choose one available resource",
                    resource_options,
                    format_func=lambda item: (
                        f"{item[1].get('name')} — {item[0].replace('_', ' ').title()} "
                        f"(capacity {item[1].get('capacity')}, {item[1].get('location') or 'location not listed'})"
                    ),
                )
                confirmed = st.checkbox(
                    "I confirm that I want to submit this selected resource as a booking request."
                )
                submit_request = st.form_submit_button(
                    "Confirm and submit request",
                    use_container_width=True,
                )

            if submit_request:
                if not confirmed:
                    st.warning("Please tick the confirmation box before submitting.")
                else:
                    try:
                        demo_user = get_demo_user(role)
                        selected_type, selected_resource = selected
                        start_dt = datetime.fromisoformat(
                            f"{parsed['date']}T{parsed['start_time']}:00+05:30"
                        )
                        end_dt = datetime.fromisoformat(
                            f"{parsed['date']}T{parsed['end_time']}:00+05:30"
                        )
                        booking_result = create_booking_request({
                            "user_id": demo_user["id"],
                            "resource_id": selected_resource["id"],
                            "start_datetime": start_dt.isoformat(),
                            "end_datetime": end_dt.isoformat(),
                            "capacity": int(parsed.get("capacity") or 1),
                            "purpose": parsed.get("purpose") or "Campus resource request",
                        })
                        if booking_result.get("success"):
                            st.success(
                                f"Request #{booking_result['booking_id']} was submitted and is PENDING admin approval. "
                                "This is not a confirmed booking."
                            )
                            st.session_state["last_agent_result"] = {}
                        else:
                            st.error(booking_result.get("message", "Booking request was not submitted."))
                    except Exception as exc:
                        st.error(f"Could not submit request: {type(exc).__name__}: {exc}")

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
            request["resource_type"] = resource_type.lower().replace(" ", "_")

            st.subheader("📌 Availability Results")
            st.write(f"**Resource:** {resource_type}")
            st.write(f"**Date:** {booking_date}")
            st.write(f"**Time:** {request['start_time']} - {request['end_time']}")
            st.write(f"**Capacity requested:** {capacity}")
            st.write(f"**Purpose:** {purpose}")

            try:
                with st.spinner("Checking PostgreSQL bookings and published timetable..."):
                    result = check_resource_availability(request)
                if result.get("success"):
                    options = result.get("available_resources", [])
                    if options:
                        st.success(f"{len(options)} available option(s) found.")
                        st.dataframe([
                            {"Resource": r.get("name"), "Type": r.get("resource_type"),
                             "Capacity": r.get("capacity"), "Location": r.get("location")}
                            for r in options
                        ], use_container_width=True, hide_index=True)
                    else:
                        st.warning("No matching resources are available for this time.")

                    if options:
                        st.subheader("📝 Submit a Booking Request")
                        selected_resource = st.selectbox(
                            "Choose an available resource",
                            options,
                            format_func=lambda item: (
                                f"{item.get('name')} — {item.get('location') or 'Location not listed'} "
                                f"(capacity {item.get('capacity')})"
                            ),
                            key="booking_resource_choice",
                        )
                        if st.button("📨 Submit Booking Request", use_container_width=True):
                            try:
                                demo_user = get_demo_user(role)
                                booking_result = create_booking_request({
                                    "user_id": demo_user["id"],
                                    "resource_id": selected_resource["id"],
                                    "start_datetime": (
                                        f"{booking_date.isoformat()}T{start_time.strftime('%H:%M')}:00+05:30"
                                    ),
                                    "end_datetime": (
                                        f"{booking_date.isoformat()}T{end_time.strftime('%H:%M')}:00+05:30"
                                    ),
                                    "capacity": int(capacity),
                                    "purpose": purpose.strip(),
                                })
                                if booking_result.get("success"):
                                    st.success(
                                        f"Booking request #{booking_result.get('booking_id')} submitted. "
                                        "It is pending admin approval."
                                    )
                                else:
                                    st.error(booking_result.get("message", "Booking request could not be submitted."))
                            except Exception as exc:
                                st.error(f"Booking request failed: {type(exc).__name__}: {exc}")

                else:
                    st.error(result.get("message", "Availability check failed."))
            except Exception as exc:
                st.error(f"Availability service could not run: {type(exc).__name__}: {exc}")
                st.info("Configure PostgreSQL, run init_db.py and seed_demo.py, then retry.")

            st.caption("Availability check only. This does not create or confirm a booking.")



elif page == "My Bookings":

    st.title("📅 My Campus Bookings")
    st.write(
        "View and track booking requests saved in the CampusPilot PostgreSQL database."
    )
    st.divider()

    # Demo identities only. This is not authentication; replace with verified login
    # before exposing the application publicly.
    try:
        demo_user = get_demo_user(role)
        bookings = get_user_bookings(demo_user["id"])

        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "Approved", "Rejected", "Cancelled"],
            key="my_bookings_status_filter",
        )
        status_counts = {
            status: sum(1 for booking in bookings if booking["status"] == status)
            for status in ("pending", "approved", "rejected", "cancelled")
        }

        st.subheader("📊 Booking Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Requests", len(bookings))
        c2.metric("Approved", status_counts["approved"])
        c3.metric("Pending", status_counts["pending"])
        c4.metric("Rejected", status_counts["rejected"])

        visible = bookings if status_filter == "All" else [
            booking for booking in bookings
            if booking["status"] == status_filter.lower()
        ]

        st.subheader("📋 Booking History")
        if not visible:
            st.info("No database bookings found for this demo profile and filter.")
        else:
            for booking in visible:
                start_dt = booking["start_datetime"]
                end_dt = booking["end_datetime"]
                with st.container(border=True):
                    left, right = st.columns([3, 1])
                    with left:
                        st.markdown(f"### {booking['resource_name']}")
                        st.write(f"**Booking ID:** {booking['id']}")
                        st.write(f"**Type:** {booking['resource_type'].replace('_', ' ').title()}")
                        st.write(f"**Date:** {start_dt.strftime('%Y-%m-%d')}")
                        st.write(f"**Time:** {start_dt.strftime('%H:%M')} – {end_dt.strftime('%H:%M')}")
                        st.write(f"**Purpose:** {booking['purpose']}")
                        st.write(f"**Requested capacity:** {booking['requested_capacity']}")
                        if booking.get("decision_reason"):
                            st.write(f"**Decision note:** {booking['decision_reason']}")
                    with right:
                        st.write("**Status**")
                        status = booking["status"]
                        if status == "approved":
                            st.success(status.title())
                        elif status == "pending":
                            st.warning(status.title())
                        elif status == "rejected":
                            st.error(status.title())
                        else:
                            st.info(status.title())

        st.caption(
            "These records are read from PostgreSQL. The selected role is a demo profile, "
            "not a secure login identity."
        )
    except Exception as exc:
        st.error(f"Could not load bookings from PostgreSQL: {type(exc).__name__}: {exc}")
        st.info("Check DATABASE_URL, run init_db.py and ensure the demo profile exists.")

    
elif page == "Admin Panel":

    st.title("🛡️ Campus Administration Dashboard")
    st.write("Review and decide real booking requests stored in PostgreSQL.")
    st.caption("Synthetic demo admin profile. Backend admin-role checks are enforced for every decision.")
    st.divider()

    try:
        admin_user = get_demo_user("Admin")
        pending_bookings = get_pending_bookings(admin_user["id"])

        if st.session_state.get("admin_action_message"):
            st.success(st.session_state.pop("admin_action_message"))

        st.subheader("📋 Pending Booking Requests")
        st.metric("Pending requests", len(pending_bookings))

        if not pending_bookings:
            st.info("There are no pending database booking requests.")
        else:
            for booking in pending_bookings:
                with st.container(border=True):
                    st.markdown(f"### {booking['resource_name']}")
                    st.write(f"**Booking ID:** {booking['id']}")
                    st.write(f"**Requested by:** {booking['full_name']} ({booking['email']})")
                    st.write(f"**Resource type:** {booking['resource_type'].replace('_', ' ').title()}")
                    st.write(f"**From:** {booking['start_datetime']}")
                    st.write(f"**To:** {booking['end_datetime']}")
                    st.write(f"**Capacity:** {booking['requested_capacity']}")
                    st.write(f"**Purpose:** {booking['purpose']}")

                    reject_reason = st.text_input(
                        "Reason (required when rejecting)",
                        key=f"reject_reason_{booking['id']}",
                    )
                    approve_col, reject_col = st.columns(2)
                    with approve_col:
                        approve_clicked = st.button(
                            "✅ Approve request",
                            key=f"db_approve_{booking['id']}",
                            use_container_width=True,
                        )
                    with reject_col:
                        reject_clicked = st.button(
                            "❌ Reject request",
                            key=f"db_reject_{booking['id']}",
                            use_container_width=True,
                        )

                    if approve_clicked:
                        decision = approve_booking(booking["id"], admin_user["id"])
                        if decision.get("success"):
                            verified = get_booking_by_id(booking["id"], admin_user["id"])
                            if verified and verified["status"] == "approved":
                                st.session_state["admin_action_message"] = (
                                    f"Booking #{booking['id']} is APPROVED in PostgreSQL."
                                )
                            else:
                                st.session_state["admin_action_message"] = (
                                    f"Approval response received, but database verification failed for booking #{booking['id']}."
                                )
                        else:
                            st.session_state["admin_action_message"] = decision.get(
                                "message", "Approval failed."
                            )
                        st.rerun()

                    if reject_clicked:
                        if not reject_reason.strip():
                            st.warning("Enter a rejection reason first.")
                        else:
                            decision = reject_booking(
                                booking["id"], admin_user["id"], reject_reason.strip()
                            )
                            if decision.get("success"):
                                verified = get_booking_by_id(booking["id"], admin_user["id"])
                                if verified and verified["status"] == "rejected":
                                    st.session_state["admin_action_message"] = (
                                        f"Booking #{booking['id']} is REJECTED in PostgreSQL."
                                    )
                                else:
                                    st.session_state["admin_action_message"] = (
                                        f"Rejection response received, but database verification failed for booking #{booking['id']}."
                                    )
                            else:
                                st.session_state["admin_action_message"] = decision.get(
                                    "message", "Rejection failed."
                                )
                            st.rerun()

    except Exception as exc:
        st.error(f"Could not load or update database booking requests: {type(exc).__name__}: {exc}")
        st.info("Check DATABASE_URL, run init_db.py and seed_demo.py, then retry.")

    # Timetable publishing is a separate reviewed workflow; keep this clear in the demo.
    st.divider()
    st.subheader("📅 Timetable Management")
    st.info(
        "Timetable parser review and publishing are available in the backend. "
        "The upload/review screen is not yet connected. The demo uses the synthetic "
        "published timetable created by seed_demo.py; do not publish unverified institutional rows."
    )

    # Database-backed resource inventory.
    st.divider()
    st.subheader("🏫 Resource Management — PostgreSQL")
    try:
        admin_user = get_demo_user("Admin")
        admin_id = admin_user["id"]

        with st.form("db_add_resource_form"):
            st.markdown("#### Add a campus resource")
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                resource_code = st.text_input("Unique resource code", placeholder="DEMO-ROOM-03")
                resource_name = st.text_input("Resource name", placeholder="Seminar Room 3")
                resource_type_label = st.selectbox(
                    "Resource type",
                    ["Classroom", "Lab", "Amphitheatre", "Guest House", "Parking"],
                )
            with form_col2:
                resource_location = st.text_input("Location", placeholder="Academic Block")
                resource_capacity = st.number_input(
                    "Capacity (people / beds / slots)",
                    min_value=1,
                    max_value=1000,
                    value=30,
                )
            add_resource_clicked = st.form_submit_button(
                "Add resource to PostgreSQL",
                use_container_width=True,
            )

        if add_resource_clicked:
            if not resource_code.strip() or not resource_name.strip():
                st.warning("Resource code and name are required.")
            else:
                created = add_resource(
                    resource_code.strip(),
                    resource_name.strip(),
                    resource_type_label.lower().replace(" ", "_"),
                    int(resource_capacity),
                    resource_location.strip() or None,
                    actor_id=admin_id,
                )
                if created.get("success"):
                    st.success("Resource saved in PostgreSQL.")
                    st.rerun()
                else:
                    st.error(created.get("message", "Resource could not be saved."))

        resource_filter = st.selectbox(
            "Filter inventory",
            ["All", "Classroom", "Lab", "Amphitheatre", "Guest House", "Parking"],
            key="db_resource_filter",
        )
        filter_value = (
            None if resource_filter == "All"
            else resource_filter.lower().replace(" ", "_")
        )
        inventory = get_resources(resource_type=filter_value, include_inactive=True)

        if not inventory:
            st.info("No resources found. Add synthetic demo resources above.")
        else:
            for resource in inventory:
                with st.container(border=True):
                    left, right = st.columns([4, 1])
                    with left:
                        st.markdown(f"**{resource['name']}**")
                        st.caption(
                            f"Code: {resource['resource_code']} · "
                            f"Type: {resource['resource_type'].replace('_', ' ').title()} · "
                            f"Capacity: {resource['capacity']} · "
                            f"Location: {resource.get('location') or 'Not listed'}"
                        )
                    with right:
                        is_active = bool(resource["is_active"])
                        st.success("Active") if is_active else st.warning("Inactive")
                        if st.button(
                            "Deactivate" if is_active else "Activate",
                            key=f"toggle_db_resource_{resource['id']}",
                            use_container_width=True,
                        ):
                            changed = update_resource(
                                resource["id"], admin_id, is_active=not is_active
                            )
                            if changed.get("success"):
                                st.session_state["resource_action_message"] = (
                                    f"{resource['name']} status saved in PostgreSQL."
                                )
                            else:
                                st.session_state["resource_action_message"] = changed.get(
                                    "message", "Resource update failed."
                                )
                            st.rerun()

        if st.session_state.get("resource_action_message"):
            st.info(st.session_state.pop("resource_action_message"))

    except Exception as exc:
        st.error(f"Could not load or update PostgreSQL resources: {type(exc).__name__}: {exc}")
        st.info("Check DATABASE_URL, run init_db.py and seed_demo.py, then retry.")

    # REPORTS AND ANALYTICS
    # ----------------------------------

    st.divider()

    st.subheader("📊 Reports & Analytics")

    st.write(
        "Monitor campus resource usage and booking activity."
    )

    # Synthetic demonstration data
    st.markdown("### Booking Statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Bookings", 45)
    col2.metric("Approved", 30)
    col3.metric("Pending", 10)
    col4.metric("Rejected", 5)

    st.divider()

    # Resource demand chart
    st.markdown("### 🏫 Resource-wise Booking Demand")

    resource_chart_data = {
        "Resource Type": [
            "Classroom",
            "Amphitheatre",
            "Lab",
            "Guest House",
            "Parking"
        ],
        "Bookings": [18, 8, 7, 5, 7]
    }

    st.bar_chart(
        resource_chart_data,
        x="Resource Type",
        y="Bookings",
        x_label="Resource Type",
        y_label="Number of Bookings"
    )

    st.divider()

    # Booking status chart
    st.markdown("### 📋 Booking Status Overview")

    status_chart_data = {
        "Status": [
            "Approved",
            "Pending",
            "Rejected"
        ],
        "Count": [30, 10, 5]
    }

    st.bar_chart(
        status_chart_data,
        x="Status",
        y="Count",
        x_label="Booking Status",
        y_label="Number of Requests"
    )

    st.divider()

    # Resource utilisation
    st.markdown("### 📈 Resource Utilisation")

    utilisation_data = {
        "Resource": [
            "Classrooms",
            "Amphitheatres",
            "Labs",
            "Guest House",
            "Parking"
        ],
        "Utilisation (%)": [75, 60, 80, 45, 55]
    }

    for item in utilisation_data["Resource"]:
        index = utilisation_data["Resource"].index(item)

        st.write(
            f"**{item} — "
            f"{utilisation_data['Utilisation (%)'][index]}%**"
        )

        st.progress(
            utilisation_data["Utilisation (%)"][index] / 100
        )

    st.caption(
        "All figures are synthetic demonstration data. "
        "Member 2 will connect these reports to actual "
        "booking and resource database records."
    )

    st.subheader("📝 Audit Logs")

    st.info(
        "Booking approvals, rejections and other "
        "administrative actions will be recorded "
        "in the database by Member 2."
    )

    st.caption(
        "Demonstration dashboard. Approval actions currently "
        "update sample session data only, not the database."
    )

st.divider()
st.caption("CampusPilot AI | JKLU AI Buildathon 2026")
