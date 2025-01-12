import math
import streamlit as st
import json
import os
import pandas as pd
import altair as alt

STORY_POINTS_FILE = 'story_points.json'
GRID_VISIBILITY_FILE = 'grid_visibility.json'

#fibonacii check 
def isFibonacii(num):
    def is_perfect_square(x):
        s = int(math.sqrt(x))
        return s * s == x

    # A number is a Fibonacci number if and only if one of these is a perfect square
    return is_perfect_square(5 * num * num + 4) or is_perfect_square(5 * num * num - 4)

    
# Function to create files if they do not exist
def createfileifnotexists(filename, default_value=None):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(default_value, f)  # Create file with default value
    else:
        # Ensure the file is not empty or invalid
        try:
            with open(filename, 'r') as f:
                json.load(f)
        except (json.JSONDecodeError, ValueError):
            with open(filename, 'w') as f:
                json.dump(default_value, f)  # Write default value if corrupted

# Load story points
def load_story_points():
    createfileifnotexists(STORY_POINTS_FILE, {})
    with open(STORY_POINTS_FILE, 'r') as f:
        return json.load(f)

# Save story points
def save_story_points(story_points):
    with open(STORY_POINTS_FILE, 'w') as f:
        json.dump(story_points, f)

# Load grid visibility from the file
def load_grid_visibility():
    createfileifnotexists(GRID_VISIBILITY_FILE, {"show_grid": False})
    with open(GRID_VISIBILITY_FILE, "r") as f:
        return json.load(f)

# Save grid visibility to the file
def save_grid_visibility(show_grid):
    with open(GRID_VISIBILITY_FILE, "w") as f:
        json.dump({"show_grid": show_grid}, f)

# Guest mode: Ask for guest name if not already set
def guest_mode():
    if "username" not in st.session_state:
        # Ask the user for their name
        st.title("Welcome to Story Points Board!!!")
        guest_name = st.text_input("Enter your name", "", placeholder="Type your name here...", max_chars=20)

        guest_mode_button = st.button("Submit as Guest")
        
        if guest_mode_button:
            if guest_name.strip():
                st.session_state.username = guest_name.strip()  # Store the guest name in session state
                st.session_state.logged_in = True  # Mark user as logged in
                st.success(f"Welcome, {guest_name.strip()}!")
                # Proceed to show the sidebar
                show_sidebar()
            else:
                st.warning("Please enter a valid name!")
    else:
        # If the username is already set, show the sidebar
        show_sidebar()

# Sidebar navigation after login
def show_sidebar():
    st.sidebar.title("Navigation")
    page_option = st.sidebar.selectbox("Select Action", ["Add Story Points", "Toggle Grid Visibility", "View Charts"])

    if page_option == "Add Story Points":
        add_story_points_page()
    elif page_option == "Toggle Grid Visibility":
        toggle_grid_visibility()  # Scrum Master can toggle visibility
    elif page_option == "View Charts":
        view_charts_page()  # All users can view the charts if the grid is visible

def add_story_points_page():
    # Ensure user is logged in and has a username
    if "username" not in st.session_state or not st.session_state.username:
        st.warning("Please enter your name before submitting story points.")
        return

    st.title(f"Submit Story Points for {st.session_state.username}")
    story_point = st.number_input("Enter your story points", min_value=1, step=1)
    submit_button = st.button("Submit Story Points")

    if submit_button:
        if submit_story_points(st.session_state.username, story_point):
            st.success("Story points submitted successfully!")
        else:
            st.error("You've already submitted your story points or didnt maintain a fibonacii series.")

def submit_story_points(username, points):
    story_points = load_story_points()
    
    if isFibonacii(points):
        if username in story_points:
            return False  # Already submitted
    
        story_points[username] = points
        save_story_points(story_points)
        return True
    else:
        st.warning("Please enter fibonacii numbers")
        
def view_story_points_grid():
    st.title("View Submitted Story Points")
    
    story_points = load_story_points()
    
    if not story_points:
        st.write("No story points have been submitted yet.")
        return
    
    checkboxes = [st.checkbox(user, key=user) for user in story_points.keys()]
    data = {"Select" : checkboxes, "User": list(story_points.keys()), "Story Points": list(story_points.values())}
    df = pd.DataFrame(data)

    # Display the grid in a single table with the checkboxes
    st.write("**Story Points Grid**")
    st.write(df)

    delete_selected_button = st.button("Delete Selected", key="delete_selected", help="Delete selected story points")
    
    delete_all_button = st.button("Delete All", key="delete_all", help="Delete all story points")
    
    # Handle "Delete Selected" button action
    if delete_selected_button:
        selected_users = [df['User'][i] for i in range(len(checkboxes)) if checkboxes[i]]
        if selected_users:
            for user in selected_users:
                delete_story_point(user)
            st.success(f"Deleted selected users: {', '.join(selected_users)}")
        else:
            st.warning("No users selected for deletion.")

    # Handle "Delete All" button action
    if delete_all_button:
        delete_all_story_points()
        st.success("All story points have been deleted.")

def delete_story_point(username):
    story_points = load_story_points()
    if username in story_points:
        del story_points[username]
        save_story_points(story_points)
    

def delete_all_story_points():
    # Clears all story points data
    save_story_points({})  # Save an empty dictionary, effectively deleting all records

def toggle_grid_visibility():
     # Load grid visibility state
    grid_visibility = load_grid_visibility()
    show_grid = grid_visibility["show_grid"]

    if st.session_state.username == "scrum.master":
        # Button to toggle visibility
        if st.button("Show/Hide Story Points Grid"):
            show_grid = not show_grid  # Toggle visibility
            save_grid_visibility(show_grid)  # Save the updated state

    # Update visibility based on the state
    if show_grid:
        view_story_points_grid()
    else:
        st.warning("You dont have access to see the grid until scrum master gives it!!!")

def plot_story_points_chart():
    grid_visibility = load_grid_visibility()
    show_grid = grid_visibility["show_grid"]

    if show_grid:
        # Load the story points data
        story_points = load_story_points()

        # Convert story points to a DataFrame
        data = pd.DataFrame({
            'User': list(story_points.keys()),
            'Story Points': list(story_points.values())
        })

        # Create the Altair chart with a selection
        selection = alt.selection_single(fields=['User'], bind='legend', name="user_selection", empty="all")

        chart = alt.Chart(data).mark_arc().encode(
            theta='Story Points:Q',
            color='User:N',
            tooltip=['User:N', 'Story Points:Q']
        ).add_selection(
            selection
        ).properties(
            title="Story Points Submitted by Users"
        )

        # Display the chart
        st.altair_chart(chart, use_container_width=True)

        return data  # Return data to be used for chart information

    else:
        st.warning("You don't have access to see the chart until the scrum master gives it!!!")
        return None

# Streamlit page to view the chart and toggle chart information
def view_charts_page():
    st.title("Story Points Charts")

    # Load the chart data
    data = plot_story_points_chart()

    # If data is loaded and displayed, show the "Show Chart Information" button
    if data is not None:
        # Button to reveal chart information
        show_info_button = st.button("Show Chart Information")

        if show_info_button:
            # Calculate min/max story points and corresponding users
            min_points = data['Story Points'].min()
            max_points = data['Story Points'].max()

            min_user = data[data['Story Points'] == min_points]['User'].values[0]
            max_user = data[data['Story Points'] == max_points]['User'].values[0]

            st.markdown(f"""
             <div style="background-color:red; padding:20px; color:white; border-radius:10px;">
    <h3>Story Points Information</h3>
    <p>Min Story Points: 
        <span style="background-color:white; color:black; padding:3px 6px;">{min_points}</span> 
        by <span style="background-color:white; color:black; padding:3px 6px;">{min_user}</span>
    </p>
    <p>Max Story Points: 
        <span style="background-color:white; color:black; padding:3px 6px;">{max_points}</span> 
        by <span style="background-color:white; color:black; padding:3px 6px;">{max_user}</span>
    </p>
</div>

            """, unsafe_allow_html=True)
    else:
        st.warning("No data available to show information.")


# Main entry point
def main():
    guest_mode()  # Set up the guest mode

if __name__ == "__main__":
    main()
