import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- App configuration ---
st.set_page_config(
    page_title="Data Cleaner App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar / Navigation ---
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "👤 Profile", "📊 Data Cleaner", "📤 Export"])

# --- Sidebar footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("Created by **Your Name**")
st.sidebar.markdown("[GitHub](https://github.com/your-username) | [LinkedIn](https://linkedin.com/in/your-link)")

def import_user_file():
    """Streamlit uploader for CSV and Excel files. Returns a DataFrame or None."""
    uploaded_file = st.file_uploader("📂 Upload your CSV or Excel file", type=["csv", "xlsx", "xls"])
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

    required_cols = ['zone', 'department', 'located at', 'machine/equipment name', 
                     'year of purchase', 'person in charge', 'remark']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        return None, None, None

    group1 = (
        df.groupby(['zone', 'department', 'located at'])['machine/equipment name']
          .value_counts()
          .reset_index(name='count')
          .sort_values(['zone', 'department', 'located at', 'count'], ascending=[True, True, True, False])
    )
    group2 = (
        df.groupby(['zone', 'department'])['machine/equipment name']
          .value_counts()
          .reset_index(name='count')
          .sort_values(['zone', 'department', 'count'], ascending=[True, True, False])
    )
    group3 = (
        df.groupby(['zone'])['machine/equipment name']
          .value_counts()
          .reset_index(name='count')
          .sort_values(['zone', 'count'], ascending=[True, False])
    )
    return group1, group2, group3

def plot_bar_chart(df, x_col, y_col, color_col, title, hover_extra=None):
    if hover_extra is None:
        hover_extra = []
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={y_col: 'Count', x_col: x_col.title()},
        barmode='group',
        hover_data=hover_extra
    )
    st.plotly_chart(fig, use_container_width=True)

def create_excel_report(group1, group2, group3):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        group1.to_excel(writer, sheet_name='Zone_Department_Building', index=False)
        group2.to_excel(writer, sheet_name='Zone_Department', index=False)
        group3.to_excel(writer, sheet_name='Zone', index=False)
    return output.getvalue()

# --- Main Area ---
if page == "🏠 Home":
    st.title("🏠 Welcome to the Data Cleaner App")
    st.write("This app will help you upload, clean, analyze, and export equipment data efficiently.")
    st.info("Use the sidebar to navigate to different sections.")

elif page == "👤 Profile":
    st.title("👤 User Profile")
    st.write("This is a placeholder for a future profile section.")
    with st.expander("User Info"):
        st.write("Name: Menghorng")
        st.write("Role: Data Engineer")
        st.write("Email: menghorng@example.com")

elif page == "📊 Data Cleaner":
    st.title("📊 Data Cleaning and Analysis")

    df = import_user_file()
    if df is not None:
        st.subheader("Raw Data Preview")
        st.dataframe(df, use_container_width=True)

        group1, group2, group3 = generate_grouped_counts(df)

        if group1 is not None:
            st.header("Grouped Counts & Visualizations")

            tab1, tab2, tab3 = st.tabs([
                "Zone + Dept + Building",
                "Zone + Dept",
                "Zone Only"
            ])

            with tab1:
                st.subheader("1️⃣ By Zone + Department + Building")
                st.dataframe(group1, use_container_width=True)
                plot_bar_chart(group1, 'machine/equipment name', 'count', 'department',
                            'Machine Count by Zone, Department & Building',
                            hover_extra=['zone', 'department', 'located at'])

            with tab2:
                st.subheader("2️⃣ By Zone + Department")
                st.dataframe(group2, use_container_width=True)
                plot_bar_chart(group2, 'machine/equipment name', 'count', 'department',
                            'Machine Count by Zone & Department',
                            hover_extra=['zone', 'department'])

            with tab3:
                st.subheader("3️⃣ By Zone")
                st.dataframe(group3, use_container_width=True)
                plot_bar_chart(group3, 'machine/equipment name', 'count', 'zone',
                            'Machine Count by Zone',
                            hover_extra=['zone'])

            st.header("🛠️ Maintenance Information")
            cols_to_show = ['machine/equipment name', 'year of purchase', 'person in charge', 'remark']
            available_cols = [col for col in cols_to_show if col in df.columns]
            st.dataframe(df[available_cols], use_container_width=True)

            # Save grouped data for export page
            st.session_state.group1 = group1
            st.session_state.group2 = group2
            st.session_state.group3 = group3
        else:
            st.warning("Please fix missing columns and reload your data.")

elif page == "📤 Export":
    st.title("📤 Export Report")

    group1 = st.session_state.get('group1', None)
    group2 = st.session_state.get('group2', None)
    group3 = st.session_state.get('group3', None)

    if all([group1 is not None, group2 is not None, group3 is not None]):
        st.subheader("Grouped Data Preview")
        st.write("Preview before download:")
        st.dataframe(group1, use_container_width=True)

        excel_data = create_excel_report(group1, group2, group3)

        st.download_button(
            label="⬇️ Download Full Equipment Report (Excel)",
            data=excel_data,
            file_name="equipment_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No grouped data found. Please upload and process data in the Data Cleaner page first.")
