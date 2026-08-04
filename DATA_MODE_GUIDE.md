# VibeFinder Data Mode Guide

VibeFinder supports two modes for song data and audio features:

## Mode 1: Dataset Mode (DEFAULT - RECOMMENDED) ✅

**What it uses:**
- Local CSV with 603 real songs (2010-2019 Billboard top songs)
- **REAL audio features** from Spotify dataset (valence, energy, danceability, acousticness)
- No API calls needed

**When to use:**
- ✅ Free (no Spotify API required)
- ✅ Instant results (no API latency)
- ✅ Honest scoring (real data)
- ✅ Perfect for demos/prototypes

**Limitations:**
- ⚠️ Limited to 603 songs
- ⚠️ Only 2010-2019 era music
- ⚠️ No real-time Spotify search

**How to use (in code):**
```python
from spotify_client import SpotifyRetriever

# Default: dataset mode
spotify = SpotifyRetriever(use_dataset=True)
songs = spotify.search_and_enrich("sad pop songs", limit=10)
```

**Audio features in this mode:**
- valence (0-1): Musical positivity
- energy (0-1): Intensity/loudness
- danceability (0-1): Suitability for dancing
- acousticness (0-1): Acoustic vs electronic
- **All values are REAL from Spotify, normalized to 0-1**

---

## Mode 2: Spotify API Mode (OPTIONAL)

**What it uses:**
- Live Spotify Web API (millions of songs)
- **SIMULATED audio features** (free tier blocks real audio endpoint)
- Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET

**When to use:**
- If you have paid Spotify API access
- Need access to full Spotify catalog
- Want real-time search across all releases

**Limitations:**
- ❌ Free tier: Blocks audio features endpoint (403 Forbidden)
- ❌ Scores based on simulated features (not real Spotify data)
- ❌ Requires valid Spotify credentials

**How to use (in code):**
```python
from spotify_client import SpotifyRetriever

# Use Spotify API instead
spotify = SpotifyRetriever(use_dataset=False)
songs = spotify.search_and_enrich("sad pop songs", limit=10)
```

---

## Comparison Table

| Feature | Dataset Mode | Spotify API Mode |
|---------|---|---|
| **Audio Features** | ✅ REAL | ❌ SIMULATED (free tier) |
| **Songs Available** | 603 (2010-2019) | Millions (all eras) |
| **API Required** | ❌ No | ✅ Yes (paid) |
| **Latency** | <100ms | 500ms+ |
| **Cost** | Free | Paid API access |
| **Data Honesty** | ✅ Real Spotify data | ❌ Generated ranges |
| **Recommended** | ✅ YES | No (unless paid access) |

---

## Score Interpretation

### Dataset Mode (RECOMMENDED)
- Scores are based on **REAL audio features**
- Score of 5.5/7.5 is trustworthy
- Feature matches are genuine Spotify characteristics
- Lower scores are honest (song doesn't match preferences)

**Example:**
```
Query: "sad pop songs"
Result: Girl On Fire (3.59/7.5)
Reason: Song has HIGH valence/energy (upbeat), 
        NOT actually sad. Score reflects reality.
```

### Spotify API Mode
- Scores are based on **SIMULATED features**
- Score of 5.5/7.5 is an estimate
- Feature matches are calculated from genre/mood ranges
- Lower scores may be inaccurate (features are fake)

---

## Recommendation

**Use Dataset Mode by default.** It provides:
- ✅ Real audio features (honest scoring)
- ✅ No API dependency
- ✅ Reproducible results
- ✅ Transparent data source

If you need a larger catalog and have paid Spotify access, you can switch to API mode, but note that audio features will be simulated on the free tier.

---

## How Features Are Inferred

### Dataset Mode
- Uses actual Spotify audio feature values from the CSV
- All 603 songs include: energy, valence, danceability, acousticness
- No simulation or guessing

### Spotify API Mode (Free Tier)
- Genre is fetched from real Spotify artist data
- Audio features are **simulated** based on genre+mood combinations
- Example ranges:
  - Pop + Sad: energy 0.3-0.5, valence 0.2-0.4
  - Rock + Energetic: energy 0.8-0.95, valence 0.5-0.7

---

## Switching Modes

To switch from dataset to API mode, change one line in `demo.py`:

```python
# Current (recommended):
spotify = SpotifyRetriever(use_dataset=True)

# To use Spotify API:
spotify = SpotifyRetriever(use_dataset=False)
```

That's it! The rest of the code works the same way.
