import streamlit as st
import pandas as pd

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


# --- Main Area ---
if page == "🏠 Home":
    st.title("🏠 Welcome to the Data Cleaner App")
    st.write("This app will help you upload, clean, and export equipment data efficiently.")
    st.info("Use the sidebar to navigate to different sections.")

elif page == "👤 Profile":
    st.title("👤 User Profile")
    st.write("This is a placeholder for a future profile section.")
    with st.expander("User Info"):
        st.write("Name: Menghorng")
        st.write("Role: Data Engineer")
        st.write("Email: menghorng@example.com")
        
elif page == "📊 Data Cleaner":
    st.title("📊 Data Cleaning Section")

    df = import_user_file()

    if df is not None:
        st.subheader("Preview of Uploaded Data")
        st.dataframe(df, use_container_width=True)

elif page == "📤 Export":
    st.title("📤 Export Options")
    st.warning("This section will allow downloads and cloud sync later.")