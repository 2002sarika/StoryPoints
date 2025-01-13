import math
import time
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
        guest_mode_button = st.button("Submit as Guest 👤")
        
        if guest_mode_button:
            if guest_name.strip():
                st.session_state.username = guest_name.strip()  # Store the guest name in session state
                st.session_state.logged_in = True  # Mark user as logged in
                st.success(f"Welcome, {guest_name.strip()}! 🎉")
                show_sidebar()  # Proceed to show the sidebar
            else:
                st.warning("Please enter a valid name !")
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
        st.warning("Please enter your name before submitting story points. ❌")
        return

    st.title(f"Submit Story Points for {st.session_state.username}")
    fibonacci_numbers = [1, 2, 3, 5, 8, 13, 21, 34]
    story_point = st.selectbox("Choose Fibonacci Story Points 🔢", fibonacci_numbers)
    submit_button = st.button("Submit Story Points 📥")

    emoji_feedback = ""  # Initialize emoji feedback

    if submit_button:
        with st.spinner("Saving... ⏳"):
            # Simulate grid transition with a progress bar
            progress = st.progress(0)
            for i in range(100):
                progress.progress(i + 1)
                time.sleep(0.02)  # Delay to simulate loading

            if submit_story_points(st.session_state.username, story_point):
                emoji_feedback = "✅"  # Success emoji
                st.success(f"Story points submitted successfully! {emoji_feedback}")
            else:
                emoji_feedback = "❌"  # Error emoji
                st.error(f"You've already submitted your story points or didn't maintain a Fibonacci series. {emoji_feedback}")

def submit_story_points(username, points):
    story_points = load_story_points()
    if username in story_points:
        return False  # Already submitted
    story_points[username] = points
    save_story_points(story_points)
    return True

def delete_story_point(username):
    story_points = load_story_points()
    if username in story_points:
        del story_points[username]
        save_story_points(story_points)

def delete_all_story_points():
    save_story_points({})  # Save an empty dictionary to clear all records

def display_story_points_grid():
    st.title("View and Manage Story Points Grid 🔢")

    # Load the story points
    story_points = load_story_points()

    if not story_points:
        st.write("No story points have been submitted yet. 🕒")
        return

    # Prepare DataFrame for displaying the grid
    data = pd.DataFrame({
        'User': list(story_points.keys()),
        'Story Points': list(story_points.values())
    })

    # Add CSS for animated transitions and color
    st.markdown("""
        <style>
            /* Color based on Story Points */
            .high { background-color: #ffcccb; } /* Red for high values */
            .medium { background-color: #fff799; } /* Yellow for medium values */
            .low { background-color: #c8e6c9; } /* Green for low values */
            .row-selected { background-color: #d1f7d1; } /* Light green for selected rows */
        </style>
    """, unsafe_allow_html=True)

    # Display checkboxes for selecting rows
    selected_rows = []
    for index, row in data.iterrows():
        selected = st.checkbox(f"Select {row['User']} ({row['Story Points']} points)", key=row['User'])
        if selected:
            selected_rows.append(row['User'])

    # Display the styled dataframe with rows colored
    st.dataframe(data)

    # Add the delete functionality
    delete_button = st.button("Delete Selected Story Points 🗑️")
    if delete_button:
        if selected_rows:
            for user in selected_rows:
                delete_story_point(user)
            st.success(f"Deleted selected users: {', '.join(selected_rows)}")
        else:
            st.warning("No users selected for deletion.")

# Function to delete a user's story points
def delete_story_point(username):
    story_points = load_story_points()
    if username in story_points:
        del story_points[username]
        save_story_points(story_points)
        
def toggle_grid_visibility():
    grid_visibility = load_grid_visibility()
    show_grid = grid_visibility["show_grid"]

    if st.session_state.username in SCRUM_MASTER:
        if st.button("Show/Hide Story Points Grid 👀"):
            show_grid = not show_grid
            save_grid_visibility(show_grid)

    if show_grid:
        st.success("Grid is now visible! 🎉")
        display_story_points_grid()
    else:
        st.warning("Grid is hidden! 🚫")

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
    st.title("Story Points Charts 📊")
    data = plot_story_points_chart()

    if data is not None:
        show_info_button = st.button("Show Chart Information ℹ️")

        if show_info_button:
            story_point_counts = data['Story Points'].value_counts()

            # Dynamically update emoji based on most frequent story point
            most_common = story_point_counts.idxmax()
            emoji = "🔥" if most_common >= 13 else "🌱"

            st.markdown(f"Most common story point: {most_common} {emoji}")
            
            st.markdown("""<style> .streamlit-expanderHeader { background-color: #4CAF50 !important; color: white !important; font-size: 18px !important; font-weight: bold !important; } .streamlit-expanderContent { background-color: #f0f8f0 !important; padding: 15px !important; border-radius: 10px !important; } </style>""", unsafe_allow_html=True)

            with st.expander("Story Point Counts 📈"):
                for story_point, count in story_point_counts.items():
                    users = data[data['Story Points'] == story_point]['User'].tolist()
                    st.write(f"Story Point {story_point} with users - {', '.join(users)}")
    else:
        st.warning("No data available to show information. ❌")


def main():
    guest_mode()

if __name__ == "__main__":
    main()
