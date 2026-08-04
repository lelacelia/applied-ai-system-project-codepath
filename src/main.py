"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from recommender import load_songs, recommend_songs
from test_profiles import TEST_PROFILES


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile with all 6 scoring components
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.75,        # emotional positivity (upbeat vs introspective)
        "danceability": 0.70,   # groove/rhythm-driven quality
        "acousticness": 0.30    # acoustic vs electronic preference
    }

    # Override with a test profile if desired
    user_prefs = TEST_PROFILES["extreme_maxed"]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 70)
    print("🎵 TOP SONG RECOMMENDATIONS")
    print("=" * 70 + "\n")

    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"{i}. {song['title']}")
        print(f"   Artist: {song['artist']} | Genre: {song['genre']}")
        print(f"   Score: {score:.2f}/7.5")

        # Display reasons as bullet points
        if explanation and explanation != "no matches":
            print("   Why this recommendation:")
            for reason in explanation.split("; "):
                print(f"      • {reason}")
        else:
            print("   (No strong matches)")
        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
