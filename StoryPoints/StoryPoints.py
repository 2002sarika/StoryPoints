import math
import streamlit as st
import json
import os
import pandas as pd
import altair as alt

STORY_POINTS_FILE = 'story_points.json'
GRID_VISIBILITY_FILE = 'grid_visibility.json'
SCRUM_MASTER = ['scrum.master', 'Bhavesh', 'Sarika'] 

# Fibonacci check function
def isFibonacci(num):
    def is_perfect_square(x):
        s = int(math.sqrt(x))
        return s * s == x

    return is_perfect_square(5 * num * num + 4) or is_perfect_square(5 * num * num - 4)

# Function to create files if they don't exist
def createfileifnotexists(filename, default_value=None):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(default_value, f)
    else:
        try:
            with open(filename, 'r') as f:
                json.load(f)
        except (json.JSONDecodeError, ValueError):
            with open(filename, 'w') as f:
                json.dump(default_value, f)

# Load and save story points
def load_story_points():
    createfileifnotexists(STORY_POINTS_FILE, {})
    with open(STORY_POINTS_FILE, 'r') as f:
        return json.load(f)

def save_story_points(story_points):
    with open(STORY_POINTS_FILE, 'w') as f:
        json.dump(story_points, f)

# Load and save grid visibility
def load_grid_visibility():
    createfileifnotexists(GRID_VISIBILITY_FILE, {"show_grid": False})
    with open(GRID_VISIBILITY_FILE, "r") as f:
        return json.load(f)

def save_grid_visibility(show_grid):
    with open(GRID_VISIBILITY_FILE, "w") as f:
        json.dump({"show_grid": show_grid}, f)

# Guest mode (ask for name and login as guest)
def guest_mode():
    if "username" not in st.session_state:
        st.title("Welcome to Story Points Board!!!")
        guest_name = st.text_input("Enter your name", "", placeholder="Type your name here...", max_chars=20)

        guest_mode_button = st.button("Submit as Guest")
        
        if guest_mode_button:
            if guest_name.strip():
                st.session_state.username = guest_name.strip()  # Store the guest name in session state
                st.session_state.logged_in = True  # Mark user as logged in
                st.success(f"Welcome, {guest_name.strip()}!")
                show_sidebar()  # Proceed to show the sidebar
            else:
                st.warning("Please enter a valid name!")
    else:
        show_sidebar()  # If already logged in, show the sidebar

# Sidebar navigation after login
def show_sidebar():
    st.sidebar.title("Navigation")
    page_option = st.sidebar.selectbox("Select Action", ["Add Story Points", "Toggle Grid Visibility", "View Charts"])

    if page_option == "Add Story Points":
        add_story_points_page()
    elif page_option == "Toggle Grid Visibility":
        toggle_grid_visibility()  # Scrum Master can toggle visibility
    elif page_option == "View Charts":
        view_charts_page()  # All users can view the charts if grid is visible

def add_story_points_page():
    if "username" not in st.session_state or not st.session_state.username:
        st.warning("Please enter your name before submitting story points.")
        return

    st.title(f"Submit Story Points for {st.session_state.username}")
    fibonacci_numbers = [1, 2, 3, 5, 8, 13, 21, 34]
    story_point = st.selectbox("Choose Fibonacci Story Points", fibonacci_numbers)
    submit_button = st.button("Submit Story Points")

    if submit_button:
        if submit_story_points(st.session_state.username, story_point):
            st.success("Story points submitted successfully!")
        else:
            st.error("You've already submitted your story points or didn't maintain a Fibonacci series.")

def submit_story_points(username, points):
    story_points = load_story_points()
    if isFibonacci(points):
        if username in story_points:
            return False  # Already submitted
        story_points[username] = points
        save_story_points(story_points)
        return True
    else:
        st.warning("Please enter Fibonacci numbers only.")

def delete_story_point(username):
    story_points = load_story_points()
    if username in story_points:
        del story_points[username]
        save_story_points(story_points)

def delete_all_story_points():
    save_story_points({})  # Save an empty dictionary to clear all records

def display_story_points_grid():
    st.title("View and Manage Story Points")
    story_points = load_story_points()

    if not story_points:
        st.write("No story points have been submitted yet.")
        return

    data = {"User": list(story_points.keys()), "Story Points": list(story_points.values())}
    df = pd.DataFrame(data)
    checkboxes = [st.checkbox(f"Select {user}", key=user) for user in df['User']]
    df["Select"] = checkboxes
    st.write(df)

    selected_users = df[df['Select']].User.tolist()
    delete_selected_button = st.button("Delete Selected", key="delete_selected")
    delete_all_button = st.button("Delete All", key="delete_all")

    if delete_selected_button:
        if selected_users:
            for user in selected_users:
                delete_story_point(user)
            st.success(f"Deleted selected users: {', '.join(selected_users)}")
        else:
            st.warning("No users selected for deletion.")

    if delete_all_button:
        delete_all_story_points()
        st.success("All story points have been deleted.")

def toggle_grid_visibility():
    grid_visibility = load_grid_visibility()
    show_grid = grid_visibility["show_grid"]

    if st.session_state.username in SCRUM_MASTER:
        if st.button("Show/Hide Story Points Grid"):
            show_grid = not show_grid
            save_grid_visibility(show_grid)

    if show_grid:
        display_story_points_grid()
    else:
        st.warning("You don't have access to see the grid until the Scrum Master gives it!")

def plot_story_points_chart():
    grid_visibility = load_grid_visibility()
    show_grid = grid_visibility["show_grid"]

    if show_grid:
        story_points = load_story_points()
        data = pd.DataFrame({'User': list(story_points.keys()), 'Story Points': list(story_points.values())})

        selection = alt.selection_single(fields=['User'], bind='legend', name="user_selection", empty="all")
        chart = alt.Chart(data).mark_arc().encode(
            theta='Story Points:Q', color='User:N', tooltip=['User:N', 'Story Points:Q']
        ).add_selection(selection).properties(title="Story Points Submitted by Users")

        st.altair_chart(chart, use_container_width=True)
        return data
    else:
        st.warning("You don't have access to see the chart until the Scrum Master gives it!")
        return None

def view_charts_page():
    st.title("Story Points Charts")
    data = plot_story_points_chart()

    if data is not None:
        show_info_button = st.button("Show Chart Information")

        if show_info_button:
            story_point_counts = data['Story Points'].value_counts()

            st.markdown("""
            <style>
                .streamlit-expanderHeader {
                    background-color: #4CAF50 !important;
                    color: white !important;
                    font-size: 18px !important;
                    font-weight: bold !important;
                }
                .streamlit-expanderContent {
                    background-color: #f0f8f0 !important;
                    padding: 15px !important;
                    border-radius: 10px !important;
                }
            </style>
            """, unsafe_allow_html=True)

            with st.expander("Story Point Counts"):
                for story_point, count in story_point_counts.items():
                    users = data[data['Story Points'] == story_point]['User'].tolist()
                    st.write(f"Story Point {story_point} with users - {', '.join(users)}")
    else:
        st.warning("No data available to show information.")

def main():
    guest_mode()

if __name__ == "__main__":
    main()
