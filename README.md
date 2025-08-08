# VibeSync 🎵

VibeSync is an interactive web application that recommends songs based on their musical attributes. Select a song you like, and the app will find other tracks with a similar "vibe" by analyzing their audio features, structure, and popularity.

The Web app is already deployed and available to try at:
[https://vibesyncmysong.streamlit.app/](https://vibesyncmysong.streamlit.app/)

---

##  Features

- **Content-Based Recommendations:** Uses a rich set of audio features from the Spotify dataset to find sonically similar songs. The attributes used include:
    - **Audio Features:** `danceability`, `energy`, `loudness`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`.
    - **Structural Features:** `key`, `mode`, `duration_ms`, `time_signature`.
    - **Metadata:** `popularity`, `explicit`.

- **Popularity Re-ranking:** The model first finds the 200 most similar songs and then re-ranks them by their Spotify popularity score to ensure the recommendations are both relevant and well-known.

- **Interactive UI:** Built with Streamlit for a clean, user-friendly experience.

- **Direct Spotify Integration:** Each recommended song includes a "Play on Spotify" button that opens the track directly in the Spotify web player.

- **Adjustable Recommendations:** A slider allows the user to choose how many recommendations they want to see (from 5 to 25), allowing user to find a better match if required.

---

##  How It Works

The recommendation engine is built on the principle of **content-based filtering**. The "vibe" or "DNA" of each song is represented by a numerical vector.

1.  **Data Preprocessing:** The initial dataset is cleaned by handling missing values and removing duplicate tracks.
2.  **Feature Engineering:**
    - **Numerical Scaling:** Audio features like `popularity`, `tempo`, and `loudness` are scaled using `StandardScaler` to ensure they have an equal impact on the model.
    - **Categorical Encoding:** Features like `key`, `mode`, and `explicit` are converted into a numerical format using one-hot encoding.
3.  **Similarity Calculation:**
    - The processed numerical and categorical features are combined into a single feature vector for each song.
    - When a user selects a song, its vector is compared against all other song vectors in the dataset using **Cosine Similarity**. This metric calculates the "angle" between two vectors to determine how similar they are.
4.  **Re-ranking and Display:**
    - The system identifies the top 200 most similar songs.
    - This list of 200 songs is then sorted by the `popularity` metric.
    - The top required number of songs from this re-ranked list are presented to the user.

---

##  Tech Stack

- **Language:** Python
- **Web Framework:** Streamlit
- **Data Manipulation:** Pandas, NumPy
- **Machine Learning:** Scikit-learn (for `StandardScaler`, `cosine_similarity`)

---

## 🚀 Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/parthsaxena2005/vibesync.git](https://github.com/parthsaxena2005/vibesync.git)
    cd vibesync
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```
    streamlit
    pandas
    scikit-learn
    ```
    Then, run the installation command:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the Dataset:**
    - Create a folder named `datasets` in the root of your project directory.
    - Download the dataset from [Spotify Tracks DB on Kaggle](https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks).
    - Place the `archive.zip` file inside the `datasets` folder. The app will automatically extract it on the first run.

5.  **Run the Streamlit app:**
    ```bash
    streamlit run streamlit.py
    ```

---

## Usage

Once the app is running:
1.  Wait for the dataset to load (this is cached and will be instant on subsequent runs).
2.  Use the dropdown menu to search for and select a song.
3.  Use the slider to choose the number of recommendations you want.
4.  Click the "Recommend" button.
5.  Browse the list of recommended songs and click "Play on Spotify" to listen to them.
