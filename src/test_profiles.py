"""
Test profiles designed to expose edge cases and contradictions in the scoring algorithm.
Use these to verify the recommender handles conflicting preferences gracefully.
"""

# Profile 1: Contradictory - High energy but melancholic mood
CONTRADICTORY = {
    "genre": "pop",
    "mood": "sad",
    "energy": 0.90,            # conflicts with sad mood
    "valence": 0.15,           # introspective, conflicts with energy
    "danceability": 0.85,      # danceable but sad? unusual combo
    "acousticness": 0.10       # electronic but melancholic
}

# Profile 2: Extreme maximalist - Everything cranked to 1.0
EXTREME_MAXED = {
    "genre": "rock",
    "mood": "intense",
    "energy": 1.0,             # absolute maximum
    "valence": 1.0,            # upbeat AND intense (contradiction?)
    "danceability": 1.0,       # max groove
    "acousticness": 1.0        # max acoustic (unusual for rock)
}

# Profile 3: Conflicting production style - Wants extreme acoustic AND electronic vibes
ACOUSTIC_ELECTRONIC_CONFLICT = {
    "genre": "lofi",
    "mood": "chill",
    "energy": 0.5,
    "valence": 0.5,
    "danceability": 0.5,
    "acousticness": 0.95       # wants very acoustic...but lofi is typically electronic
}

# Profile 4: Niche with internal conflicts - Angry k-pop that's not danceable
NICHE_CONFLICTS = {
    "genre": "k-pop",
    "mood": "angry",
    "energy": 0.95,            # very high
    "valence": 0.10,           # very dark/negative (conflicts with angry)
    "danceability": 0.15,      # not danceable (conflicts with k-pop genre)
    "acousticness": 0.90       # very acoustic (conflicts with k-pop production)
}

# Map of all test profiles for easy iteration
TEST_PROFILES = {
    "contradictory": CONTRADICTORY,
    "extreme_maxed": EXTREME_MAXED,
    "acoustic_electronic_conflict": ACOUSTIC_ELECTRONIC_CONFLICT,
    "niche_conflicts": NICHE_CONFLICTS,
}
