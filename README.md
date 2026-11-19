# 🎵 Music Recommender Simulation

## Project Summary

This is a small, content-based music recommender. It stores a catalog of
songs and a user "taste profile" as plain data, scores every song against
that profile with a simple rule I designed, and returns the highest
scoring songs along with a short explanation of *why* each one was picked.

My version, **VibeFinder 1.0**, works on a catalog of 22 songs spread
across genres like pop, lofi, rock, hip hop, jazz, r&b, country and metal.
It recommends songs by rewarding genre and mood matches and by favoring
songs whose energy is close to what the user is in the mood for. Because
every recommendation comes with its reasons, you can always see what the
system was "thinking."

---

## How The System Works

The whole idea is: **turn taste into numbers, then rank by the numbers.**

**What each `Song` stores.** Every song has a genre, a mood, and four
numeric "audio features" between 0 and 1: energy, valence (how positive it
sounds), danceability, and acousticness, plus a tempo in BPM. My scoring
rule uses genre, mood, energy, and acousticness.

**What the `UserProfile` stores.** A user has a favorite genre, a favorite
mood, a target energy level (0 = very calm, 1 = very intense), and a
yes/no flag for whether they like acoustic music.

**How a score is computed (my Algorithm Recipe).** For each song I add up
points:

- **+2.0** if the song's genre is the user's favorite genre.
- **+1.0** if the song's mood is the user's favorite mood.
- **up to +1.5** for energy *closeness*. I take the gap between the song's
  energy and the user's target energy, and award `(1 - gap) × 1.5`. A
  perfect energy match earns the full 1.5; the bonus shrinks as the gap
  grows.
- **+0.5** if the user likes acoustic music *and* the song is actually
  acoustic (acousticness ≥ 0.6).

Genre is weighted the most because it is the strongest signal of taste.
Energy is a *similarity* score instead of an exact match, because "I want
something around this energy" is more realistic than "I want exactly
0.8."

**How songs are chosen.** I score every song, sort them from highest to
lowest, and return the top `k` (default 5). Each recommendation carries
the list of reasons it earned points, which becomes the "because…" line.

The same rule lives in one helper function and is shared by both the
class-based `Recommender` (used by the tests) and the dictionary-based
`recommend_songs` (used by the command line app), so the two can never
disagree.

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
plus four I added for the scoring rule, energy similarity, and CSV
loading.

---

## Sample Recommendation Output

This is the real output of `python -m src.main` (trimmed to two of the
three profiles):

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
energy=0.95), correctly puts *Storm Runner* (rock/intense) at the top with
a score of 4.44.

---

## Experiments You Tried

**1. Changing the genre weight from 2.0 to 0.5.**
With genre weighted at 2.0, the High-Energy Pop user's top 5 is dominated
by pop and indie-pop songs, and *Gym Hero* (a pop song, but with an
*intense* mood) makes the list purely on its genre and energy. When I drop
the genre weight to 0.5, *Gym Hero* falls out of the top 5 and *Open
Highway* (a **country** song that is happy and mid-energy) climbs in. So
the genre weight is basically a "how strict about genre" dial: high means
"stay in my lane," low means "surprise me with other genres that still fit
my mood and energy."

**2. The acoustic bonus.**
Turning on `likes_acoustic` for the Chill Lofi user pushes acoustic songs
(*Library Rain*, *Midnight Coding*) above non-acoustic ones with otherwise
similar scores. It is a small +0.5, so it acts as a tie-breaker rather
than something that overrides genre or mood.

**3. Very different users get very different lists.**
Running all three profiles shows the recommender is actually responding to
the profile and not just returning popular songs: the pop user, the lofi
user, and the rock user share almost no songs in their top 5.

---

## Limitations and Risks

- **Tiny catalog.** With only 22 songs, there often are not many true
  genre matches, so lower-ranked recommendations lean heavily on energy.
- **Exact-match genre and mood.** "indie pop" and "pop" are treated as
  completely different genres, even though a pop fan would probably enjoy
  both. The system has no idea that some genres are neighbors.
- **No understanding of the actual music.** It never hears a note or reads
  a lyric; it only trusts the numbers in the CSV, which I made up.
- **Popularity and novelty are ignored.** It cannot recommend something
  genuinely new to you, and it has no sense of what is popular.
- **Can over-favor one preference.** Because genre is worth the most
  points, a user with a strong favorite genre can get a top 5 that is all
  one genre, which is not very diverse.

I go deeper on these in the model card.

---

## Reflection

Building this made the idea of a recommender feel a lot less magical and a
lot more like bookkeeping. At its core, the system just assigns points and
sorts — the "intelligence" is entirely in the scoring rule I chose, and
every weight I picked is a value judgment about what matters more. Deciding
that genre is worth 2.0 and mood only 1.0 is not a neutral fact about
music; it is my opinion baked into math, and it visibly changes whose
songs win.

That is also where I can see bias creeping into real systems. If my catalog
had very few songs of a certain genre, that genre would almost never win,
no matter how much a user liked it — the data shapes the output as much as
the formula does. And because the model rewards "more of what you already
like," it naturally narrows what people see over time instead of broadening
it. Seeing that happen on 22 songs made it easy to imagine how a system
trained on millions could quietly push everyone deeper into their own
bubble.
