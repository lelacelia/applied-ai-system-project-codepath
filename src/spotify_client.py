"""
Music Retrieval - Get songs from either local dataset or Spotify API.

Two modes available:

1. DATASET MODE (DEFAULT, RECOMMENDED):
   - 603 songs with REAL Spotify audio features
   - Data source: Billboard top songs 2010-2019
   - Audio features: valence, energy, danceability, acousticness (actual Spotify data)
   - Cost: FREE (no API calls needed)
   - Scores: Honest (based on real data)

2. SPOTIFY API MODE (OPTIONAL):
   - Access to millions of Spotify songs
   - Audio features: SIMULATED (free tier blocks real endpoint)
   - Cost: Requires paid Spotify API credentials
   - Scores: Estimates (based on genre/mood ranges)

Usage:
  spotify = SpotifyRetriever(use_dataset=True)   # Dataset mode (default)
  spotify = SpotifyRetriever(use_dataset=False)  # Spotify API mode
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from song_database import SongDatabase

# Load environment variables (.env file)
# This loads SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
load_dotenv(verbose=False)


class SpotifyRetriever:
    """
    Spotify API client for music search and feature extraction.

    This class wraps the Spotify Web API to:
    - Search for songs by query (mood, genre, keywords)
    - Get audio features for songs (energy, valence, danceability, acousticness)
    - Format results for compatibility with the recommender

    Attributes:
        sp: Spotipy client instance (authenticated with credentials)
    """

    # Realistic audio feature ranges by genre and mood
    GENRE_MOOD_FEATURES = {
        'pop': {
            'romantic': {'energy': (0.5, 0.7), 'valence': (0.6, 0.8), 'danceability': (0.5, 0.7), 'acousticness': (0.2, 0.5)},
            'happy': {'energy': (0.7, 0.9), 'valence': (0.7, 0.95), 'danceability': (0.6, 0.8), 'acousticness': (0.1, 0.3)},
            'sad': {'energy': (0.3, 0.5), 'valence': (0.2, 0.4), 'danceability': (0.3, 0.5), 'acousticness': (0.4, 0.7)},
            'chill': {'energy': (0.3, 0.5), 'valence': (0.4, 0.6), 'danceability': (0.4, 0.6), 'acousticness': (0.3, 0.6)},
            'upbeat': {'energy': (0.75, 0.95), 'valence': (0.7, 0.9), 'danceability': (0.7, 0.85), 'acousticness': (0.1, 0.4)},
        },
        'indie': {
            'chill': {'energy': (0.2, 0.4), 'valence': (0.4, 0.6), 'danceability': (0.3, 0.5), 'acousticness': (0.5, 0.8)},
            'upbeat': {'energy': (0.6, 0.8), 'valence': (0.6, 0.8), 'danceability': (0.5, 0.7), 'acousticness': (0.3, 0.6)},
            'sad': {'energy': (0.2, 0.4), 'valence': (0.2, 0.4), 'danceability': (0.2, 0.4), 'acousticness': (0.6, 0.9)},
        },
        'hip-hop': {
            'upbeat': {'energy': (0.7, 0.9), 'valence': (0.5, 0.7), 'danceability': (0.7, 0.9), 'acousticness': (0.0, 0.2)},
            'moody': {'energy': (0.5, 0.7), 'valence': (0.3, 0.5), 'danceability': (0.6, 0.8), 'acousticness': (0.0, 0.1)},
            'sad': {'energy': (0.4, 0.6), 'valence': (0.2, 0.4), 'danceability': (0.4, 0.6), 'acousticness': (0.0, 0.2)},
            'chill': {'energy': (0.3, 0.5), 'valence': (0.3, 0.5), 'danceability': (0.3, 0.5), 'acousticness': (0.0, 0.1)},
            'romantic': {'energy': (0.5, 0.7), 'valence': (0.5, 0.7), 'danceability': (0.5, 0.7), 'acousticness': (0.0, 0.3)},
        },
        'rock': {
            'energetic': {'energy': (0.8, 0.95), 'valence': (0.5, 0.7), 'danceability': (0.4, 0.6), 'acousticness': (0.0, 0.3)},
            'moody': {'energy': (0.5, 0.7), 'valence': (0.3, 0.5), 'danceability': (0.3, 0.5), 'acousticness': (0.2, 0.5)},
            'sad': {'energy': (0.4, 0.6), 'valence': (0.2, 0.4), 'danceability': (0.3, 0.5), 'acousticness': (0.1, 0.4)},
            'chill': {'energy': (0.3, 0.5), 'valence': (0.4, 0.6), 'danceability': (0.3, 0.5), 'acousticness': (0.3, 0.6)},
            'romantic': {'energy': (0.5, 0.7), 'valence': (0.6, 0.8), 'danceability': (0.4, 0.6), 'acousticness': (0.2, 0.5)},
        },
        'lo-fi': {
            'chill': {'energy': (0.2, 0.35), 'valence': (0.3, 0.5), 'danceability': (0.2, 0.4), 'acousticness': (0.4, 0.7)},
            'sad': {'energy': (0.2, 0.4), 'valence': (0.2, 0.4), 'danceability': (0.2, 0.4), 'acousticness': (0.5, 0.8)},
            'romantic': {'energy': (0.3, 0.5), 'valence': (0.5, 0.7), 'danceability': (0.3, 0.5), 'acousticness': (0.5, 0.8)},
            'happy': {'energy': (0.4, 0.6), 'valence': (0.6, 0.8), 'danceability': (0.3, 0.5), 'acousticness': (0.4, 0.7)},
        },
    }

    def __init__(self, use_dataset: bool = True):
        """
        Initialize music retrieval client (dataset or Spotify API).

        Args:
            use_dataset (bool): If True, use local song database (default, FREE).
                               If False, use Spotify API (requires paid credentials).
        """
        self.use_dataset = use_dataset
        self.db = None
        self.sp = None

        if use_dataset:
            # Load local song database (600 songs with real audio features)
            try:
                self.db = SongDatabase()
                print(f"✅ Local song database initialized ({self.db.stats()['total']} songs)")
            except Exception as e:
                print(f"⚠️  Could not load database: {e}")
                self.use_dataset = False

        if not use_dataset or not self.db:
            # Fall back to Spotify API (only if requested and database unavailable)
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

            # Only raise error if user explicitly requested API mode but credentials missing
            if not use_dataset and (not client_id or not client_secret):
                raise ValueError(
                    "Spotify credentials missing! Check your .env file:\n"
                    "  SPOTIFY_CLIENT_ID=...\n"
                    "  SPOTIFY_CLIENT_SECRET=..."
                )

            # If credentials exist, initialize API client
            if client_id and client_secret:
                auth_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                self.use_dataset = False
                print("✅ Spotify API client initialized successfully")
            else:
                print("⚠️  Spotify API unavailable (credentials missing). Using dataset mode only.")
                self.use_dataset = True

    def search_songs(self, query: str, limit: int = 50, min_popularity: int = 0) -> list:
        """
        Search Spotify for songs matching a query, optionally filtering by popularity.

        Args:
            query (str): Search query (e.g., "lofi chill", "upbeat pop", "acoustic indie")
            limit (int): Max number of results to return (default: 50, max: 50)
            min_popularity (int): Minimum popularity score to include (0-100, default: 0 = no filter)
                                 Try 15-20 to filter out low-quality/spam songs

        Returns:
            list: List of song dictionaries with:
                - id: Spotify track ID
                - title: Song name
                - artist: Artist name
                - album: Album name
                - explicit: Whether song has explicit content
                - popularity: Spotify popularity score (0-100)
                - duration_ms: Song duration in milliseconds
                - uri: Spotify URI for playback
                - artist_id: Spotify artist ID (for genre lookup)

        Example:
            spotify = SpotifyRetriever()
            songs = spotify.search_songs("lofi chill beats", limit=20, min_popularity=25)
            for song in songs:
                print(f"{song['title']} - {song['artist']}")
        """
        try:
            # Call Spotify search API
            # type='track' means we only want songs, not albums/artists/playlists
            results = self.sp.search(q=query, type='track', limit=limit)

            # Extract tracks from results
            tracks = results.get('tracks', {}).get('items', [])

            # Format songs into consistent structure
            songs = []
            filtered_out = 0
            for rank, track in enumerate(tracks):
                popularity = track.get('popularity', 0)

                # Skip low-popularity songs (spam/auto-generated content)
                if min_popularity > 0 and popularity < min_popularity:
                    filtered_out += 1
                    continue

                # Use search rank as a popularity proxy (rank 0 = most relevant = most popular)
                # Convert to 0-100 scale: rank 0 → 100, rank 49 → 2
                search_rank_popularity = max(2, 100 - (rank * 2))

                song = {
                    'id': track['id'],
                    'title': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                    'artist_id': track['artists'][0]['id'] if track['artists'] else None,
                    'album': track['album']['name'] if track['album'] else 'Unknown',
                    'explicit': track.get('explicit', False),
                    'popularity': popularity,
                    'duration_ms': track.get('duration_ms', 0),
                    'uri': track['uri'],
                    'search_rank_popularity': search_rank_popularity,  # Proxy for popularity
                }
                songs.append(song)

            if filtered_out > 0:
                print(f"✅ Found {len(songs)} songs for query: '{query}' (filtered out {filtered_out} low-popularity)")
            else:
                print(f"✅ Found {len(songs)} songs for query: '{query}'")
            return songs

        except Exception as e:
            print(f"❌ Error searching Spotify: {e}")
            return []

    def get_audio_features(self, songs: list) -> dict:
        """
        Fetch REAL audio features from Spotify API for tracks.

        Attempts to fetch actual audio characteristics from Spotify:
        - energy: intensity/loudness (0-1)
        - valence: musical positivity (0-1, where 1 is happy/upbeat)
        - danceability: how suitable for dancing (0-1)
        - acousticness: acoustic vs electronic (0-1, where 1 is acoustic)
        - tempo: speed in BPM

        NOTE: Spotify's audio features endpoint requires premium/developer access.
        Free tier credentials fall back to simulated features.

        Args:
            songs (list): List of song dicts with 'id' key

        Returns:
            dict: Mapping of track_id -> audio features (real or simulated)
        """
        if not songs:
            return {}

        all_features = {}

        try:
            # Try to fetch real audio features from Spotify API
            track_ids = [song.get('id') for song in songs if song.get('id')]
            if track_ids:
                features_response = self.sp.audio_features(*track_ids)

                # Parse response
                for feature_data in features_response:
                    if feature_data:
                        track_id = feature_data.get('id')
                        all_features[track_id] = {
                            'energy': round(feature_data.get('energy', 0.5), 2),
                            'valence': round(feature_data.get('valence', 0.5), 2),
                            'danceability': round(feature_data.get('danceability', 0.5), 2),
                            'acousticness': round(feature_data.get('acousticness', 0.5), 2),
                            'tempo': feature_data.get('tempo', 100),
                        }

                # If we got real features, use them
                if all_features:
                    return all_features

        except Exception as e:
            # Audio features endpoint blocked (free tier limitation)
            pass

        # Fall back to simulation (free tier uses this)
        return self._simulate_audio_features(songs)

        return all_features

    def _simulate_audio_features(self, songs: list) -> dict:
        """Fallback: simulate features if Spotify API call fails."""
        import random
        all_features = {}

        for song in songs:
            track_id = song.get('id')
            genre = song.get('genre', 'pop').lower()
            mood = song.get('mood', 'upbeat').lower()

            # Get feature ranges for this genre/mood combo
            genre_features = self.GENRE_MOOD_FEATURES.get(genre, self.GENRE_MOOD_FEATURES['pop'])
            ranges = genre_features.get(mood, genre_features.get('upbeat', {
                'energy': (0.5, 0.7), 'valence': (0.5, 0.7), 'danceability': (0.5, 0.7), 'acousticness': (0.3, 0.6)
            }))

            # Generate features within the realistic range for this genre/mood
            all_features[track_id] = {
                'energy': round(random.uniform(*ranges.get('energy', (0.5, 0.7))), 2),
                'valence': round(random.uniform(*ranges.get('valence', (0.5, 0.7))), 2),
                'danceability': round(random.uniform(*ranges.get('danceability', (0.5, 0.7))), 2),
                'acousticness': round(random.uniform(*ranges.get('acousticness', (0.3, 0.6))), 2),
                'tempo': random.randint(80, 130),
            }

        return all_features

    def get_song_genre(self, artist_id: str) -> str:
        """
        Get REAL genre from artist information.

        Spotify doesn't provide genre directly on tracks,
        but we can fetch it from the artist profile.

        Args:
            artist_id (str): Spotify artist ID

        Returns:
            str: Primary genre of the artist
        """
        try:
            artist = self.sp.artist(artist_id)
            genres = artist.get('genres', [])
            return genres[0] if genres else 'unknown'
        except Exception:
            return 'unknown'

    def search_and_enrich(self, query: str, limit: int = 10, context_mood: str = None, min_popularity: int = 0, use_dataset: bool = None) -> list:
        """
        Search for songs AND get their audio features in one call.

        Supports two modes:
        1. Dataset mode (default): ~600 songs with REAL audio features from Spotify
           Uses mood-aware matching with pre-calculated mood scores
        2. Spotify API mode: Millions of songs but audio features blocked on free tier

        MOOD MATCHING: In dataset mode, uses pre-calculated mood scores for fast,
        accurate mood matching. Songs are sorted by how well their audio features
        match the requested mood (sad, energetic, chill).

        Args:
            query (str): Search query (e.g., "sad pop", "chill indie")
            limit (int): Max songs to return (default: 10)
            context_mood (str): Mood from agent (sad, energetic, chill) - used if mood not in query
            min_popularity (int): Minimum popularity (API mode only)
            use_dataset (bool): If None, uses self.use_dataset; if set, overrides

        Returns:
            list: Song dictionaries with REAL audio features, mood-matched (dataset mode)
        """
        # Determine which mode to use
        mode = use_dataset if use_dataset is not None else self.use_dataset

        if mode and self.db:
            # Dataset mode: mood-aware search with pre-calculated scores
            return self._search_dataset(query, limit, context_mood=context_mood)
        else:
            # API mode: mood inference from genre signals
            return self._search_spotify_api(query, limit, context_mood, min_popularity)

    def _search_dataset(self, query: str, limit: int = 10, context_mood: str = None) -> list:
        """
        Search the local song database with MOOD-AWARE matching.

        MOOD MATCHING: Uses pre-calculated mood scores to find songs that
        actually match the requested mood, not just genre keywords.

        Example:
          Query: "sad pop songs"
          → Searches for pop songs
          → Filters by sad_score (pre-calculated at load time)
          → Returns songs with low valence/energy (actually sad)
          → NOT upbeat pop songs like "Legendary Lovers"

        Args:
            query: Search query (e.g., "pop sad", "indie chill")
            limit: Max songs to return
            context_mood: Optional mood from agent (sad, energetic, chill)

        Returns:
            Songs with REAL audio features, sorted by mood match
        """
        # Extract mood from query or use context_mood from agent
        # e.g., "sad pop" → mood="sad", genre="pop"
        # Also handle artist: prefix (e.g., "artist:Taylor Swift")
        query_lower = query.lower()

        # Preserve artist: prefix if present
        if query_lower.startswith("artist:"):
            # Keep artist search as-is
            genre_query = query
            target_mood = context_mood or 'neutral'
        else:
            query_parts = query_lower.split()
            mood_keywords = []
            genre_keywords = []

            mood_map = {
                'sad': 'sad', 'sadder': 'sad', 'depressing': 'sad',
                'energetic': 'energetic', 'upbeat': 'energetic', 'party': 'energetic',
                'chill': 'chill', 'relaxed': 'chill', 'lofi': 'chill', 'lo-fi': 'chill',
            }

            for part in query_parts:
                if part in mood_map:
                    mood_keywords.append(mood_map[part])
                else:
                    genre_keywords.append(part)

            # Determine target mood (priority: query > agent context > default to neutral)
            target_mood = mood_keywords[0] if mood_keywords else (context_mood or 'neutral')
            genre_query = ' '.join(genre_keywords) if genre_keywords else 'pop'

        # Use MOOD-AWARE search (uses pre-calculated mood scores)
        results = self.db.search_by_mood(genre_query, target_mood, limit=limit)

        if not results:
            print(f"⚠️  No songs found matching '{target_mood} {genre_query}'")
            return []

        # Set mood for recommender (already has mood_confidence from search_by_mood)
        for song in results:
            song['mood'] = target_mood

        print(f"✅ Found {len(results)} songs from dataset ({target_mood} {genre_query}, REAL features)")
        return results

    def _infer_mood_from_audio(self, song: dict) -> str:
        """
        Infer mood from REAL audio features and genre.

        Uses the same logic as demo.py for consistency.
        """
        genre = song.get('genre', 'pop').lower()
        valence = song.get('valence', 0.5)
        energy = song.get('energy', 0.5)

        # Strong genre signals
        strong_moods = {
            'lo-fi': 'chill', 'lofi': 'chill', 'ambient': 'chill',
            'ballad': 'sad',
            'metal': 'energetic', 'hardcore': 'energetic', 'punk': 'energetic',
        }

        for key, mood in strong_moods.items():
            if key in genre:
                return mood

        # Infer from audio features
        if valence > 0.7 and energy > 0.6:
            return 'energetic'
        elif valence < 0.4 and energy < 0.5:
            return 'sad'
        elif energy < 0.4:
            return 'chill'
        elif energy > 0.75:
            return 'energetic'
        else:
            return 'neutral'

    def _search_spotify_api(self, query: str, limit: int = 10, context_mood: str = None, min_popularity: int = 0) -> list:
        """
        Search Spotify API (fallback if dataset unavailable).

        Note: Audio features endpoint is blocked on free tier.
        Features are SIMULATED based on genre/mood, NOT REAL.
        """
        if not self.sp:
            print("❌ Spotify API not initialized")
            return []

        # Step 1: Search for songs
        songs = self.search_songs(query, limit=limit, min_popularity=min_popularity)

        if not songs:
            print("No songs found to enrich")
            return []

        # Step 2: Infer mood from genre
        def infer_mood_from_genre(genre: str) -> str:
            genre_lower = genre.lower() if genre else 'pop'
            if 'lo-fi' in genre_lower or 'lofi' in genre_lower:
                return 'chill'
            elif 'ambient' in genre_lower:
                return 'chill'
            elif 'metal' in genre_lower or 'hard' in genre_lower:
                return 'energetic'
            elif 'ballad' in genre_lower:
                return 'sad'
            else:
                return 'upbeat'

        def infer_mood_for_features(song: dict, context_mood: str = None) -> str:
            import random
            genre = song.get('genre', '').lower()
            genre_mood = infer_mood_from_genre(genre)
            if genre_mood != 'upbeat':
                return genre_mood
            if context_mood and random.random() < 0.4:
                return context_mood.lower()
            return genre_mood

        # Assign mood and genre
        for song in songs:
            if not song.get('genre'):
                song['genre'] = 'pop'
            if not song.get('mood'):
                song['mood'] = infer_mood_for_features(song, context_mood)

        # Step 3: Get audio features (simulated on free tier)
        features = self.get_audio_features(songs)

        # Step 4: Get REAL genre from artist
        print(f"📊 Fetching real genre data...")
        for i, song in enumerate(songs):
            if i < 5 and song.get('artist_id'):
                song['genre'] = self.get_song_genre(song['artist_id'])
            else:
                if not song.get('genre'):
                    song['genre'] = 'unknown'

        # Step 5: Merge features
        enriched_songs = []
        for song in songs:
            track_id = song['id']
            if track_id in features:
                song.update(features[track_id])
                enriched_songs.append(song)

        print(f"⚠️  Enriched {len(enriched_songs)} songs (SIMULATED audio features - real Spotify features blocked on free tier)")
        return enriched_songs


def main():
    """
    Simple example showing how to use the Spotify retriever.

    Demonstrates:
    - Initializing the client
    - Searching for songs
    - Getting audio features
    - Combined search + enrich
    """
    print("\n" + "=" * 70)
    print("🎵 SPOTIFY RETRIEVER DEMO")
    print("=" * 70)

    # Create client
    spotify = SpotifyRetriever()

    # Example 1: Search for songs
    print("\n--- Example 1: Search for songs ---")
    query = "lofi chill beats"
    songs = spotify.search_songs(query, limit=5)

    for i, song in enumerate(songs, 1):
        print(f"\n{i}. {song['title']}")
        print(f"   Artist: {song['artist']}")
        print(f"   Popularity: {song['popularity']}/100")

    # Example 2: Get audio features for those songs
    if songs:
        print("\n--- Example 2: Get audio features ---")
        track_ids = [song['id'] for song in songs]
        features = spotify.get_audio_features(track_ids)

        for track_id, feature_data in list(features.items())[:3]:
            song = next((s for s in songs if s['id'] == track_id), None)
            if song:
                print(f"\n{song['title']}:")
                print(f"  Energy: {feature_data['energy']:.2f}")
                print(f"  Valence: {feature_data['valence']:.2f}")
                print(f"  Danceability: {feature_data['danceability']:.2f}")
                print(f"  Acousticness: {feature_data['acousticness']:.2f}")

    # Example 3: Search + enrich in one call
    print("\n--- Example 3: Search and enrich (combined) ---")
    enriched = spotify.search_and_enrich("upbeat indie pop", limit=3)

    for song in enriched:
        print(f"\n{song['title']} - {song['artist']}")
        print(f"  Energy: {song['energy']:.2f} | Valence: {song['valence']:.2f}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()