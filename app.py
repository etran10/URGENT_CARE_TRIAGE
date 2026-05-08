import streamlit as st
from patient import Patient
from triage_queue import TriageQueue
from providers import Provider, ProviderPool

# set page title and layout
st.set_page_config(
    page_title="Urgent Care Triage",
    layout="wide"
)

# custom CSS styling
st.markdown(
    """
    <style>

    .stApp {
        background-color: #F4F8FB;
    }

    h1, h2, h3 {
        color: #0F4C81;
        font-family: Arial;
    }

    .main-title {
        text-align: center;
        padding: 25px;
        background-color: #0F4C81;
        color: white;
        border-radius: 20px;
        margin-bottom: 30px;
    }

    .main-title h1 {
        color: white;
        margin-bottom: 10px;
        font-size: 60px;
    }

    .kiosk-card {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        text-align: center;
    }

    .provider-available {
        background-color: #DFF5E3;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 8px solid #28A745;
    }

    .provider-busy {
        background-color: #FFF3CD;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 8px solid #FF9800;
    }

    /* style all buttons */
    div.stButton > button {
        width: 100%;
        height: 110px;
        font-size: 26px;
        font-weight: bold;
        border-radius: 20px;
        border: none;
        background-color: #2EC4B6;
        color: white;
        margin-top: 10px;
    }

    /* button hover effect */
    div.stButton > button:hover {
        background-color: #239B90;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# create session variables if missing
if "page" not in st.session_state:
    st.session_state.page = "home"

if "queue" not in st.session_state:
    st.session_state.queue = TriageQueue()

# create provider pool once
if "pool" not in st.session_state:

    pool = ProviderPool()

    # add providers
    pool.add_provider(Provider("Dr. Nguyen", "MD"))
    pool.add_provider(Provider("Nurse Alex", "NP"))
    pool.add_provider(Provider("Dr. Hyun", "PA"))

    st.session_state.pool = pool

# shortcuts for easier access
queue = st.session_state.queue
pool = st.session_state.pool

# auto assign patient if provider is free
def try_auto_assign():

    available = pool.get_available()

    # get next patient in queue
    next_patient = queue.call_next()

    # assign patient if possible
    if available and next_patient:

        provider = pool.assign_next(next_patient)
        return next_patient, provider

    # return patient to queue if no provider
    elif next_patient:

        queue.add_patient(next_patient)

    return None, None

# app title header
st.markdown(
    """
    <div class='main-title'>
        <h1>URGENT CARE TRIAGE</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# home page
if st.session_state.page == "home":

    st.markdown("## Welcome")

    st.markdown(
        "<div style='text-align:center; font-size:22px;'>"
        "Please choose an option below."
        "</div>",
        unsafe_allow_html=True
    )

    st.write("")

    # create two columns
    col1, col2 = st.columns(2)

    with col1:

        # go to check-in page
        if st.button("Check In"):
            st.session_state.page = "checkin"
            st.rerun()

        # go to waiting list page
        if st.button("View Waiting List"):
            st.session_state.page = "waiting_list"
            st.rerun()

    with col2:

        # go to update page
        if st.button("Update Status"):
            st.session_state.page = "update"
            st.rerun()

        # go to staff login page
        if st.button("Staff Login"):
            st.session_state.page = "staff_login"
            st.rerun()

# patient check-in page
elif st.session_state.page == "checkin":

    st.header("Patient Check-In")

    # patient name input
    name = st.text_input("Full Name")

    # pain level slider
    pain = st.select_slider(
        "Pain Level",
        options=[1, 2, 3, 4, 5],
        value=3
    )

    # pain level descriptions
    st.write("### Pain Level Guide")
    st.write("1 — Minimal")
    st.write("2 — Mild")
    st.write("3 — Moderate")
    st.write("4 — Severe")
    st.write("5 — Most Urgent")

    # submit check-in button
    if st.button("Submit Check-In"):

        # prevent blank names
        if name.strip() == "":
            st.error("Please enter your name.")

        else:

            # create patient object
            patient = Patient(name, pain)

            # add patient to queue
            queue.add_patient(patient)

            # try assigning provider
            assigned_patient, provider = try_auto_assign()

            st.success(f"{name} checked in successfully.")

            # provider available
            if assigned_patient and provider:

                st.success(
                    f"A provider is ready for you: {provider.name}"
                )

            # no provider available
            else:

                st.info(
                    "Please have a seat. "
                    "A provider will be with you shortly."
                )

    # return to home page
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# update status page
elif st.session_state.page == "update":

    st.header("Update Your Status")

    # get patient name
    name = st.text_input("Enter your name")

    patients = queue.all_patients()

    # find matching patient
    patient_match = next(
        (p for p in patients if p.name.lower() == name.lower()),
        None
    )

    # wait time dropdown
    st.selectbox(
        "How long have you been waiting?",
        [
            "Less than 30 minutes",
            "30–60 minutes",
            "1–2 hours",
            "More than 2 hours"
        ]
    )

    # ask if pain changed
    pain_change = st.radio(
        "Has your pain level changed?",
        [
            "Yes, it is worse",
            "Yes, it has improved",
            "No change"
        ]
    )

    new_pain = None

    # show new pain slider if pain worsened
    if pain_change == "Yes, it is worse":

        new_pain = st.select_slider(
            "New Pain Level",
            options=[1, 2, 3, 4, 5],
            value=4
        )

    # submit update button
    if st.button("Submit Update"):

        # prevent blank names
        if name.strip() == "":
            st.error("Please enter your name.")

        # patient not found
        elif not patient_match:
            st.error("Patient not found.")

        else:

            # update pain level
            if new_pain:
                patient_match.pain_level = new_pain

            st.success("Status updated successfully.")

    # return to home page
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# waiting list page
elif st.session_state.page == "waiting_list":

    st.header("Current Waiting List")

    # sort patients by priority
    patients = sorted(
        queue.all_patients(),
        key=lambda p: (-p.pain_level, p.check_in_time)
    )

    # display patients
    if patients:

        for i, p in enumerate(patients, start=1):

            checkin_time = p.check_in_time.strftime("%I:%M %p")

            st.markdown(
                f"""
                <div class='kiosk-card'>
                    <h3>#{i} — {p.name}</h3>
                    <p>Pain Level: {p.pain_level}</p>
                    <p>Checked In: {checkin_time}</p>
                    <p>Waiting: {p.wait_time_minutes()} minutes</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("No patients currently waiting.")

    # return to home page
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# staff login page
elif st.session_state.page == "staff_login":

    st.header("Staff Login")

    # password input
    password = st.text_input(
        "Enter Staff Password",
        type="password"
    )

    # login button
    if st.button("Login"):

        # check password
        if password == "admin123":

            st.session_state.page = "staff_dashboard"
            st.rerun()

        else:
            st.error("Incorrect password.")

    # return to home page
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# staff dashboard page
elif st.session_state.page == "staff_dashboard":

    st.sidebar.title("Staff Navigation")

    # sidebar navigation
    staff_page = st.sidebar.radio(
        "Go To",
        [
            "Queue",
            "Providers",
            "Assign Patient"
        ]
    )

    # logout button
    if st.sidebar.button("Logout"):

        st.session_state.page = "home"
        st.rerun()

    st.header("Staff Dashboard")

    # queue section
    if staff_page == "Queue":

        st.subheader("Waiting Patients")

        # sort waiting patients
        patients = sorted(
            queue.all_patients(),
            key=lambda p: (-p.pain_level, p.check_in_time)
        )

        if patients:

            for i, p in enumerate(patients, start=1):

                checkin_time = p.check_in_time.strftime("%I:%M %p")

                st.markdown(
                    f"""
                    <div class='kiosk-card'>
                        <h3>#{i} — {p.name}</h3>
                        <p>Pain Level: {p.pain_level}</p>
                        <p>Checked In: {checkin_time}</p>
                        <p>Waiting: {p.wait_time_minutes()} minutes</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.info("No patients waiting.")

    # provider section
    elif staff_page == "Providers":

        st.subheader("Provider Status")

        providers = pool.get_all()

        for i, provider in enumerate(providers):

            # provider is available
            if provider.available:

                st.markdown(
                    f"""
                    <div class='provider-available'>
                        <h3>{provider.name}</h3>
                        <p>{provider.role}</p>
                        <strong>AVAILABLE</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # provider is busy
            else:

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.markdown(
                        f"""
                        <div class='provider-busy'>
                            <h3>{provider.name}</h3>
                            <p>{provider.role}</p>
                            <strong>
                                With Patient:
                                {provider.current_patient.name}
                            </strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:

                    # free up provider
                    if st.button(
                        "Mark Available",
                        key=f"free_{i}"
                    ):

                        provider.free_up()

                        st.success(
                            f"{provider.name} is now available."
                        )

                        st.rerun()

    # assign patient section
    elif staff_page == "Assign Patient":

        st.subheader("Assign Next Patient")

        # get counts for dashboard
        waiting_count = len(queue.all_patients())
        available_count = len(pool.get_available())

        col1, col2 = st.columns(2)

        # show waiting patients count
        with col1:
            st.metric("Patients Waiting", waiting_count)

        # show provider count
        with col2:
            st.metric(
                "Providers Available",
                available_count
            )

        st.write("")

        # assign next patient button
        if st.button("Call Next Patient"):

            available = pool.get_available()

            # no providers free
            if not available:
                st.error("No providers available.")

            else:

                # get next patient
                next_patient = queue.call_next()

                if not next_patient:
                    st.warning("Queue is empty.")

                else:

                    # assign patient to provider
                    provider = pool.assign_next(next_patient)

                    st.success(
                        f"{next_patient.name} assigned to "
                        f"{provider.name}"
                    )

                    st.rerun()