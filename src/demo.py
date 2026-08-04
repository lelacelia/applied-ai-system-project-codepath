"""
End-to-End Music Recommendation Demo

This script demonstrates the complete VibeFinder system:
1. User describes music taste in NATURAL LANGUAGE
2. Gemini agent extracts structured preferences
3. Spotify retrieves real songs matching the query
4. Recommender scores songs using the 6-component algorithm
5. Top recommendations are displayed with explanations

Perfect for class presentations!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from spotify_client import SpotifyRetriever
from recommender import score_song
from agent import MusicAgent


def main():
    """
    Run the complete end-to-end recommendation system.

    Flow:
    1. Ask user: Dataset mode or Spotify API mode?
    2. Get natural language input from user
    3. Use Gemini agent to extract preferences
    4. Search for matching songs (using chosen mode)
    5. Score with recommender algorithm
    6. Display top 5 recommendations
    """

    print("\n" + "=" * 70)
    print("🎵 VibeFinder - AI Music Recommendation System")
    print("=" * 70)

    # STEP 1: MODE SELECTION
    print("\n📋 Choose Data Source:")
    print("  1) Local Dataset (603 songs, REAL Spotify features, fast, FREE) [default]")
    print("  2) Spotify API (millions of songs, requires SPOTIFY_CLIENT_ID/SECRET)")
    print()

    mode_input = input("Your choice (1 or 2, press Enter for 1): ").strip() or "1"
    use_dataset = mode_input == "1"

    # Initialize components with chosen mode
    print("\n📱 Initializing system...")
    try:
        spotify = SpotifyRetriever(use_dataset=use_dataset)

        if use_dataset:
            print("   ✅ Dataset Mode: Mood-aware search with REAL audio features")
        else:
            print("   ✅ Spotify API Mode: Live search (audio features simulated on free tier)")
    except Exception as e:
        print(f"   ❌ Error initializing: {e}")
        return

    print("🤖 Starting Gemini agent...")
    try:
        agent = MusicAgent()
        agent_available = True
    except Exception as e:
        print(f"⚠️  Agent unavailable: {e}")
        agent_available = False

    # Get natural language input
    print("\n🎤 Describe your music taste (natural language):")
    print("   Example: 'I want upbeat indie pop with good energy'\n")

    user_input = input("You: ").strip()
    if not user_input:
        user_input = "lofi chill beats"

    # Extract preferences using agent
    print(f"\n🤖 Agent analyzing: '{user_input}'...")

    if agent_available:
        try:
            prefs = agent.extract_preferences_only(user_input)
            if prefs:
                user_prefs = {
                    'mood': prefs.get('mood', 'chill'),
                    'genre': prefs.get('genre') or 'pop',  # Default to 'pop' if None
                    'energy': prefs.get('energy', 0.5) or 0.5,
                    'valence': prefs.get('valence', 0.5) or 0.5,
                    'danceability': prefs.get('danceability', 0.4) or 0.4,
                    'acousticness': prefs.get('acousticness', 0.6) or 0.6
                }
                print("✅ Agent extracted preferences:")
            else:
                raise Exception("No preferences extracted")
        except Exception as e:
            print(f"⚠️  Agent error: {e}")
            print("   Using default preferences...")
            user_prefs = {
                'mood': 'chill',
                'genre': 'lofi',
                'energy': 0.5,
                'valence': 0.5,
                'danceability': 0.4,
                'acousticness': 0.6
            }
    else:
        print("⚠️  Agent not available, using default preferences...")
        user_prefs = {
            'mood': 'chill',
            'genre': 'lofi',
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.4,
            'acousticness': 0.6
        }

    print(f"\n👤 Your taste profile:")
    print(f"   Mood: {user_prefs['mood']}")
    print(f"   Genre: {user_prefs['genre']}")
    print(f"   Energy: {user_prefs['energy']}")
    print(f"   Valence: {user_prefs['valence']}")
    print(f"   Danceability: {user_prefs['danceability']}")
    print(f"   Acousticness: {user_prefs['acousticness']}")

    # Build search query from extracted preferences
    # If artist mentioned, search specifically for that artist to avoid unrelated songs
    if prefs and prefs.get('artist'):
        search_query = f"artist:{prefs['artist']}"  # Spotify artist search filter
    else:
        search_query = f"{user_prefs['genre']} {user_prefs['mood']}"

    print(f"\n🔍 Searching Spotify for '{search_query.strip()}'...")
    # Pass user's mood as context for feature generation (reflects search intent)
    songs = spotify.search_and_enrich(search_query.strip(), limit=10, context_mood=user_prefs['mood'])

    if not songs:
        print("❌ No songs found. Try a different query.")
        return

    print(f"✅ Found {len(songs)} songs")

    # Mood already inferred by search_and_enrich (dataset uses real features, API uses genre signals)
    # Filter out songs whose inferred mood doesn't match user request
    print(f"\n🔍 Filtering songs by mood match...")
    matching_mood_songs = [s for s in songs if s['mood'] == user_prefs['mood']]
    if matching_mood_songs:
        filtered_out = len(songs) - len(matching_mood_songs)
        print(f"   Kept {len(matching_mood_songs)} songs with {user_prefs['mood']} mood")
        if filtered_out > 0:
            print(f"   Filtered out {filtered_out} songs with mismatched mood")
        songs = matching_mood_songs
    else:
        print(f"   ⚠️  No songs matched {user_prefs['mood']} mood, keeping all results")

    # Score songs with recommender
    print(f"\n⭐ Scoring songs with recommender...")
    scored_songs = []

    for song in songs:
        # Score the song with REAL genre and INFERRED mood (from features)
        score, reasons = score_song(user_prefs, song)
        scored_songs.append({
            'song': song,
            'score': score,
            'reasons': reasons
        })

    # Sort by score
    scored_songs.sort(key=lambda x: x['score'], reverse=True)

    # Display results
    print("\n" + "=" * 70)
    print("🎵 TOP 5 RECOMMENDATIONS")
    print("=" * 70)

    for i, item in enumerate(scored_songs[:5], 1):
        song = item['song']
        score = item['score']
        reasons = item['reasons']

        print(f"\n{i}. {song['title']}")
        print(f"   Artist: {song['artist']}")

        # Display search rank popularity (proxy metric)
        rank_pop = song.get('search_rank_popularity', 0)
        if rank_pop > 0:
            popularity_bar = "█" * (rank_pop // 10) + "░" * (10 - rank_pop // 10)
            print(f"   Relevance: {popularity_bar} {rank_pop}/100")

        print(f"   Score: {score:.2f}/7.5")

        if reasons:
            print("   Why recommended:")
            for reason in reasons:
                print(f"      • {reason}")

    print("\n" + "=" * 70)
    print(f"✅ Complete! Top match: {scored_songs[0]['song']['title']} ({scored_songs[0]['score']:.2f}/7.5)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()