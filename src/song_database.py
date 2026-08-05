"""Local song database from Spotify top songs dataset (600 songs with real audio features)"""
import csv
import random
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class SongDatabase:
    """Load and search a CSV dataset of songs with real audio features."""

    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize the song database.

        Args:
            csv_path: Path to CSV file. If None, uses default location.
        """
        if csv_path is None:
            # Default location: ../spotify_songbank/spotify_top_music.csv
            csv_path = str(Path(__file__).parent.parent / "spotify_songbank" / "spotify_top_music.csv")

        self.csv_path = csv_path
        self.songs = []
        self.genre_index = {}  # Maps genre -> list of song indices
        self.load_database()

    def load_database(self):
        """
        Load CSV file, build genre index, and pre-calculate mood scores.

        Mood caching: We pre-calculate sad_score, energetic_score, chill_score
        for each song at load time. This makes searches fast (O(1) lookup)
        without modifying the CSV file. Mood scores are calculated once per
        session and cached in the song objects.
        """
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    song = self._normalize_song(row)
                    self.songs.append(song)

                    # Build genre index for fast genre lookups
                    genre = song['genre'].lower()
                    if genre not in self.genre_index:
                        self.genre_index[genre] = []
                    self.genre_index[genre].append(len(self.songs) - 1)

            # PRE-CALCULATE MOOD SCORES (cached in memory)
            # This is fast for 603 songs and makes searches much quicker
            print(f"📊 Pre-calculating mood scores for {len(self.songs)} songs...")
            for song in self.songs:
                # Cache mood scores so search_by_mood doesn't recalculate
                song['sad_score'] = self.calculate_sad_score(song)
                song['energetic_score'] = self.calculate_energetic_score(song)
                song['chill_score'] = self.calculate_chill_score(song)

            print(f"✅ Loaded {len(self.songs)} songs with mood scores")
        except FileNotFoundError:
            print(f"❌ Could not find CSV at {self.csv_path}")
            self.songs = []

    def _normalize_song(self, row: Dict) -> Dict:
        """
        Normalize raw CSV row to song object with 0-1 audio features.

        Spotify dataset uses 0-100 scales; convert to 0-1 for scoring algorithm.
        """
        return {
            'title': row.get('title', '').strip('"'),
            'artist': row.get('artist', '').strip('"'),
            'genre': row.get('top genre', 'pop'),
            'year': int(row.get('year', 2010)),

            # Audio features: normalize 0-100 to 0-1
            'energy': float(row.get('nrgy', 50)) / 100.0,
            'valence': float(row.get('val', 50)) / 100.0,
            'danceability': float(row.get('dnce', 50)) / 100.0,
            'acousticness': float(row.get('acous', 50)) / 100.0,

            # Other features (not normalized, kept for reference)
            'bpm': float(row.get('bpm', 100)),
            'loudness_db': float(row.get('dB', -5)),
            'liveness': float(row.get('live', 10)),
            'duration_ms': float(row.get('dur', 200)) * 1000,  # Convert to ms
            'speechiness': float(row.get('spch', 5)),
            'popularity': int(row.get('pop', 50)),
            'explicit': False,  # Dataset doesn't have explicit flag
            'search_rank_popularity': 100,  # All dataset songs are "equally discoverable"
            'id': f"db_{len(self.songs)}",  # Synthetic ID
        }

    def search(self, query: str, limit: int = 10, genres_only: bool = False) -> List[Dict]:
        """
        Search database by query string (artist, title, or genre).

        For multi-word queries like "pop sad", searches by ANY matching word
        (not requiring all words to match), prioritizing genre matches.

        Args:
            query: Search query (e.g., "pop sad", "Ariana Grande")
            limit: Max number of results
            genres_only: If True, treat query as genre names only

        Returns:
            List of matching songs
        """
        if not self.songs:
            return []

        query_lower = query.lower()
        matches = []

        # Handle artist: prefix (e.g., "artist:Taylor Swift")
        if query_lower.startswith("artist:"):
            artist_name = query_lower.replace("artist:", "").strip()
            for song in self.songs:
                if artist_name in song['artist'].lower():
                    matches.append(song)
        else:
            # Regular search: any word matching title, artist, or genre
            parts = query_lower.split()
            for song in self.songs:
                song_title = song['title'].lower()
                song_artist = song['artist'].lower()
                song_genre = song['genre'].lower()

                # Check if ANY query part matches ANY field
                for part in parts:
                    if (part in song_title or
                        part in song_artist or
                        part in song_genre):
                        matches.append(song)
                        break  # Don't add duplicate if multiple parts match

        # If no results, return random sample from database
        if not matches:
            matches = random.sample(self.songs, min(limit, len(self.songs)))

        # Shuffle to add variety (database is ordered by year/popularity)
        random.shuffle(matches)
        return matches[:limit]

    def search_by_genre(self, genre: str, limit: int = 10) -> List[Dict]:
        """
        Get random songs from a specific genre.

        Args:
            genre: Genre to search for
            limit: Max number of results

        Returns:
            List of songs from that genre
        """
        genre_lower = genre.lower()

        # Exact match first
        if genre_lower in self.genre_index:
            indices = self.genre_index[genre_lower]
            selected = random.sample(indices, min(limit, len(indices)))
            return [self.songs[i] for i in selected]

        # Fuzzy match: any song with genre substring
        matches = [s for s in self.songs if genre_lower in s['genre'].lower()]
        if matches:
            selected = random.sample(matches, min(limit, len(matches)))
            return selected

        return []

    def get_random_sample(self, limit: int = 10) -> List[Dict]:
        """Get random sample of songs from database."""
        if not self.songs:
            return []
        return random.sample(self.songs, min(limit, len(self.songs)))

    def stats(self) -> Dict:
        """Get database statistics."""
        if not self.songs:
            return {'total': 0}

        genres = set(s['genre'] for s in self.songs)
        return {
            'total': len(self.songs),
            'genres': len(genres),
            'year_range': (min(s['year'] for s in self.songs),
                          max(s['year'] for s in self.songs)),
            'popularity_range': (min(s['popularity'] for s in self.songs),
                                max(s['popularity'] for s in self.songs)),
        }

    @staticmethod
    def calculate_sad_score(song: Dict) -> float:
        """
        Calculate how sad a song is (0-1, higher = sadder).

        Combines: low valence (40%), low energy (30%), acoustic (15%),
        slow tempo (10%), not danceable (5%).
        """
        valence = song.get('valence', 0.5)
        energy = song.get('energy', 0.5)
        acousticness = song.get('acousticness', 0.5)
        bpm = song.get('bpm', 100)
        danceability = song.get('danceability', 0.5)

        sad_score = (
            (1 - valence) * 0.40 +
            (1 - energy) * 0.30 +
            acousticness * 0.15 +
            (1 - min(bpm / 120, 1.0)) * 0.10 +
            (1 - danceability) * 0.05
        )
        return min(1.0, max(0.0, sad_score))

    @staticmethod
    def calculate_energetic_score(song: Dict) -> float:
        """
        Calculate how energetic a song is (0-1, higher = more energetic).

        Combines: high energy (40%), high valence (30%), danceable (20%), fast tempo (10%).
        """
        energy = song.get('energy', 0.5)
        valence = song.get('valence', 0.5)
        danceability = song.get('danceability', 0.5)
        bpm = song.get('bpm', 100)

        energetic_score = (
            energy * 0.40 +
            valence * 0.30 +
            danceability * 0.20 +
            min(bpm / 120, 1.0) * 0.10
        )
        return min(1.0, max(0.0, energetic_score))

    @staticmethod
    def calculate_chill_score(song: Dict) -> float:
        """
        Calculate how chill/relaxed a song is (0-1, higher = more chill).

        Combines: low energy (35%), acoustic (25%), not danceable (20%), slow tempo (20%).
        """
        energy = song.get('energy', 0.5)
        acousticness = song.get('acousticness', 0.5)
        danceability = song.get('danceability', 0.5)
        bpm = song.get('bpm', 100)

        chill_score = (
            (1 - energy) * 0.35 +
            acousticness * 0.25 +
            (1 - danceability) * 0.20 +
            (1 - min(bpm / 120, 1.0)) * 0.20
        )
        return min(1.0, max(0.0, chill_score))

    @staticmethod
    def calculate_mood_scores(song: Dict) -> Dict[str, float]:
        """Calculate mood scores for a song across all mood dimensions."""
        return {
            'sad': SongDatabase.calculate_sad_score(song),
            'energetic': SongDatabase.calculate_energetic_score(song),
            'chill': SongDatabase.calculate_chill_score(song),
            'neutral': 0.5,
        }

    @staticmethod
    def genre_mood_alignment(genre: str, target_mood: str) -> float:
        """
        How well does a genre align with a mood (0-1)?

        Some genres are inherently tied to moods.
        Returns 1.0 if perfect match, 0.0 if opposite, 0.5 if neutral.
        """
        genre_lower = genre.lower()

        # Genres that strongly indicate sadness
        sad_genres = {'ballad', 'blues', 'country', 'soul'}
        if any(g in genre_lower for g in sad_genres):
            return 1.0 if target_mood == 'sad' else 0.2

        # Genres that strongly indicate chill
        chill_genres = {'lo-fi', 'lofi', 'ambient', 'acoustic'}
        if any(g in genre_lower for g in chill_genres):
            return 1.0 if target_mood == 'chill' else 0.3

        # Genres that strongly indicate energetic
        energetic_genres = {'metal', 'punk', 'hardcore', 'dance', 'disco', 'edm', 'electronic'}
        if any(g in genre_lower for g in energetic_genres):
            return 1.0 if target_mood == 'energetic' else 0.1

        # Neutral genres (pop, rock, indie, hip-hop)
        return 0.5

    @staticmethod
    def mood_distance(user_prefs: Dict, song: Dict) -> float:
        """
        Calculate mood similarity between user preferences and a song (0-1, higher = better).

        Combines:
        - Audio feature distance (70%): Euclidean distance between feature vectors
        - Genre alignment (30%): How well genre matches target mood
        """
        # Extract user preference features
        features_to_compare = ['energy', 'valence', 'danceability', 'acousticness']
        user_features = [user_prefs.get(f, 0.5) for f in features_to_compare]
        song_features = [song.get(f, 0.5) for f in features_to_compare]

        # Euclidean distance (0 to sqrt(4) ≈ 2.0)
        sum_squared_diff = sum(
            (user - song) ** 2
            for user, song in zip(user_features, song_features)
        )
        distance = math.sqrt(sum_squared_diff)
        feature_similarity = 1.0 - (distance / 2.0)
        feature_similarity = max(0.0, min(1.0, feature_similarity))

        # Genre alignment
        target_mood = user_prefs.get('mood', 'neutral')
        genre = song.get('genre', 'pop')
        genre_alignment = SongDatabase.genre_mood_alignment(genre, target_mood)

        # Weighted combination: 70% features, 30% genre
        combined_score = (feature_similarity * 0.7) + (genre_alignment * 0.3)
        return combined_score

    def search_by_mood(self, query: str, target_mood: str, limit: int = 10) -> List[Dict]:
        """
        Search database for songs matching both genre/artist AND mood.

        MOOD CACHING: Uses pre-calculated mood scores for O(1) lookup.
        Mood scores are computed once during load_database() and stored
        in each song object (sad_score, energetic_score, chill_score).
        This makes searches instant even with complex mood matching.

        Args:
            query: Genre/artist to search (e.g., "pop", "indie")
            target_mood: Mood to match (sad, energetic, chill, neutral)
            limit: Max results

        Returns:
            List of songs matching both criteria, sorted by mood match
        """
        if not self.songs:
            return []

        query_lower = query.lower()

        # STEP 1: Filter songs matching the genre/artist query
        # This narrows the search space before applying mood filtering
        matching_genre = []
        for song in self.songs:
            if (query_lower in song['genre'].lower() or
                query_lower in song['artist'].lower() or
                query_lower in song['title'].lower()):
                matching_genre.append(song)

        # If no genre matches, expand to all songs (better to show results than none)
        if not matching_genre:
            matching_genre = random.sample(self.songs, min(limit * 2, len(self.songs)))

        # STEP 2: Sort by cached mood score (FAST - already calculated at load time)
        # The mood score key changes based on target_mood
        mood_score_key = f'{target_mood}_score'

        sorted_by_mood = sorted(
            matching_genre,
            key=lambda s: s.get(mood_score_key, 0.5),
            reverse=True
        )

        # STEP 3: Return top matches (with mood score attached for debugging)
        results = sorted_by_mood[:limit]
        for song in results:
            # Attach mood confidence so recommender can display it
            song['mood_confidence'] = song.get(mood_score_key, 0.5)

        return results
