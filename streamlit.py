import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import zipfile
import urllib.request


@st.cache_data
def load_data():
    zipfile_path = Path("datasets/archive.zip")
    csv_name = "tracks.csv"
    csv_path = Path("datasets/tracks.csv")

    if csv_path.is_file():
        df = pd.read_csv(csv_path)
    
    

    if not zipfile_path.is_file():
        Path("datasets").mkdir(parents=True, exist_ok=True)
        url = 'https://storage.googleapis.com/kaggle-data-sets/1993933/3294812/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20250811%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250811T165625Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=6c9cc66f572790e70b6b68dab01dd0c048638bacc8114dbcd08f71d48a9fd4500ab09b3be6791561b6d2a4c1254803eb5414b46cdc327329e2480b3cd89cd6c1199fe316d7e26eef83e02a4663e7fe53d5b03839c2e0a92fa9270c24f7ed8d9183c0696b815ecedb8fce6273473b8097751f47923bb296ff32cef4d773bf8198ffba45d8998590c6594a3d298724f18ac3b44022f2aff0da3b8d9d9c59d2efb416355290cff0c0752ef6c070665b05ac1900759b002ea2756e13689a92faa86310dbd0d6bd2f3eae762ff7da1bf4b0d118d677c4851df16843c1e49ba4aee9b14e10eef9d5320be5f382a2204a2c59fe6e66131626789b01e3ede6fa8fbd0047'

        urllib.request.urlretrieve(url,zipfile_path)

    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall("datasets")

    df =  pd.read_csv(csv_path)
    df_backup = df.copy()
    df_c = df.dropna()
    df_c = df_c.drop(["release_date"], axis=1)  
    scaler = StandardScaler()
    normalize_list = ["popularity", "duration_ms", "danceability", "energy",  "loudness", "speechiness",  "acousticness", 
                  "instrumentalness", "liveness",  "valence","tempo",     ]

    onehot_list = [
        "explicit",
        "key",
        "mode",
        "time_signature"
    ]
    id_cols = ['id', 'name', 'artists', 'id_artists']

    df_c[onehot_list] = df_c[onehot_list].astype('category')
    df_c_norm = scaler.fit_transform(df_c[normalize_list])
    df_c_norm_df = pd.DataFrame(df_c_norm, columns=normalize_list)
    df_c_hot = pd.get_dummies(df_c[onehot_list])
    df_c_id = df_c[id_cols]
    df_final = pd.concat([df_c_id, df_c_norm_df, df_c_hot], axis = 1)
    df_final.dropna(inplace=True)

    df_final_backup = df_final.copy()
    df_final_cols = df_final[['id', 'name', 'artists', 'id_artists']]
    df_final.drop(columns=['id', 'name', 'artists', 'id_artists'], axis=1, inplace=True)
    song_indices = pd.Series(df_final_backup.index, index= df_final_backup['id'])

    return df_final, df_final_backup, song_indices

def recommend_songs(song_id, song_indices, df_final, df_final_backup, num_recommendation = 10):

    if(song_id not in song_indices):
        return f"songid not found"
    
    idx = song_indices[song_id]
    song_vec = df_final.iloc[idx].values.reshape(1,-1)

    sim_scores = cosine_similarity(song_vec, df_final.values)

    sim_scores_list = list(enumerate(sim_scores[0]))


    sim_scores_list = sorted(sim_scores_list ,key=lambda x:x[1] ,reverse=True)

    top_k_songs = [i[0] for i in sim_scores_list[1:201]]

    top_k_df = df_final_backup.iloc[top_k_songs]

    top_n = top_k_df.sort_values(by='popularity', ascending=False)

    # songs_list = (sim_scores_list[1:(1001)])
    # sim_scores_list = sim_scores_list.sort_values(by='popularity', ascending=False)
    return top_n.head(num_recommendation)[['id','name', 'artists', 'popularity']]


st.title("VibeSync🎵")
st.write("click and type your song to get recommendations based on the vibe of the song")
# with st.spinner("Loading Dataset, please wait a min"):
#     df_final, df_final_backup, song_indices = load_data()
#     song_names_to_id = pd.Series(df_final_backup.id.values, index=df_final_backup.name +" - " + df_final_backup.artists.str.replace("[\[\]']", "", regex=True)).to_dict()
#     song_names = song_names_to_id.keys()

st.success("The recommendations are currently optimized only for english songs and support songs released till 2020.")

# song_name_selected =  st.selectbox(label="type your song here to search (Case Sensitive)", options= song_names)

if 'search_results' not in st.session_state:
    st.session_state['search_results']=None

with st.spinner("Loading Dataset, please wait a min"):
    df_final, df_final_backup, song_indices = load_data()
    # song_display_list = pd.Series(df_final_backup.id.values, index=df_final_backup.name +" - " + df_final_backup.artists.str.replace("[\[\]']", "", regex=True)).to_dict()
    # song_names = song_names_to_id.keys()



st.subheader("Search for a song")
search_query = st.text_input("Enter a song title:", key="search_input")

if st.button("Search"):
    if search_query:

        results = df_final_backup[df_final_backup['name'].str.contains(search_query, case=False, na=False)]
        st.session_state['search_results']  = results
    else:
        st.session_state['search_results'] = None


if st.session_state['search_results'] is not None and not st.session_state['search_results'].empty:
    st.subheader("Select the exact match")
    search_results_df = st.session_state['search_results']
    song_names_to_display = search_results_df['name'] + ' - ' + search_results_df['artists'].str.replace(r"[\[\]']", "",regex = True).tolist()

    song_name_selected = st.selectbox("Choose a song from the results", options = song_names_to_display)

    num_of_songs = st.slider("Number of Recommendations", 5,50,15)

    if st.button("Recommend"):
        if song_name_selected:
            with st.spinner(f"Analysing Simmilar Songs to '{song_name_selected}' ..."):
                song_to_recommend  = df_final_backup[
                    (df_final_backup['name'] + ' - ' +df_final_backup['artists'].str.replace(r"[\[\]']", "", regex=True)) == song_name_selected
                                                     ]
                
                song_id = song_to_recommend['id'].iloc[0]

                ans = recommend_songs(song_id, song_indices, df_final, df_final_backup, num_recommendation=num_of_songs)


                st.subheader("Here are your recommendations:")
                # st.dataframe(ans)
                for index, row in ans.iterrows():
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.write(f"**{row['name']}** by {row['artists'].strip('[]')}")
                    with col2:
                        spotify_url = f"https://open.spotify.com/track/{row['id']}"
                        st.link_button("Play on Spotify", spotify_url)


elif st.session_state['search_results'] is not None:
    st.warning("No song matches your query, please try again.")
# st.write(song_name)