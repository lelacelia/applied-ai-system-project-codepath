# 🎵 VibeFinder: System Architecture & Design Plan

## Vision

Build an end-to-end music recommendation system that converts natural language preferences into personalized song recommendations using AI and a scoring algorithm.

---

## High-Level Architecture

```
User Input (Natural Language)
    ↓
AI Agent (Extract Preferences)
    ↓
Song Retrieval (Search for matching songs)
    ↓
Recommender Scoring (Rank by fit)
    ↓
Top 5 Recommendations with Explanations
```

---

## Component Design

### 1. User Input Layer
- Accept natural language: "sad pop songs", "chill indie music"
- No structured forms - conversational UX

### 2. AI Agent (NLP)
- Extract mood, genre, audio preferences from text
- Normalize to standard format
- Use Gemini or Claude for understanding context

**Output:**
```json
{
  "mood": "sad",
  "genre": "pop",
  "energy": 0.3,
  "valence": 0.2,
  "danceability": 0.5,
  "acousticness": 0.4
}
```

### 3. Song Retrieval
**Options:**
- Use Spotify API (live data, millions of songs)
- Use local dataset (pre-built, limited but reliable)

### 4. Recommender Scoring
**6-Component Algorithm:**
- Mood match (+2.0)
- Genre match (+1.0)
- Audio feature similarity (Gaussian curves)

**Max Score:** 7.5

### 5. Output Ranking
- Sort by score
- Display top 5 with explanations
- Show why each song was recommended

---

## Key Design Decisions

| Decision | Options | Chosen | Why |
|----------|---------|--------|-----|
| **AI Model** | Gemini / Claude / Rules | TBD | Natural language understanding |
| **Song Data** | Spotify API / Local Dataset | TBD | Real data vs curated selection |
| **Audio Features** | Real / Simulated | TBD | Accuracy vs API limits |
| **Scoring** | Binary / Gaussian | Gaussian | Smooth matching |

---

## Implementation Plan

### Phase 1: Setup
- [ ] Project structure
- [ ] Dependencies (Gemini/Spotify SDKs)
- [ ] Environment variables

### Phase 2: AI Agent
- [ ] Implement NLP preference extraction
- [ ] Test with 5+ queries
- [ ] Normalize moods to standard set

### Phase 3: Song Retrieval
- [ ] Connect to data source
- [ ] Implement search function
- [ ] Handle edge cases (no results, API limits)

### Phase 4: Recommender
- [ ] Implement scoring algorithm
- [ ] Test with unit tests
- [ ] Validate scoring range (0-7.5)

### Phase 5: Integration & Demo
- [ ] Connect all components
- [ ] Build CLI/UI
- [ ] Test end-to-end

### Phase 6: Evaluation
- [ ] Unit tests (7+)
- [ ] Human evaluation (5+ real queries)
- [ ] Error handling tests

---

## Success Criteria

- ✅ System runs end-to-end without crashes
- ✅ Recommendations match user preferences (human eval)
- ✅ All tests passing (unit + integration)
- ✅ Clear explanations for each recommendation
- ✅ Handles edge cases gracefully

---

## Open Questions (To Explore)

1. Which AI model is best for mood extraction?
2. Should we use Spotify API or pre-built dataset?
3. How accurate are audio features from free-tier APIs?
4. What's the optimal scoring formula?
5. How do we handle "no results" cases?

---

## Notes

- Focus on honest recommendations over confident guesses
- Real data > simulated data
- Simple solutions often beat complex ones
- Document decisions as we go
