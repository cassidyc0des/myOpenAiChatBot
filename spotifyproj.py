import openai as OpenAI
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from scipy.spatial.distance import euclidean
import os

# Spotify keys
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
audio_decription_promp = ""

def get_top_tracks(sp, limit=50):
    playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Spotify's Global Top 50 Playlist ID
    results = sp.playlist_tracks(playlist_id, limit=limit)
    top_tracks = []
    for item in results['items']:
        track = item['track']
        top_tracks.append({
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name']
        })
    return top_tracks


def get_audio_features(sp, track_ids):
    features = sp.audio_features(track_ids)
    return {feat['id']: feat for feat in features if feat}


def calculate_weighted_distance(input_features, features, weights):
    weighted_distance = 0
    keys = ['danceability', 'energy', 'loudness', 'instrumentalness', 'tempo', 'key']

    if len(weights) > len(keys):
        weights = weights[:len(keys)]

    for i, key in enumerate(keys):
        input_value = input_features.get(key, 0)
        track_value = features.get(key, 0)
        weight = weights[i] if i < len(weights) else 1

        if isinstance(input_value, str) and isinstance(track_value, str):
            if input_value != track_value:
                weighted_distance += weight * 1
        else:
            try:
                input_value = float(input_value)
                track_value = float(track_value)
                weighted_distance += weight * abs(input_value - track_value)
            except ValueError:
                pass

    return weighted_distance


def weighted_find_closest_match(input_features, top_tracks_features, weights):
    min_distance = float('inf')
    closest_track = None
    second_closest_track = None
    second_min_distance = float('inf')

    for track_id, features in top_tracks_features.items():
        distance = calculate_weighted_distance(input_features, features, weights)

        if distance < min_distance:
            second_min_distance = min_distance
            second_closest_track = closest_track
            min_distance = distance
            closest_track = track_id
        elif distance < second_min_distance and track_id != closest_track:
            second_min_distance = distance
            second_closest_track = track_id

    return closest_track, second_closest_track


def interpreter():
    api_key = os.getenv("OPENAI_API_KEY")
    print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
    if api_key is None:
        raise ValueError("API key not found in environment variables")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")

    OpenAI.api_key = api_key
    client = OpenAI

    conversation_history = [
        {"role": "system", "content": "You are an assistant who helps with music recommendations with the Spotify API."}
    ]

    while True:
        query = input("Enter the song name and artist: ")
        if query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        results = sp.search(q=query, type='track', limit=1)
        track_id = ""

        if results['tracks']['items']:
            track_id = results['tracks']['items'][0]['id']
            print(f"Track ID: {track_id}")
        else:
            print("Track not found.")
            continue

        audio_analysis = sp.audio_analysis(track_id)
        audio_features = sp.audio_features(track_id)

        if audio_analysis and audio_features:
            tempo = audio_analysis['track']['tempo']
            key = audio_analysis['track']['key']
            dance = audio_features[0]['danceability']
            energy = audio_features[0]['energy']
            loud = audio_features[0]['loudness']
            instrumentalness = audio_features[0]['instrumentalness']
            print(f"Tempo: {tempo} BPM")
            print(f"Key: {key}")
            print(f"Danceability: {dance}")
            print(f"Energy: {energy}")
            print(f"Loudness: {loud}")
            print(f"Instrumentalness: {instrumentalness}")
        else:
            print("Audio features not found.")
            continue

        print("Please input the weight for each feature (1-10):")
        genre_weight = float(input("1. Genre: "))
        danceability_weight = float(input("2. Danceability: "))
        tempo_weight = float(input("3. Tempo: "))
        key_weight = float(input("4. Key: "))
        energy_weight = float(input("5. Energy: "))

        weights = [genre_weight, danceability_weight, tempo_weight, key_weight, energy_weight]
        feature_keys = ['genre', 'danceability', 'tempo', 'key', 'energy']

        if audio_features:
            input_features = audio_features[0]
            top_tracks = get_top_tracks(sp)
            top_track_ids = [track['id'] for track in top_tracks]
            top_tracks_features = get_audio_features(sp, top_track_ids)

            closest_track_id, second_closest_track_id = weighted_find_closest_match(input_features, top_tracks_features,
                                                                                    weights)

            if closest_track_id:
                closest_track = next(track for track in top_tracks if track['id'] == closest_track_id)
                closest_features = top_tracks_features[closest_track_id]
                similar_track_info = {
                    "name": closest_track['name'],
                    "artist": closest_track['artist'],
                    "album": closest_track['album'],
                    "tempo": closest_features['tempo'],
                    "key": closest_features['key'],
                    "danceability": closest_features['danceability'],
                    "energy": closest_features['energy']
                }

                # Determine the highest weight
                max_weight = max(weights)
                max_weight_index = weights.index(max_weight)
                max_weight_feature = feature_keys[max_weight_index]

                # Print comparison based on the highest weight feature
                input_feature_value = input_features.get(max_weight_feature, 'N/A')
                closest_feature_value = closest_features.get(max_weight_feature, 'N/A')

                print(
                    f"Found a similar track: {similar_track_info['name']} by {similar_track_info['artist']} from the album {similar_track_info['album']}")
                print(
                    f"{similar_track_info['name']} has a {max_weight_feature} of {closest_feature_value} which is close to {query} with a {max_weight_feature} of {input_feature_value}")

                if second_closest_track_id:
                    second_closest_track = next(track for track in top_tracks if track['id'] == second_closest_track_id)
                    second_closest_features = top_tracks_features[second_closest_track_id]
                    second_similar_track_info = {
                        "name": second_closest_track['name'],
                        "artist": second_closest_track['artist'],
                        "album": second_closest_track['album'],
                        "tempo": second_closest_features['tempo'],
                        "key": second_closest_features['key'],
                        "danceability": second_closest_features['danceability'],
                        "energy": second_closest_features['energy']
                    }
                    second_input_feature_value = second_closest_features.get(max_weight_feature, 'N/A')
                    print(
                        f"Second closest track: {second_similar_track_info['name']} by {second_similar_track_info['artist']} from the album {second_similar_track_info['album']}")
                    print(
                        f"{second_similar_track_info['name']} has a {max_weight_feature} of {second_input_feature_value} which is close to {query} with a {max_weight_feature} of {input_feature_value}")
                    audio_description_prompt = (
                        f"Describe how we found a similar track: {similar_track_info['name']} by {similar_track_info['artist']} from the album {similar_track_info['album']} {similar_track_info['name']} has a {max_weight_feature} of {closest_feature_value} which is close to {query} with a {max_weight_feature} of {input_feature_value}")

            else:
                print("No similar track found in the top 50.")

        conversation_history.append({"role": "user", "content": query})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a music expert who describes audio features and analysis."},
                {"role": "user", "content": audio_description_prompt}
            ]
        )

        if response.choices:
            message_content = response.choices[0].message.content
            print(message_content.strip())
            conversation_history.append({"role": "assistant", "content": message_content.strip()})
        else:
            print("No completion response received.")


if __name__ == "__main__":
    print("Welcome to the Spotify Assistant! Type 'exit' or 'quit' to end the conversation.")
    interpreter()
