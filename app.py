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
    st.warning("This section is under construction...")

elif page == "📤 Export":
    st.title("📤 Export Options")
    st.warning("This section will allow downloads and cloud sync later.")