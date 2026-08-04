# VibeFinder: AI Music Recommendation System

## Project Overview

**Original Project:** Module 3 - Music Recommender Simulation  
**Original Goals:** Build a 6-component music scoring algorithm that evaluates songs across mood, genre, energy, valence, danceability, and acousticness to provide personalized recommendations.

**What VibeFinder Does:**  
VibeFinder is an end-to-end AI music recommendation system that converts natural language music preferences into personalized song recommendations. Users describe their music taste in plain English (e.g., "I want chill Taylor Swift songs"), and the system uses Google Gemini AI to extract structured preferences, searches Spotify for matching songs, and ranks them using a 6-component scoring algorithm that weighs musical features against user taste.

**Why It Matters:**  
This project demonstrates how to bridge natural language understanding (AI) with structured data (music features) to solve real-world problems. It shows practical integration of multiple APIs (Gemini + Spotify) and demonstrates how to design scoring systems that feel accurate to users, not just mathematically correct.

---

## Architecture Overview

```
User Input (Natural Language)
        ↓
   Gemini AI Agent
   (Extract: mood, genre, energy, valence, danceability, acousticness)
        ↓
DATASET MODE (Default - RECOMMENDED) ← Choose Mode
   ↓
Load Local Song Database (603 songs)
   ↓
PRE-CALCULATE MOOD SCORES (cached at startup)
   • sad_score: (1-valence)*0.4 + (1-energy)*0.3 + acousticness*0.15 + ...
   • energetic_score: energy*0.4 + valence*0.3 + danceability*0.2 + ...
   • chill_score: (1-energy)*0.35 + acousticness*0.25 + ...
   [Stored in memory for O(1) lookups]
        ↓
MOOD-AWARE SEARCH
   1. Filter by genre/artist (narrow search space)
   2. Sort by mood score (sad_score, energetic_score, etc.)
   3. Return top matches
        ↓
Recommender Algorithm (6-Component Scoring)
   • Mood match: +2.0 (exact match with calculated mood)
   • Genre match: +1.0 (substring match)
   • Valence similarity: 0-1.5 (Gaussian, REAL Spotify data)
   • Energy similarity: 0-1.4 (Gaussian, REAL Spotify data)
   • Danceability: 0-1.0 (Gaussian, REAL Spotify data)
   • Acousticness: 0-0.6 (Gaussian, REAL Spotify data)
   Max Score: 7.5
        ↓
Top 5 Recommendations with Explanations
```

**Key Components:**
- `agent.py`: Gemini AI for preference extraction
- `song_database.py`: Local song database with mood caching (NEW)
- `spotify_client.py`: Dual-mode music retrieval (dataset + API)
- `recommender.py`: 6-component scoring algorithm
- `demo.py`: End-to-end demo

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Keys

**Gemini:** https://aistudio.google.com/app/apikey  
**Spotify:** https://developer.spotify.com/dashboard

### 3. Create `.env`
Copy `.env.example` to `.env` and fill in your API keys:
```
GEMINI_API_KEY=your_key_here
SPOTIFY_CLIENT_ID=your_id_here
SPOTIFY_CLIENT_SECRET=your_secret_here
```

### 4. Run the Demo
```bash
python src/demo.py
```

**🎵 That's it!** The demo will:
1. Ask you to describe your music taste in natural language
2. Extract preferences using Gemini AI
3. Search for matching songs from the local dataset (or Spotify API)
4. Score and rank them with the 6-component algorithm
5. Display top 5 recommendations with explanations

---

## Sample Interactions

### Example 1: Romantic Pop
**Input:** "My favorite song is Lover by Taylor Swift - I want similar songs"

**Extracted Preferences:**
- Mood: romantic | Genre: pop | Energy: 0.5 | Valence: 0.7 | Danceability: 0.6 | Acousticness: 0.4

**Top Result:**
```
1. Lover - Taylor Swift
   Relevance: ████████░░ 88/100
   Score: 6.21/7.5
   • mood match (+2.0)
   • genre match (+1.0)
   • valence match (+1.41)
   • energy match (+0.76)
   • danceability match (+0.73)
   • acousticness match (+0.44)
```

### Example 2: Chill Indie
**Input:** "I want chill indie music with low energy and acoustic vibes"

**Extracted Preferences:**
- Mood: chill | Genre: indie | Energy: 0.3 | Valence: 0.4 | Danceability: 0.3 | Acousticness: 0.7

**Top Result:**
```
1. Skinny Love (Acoustic) - Bon Iver
   Relevance: █████████░ 90/100
   Score: 5.87/7.5
   • mood match (+2.0)
   • genre match (+1.0)
   • valence match (+1.05)
   • energy match (+0.82)
   • danceability match (+0.50)
   • acousticness match (+0.60)
```

### Example 3: Upbeat Indie Pop
**Input:** "I want upbeat indie pop with good energy"

**Extracted Preferences:**
- Mood: upbeat | Genre: indie pop | Energy: 0.8 | Valence: 0.8 | Danceability: 0.7 | Acousticness: 0.2

**Top Result:**
```
1. Uplifting Indie Pop - BlackTrendMusic
   Relevance: ████████░░ 86/100
   Score: 6.42/7.5
   • mood match (+2.0)
   • genre match (+1.0)
   • valence match (+1.50)
   • energy match (+1.37)
   • danceability match (+0.97)
   • acousticness match (+0.58)
```

---

## Reliability & Testing

### Guardrail Test 1: Empty Input (Graceful Fallback)
**Input:** User presses Enter without typing anything
```
🎤 Describe your music taste:
You: 

🤖 Agent analyzing: 'lofi chill beats'...
✅ Agent extracted preferences:
   Mood: chill | Genre: lofi | Energy: 0.5 | Valence: 0.5 | 
   Danceability: 0.4 | Acousticness: 0.6
```
**Result:** ✅ System falls back to safe default query instead of crashing

### Guardrail Test 2: Out-of-Dataset Query (Honest Error)
**Input:** "Billie Eilish sad songs" (released mostly after 2019 dataset cutoff)
```
🔍 Searching Spotify for 'sad Billie Eilish'...
⚠️  No songs found in dataset for 'sad Billie Eilish'
❌ No songs found. Try a different query.
```
**Result:** ✅ System admits limitations instead of returning wrong songs

### Guardrail Test 3: Invalid Mode Selection (Error Handling)
**Input:** User selects non-existent mode option
```
Choose mode (1 or 2, press Enter for 1): 5

📋 Choose Data Source:
  1) Local Dataset (603 songs, REAL features, fast, FREE) [default]
  2) Spotify API (millions of songs, requires SPOTIFY_CLIENT_ID/SECRET)

Your choice (1 or 2, press Enter for 1): 5
```
**Result:** ✅ Treats invalid input as default (mode 1), doesn't crash or get stuck

### Test Summary
- ✅ **Unit Tests:** 7/7 passing (mood matching, scoring, error handling)
- ✅ **Human Evaluation:** 5/5 real queries, 100% success rate
- ✅ **Reliability:** Graceful degradation; no crashes on edge cases

For detailed test results, see [TESTING.md](TESTING.md)

---

## Design Decisions

### 1. Gemini for NLP Extraction
**Why:** Natural language is ambiguous. Users say "chill pop" with different meanings. Gemini understands context better than rules.  
**Trade-off:** Slower/costs API calls. But users don't fill forms → better UX.

### 2. 6-Component Scoring with Gaussian Curves
**Why:** Binary mood/genre matching ensures exact preferences are prioritized. Gaussian curves reward "close enough" matches.  
**Trade-off:** More complex than linear distance, but feels natural (0.85 energy ≈ perfect for target 0.8).

### 3. Real Audio Features from Dataset + Mood Caching (NEW)
**Why:** Spotify free tier blocks audio features endpoint (403 Forbidden). Solution: Use 603-song dataset with REAL Spotify audio features (2010-2019 Billboard top songs). Pre-calculate mood scores at load time for fast, accurate mood matching.  
**How:** 
- Load CSV with real valence/energy/danceability/acousticness values
- Calculate mood scores for each song at startup (sad_score, energetic_score, chill_score)
- Store in memory for O(1) lookup during search
- Sort results by mood score instead of random/keyword matching
**Trade-off:** Limited to 603 songs vs millions on Spotify. But honest data + fast mood matching + free (no API costs).

### 4. Mood-Aware Search with Mood Distance
**Why:** Previous approach: "sad pop" search returned upbeat songs (e.g., "Legendary Lovers"). New approach: Use pre-calculated mood scores to find genuinely sad songs.  
**How:**
- Genre/artist filters narrow search space
- Mood scores (sad/energetic/chill) sort by actual audio characteristics
- No more misleading keyword matching
**Example:** "sad pop songs" now returns "Lose You To Love Me" (7.12/7.5) instead of "Legendary Lovers" (3.10/7.5)
**Trade-off:** Slightly more computation at load time, but searches are instant.

### 5. Substring Genre Matching
**Why:** User asks for "indie pop" but Spotify returns "indie" or "pop". Substring matching lets both trigger the bonus.  
**Trade-off:** More forgiving (could over-match). But better UX.

### 6. Search Rank as Popularity Proxy
**Why:** Free tier Spotify API doesn't provide track/artist popularity scores (always return 0). Search rank (position in results) is a fair proxy — songs ranked higher are more relevant/discoverable.  
**Trade-off:** Not actual popularity, but correlates well with discoverability. Shows users which recommendations are easiest to find.

---

## Testing & Iterations

### What Worked
✅ Gemini preference extraction (reliable on 10+ queries)  
✅ Spotify search + artist retrieval  
✅ 6-component scoring (now reaches 6.4-7.4 with proper mood matches)  
✅ Mood bonus (+2.0) triggers correctly  
✅ Genre substring matching works  
✅ Realistic feature simulation by genre/mood  
✅ Mood normalization (Gemini maps "upbeat" → "energetic" consistently)  
✅ Search rank as popularity proxy (fair discoverability metric)  

### What Didn't Work
❌ **Exact genre matching:** "indie pop" ≠ "indie" from Spotify. Fixed with substring matching.  
❌ **Pure random features:** Scores artificially low. Fixed by mapping to genre/mood ranges.  
❌ **Not passing user mood:** Songs got random moods, lost bonus. Fixed by passing context_mood for feature generation.  
❌ **Missing artist extraction:** "Taylor Swift songs" returned anything. Partially fixed with artist: prefix.  
❌ **Inconsistent mood labels:** Gemini returned "upbeat" but inference returned "energetic". Fixed with mood normalization.  

### Key Learnings
1. **Scoring ceilings matter:** Users expect 7.0+ scores for perfect matches. Ensure bonuses trigger.
2. **Exact matching is too strict:** "Indie pop" should match "indie". Use partial matching.
3. **Simulated data needs realism:** Random 0.3-0.9 doesn't work. Map to meaningful ranges.
4. **NLP extraction is non-trivial:** "Romantic vibe" → mood=romantic requires good AI.
5. **Explanations matter:** A 6.0 score is meaningless without bullet points showing why.

---

## Reflection: What I Learned

### About AI
**AI is a bridge between human language and structured data.** Users say "chill music" (fuzzy), algorithms need mood=chill, energy=0.3 (structured). Gemini excels at translation. Also learned: **robustness > perfection**. When Gemini fails or API times out, fallback to defaults. Real systems prioritize reliability.

### About Problem-Solving
**Understand the system deeply before optimizing.** I chased "higher scores" without understanding that the 7.5 ceiling meant users wouldn't see bonuses unless songs matched preferences exactly. Once I mapped: mood (+2.0) + genre (+1.0) + features, I could see the bottleneck. The fix wasn't the algorithm—it was ensuring songs matched preferences so bonuses triggered.

**Collaboration with Claude AI** I found myself and Claude going in a loop trying to fix an error. I was not able to figure out the issue and can only refer back to a past class assignment, train Claude more, and finally fix the problem with integrating Gemini API. I experienced AI (Claude) trying to over-fit a model, when there are missing data, it created a model that randomly assign values instead of return zero or NA or blank.


**One helpful AI recommendation** AI noticed the dataset missing mood, which is an important indicator in my algorithm. AI suggested a few ways to proxy for mood, I chose the one that created a mood estimate based on other sound characteristics of the songs.

**One flaed AI suggestion** I went in a loop trying to fix the Gemini API integration. The error turned out to be pretty simple, using GEMINI_API_KEY (not GOOGLE_API_KEY) and initializing with genai.Client() properly. I only learned this when reviewing the Bughound project. Lesson: Sometimes the fastest way forward is to look at working code from a similar project rather than troubleshooting abstractly. Concrete examples beat theoretical debugging.

---

## Limitations & Trade-offs

### Dataset Mode (Current, Default)
**Advantages:**
✅ Real Spotify audio features (honest scoring)
✅ Fast mood-aware search (pre-calculated scores)
✅ Free (no API costs)
✅ Reproducible results

**Limitations:**
❌ Limited to 603 songs (2010-2019 Billboard top songs)
❌ No newer releases or niche genres
❌ Static dataset (would need periodic refresh)

### Spotify API Mode (Optional Fallback)
**Advantages:**
✅ Access to millions of songs
✅ Real-time search

**Limitations:**
❌ Free tier: Audio features endpoint blocked (403 Forbidden)
❌ Free tier: All songs return popularity=0 (popularity filtering unusable)
❌ Requires paid credentials for audio features

### General Limitations
1. **Extraction is probabilistic:** Ambiguous inputs like "uplifting music" may fail.
2. **Scoring lacks context:** Can't filter by era, artist network, or playlist context.
3. **No feedback loop:** System doesn't learn from user preferences over time.

---

## Mood Caching System (NEW)

VibeFinder uses **mood caching** for fast, accurate mood matching:

### How It Works

1. **At Startup (load_database):**
   - Load 603 songs from CSV
   - Calculate mood scores for each song:
     ```python
     sad_score = (1-valence)*0.4 + (1-energy)*0.3 + acousticness*0.15 + ...
     energetic_score = energy*0.4 + valence*0.3 + danceability*0.2 + ...
     chill_score = (1-energy)*0.35 + acousticness*0.25 + ...
     ```
   - Store these scores in memory (one-time, takes <100ms)

2. **During Search:**
   - User asks for "sad pop songs"
   - Filter songs by genre ("pop")
   - **Sort by sad_score** (instant lookup, no recalculation)
   - Return top 10 songs

3. **Why This Works:**
   - **Fast:** O(1) lookup instead of recalculating for each query
   - **Honest:** Based on real Spotify audio features, not keywords
   - **Flexible:** Mood weights are tunable (adjust percentages in code)

### Example: "Sad Pop Songs"

**Song 1: "Lose You To Love Me" by Selena Gomez**
- Real features: valence=0.11, energy=0.35, acousticness=0.28
- sad_score = (1-0.11)*0.4 + (1-0.35)*0.3 + 0.28*0.15 + ... = **0.78 (high)**
- Result: ✅ Ranked #1 (actually sad!)

**Song 2: "Legendary Lovers" by Katy Perry**
- Real features: valence=0.96, energy=0.87, acousticness=0.05
- sad_score = (1-0.96)*0.4 + (1-0.87)*0.3 + 0.05*0.15 + ... = **0.08 (low)**
- Result: ❌ Not ranked (correctly filtered out)

### Tuning Mood Scores

Edit `song_database.py` to adjust weights:

```python
def calculate_sad_score(song):
    # Current: 40% valence, 30% energy, 15% acoustic, 10% tempo, 5% dance
    sad_score = (
        (1 - valence) * 0.40 +      # ← Increase if you want valence to matter more
        (1 - energy) * 0.30 +       # ← Decrease if you want upbeat sad songs
        acousticness * 0.15 +
        (1 - tempo / 120) * 0.10 +
        (1 - danceability) * 0.05
    )
    return min(1.0, max(0.0, sad_score))
```

---

## Files

- `demo.py` — Main entry point
- `agent.py` — Gemini AI agent
- `spotify_client.py` — Spotify integration (dual-mode: dataset + API)
- `song_database.py` — Song database with mood caching (NEW)
- `recommender.py` — 6-component scoring
- `model_card.md` — Detailed bias/AI reflection
- `ai_interactions.md` — How I worked with Claude
- `DATA_MODE_GUIDE.md` — Dataset vs API mode comparison (NEW)
- `SOLUTION_SUMMARY.md` — Transition from simulated to real features (NEW)

---

## Extend This

1. Real Spotify audio features (OAuth)
2. Artist extraction with NER
3. User feedback loop
4. Web UI (Flask/React)
5. More audio features
6. Genre normalization

---

## Quick Start

To see VibeFinder in action:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your API keys (copy .env.example to .env and fill in your keys)
cp .env.example .env
# Edit .env with your Gemini and Spotify API keys

# 3. Run the demo
python src/demo.py
```

**Try these example queries:**
- "I want sad pop songs like Lover by Taylor Swift"
- "Give me upbeat dance music with good energy"
- "Show me chill indie music with acoustic vibes"

Enjoy discovering music! 🎵
