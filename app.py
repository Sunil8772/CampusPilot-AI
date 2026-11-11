
import streamlit as st
from datetime import time
from agent.orchestrator import process_user_request

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

role = st.sidebar.selectbox(
    "Login as",
    ["Student", "Faculty", "Admin"]
)

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

        with st.spinner("Gemini is understanding your request and checking campus systems..."):
            agent_result = process_user_request(user_message, user_id=None)

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

    st.title("🛡️ Campus Administration Dashboard")

    st.write(
        "Manage booking requests, campus resources "
        "and timetable operations."
    )

    st.divider()

    # Demo booking data
    if "admin_bookings" not in st.session_state:
        st.session_state.admin_bookings = [
            {
                "id": "BK-2001",
                "user": "FAC-001",
                "resource": "Classroom EB1-101",
                "date": "2026-11-12",
                "time": "14:00 - 16:00",
                "status": "Pending"
            },
            {
                "id": "BK-2002",
                "user": "FAC-002",
                "resource": "Amphitheatre 1",
                "date": "2026-11-14",
                "time": "10:00 - 12:00",
                "status": "Pending"
            },
            {
                "id": "BK-2003",
                "user": "FAC-003",
                "resource": "Guest House Room 2",
                "date": "2026-11-16",
                "time": "Check-in",
                "status": "Approved"
            }
        ]

    bookings = st.session_state.admin_bookings

    # Dashboard metrics
    total = len(bookings)
    pending = sum(
        b["status"] == "Pending" for b in bookings
    )
    approved = sum(
        b["status"] == "Approved" for b in bookings
    )
    rejected = sum(
        b["status"] == "Rejected" for b in bookings
    )

    st.subheader("📊 Booking Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Requests", total)
    c2.metric("Pending", pending)
    c3.metric("Approved", approved)
    c4.metric("Rejected", rejected)

    st.divider()

    # Booking approvals
    st.subheader("📋 Booking Approval Requests")

    pending_bookings = [
        b for b in bookings if b["status"] == "Pending"
    ]

    if pending_bookings:

        for booking in pending_bookings:

            with st.container(border=True):

                st.markdown(f"### {booking['resource']}")

                st.write(f"Booking ID: {booking['id']}")
                st.write(f"Requested by: {booking['user']}")
                st.write(f"Date: {booking['date']}")
                st.write(f"Time: {booking['time']}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "✅ Approve",
                        key=f"approve_{booking['id']}",
                        use_container_width=True
                    ):
                        booking["status"] = "Approved"
                        st.session_state[
                            "admin_action_message"
                        ] = f"{booking['id']} approved."
                        st.rerun()

                with col2:
                    if st.button(
                        "❌ Reject",
                        key=f"reject_{booking['id']}",
                        use_container_width=True
                    ):
                        booking["status"] = "Rejected"
                        st.session_state[
                            "admin_action_message"
                        ] = f"{booking['id']} rejected."
                        st.rerun()

    else:
        st.success("No pending booking requests.")

    if st.session_state.get("admin_action_message"):
        st.info(st.session_state.admin_action_message)

    st.divider()

    # Management sections
    st.subheader("⚙️ Campus Management")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### 📅 Timetable Management")
            st.write("Upload and review semester timetables.")

            st.info(
                "Member 1 and Member 2 will integrate "
                "timetable parsing and publishing."
            )

    with col2:
        with st.container(border=True):
            st.markdown("### 🏫 Resource Management")
            st.write("Manage classrooms, labs and parking.")

            st.info(
                "Member 2 will integrate resource management."
            )
    
    # ----------------------------------
    # TIMETABLE MANAGEMENT
    # ----------------------------------

    st.subheader("📅 Timetable Management")

    st.write(
        "Upload and manage semester-wise campus timetables."
    )

    with st.container(border=True):

        st.markdown("### 📤 Upload New Timetable")

        col1, col2 = st.columns(2)

        with col1:
            semester = st.selectbox(
                "Select Semester",
                [1, 2, 3, 4, 5, 6, 7, 8],
                key="timetable_semester"
            )

        with col2:
            academic_year = st.text_input(
                "Academic Year",
                value="2026-27",
                key="timetable_academic_year"
            )

        uploaded_file = st.file_uploader(
            "Upload Timetable",
            type=["pdf", "xlsx", "xls", "csv"],
            help="Supported formats: PDF, Excel and CSV",
            key="timetable_file"
        )

        if uploaded_file is not None:

            st.success("File selected successfully!")

            st.write(f"**File name:** {uploaded_file.name}")
            st.write(
                f"**File size:** "
                f"{uploaded_file.size / 1024:.2f} KB"
            )

            if st.button(
                "📥 Submit Timetable for Parsing",
                use_container_width=True,
                key="submit_timetable"
            ):

                if not academic_year.strip():
                    st.error("Please enter the academic year.")

                elif "-" not in academic_year:
                    st.error(
                        "Enter academic year in format 2026-27."
                    )

                else:
                    st.session_state["timetable_upload"] = {
                        "file_name": uploaded_file.name,
                        "semester": semester,
                        "academic_year": academic_year.strip(),
                        "file_size": uploaded_file.size,
                        "status": "Uploaded - awaiting parser integration"
                    }

                    st.success(
                        "Timetable upload details saved successfully!"
                    )

        else:
            st.info("Please select a timetable file to continue.")

    st.divider()

    # ----------------------------------
    # UPLOAD STATUS AND REVIEW
    # ----------------------------------

    st.subheader("📋 Timetable Import Status")

    timetable_upload = st.session_state.get(
        "timetable_upload"
    )

    if timetable_upload:

        with st.container(border=True):

            st.write(
                f"**File:** {timetable_upload['file_name']}"
            )

            st.write(
                f"**Semester:** "
                f"{timetable_upload['semester']}"
            )

            st.write(
                f"**Academic Year:** "
                f"{timetable_upload['academic_year']}"
            )

            st.warning(
                "Waiting for Member 1's timetable parser. "
                "Extracted records and validation results "
                "will appear here after integration."
            )

            st.write(
                f"**Status:** {timetable_upload['status']}"
            )

    else:
        st.info("No timetable has been submitted yet.")

    st.divider()

    # ----------------------------------
    # TIMETABLE VERSION HISTORY
    # ----------------------------------

    st.subheader("🗂️ Timetable Version History")

    st.info(
        "Member 2 will connect the database here to display "
        "published timetable versions, upload dates and "
        "the active version for each semester."
    )

    st.caption(
        "Only validated and admin-reviewed timetables "
        "should be published. Previous versions must be preserved."
    )
  

    st.divider()
    # ----------------------------------
    # RESOURCE MANAGEMENT
    # ----------------------------------

    st.divider()

    st.subheader("🏫 Resource Management")

    st.write(
        "Add, view and manage campus classrooms, "
        "labs, event venues, guest house rooms and parking."
    )

    # Initialize demo resources
    if "campus_resources" not in st.session_state:
        st.session_state.campus_resources = [
            {
                "id": "R001",
                "name": "EB1-101",
                "type": "Classroom",
                "location": "EB1",
                "capacity": 60,
                "status": "Active"
            },
            {
                "id": "R002",
                "name": "Amphitheatre 1",
                "type": "Amphitheatre",
                "location": "Main Campus",
                "capacity": 200,
                "status": "Active"
            },
            {
                "id": "R003",
                "name": "Computer Lab 1",
                "type": "Lab",
                "location": "Academic Block",
                "capacity": 40,
                "status": "Active"
            }
        ]

    resources = st.session_state.campus_resources

    # Add new resource
    with st.container(border=True):

        st.markdown("### ➕ Add New Resource")

        with st.form("add_resource_form"):

            col1, col2 = st.columns(2)

            with col1:
                resource_name = st.text_input(
                    "Resource Name",
                    placeholder="Example: EB1-102"
                )

                resource_type = st.selectbox(
                    "Resource Type",
                    [
                        "Classroom",
                        "Amphitheatre",
                        "Lab",
                        "Guest House",
                        "Parking"
                    ]
                )

            with col2:
                location = st.text_input(
                    "Location",
                    placeholder="Example: Academic Block"
                )

                capacity = st.number_input(
                    "Capacity (people, beds or slots)",
                    min_value=1,
                    max_value=1000,
                    value=50
                )

            add_resource = st.form_submit_button(
                "➕ Add Resource",
                use_container_width=True
            )

            if add_resource:

                if not resource_name.strip():
                    st.error("Please enter a resource name.")

                elif not location.strip():
                    st.error("Please enter the resource location.")

                elif any(
                    r["name"].lower() == resource_name.strip().lower()
                    for r in resources
                ):
                    st.error("This resource already exists.")

                else:
                    new_resource = {
                        "id": f"R{len(resources) + 1:03d}",
                        "name": resource_name.strip(),
                        "type": resource_type,
                        "location": location.strip(),
                        "capacity": int(capacity),
                        "status": "Active"
                    }

                    st.session_state.campus_resources.append(
                        new_resource
                    )

                    st.success("Resource added successfully!")
                    st.rerun()

    st.divider()

    # View resources
    st.subheader("📋 Campus Resource Inventory")

    filter_type = st.selectbox(
        "Filter by Resource Type",
        [
            "All",
            "Classroom",
            "Amphitheatre",
            "Lab",
            "Guest House",
            "Parking"
        ],
        key="resource_filter"
    )

    if filter_type == "All":
        filtered_resources = resources
    else:
        filtered_resources = [
            r for r in resources
            if r["type"] == filter_type
        ]

    st.write(f"**Total resources displayed:** {len(filtered_resources)}")

    if filtered_resources:

        for resource in filtered_resources:

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {resource['name']}")
                    st.write(f"**Resource ID:** {resource['id']}")
                    st.write(f"**Type:** {resource['type']}")
                    st.write(f"**Location:** {resource['location']}")
                    st.write(f"**Capacity:** {resource['capacity']}")

                with col2:
                    st.write("**Status**")

                    if resource["status"] == "Active":
                        st.success("Active")
                    else:
                        st.error("Inactive")

                    if st.button(
                        "Deactivate" if resource["status"] == "Active"
                        else "Activate",
                        key=f"toggle_{resource['id']}"
                    ):
                        resource["status"] = (
                            "Inactive"
                            if resource["status"] == "Active"
                            else "Active"
                        )
                        st.rerun()

    else:
        st.info("No resources found.")

    st.caption(
        "Demonstration data only. Member 2 will connect "
        "resource management to PostgreSQL."
    )
    
    # ----------------------------------
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
