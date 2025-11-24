"""
Simple password authentication for Streamlit app
"""

import streamlit as st
import hashlib
import os

def check_password():
    """
    Returns True if the user has entered the correct password.
    Displays a password input form if not authenticated.
    """

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get password from environment or secrets
        correct_password = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")

        if not correct_password:
            # If no password set, allow access (for local development)
            st.session_state["password_correct"] = True
            return

        # Hash the entered password for comparison
        entered_password = st.session_state["password"]

        if entered_password == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # Return True if password is already validated
    if st.session_state.get("password_correct", False):
        return True

    # Show password input form
    st.markdown("## 🔒 Reporter Database Updater")
    st.markdown("**Please enter the password to access the application**")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password",
            label_visibility="collapsed"
        )

        if st.session_state.get("password_correct", None) == False:
            st.error("😕 Password incorrect. Please try again.")

        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <small>Contact administrator if you forgot the password</small>
        </div>
        """, unsafe_allow_html=True)

    return False
