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
        url = 'https://storage.googleapis.com/kaggle-data-sets/1993933/3294812/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20250803%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250803T100603Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=3d34988e5b9c630972d2f01e3d630dda56d592e37b4eed2a0f410fca400389f04f68441a9b1d6dbca8ddbad63f0e34ad58f2563b5652cd1521ef6132d23dac304682c022789ecf73bac022c9b02b3c9cb489044d17128ffe54db7cbbee4620fb12e138db6ad21912abb554fa4d97efd067c9154ac19f4a3a000915018aee79058f302c5e0319dd2f221c97825ddbe704052bdead48048a54db9bda39932dd63f9f578c3a693f8f1c52ac41194696d3a8d5a7e407f6f80ce1ec474799261e82e41dddf1fb5ded1cdcd326a87f037f221937fa202ec60a1b42c8eb471e39a8b423d78b9fd055dd2ceb40f51954a42844523f0e95ac087734d92e76c9cdddf443e0'

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

    top_k_songs = [i[0] for i in sim_scores_list[1:500]]

    top_k_df = df_final_backup.iloc[top_k_songs]

    top_n = top_k_df.sort_values(by='popularity', ascending=False)

    # songs_list = (sim_scores_list[1:(1001)])
    # sim_scores_list = sim_scores_list.sort_values(by='popularity', ascending=False)
    return top_n.head(num_recommendation)[['id','name', 'artists', 'popularity']]


st.title("VibeSync🎵")
st.write("click and type your song to get recommendations based on the vibe of the song")
with st.spinner("Loading Dataset, please wait a min"):
    df_final, df_final_backup, song_indices = load_data()
    song_names_to_id = pd.Series(df_final_backup.id.values, index=df_final_backup.name +" - " + df_final_backup.artists.str.replace("[\[\]']", "", regex=True)).to_dict()
    song_names = song_names_to_id.keys()

st.success("The recommendations are currently optimized only for english songs.")

song_name_selected =  st.selectbox(label="type your song here to search (Case Sensitive)", options= song_names)

num_of_songs = st.slider("Number of Recommendations", 5,50,15)

if st.button("Recommend"):
    if song_name_selected:
        with st.spinner(f"Analysing Simmilar Songs to '{song_name_selected}' ..."):
            ans = recommend_songs(song_names_to_id[song_name_selected], song_indices, df_final, df_final_backup, num_recommendation=num_of_songs)


            st.subheader("Here are your recommendations:")
            # st.dataframe(ans)
            for index, row in ans.iterrows():
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"**{row['name']}** by {row['artists'].strip('[]')}")
                with col2:
                    spotify_url = f"https://open.spotify.com/track/{row['id']}"
                    st.link_button("Play on Spotify", spotify_url)



# st.write(song_name)