"""
Core logic for the Music Recommender Simulation.

There are two ways to use the recommender in this file:

1. An object oriented version (the ``Song``, ``UserProfile`` and
   ``Recommender`` classes) that the tests in
   ``tests/test_recommender.py`` use.
2. A plain-dictionary version (``load_songs``, ``score_song`` and
   ``recommend_songs``) that ``src/main.py`` uses to run from the
   command line.

Both versions share the exact same scoring rule, which lives in the
private ``_score`` helper, so they always agree with each other.
"""

from typing import List, Dict, Tuple, Union
from dataclasses import dataclass
import csv


# ---------------------------------------------------------------------------
# Scoring weights (my "Algorithm Recipe")
# ---------------------------------------------------------------------------
# These numbers decide how much each kind of match matters. Keeping them
# as named constants up here makes it easy to run experiments by changing
# a single value instead of hunting through the code.
GENRE_WEIGHT = 2.0      # exact genre match
MOOD_WEIGHT = 1.0       # exact mood match
ENERGY_WEIGHT = 1.5     # how close the song's energy is to what the user wants
ACOUSTIC_WEIGHT = 0.5   # small bonus when an acoustic-loving user gets an acoustic song
ACOUSTIC_THRESHOLD = 0.6  # a song counts as "acoustic" at or above this value


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _field(song: Union[Song, Dict], name: str):
    """Read an attribute from either a Song object or a plain dict.

    This lets the two sides of the code (class based and dict based)
    reuse one scoring function without caring which type they hold.
    """
    if isinstance(song, dict):
        return song[name]
    return getattr(song, name)


def _score(
    genre_pref: str,
    mood_pref: str,
    energy_pref: float,
    likes_acoustic: bool,
    song: Union[Song, Dict],
) -> Tuple[float, List[str]]:
    """The one scoring rule used by everything in this file.

    Returns a tuple of ``(score, reasons)`` where ``reasons`` is a list
    of short human readable strings explaining where the points came
    from. Higher scores mean a better match.

    The recipe:
      * +2.0 if the song's genre is the user's favorite genre.
      * +1.0 if the song's mood is the user's favorite mood.
      * up to +1.5 for how close the song's energy is to the user's
        target energy (identical energy earns the full 1.5, and the
        bonus shrinks as the gap grows).
      * +0.5 if the user likes acoustic music and this song is acoustic.
    """
    score = 0.0
    reasons: List[str] = []

    # Genre: a big, exact-match bonus. Genre is the strongest signal of
    # taste, so it is weighted the most.
    if genre_pref and _field(song, "genre") == genre_pref:
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {genre_pref} (+{GENRE_WEIGHT:.1f})")

    # Mood: a smaller exact-match bonus.
    if mood_pref and _field(song, "mood") == mood_pref:
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {mood_pref} (+{MOOD_WEIGHT:.1f})")

    # Energy: a similarity score instead of an exact match. Energy is a
    # number from 0 to 1, so the gap between the song and the target is
    # also between 0 and 1. (1 - gap) turns "small gap" into "big bonus".
    if energy_pref is not None:
        gap = abs(float(_field(song, "energy")) - float(energy_pref))
        energy_points = round((1 - gap) * ENERGY_WEIGHT, 2)
        score += energy_points
        reasons.append(
            f"energy fits (gap {gap:.2f}, {energy_points:+.2f})"
        )

    # Acoustic: a gentle nudge for users who said they like acoustic
    # music, only when the song is genuinely acoustic.
    if likes_acoustic and float(_field(song, "acousticness")) >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_WEIGHT
        reasons.append(f"acoustic vibe (+{ACOUSTIC_WEIGHT:.1f})")

    return round(score, 2), reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one Song for one UserProfile using the shared rule."""
        return _score(
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            user.likes_acoustic,
            song,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top ``k`` songs for this user, best match first."""
        ranked = sorted(
            self.songs,
            key=lambda song: self._score_song(user, song)[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a sentence explaining why a song fits (or does not)."""
        score, reasons = self._score_song(user, song)
        if not reasons:
            return f"{song.title} scored {score:.2f} (no strong matches to your profile)."
        return f"{song.title} scored {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py

    Each row becomes a dictionary. The text columns stay as strings and
    the number columns are converted to ``int`` or ``float`` so the
    scoring math works.
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(float(row["tempo_bpm"]))
            for field in ("energy", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    ``user_prefs`` is a dict that must have "genre", "mood" and "energy"
    keys, and may optionally include "likes_acoustic". Returns
    ``(score, reasons)``.
    """
    return _score(
        user_prefs.get("genre"),
        user_prefs.get("mood"),
        user_prefs.get("energy"),
        user_prefs.get("likes_acoustic", False),
        song,
    )


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Scores every song, sorts them from best to worst, and returns the
    top ``k`` as ``(song_dict, score, explanation)`` tuples.
    """
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no strong matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
