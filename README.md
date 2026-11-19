# 🎵 Music Recommender Simulation

## Project Summary

This is a small **content-based** music recommender. It represents a catalog
of songs and a user "taste profile" as structured data, scores every song
against that profile with a linear weighted scoring function I designed, and
returns the top-ranked songs together with a human-readable explanation of
*why* each one was selected.

My version, **VibeFinder 1.0**, runs on a catalog of 22 songs across genres
like pop, lofi, rock, hip hop, jazz, r&b, country and metal. It ranks songs
by rewarding genre and mood matches and by favoring songs whose energy is
close to the user's target. Every recommendation ships with its scoring
rationale, so the model is fully interpretable rather than a black box.

---

## How The System Works

Answering the prompt questions directly.

**What features does each `Song` use in your system?**
Each `Song` carries two categorical features — `genre` and `mood` — and five
numeric audio features: `energy`, `valence`, `danceability`, `acousticness`
(all normalized to [0, 1]) and `tempo_bpm`. The scoring function consumes
`genre`, `mood`, `energy`, and `acousticness`. `tempo_bpm`, `valence`, and
`danceability` are carried in the schema but not yet weighted — deferred to
future work (see below) because they need rescaling or overlap with existing
signals.

**What information does your `UserProfile` store?**
Four fields: `favorite_genre`, `favorite_mood`, `target_energy` (a scalar in
[0, 1], 0 = calm → 1 = intense), and a boolean `likes_acoustic`. It is a
deliberately low-dimensional representation of taste, which keeps the model
easy to reason about and explain.

**How does your `Recommender` compute a score for each song? (Algorithm Recipe)**
The score is a weighted sum of four terms:

- **+2.0** if `song.genre == user.favorite_genre` (exact categorical match).
- **+1.0** if `song.mood == user.favorite_mood` (exact categorical match).
- **up to +1.5** for energy proximity. Since both values are in [0, 1], the
  absolute gap is also in [0, 1], so I award `(1 - gap) × 1.5` — a bounded
  similarity term that peaks at an exact energy match and decays linearly.
- **+0.5** if `likes_acoustic` is true **and** `acousticness ≥ 0.6`.

Genre carries the largest weight because it is the dominant signal of taste;
mood is secondary; energy is modeled as a graded similarity rather than a
hard equality because "around this energy" reflects real listening intent
better than exact-match. The weights are hoisted into named module-level
constants so they're a single point of control for experiments.

**How do you choose which songs to recommend?**
Score the full catalog, sort descending by score, return the top `k`
(default 5). Ties fall back to stable sort order. Each result carries the
list of reason strings that produced its score, which becomes the "because…"
line — the model is self-explaining by construction.

The categorical/OOP path (`Recommender`, used by the tests) and the
dict/functional path (`recommend_songs`, used by the CLI) both delegate to a
single private `_score` helper, so the two interfaces are guaranteed
consistent rather than two implementations that can drift apart.

```
UserProfile ─┐
             ├──> _score() ──> (score, reasons) ──> sort desc ──> top k
   Song    ─┘        │
                     ├─ +2.0 genre match
                     ├─ +1.0 mood match
                     ├─ up to +1.5 energy proximity  (1 - |Δenergy|) × 1.5
                     └─ +0.5 acoustic bonus (gated on user preference)
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the tests with:

```bash
pytest
```

There are six tests in `tests/test_recommender.py`: the two starter tests
plus four I added covering the scoring function, energy proximity, and CSV
loading/type coercion.

---

## Sample Recommendation Output

Real output of `python -m src.main` (trimmed to two of the three profiles):

```
Loaded 22 songs from the catalog.

============================================================
Profile: High-Energy Pop
  wants genre=pop, mood=happy, energy=0.85, likes_acoustic=False
------------------------------------------------------------
1. Sunrise City by Neon Echo  (score 4.46)
   because: genre match: pop (+2.0); mood match: happy (+1.0); energy fits (gap 0.03, +1.46)
2. Pop Quiz by Max Pulse  (score 4.41)
   because: genre match: pop (+2.0); mood match: happy (+1.0); energy fits (gap 0.06, +1.41)
3. Gym Hero by Max Pulse  (score 3.38)
   because: genre match: pop (+2.0); energy fits (gap 0.08, +1.38)
4. Rooftop Lights by Indigo Parade  (score 2.36)
   because: mood match: happy (+1.0); energy fits (gap 0.09, +1.36)
5. Paper Planes Again by Indigo Parade  (score 2.25)
   because: mood match: happy (+1.0); energy fits (gap 0.17, +1.25)

============================================================
Profile: Chill Lofi
  wants genre=lofi, mood=chill, energy=0.35, likes_acoustic=True
------------------------------------------------------------
1. Library Rain by Paper Lanterns  (score 5.00)
   because: genre match: lofi (+2.0); mood match: chill (+1.0); energy fits (gap 0.00, +1.50); acoustic vibe (+0.5)
2. Midnight Coding by LoRoom  (score 4.90)
   because: genre match: lofi (+2.0); mood match: chill (+1.0); energy fits (gap 0.07, +1.40); acoustic vibe (+0.5)
3. Focus Flow by LoRoom  (score 3.92)
   because: genre match: lofi (+2.0); energy fits (gap 0.05, +1.42); acoustic vibe (+0.5)
4. Spacewalk Thoughts by Orbit Bloom  (score 2.90)
   because: mood match: chill (+1.0); energy fits (gap 0.07, +1.40); acoustic vibe (+0.5)
5. Coffee Shop Stories by Slow Stereo  (score 1.97)
   because: energy fits (gap 0.02, +1.47); acoustic vibe (+0.5)
```

The third profile, **Deep Intense Rock** (genre=rock, mood=intense,
energy=0.95), correctly ranks *Storm Runner* (rock/intense) first at 4.44.

---

## Experiments You Tried

**What happened when you changed the weight on genre from 2.0 to 0.5?**
At `GENRE_WEIGHT = 2.0`, the High-Energy Pop user's top 5 is saturated with
pop and indie-pop, and *Gym Hero* (pop, but `mood=intense`) still makes the
cut on genre + energy alone. Dropping the weight to 0.5 shifts the ranking:
*Gym Hero* drops out and *Open Highway* (a **country** track that is happy
and mid-energy) moves in. Concretely, the genre term is a precision/recall
knob — a high weight biases toward intra-genre precision ("stay in my lane"),
a low weight increases cross-genre recall ("surface adjacent genres that
still fit mood and energy"). This is the classic exploration/exploitation
trade-off in miniature.

**What happened when you added tempo or valence to the score?**
I prototyped both and intentionally excluded them from the final recipe.
`tempo_bpm` lives on a ~60–170 scale, so without feature scaling it would
dominate the [0, 1] terms and effectively reduce the model to a tempo sort —
it needs min-max normalization before it's usable. `valence` is strongly
collinear with `mood`, so adding it mostly double-counted the mood signal
rather than contributing independent information. Keeping the feature set to
genre + mood + energy + acousticness preserved interpretability and avoided
redundant terms, so I logged both as future work.

**How did your system behave for different types of users?**
Across the three profiles the top-5 lists are nearly disjoint, which
confirms the model is conditioning on the profile rather than collapsing to a
popularity prior. The `likes_acoustic` flag also measurably shifts ranking
for the lofi user — enabling it promotes acoustic tracks above otherwise
comparable non-acoustic ones. Because it contributes only +0.5, it functions
as a tie-breaker and never overrides the genre or mood terms, which is the
intended behavior.

---

## Limitations and Risks

- **Small catalog / cold-start.** With only 22 songs there are few true genre
  matches, so lower ranks lean disproportionately on the energy term.
- **Exact-match categoricals.** "indie pop" and "pop" are distinct tokens, so
  the model gets no notion of genre adjacency or similarity.
- **No audio/NLP understanding.** It never processes waveforms or lyrics; it
  trusts hand-authored feature values in the CSV.
- **No popularity or novelty signal**, so it can't surface genuinely new
  material or weight by what's trending.
- **Popularity/overfitting bias.** Because genre is the heaviest term, a user
  with a strong genre preference can receive a homogeneous top 5 — a
  small-scale instance of the filter-bubble / feedback-loop problem.

The model card expands on the bias analysis.

---

## Reflection

**What did you learn about how recommenders turn data into predictions?**
The core realization is that a content-based recommender is, mechanically,
just a scoring function plus a sort — the "intelligence" is entirely encoded
in the weights, and every weight is a design decision rather than an
objective fact. Setting genre to 2.0 and mood to 1.0 is a value judgment that
directly determines which songs win, and I could watch the ranking change as
I tuned it. Building the explanation strings alongside the score was the most
valuable part: making the model self-explaining turned debugging into reading
a sentence instead of reverse-engineering a number.

**What did you learn about where bias or unfairness could show up in systems like this?**
Bias enters from two independent sources: the scoring function and the
training/catalog distribution. An underrepresented genre essentially cannot
win regardless of a user's stated preference, so a skewed dataset produces
unfair outcomes even with a "correct" formula — data imbalance is as decisive
as the model itself. And because the objective rewards similarity to existing
preferences, repeated use induces a feedback loop that narrows exposure over
time. Observing that dynamic on a 22-song toy catalog made it concrete how a
production system trained on millions of interactions can systematically
reinforce filter bubbles.
