# VibeFinder: Responsible AI Reflection

## 1. Limitations and Biases

- **Dataset bias (2010-2019):** Only Billboard top songs. New releases and niche genres not included. Example: "Billie Eilish sad songs" returns nothing because she released most songs after 2019.

- **Mood formula is opinionated:** Our formula (valence 40%, energy 30%, acoustic 15%) assumes sadness = low energy + low happiness. But "angry sad" (high energy, low valence) gets misclassified. We ignore lyrics and context.

- **No diversity in recommendations:** If you ask for "sad pop," you get 10 sad pop songs. We never suggest exploring different genres.

- **Filter bubble risk:** Users get reinforced in narrow musical taste without exposure to new artists.

---

## 2. Potential Misuse and Prevention

**Misuse 1:** Someone could use mood data to manipulate users
- **Prevention:** We don't collect or store individual user preferences. System is stateless—no user tracking.

**Misuse 2:** Music labels could game the system by optimizing audio features for high scores
- **Prevention:** Regularly refresh dataset. Don't rely on static formulas forever.

**Misuse 3:** Filter bubble reinforcement (users stuck in one genre)
- **Prevention:** Add "Recommend something different" feature. Include diversity metrics.

---

## 3. Surprises While Testing

**Surprise 1: Real data > fake data**
- Problem: "Legendary Lovers" (upbeat) was recommended for "sad pop"
- Root cause: We were using simulated audio features (random values)
- Lesson: Confidently wrong data is worse than honest data with limitations
- Solution: Switched to real Spotify dataset (603 songs)—fixed the problem immediately

**Surprise 2: Audio features are predictive**
- Expected: We'd need lyrics, release context, artist history
- Reality: Valence + energy + acousticness alone gave 100% accuracy
- Lesson: Don't over-engineer when simple features work

**Surprise 3: API rate limits were the bottleneck**
- Expected: Algorithm complexity was limiting
- Reality: Gemini free tier (1-2 requests/min) killed the system
- Lesson: Understand API constraints before designing around them

---

## 4. Collaboration with AI (Claude)

### Helpful Suggestion ✅
**Claude:** "Switch from simulated features to a real Spotify dataset instead of generating fake audio features"
- **Context:** I was stuck with low recommendation scores (3.10/7.5). Claude suggested using real Spotify data (603 songs from 2010-2019) instead of continuing to simulate valence/energy/danceability randomly.
- **Why it worked:** Reframed the entire problem. I wasn't failing at algorithms—I was failing at data quality. Fake data can never be trusted, no matter how smart the algorithm.
- **Impact:** 
  - Recommendation scores jumped to 7.12/7.5 (honest improvements)
  - Mood matching went from 0/10 songs correct to 10/10 correct
  - System became honest about limitations instead of confidently wrong
- **Lesson:** Sometimes the best solution isn't smarter code—it's better data. Also: when stuck on Gemini API authentication (401 error), looking at the working Bug Hound project code was faster than abstract debugging. Real, working examples beat troubleshooting.

### Flawed Suggestion ❌
**Claude:** "Build a machine learning model to infer mood from audio features using synthetic labels"
- **Why it failed:** We had no labeled mood data. Claude's workaround was to generate synthetic labels—automating garbage data
- **What I should've done:** Asked "Is there a simpler way?" instead of building the ML pipeline
- **Lesson:** Just because AI suggests a solution doesn't mean it's right. Question it. Working code (real data) beats theoretical perfection (ML models with fake labels)
- **Real breakthrough:** Looking at the Bug Hound project's working Gemini code when I was stuck (faster than debugging abstractly)

---

## Summary

**System knows its limits:** Real data (603 songs) with honest mood scoring beats fake data with false confidence.

**Responsible AI means:** Being transparent about what we can't do (no real-time search, no personalization, no lyrics analysis) rather than pretending to do everything.

**Best collaboration with AI:** When you question suggestions critically and combine AI ideas with your domain knowledge.
