import streamlit as st
import pandas as pd

TRENDING_CSV_PATH = "df_BB_to_app.csv"

csv_mapping = {
    "6 Clusters, 9 Columns": "dataset_with_categories_k6_9cols.csv",
    "10 Clusters, 12 Columns": "dataset_with_categories_k10_12cols.csv",
    "12 Clusters, 10 Columns": "dataset_with_categories_k12_10cols.csv",
    "12 Clusters, 12 Columns": "dataset_with_categories_k12_12cols.csv",
    "Curated: 10 Clusters, 12 Columns": "curated_dataset_with_categories_k10_12cols.csv"
}

def play_song(track_id):
    html_code = f"""
    <iframe src="https://open.spotify.com/embed/track/{track_id}" 
            width="320" 
            height="80" 
            frameborder="0" 
            allowtransparency="true" 
            allow="encrypted-media"></iframe>
    """
    return html_code

# Load the datasets
@st.cache_data
def load_main_data(csv_path):
    df_main = pd.read_csv(csv_path)
    return df_main

@st.cache_data
def load_trending_data():
    df_trending = pd.read_csv(TRENDING_CSV_PATH)
    return df_trending

# Streamlit app
st.title("Music Recommendation App")

# Sidebar for dataset and category selection
st.sidebar.header("Select Dataset and Category")

# First dropdown: Curated or No Curated
curated_option = st.sidebar.selectbox("Choose Dataset Type", ["No Curated", "Curated"])

# Second dropdown: Select specific CSV based on curated option
if curated_option == "No Curated":
    main_csv_descriptions = [
        "6 Clusters, 9 Columns",
        "10 Clusters, 12 Columns",
        "12 Clusters, 10 Columns",
        "12 Clusters, 12 Columns"
    ]
else:  # Curated
    main_csv_descriptions = ["Curated: 10 Clusters, 12 Columns"]

selected_description = st.sidebar.selectbox("Choose Dataset Configuration", main_csv_descriptions)

# Map the selected description to the actual CSV file name
selected_csv = csv_mapping[selected_description]

# Load data based on selected CSV
df_main = load_main_data(selected_csv)
df_trending = load_trending_data()

# Third dropdown: Category selection
categories = list(df_main['category'].unique()) + ["Trending Now"]
selected_category = st.sidebar.selectbox("Choose a Category", categories)

# Filter songs by the selected category
if selected_category != "Trending Now":
    filtered_df = df_main[df_main['category'] == selected_category]
else:
    filtered_df = df_trending

# Display category information
st.header(f"Category: {selected_category}")
st.write(f"Total songs in this category: {len(filtered_df)}")

# Recommend the most popular song (stored in session state)
st.header("Most Popular Song")
if not filtered_df.empty:
    if 'initial_recommendation' not in st.session_state or st.session_state.get('last_category') != selected_category:
        if selected_category != "Trending Now":
            # Select the song with the highest popularity
            initial_recommendation = filtered_df.nlargest(1, 'popularity').iloc[0]
            st.session_state.initial_recommendation = {
                'track_id': initial_recommendation['track_id'],
                'track_name': initial_recommendation['track_name'],
                'artist': initial_recommendation['artists'],
                'popularity': initial_recommendation['popularity']
            }
        else:
            # Select the song with the lowest ranking (most popular in Trending Now)
            initial_recommendation = filtered_df.nsmallest(1, 'Ranking').iloc[0]
            st.session_state.initial_recommendation = {
                'track_id': initial_recommendation['spotify_id'],
                'track_name': initial_recommendation['song'],
                'artist': initial_recommendation['artist'],
                'ranking': initial_recommendation['Ranking']
            }
        st.session_state.last_category = selected_category  # Store the last selected category
        st.session_state.recommended_songs = [st.session_state.initial_recommendation['track_id']]  # Track recommended songs
    
    initial_rec = st.session_state.initial_recommendation
    st.write(f"**Track:** {initial_rec['track_name']}")
    st.write(f"**Artist:** {initial_rec['artist']}")
    if selected_category != "Trending Now":
        st.write(f"**Popularity:** {initial_rec['popularity']}")
    else:
        st.write(f"**Ranking:** {initial_rec['ranking']}")
    st.write("Listen to the song:")
    st.components.v1.html(play_song(initial_rec['track_id']), height=100)
else:
    st.write("No songs available in this category.")

# Button for another random song within the genre
if st.button("Get Another Song"):
    if not filtered_df.empty:
        # Exclude already recommended songs
        if 'recommended_songs' not in st.session_state:
            st.session_state.recommended_songs = []
        
        # Filter out already recommended songs
        initial_track_id = st.session_state.initial_recommendation['track_id'] if selected_category != "Trending Now" else st.session_state.initial_recommendation['track_id']
        remaining_df = filtered_df[filtered_df['track_id'] != initial_track_id] if selected_category != "Trending Now" else filtered_df[filtered_df['spotify_id'] != initial_track_id]
        
        if not remaining_df.empty:
            # Select a random song from the remaining songs
            random_song = remaining_df.sample(1).iloc[0]
            if selected_category != "Trending Now":
                track_id = random_song['track_id']
                track_name = random_song['track_name']
                artist = random_song['artists']
                popularity = random_song['popularity']
            else:
                track_id = random_song['spotify_id']
                track_name = random_song['song']
                artist = random_song['artist']
                ranking = random_song['Ranking']

            # Add the new song to the list of recommended songs
            st.session_state.recommended_songs.append(track_id)

            st.write(f"**Next Song:** {track_name}")
            st.write(f"**Artist:** {artist}")
            if selected_category != "Trending Now":
                st.write(f"**Popularity:** {popularity}")
            else:
                st.write(f"**Ranking:** {ranking}")
            st.write("Listen to the song:")
            st.components.v1.html(play_song(track_id), height=100)
        else:
            st.write("No more songs available in this category to recommend.")