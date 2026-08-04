from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv
import math

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    # likes_acoustic: bool <--- I did not use this field in my logic

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        if not isinstance(user, UserProfile):
            raise TypeError(f"Expected UserProfile instance, got {type(user).__name__}")

        if k < 1:
            raise ValueError(f"k must be at least 1, got {k}")

        if k > len(self.songs):
            raise ValueError(
                f"Requested {k} recommendations but only {len(self.songs)} songs available"
            )

        user_dict = {
            'favorite_genre': user.favorite_genre,
            'favorite_mood': user.favorite_mood,
            'target_energy': user.target_energy,
        }

        recommendations = [
            (song, score)
            for song in self.songs
            for score, _ in [score_song(user_dict, self._song_to_dict(song))]
        ]

        sorted_recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
        return [song for song, _ in sorted_recommendations[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_dict = {
            'favorite_genre': user.favorite_genre,
            'favorite_mood': user.favorite_mood,
            'target_energy': user.target_energy,
        }
        _, reasons = score_song(user_dict, self._song_to_dict(song))
        return "; ".join(reasons) if reasons else "no matches"

    def _song_to_dict(self, song: Song) -> Dict:
        return {
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'genre': song.genre,
            'mood': song.mood,
            'energy': song.energy,
            'tempo_bpm': song.tempo_bpm,
            'valence': song.valence,
            'danceability': song.danceability,
            'acousticness': song.acousticness,
        }

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV file with proper type conversions for scoring."""
    import os

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Song data file not found: {csv_path}")

    print(f"Loading songs from {csv_path}...")

    required_columns = {
        'id', 'title', 'artist', 'genre', 'mood',
        'energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness'
    }

    songs = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"CSV file {csv_path} is empty or malformed")

        missing_columns = required_columns - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(
                f"CSV file missing required columns: {', '.join(sorted(missing_columns))}\n"
                f"Expected: {', '.join(sorted(required_columns))}\n"
                f"Found: {', '.join(sorted(reader.fieldnames))}"
            )

        for row_num, row in enumerate(reader, start=2):
            try:
                song = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'artist': row['artist'],
                    'genre': row['genre'],
                    'mood': row['mood'],
                    'energy': float(row['energy']),
                    'tempo_bpm': int(row['tempo_bpm']),
                    'valence': float(row['valence']),
                    'danceability': float(row['danceability']),
                    'acousticness': float(row['acousticness']),
                }
                songs.append(song)
            except ValueError as e:
                raise ValueError(
                    f"Row {row_num}: Invalid data format - {e}\n"
                    f"Row content: {row}"
                )

    if not songs:
        raise ValueError(f"No valid songs found in {csv_path}")

    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences using 6-component algorithm; return (score, reasons)."""
    required_song_fields = {
        'mood', 'genre', 'energy', 'valence', 'danceability', 'acousticness'
    }
    missing_song_fields = required_song_fields - set(song.keys())
    if missing_song_fields:
        raise ValueError(
            f"Song missing required fields: {', '.join(sorted(missing_song_fields))}\n"
            f"Song provided: {song}"
        )

    has_genre = 'favorite_genre' in user_prefs or 'genre' in user_prefs
    has_mood = 'favorite_mood' in user_prefs or 'mood' in user_prefs
    has_energy = 'target_energy' in user_prefs or 'energy' in user_prefs

    if not all([has_genre, has_mood, has_energy]):
        missing = []
        if not has_genre:
            missing.append("genre/favorite_genre")
        if not has_mood:
            missing.append("mood/favorite_mood")
        if not has_energy:
            missing.append("energy/target_energy")
        raise ValueError(
            f"User profile missing required fields: {', '.join(missing)}\n"
            f"Provided: {', '.join(sorted(user_prefs.keys()))}"
        )

    score = 0.0
    reasons = []

    # Part 1: Mood Match (Binary) — +0 or +2.0 points (highest priority)
    user_mood = user_prefs.get('mood') or user_prefs.get('favorite_mood')
    if user_mood and song['mood'] == user_mood:
        mood_score = 2.0
        score += mood_score
        reasons.append(f"mood match (+{mood_score})")

    # Part 2: Genre Match (Binary) — +0 or +1.0 points
    user_genre = user_prefs.get('genre') or user_prefs.get('favorite_genre')
    if user_genre and song['genre']:
        # Match if any word in user_genre appears in song['genre'] (case-insensitive)
        user_words = user_genre.lower().split()
        song_genre_lower = song['genre'].lower()
        if any(word in song_genre_lower for word in user_words) or song_genre_lower in user_genre.lower():
            genre_score = 1.0
            score += genre_score
            reasons.append(f"genre match (+{genre_score})")

    # Part 3: Valence Similarity (Gaussian) — 0 to 1.5 points
    user_valence = user_prefs.get('valence')
    if user_valence is not None:
        diff = abs(song['valence'] - user_valence)
        valence_score = 1.5 * math.exp(-(diff ** 2) / (2 * 0.20 ** 2))
        score += valence_score
        reasons.append(f"valence match (+{valence_score:.2f})")

    # Part 4: Energy Similarity (Gaussian) — 0 to 1.4 points
    user_energy = user_prefs.get('energy') or user_prefs.get('target_energy')
    if user_energy is not None:
        diff = abs(song['energy'] - user_energy)
        energy_score = 1.4 * math.exp(-(diff ** 2) / (2 * 0.20 ** 2))
        score += energy_score
        reasons.append(f"energy match (+{energy_score:.2f})")

    # Part 5: Danceability (Gaussian) — 0 to 1.0 points
    user_danceability = user_prefs.get('danceability')
    if user_danceability is not None:
        diff = abs(song['danceability'] - user_danceability)
        dance_score = 1.0 * math.exp(-(diff ** 2) / (2 * 0.20 ** 2))
        score += dance_score
        reasons.append(f"danceability match (+{dance_score:.2f})")

    # Part 6: Acousticness (Gaussian) — 0 to 0.6 points
    user_acousticness = user_prefs.get('acousticness')
    if user_acousticness is not None:
        diff = abs(song['acousticness'] - user_acousticness)
        acoustic_score = 0.6 * math.exp(-(diff ** 2) / (2 * 0.25 ** 2))
        score += acoustic_score
        reasons.append(f"acousticness match (+{acoustic_score:.2f})")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return top K recommendations ranked by similarity score."""
    # Score all songs and build (song, score, explanation) tuples
    recommendations = [
        (song, score, "; ".join(reasons) if reasons else "no matches")
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # Sort by score (highest first) and return top K
    return sorted(recommendations, key=lambda x: x[1], reverse=True)[:k]
