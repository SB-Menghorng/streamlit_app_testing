import io
import math
import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

# --- App configuration ---
st.set_page_config(
    page_title="Data Cleaner App", layout="wide", initial_sidebar_state="expanded"
)

# --- Sidebar / Navigation ---
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio(
    "Go to", ["🏠 Home", "👤 Profile", "📊 Data Cleaner", "📤 Export"]
)

# --- Sidebar footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("Created by **Your Name**")
st.sidebar.markdown(
    "[GitHub](https://github.com/your-username) | [LinkedIn](https://linkedin.com/in/your-link)"
)


def import_user_file():
    """Streamlit uploader for CSV and Excel files. Returns a DataFrame or None."""
    uploaded_file = st.file_uploader(
        "📂 Upload your CSV or Excel file", type=["csv", "xlsx", "xls"]
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("✅ File successfully loaded!")
            return df
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            return None
    else:
        st.info("👈 Please upload a file to begin.")
        return None


def generate_grouped_counts(df):
    df.columns = df.columns.str.lower()
    # Clean machine name example
    if "machine/equipment name" in df.columns:
        df["machine/equipment name"] = df["machine/equipment name"].str.replace(
            "Air-con", "Air Conditioner", case=False, regex=True
        )

    required_cols = [
        "zone",
        "department",
        "located at",
        "machine/equipment name",
        "year of purchase",
        "person in charge",
        "remark",
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        return None, None, None

    group1 = (
        df.groupby(["zone", "department", "located at"])["machine/equipment name"]
        .value_counts()
        .reset_index(name="count")
        .sort_values(
            ["zone", "department", "located at", "count"],
            ascending=[True, True, True, False],
        )
    )
    group2 = (
        df.groupby(["zone", "department"])["machine/equipment name"]
        .value_counts()
        .reset_index(name="count")
        .sort_values(["zone", "department", "count"], ascending=[True, True, False])
    )
    group3 = (
        df.groupby(["zone"])["machine/equipment name"]
        .value_counts()
        .reset_index(name="count")
        .sort_values(["zone", "count"], ascending=[True, False])
    )
    return group1, group2, group3


def plot_bar_chart(df, x_col, y_col, color_col, title, hover_extra=None):
    if hover_extra is None:
        hover_extra = []

    df_sum = (
        df.groupby([x_col, color_col])[y_col]
        .sum()
        .reset_index()
    )

    hover_data_safe = [col for col in hover_extra if col in df_sum.columns]

    # Find max y value and add padding (10% of max)
    max_y = df_sum[y_col].max()
    y_max_padded = math.ceil(max_y * 1.15)

    fig = px.bar(
        df_sum,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={y_col: "Count", x_col: x_col.title()},
        barmode="group",
        hover_data=hover_data_safe,
        text=y_col
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        yaxis=dict(title='Total Count', range=[0, y_max_padded]),
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis_tickangle=-30
    )

    st.plotly_chart(fig, use_container_width=True)


def create_excel_report(group1, group2, group3):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        group1.to_excel(writer, sheet_name="Zone_Department_Building", index=False)
        group2.to_excel(writer, sheet_name="Zone_Department", index=False)
        group3.to_excel(writer, sheet_name="Zone", index=False)
    return output.getvalue()


if page == "🏠 Home":
    st.title("🏠 Welcome to the Data Cleaner App")

    st.markdown(
        """
        #### Streamline Your Equipment Data Management

        This app empowers you to:
        - 📂 **Upload** your equipment data files (CSV, Excel)
        - 🧹 **Clean** and standardize your data effortlessly
        - 📊 **Analyze** grouped equipment counts with interactive charts
        - 📤 **Export** comprehensive reports for maintenance and management

        ---
        """
    )

    st.info(
        """
        **Quick Start Tips:**
        1. Use the **📊 Data Cleaner** section to upload and explore your data.
        2. Customize your view by selecting grouping options and charts.
        3. Export reports in the **📤 Export** section for sharing or offline use.
        4. Update your user profile in the **👤 Profile** section.
        """
    )

    st.image(
        "https://cdn-icons-png.flaticon.com/512/3595/3595457.png",
        width=120,
        caption="Optimize your workflow with smart data cleaning & visualization",
    )
elif page == "👤 Profile":
    st.title("👤 User Profile")

    # Initialize profile and photo in session_state if missing
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "Name": "Menghorng",
            "Role": "Data Engineer",
            "Email": "menghorng@example.com",
            "last_saved": None,
        }
    if "profile_photo" not in st.session_state:
        st.session_state.profile_photo = None

    profile = st.session_state.profile

    def is_valid_email(email):
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    st.subheader("👤 Upload or update your profile photo")
    uploaded_photo = st.file_uploader(
        "Upload profile picture (PNG/JPG, max 1MB)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
    )
    if uploaded_photo is not None:
        if uploaded_photo.size > 1_000_000:
            st.warning("⚠️ Please upload an image smaller than 1MB.")
        else:
            st.session_state.profile_photo = uploaded_photo.read()
            st.success("✅ Profile photo uploaded successfully!")

    if st.session_state.profile_photo:
        st.image(
            st.session_state.profile_photo, width=150, caption="Current Profile Photo"
        )

    st.markdown("---")
    st.subheader("Edit your profile details")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "👤 Name",
            value=profile.get("Name", ""),
            max_chars=50,
            placeholder="Enter your full name",
        )
    with col2:
        role = st.text_input(
            "💼 Role",
            value=profile.get("Role", ""),
            max_chars=50,
            placeholder="Your job title or position",
        )

    email = st.text_input(
        "📧 Email", value=profile.get("Email", ""), placeholder="name@example.com"
    )

    # Validation feedback
    email_valid = is_valid_email(email)
    if email and not email_valid:
        st.warning("⚠️ Please enter a valid email address.")

    save = st.button("💾 Save Profile")

    if save:
        if not name.strip():
            st.error("❌ Name cannot be empty.")
        elif not email_valid:
            st.error("❌ Invalid email format.")
        else:
            st.session_state.profile["Name"] = name.strip()
            st.session_state.profile["Role"] = role.strip()
            st.session_state.profile["Email"] = email.strip()
            st.session_state.profile["last_saved"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            st.success("✅ Profile updated successfully!")

    # Show current profile info with last saved time
    with st.expander("📋 Current Profile Info", expanded=True):
        st.write(f"**Name:** {st.session_state.profile['Name']}")
        st.write(f"**Role:** {st.session_state.profile['Role']}")
        st.write(f"**Email:** {st.session_state.profile['Email']}")
        last_saved = st.session_state.profile.get("last_saved")
        if last_saved:
            st.caption(f"Last saved on {last_saved}")

elif page == "📊 Data Cleaner":

    st.title("📊 Data Cleaning and Analysis")

    # Operation mode selector (extendable)
    option = st.selectbox(
        "Select cleaning or analysis operation",
        options=["Maintenance"],
        index=0,
        help="Choose the operation type you want to perform"
    )
    df = import_user_file()
    if df is not None:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(
            editable=False,
            filter=True,
            sortable=True,
            resizable=True,
            wrapText=True,
            autoHeight=True,
        )
        gb.configure_pagination(paginationAutoPageSize=True)  # Auto page size
        gb.configure_side_bar()  # Optional: adds sidebar for filters/sorting

        grid_options = gb.build()

        AgGrid(
            df,
            gridOptions=grid_options,
            theme="fresh",  # Options: "streamlit", "light", "dark", "blue", "fresh", "material"
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,  # Required for custom JS features
            enable_enterprise_modules=False  # Set True if using enterprise features
        )
        if option == "Maintenance":
            group1, group2, group3 = generate_grouped_counts(df)

            if group1 is not None:
                st.header("Grouped Counts & Visualizations")

                tab1, tab2, tab3 = st.tabs(
                    ["Zone + Dept + Building", "Zone + Dept", "Zone Only"]
                )

                with tab1:
                    st.subheader("1️⃣ By Zone + Department + Building")
                    st.dataframe(group1, use_container_width=True)
                    plot_bar_chart(
                        group1,
                        "machine/equipment name",
                        "count",
                        "department",
                        "Machine Count by Zone, Department & Building",
                        hover_extra=["zone", "department", "located at"],
                    )

                with tab2:
                    st.subheader("2️⃣ By Zone + Department")
                    st.dataframe(group2, use_container_width=True)
                    plot_bar_chart(
                        group2,
                        "machine/equipment name",
                        "count",
                        "department",
                        "Machine Count by Zone & Department",
                        hover_extra=["zone", "department"],
                    )

                with tab3:
                    st.subheader("3️⃣ By Zone")
                    st.dataframe(group3, use_container_width=True)
                    plot_bar_chart(
                        group3,
                        "machine/equipment name",
                        "count",
                        "zone",
                        "Machine Count by Zone",
                        hover_extra=["zone"],
                    )

                st.header("🛠️ Maintenance Information")
                cols_to_show = [
                    "machine/equipment name",
                    "year of purchase",
                    "person in charge",
                    "remark",
                ]
                available_cols = [col for col in cols_to_show if col in df.columns]
                st.dataframe(df[available_cols], use_container_width=True)

                # Save grouped data for export page
                st.session_state.group1 = group1
                st.session_state.group2 = group2
                st.session_state.group3 = group3
            else:
                st.warning("Please fix missing columns and reload your data.")
        else:
            st.warning("Selected operation is not yet implemented.")
elif page == "📤 Export":
    st.title("📤 Export Report")

    group1 = st.session_state.get("group1", None)
    group2 = st.session_state.get("group2", None)
    group3 = st.session_state.get("group3", None)

    if all([group1 is not None, group2 is not None, group3 is not None]):
        st.subheader("Grouped Data Preview")
        st.write("Preview before download:")
        st.dataframe(group1, use_container_width=True)

        excel_data = create_excel_report(group1, group2, group3)

        st.download_button(
            label="⬇️ Download Full Equipment Report (Excel)",
            data=excel_data,
            file_name="equipment_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.warning(
            "No grouped data found. Please upload and process data in the Data Cleaner page first."
        )
