# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender that matches songs
to a user's stated taste profile.

---

## 2. Intended Use

VibeFinder is a classroom project for learning how recommender systems
turn data into predictions. It takes a user's favorite genre, favorite
mood, target energy level, and whether they like acoustic music, and
returns a short ranked list of songs that fit, each with a reason.

It assumes the user can describe their taste in those four simple terms,
and that a good recommendation is one that matches genre and mood while
sitting near the user's desired energy. It is **not** meant for real
listeners or production use — the catalog is tiny and the audio features
are made up — but the logic mirrors how a real content-based recommender
behaves.

---

## 3. How the Model Works

Think of it like a scorecard. For every song, the model hands out points:
2 points if the song's genre is your favorite, 1 point if its mood matches
yours, up to 1.5 points depending on how close the song's energy is to the
energy you asked for, and a small half-point if you like acoustic music
and the song is acoustic. Then it sorts all the songs by their total and
hands you the top few.

The one clever part is energy. Instead of asking "is this song's energy
*exactly* what you wanted?" it measures how far off it is and gives more
points the closer it is. That way a song that is *almost* the right energy
still gets credit.

Compared to the starter code, which just returned the first few songs
unchanged, I wrote the actual scoring, the ranking, the CSV loading, and
the explanations, and I made the class version and the function version
share one scoring helper so they always agree.

---

## 4. Data

The catalog is a CSV of **22 songs** that I created. Each song has a genre,
a mood, and five numeric features (energy, tempo, valence, danceability,
acousticness).

- **Genres represented:** pop, indie pop, lofi, rock, metal, hip hop,
  jazz, r&b, country, ambient, synthwave.
- **Moods represented:** happy, chill, intense, relaxed, focused, moody,
  romantic.

I expanded the starter catalog from 10 to 22 songs and deliberately added
genres and moods (hip hop, r&b, country, metal, romantic) that were
missing, so I could test the recommender on very different users.

**What's missing:** the numbers are invented rather than measured from
real audio; there is no information about language, lyrics, release year,
or artist popularity; and many genres still have only one or two songs, so
the catalog is far from a fair sample of real musical taste.

---

## 5. Strengths

- **Clear, "obvious" users work great.** For the High-Energy Pop, Chill
  Lofi, and Deep Intense Rock profiles, the #1 pick is exactly the song I
  would have chosen by hand, and the reasons line up.
- **Energy similarity behaves sensibly.** Among songs of the same genre,
  the ones nearest the user's target energy rise to the top, which matches
  intuition ("I want pop, but *calm* pop").
- **Transparent.** Every recommendation explains itself, so it is easy to
  see why a song was picked and to spot when the logic does something odd.
- **The acoustic flag acts as a gentle tie-breaker** rather than
  overpowering the main signals, which is the behavior I wanted.

---

## 6. Limitations and Bias

- **Features it ignores:** valence, danceability, and tempo are stored but
  not scored; the model also ignores popularity, novelty, and anything
  about the lyrics or language.
- **Exact-match genre/mood:** "indie pop" and "pop" count as unrelated, so
  a pop fan never gets credit for a near-neighbor genre. The model has no
  concept of genres being similar.
- **Underrepresented genres lose by default:** genres with only one song
  (metal, synthwave, country) can almost never fill a top-5, so a fan of
  those genres gets a worse experience purely because of my dataset, not
  because of their taste.
- **Overfitting to one preference:** because genre is worth the most
  points, a user with a strong favorite genre can get an all-one-genre top
  5 with little variety — a small version of the "filter bubble" problem.
- **Made-up data:** since I assigned the audio features myself, any bias in
  how I rated songs is baked straight into the recommendations.

---

## 7. Evaluation

I evaluated VibeFinder by running three contrasting user profiles and
reading the results, plus automated tests.

- **Profiles tested:** High-Energy Pop (pop / happy / 0.85), Chill Lofi
  (lofi / chill / 0.35 / likes acoustic), and Deep Intense Rock (rock /
  intense / 0.95).
- **What I looked for:** does the #1 pick make sense, are the three lists
  actually different from each other, and do the "because…" reasons match
  the scores?
- **What surprised me:** lowering the genre weight from 2.0 to 0.5 changed
  the pop user's list in a very visible way — an off-mood pop song dropped
  out and a *country* song climbed in. It made the genre weight feel like a
  real "how adventurous" dial rather than an abstract number.
- **Automated tests:** six `pytest` tests check that recommendations come
  back sorted, that a perfect match earns the full 4.5 points with three
  reasons, that closer energy scores higher, that the loader converts
  numeric columns, and that `k` is respected. All six pass.

---

## 8. Future Work

- **Genre similarity instead of exact match**, so "indie pop" gives
  partial credit to a pop fan.
- **Use more of the features** — fold valence and danceability into the
  score, probably as more similarity terms like the energy one.
- **Encourage diversity** in the top results, for example by not letting a
  single genre take every slot.
- **Richer explanations**, such as "because you liked calmer pop" phrased
  in plain language rather than point values.
- **A bigger, more balanced catalog** with real audio features so each
  genre has a fair shot.

---

## 9. Personal Reflection

The biggest thing I learned is that a recommender is mostly just a scoring
rule plus a sort — the "AI" feeling comes from how the weights are tuned,
not from anything mysterious. Writing the explanations was the most useful
part, because it forced the system to show its work and made it obvious
when a song was ranking for a weird reason.

What surprised me was how much the *data* mattered compared to the formula:
a genre with only one song basically can't win, no matter how good my math
is. That changed how I think about real music apps — when a playlist feels
repetitive or keeps missing a genre I like, it might not be a bad algorithm
so much as an imbalance in what the system was given to choose from.
