import pytest
from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_recommend_ranks_by_score_not_by_list_order():
    # Verify that reordering the song list doesn't change recommendations
    # This ensures scoring logic actually determines rank, not input order
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
    )

    # Create recommenders with songs in different orders
    songs_pop_first = [
        Song(
            id=1, title="Test Pop Track", artist="Test Artist",
            genre="pop", mood="happy", energy=0.8, tempo_bpm=120,
            valence=0.9, danceability=0.8, acousticness=0.2,
        ),
        Song(
            id=2, title="Chill Lofi Loop", artist="Test Artist",
            genre="lofi", mood="chill", energy=0.4, tempo_bpm=80,
            valence=0.6, danceability=0.5, acousticness=0.9,
        ),
    ]
    songs_lofi_first = [songs_pop_first[1], songs_pop_first[0]]

    rec1 = Recommender(songs_pop_first)
    rec2 = Recommender(songs_lofi_first)

    results1 = rec1.recommend(user, k=2)
    results2 = rec2.recommend(user, k=2)

    # Pop song should rank first regardless of input order
    assert results1[0].id == 1
    assert results2[0].id == 1
    assert results1[0].genre == results2[0].genre


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_explain_recommendation_includes_matching_reasons():
    # Verify explanation includes reasons for why the song was recommended
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
    )
    rec = make_small_recommender()
    pop_song = rec.songs[0]

    explanation = rec.explain_recommendation(user, pop_song)

    # Pop song matches genre and mood, so explanation should mention these
    assert "genre match" in explanation.lower()
    assert "mood match" in explanation.lower()


def test_recommend_rejects_invalid_k():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
    )
    rec = make_small_recommender()

    with pytest.raises(ValueError, match="k must be at least 1"):
        rec.recommend(user, k=0)

    with pytest.raises(ValueError, match="only 2 songs available"):
        rec.recommend(user, k=5)


def test_score_song_validates_required_fields():
    from src.recommender import score_song

    valid_user = {
        'favorite_genre': 'pop',
        'favorite_mood': 'happy',
        'target_energy': 0.8,
    }
    valid_song = {
        'mood': 'happy',
        'genre': 'pop',
        'energy': 0.8,
        'valence': 0.9,
        'danceability': 0.8,
        'acousticness': 0.2,
    }

    # Should work with valid data
    score, reasons = score_song(valid_user, valid_song)
    assert score > 0
    assert len(reasons) > 0

    # Should also work with alternative field names (e.g., from main.py)
    valid_user_alt = {
        'genre': 'pop',
        'mood': 'happy',
        'energy': 0.8,
    }
    score_alt, _ = score_song(valid_user_alt, valid_song)
    assert score_alt > 0

    # Should fail if song is missing required field
    incomplete_song = valid_song.copy()
    del incomplete_song['mood']
    with pytest.raises(ValueError, match="Song missing required fields"):
        score_song(valid_user, incomplete_song)

    # Should fail if user profile is missing required field
    incomplete_user = valid_user.copy()
    del incomplete_user['favorite_genre']
    with pytest.raises(ValueError, match="missing required fields"):
        score_song(incomplete_user, valid_song)
