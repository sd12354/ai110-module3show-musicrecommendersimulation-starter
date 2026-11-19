"""
Command line runner for the Music Recommender Simulation.

Run it from the project root with:

    python -m src.main

It loads the song catalog and prints the top recommendations for a few
different user profiles so you can see how the recommender reacts to
very different tastes.
"""

from src.recommender import load_songs, recommend_songs


# A few example users with clearly different tastes. The keys here match
# what score_song expects: "genre", "mood", "energy" and the optional
# "likes_acoustic".
PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "likes_acoustic": False,
    },
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print one profile's top ``k`` recommendations in a readable block."""
    print("=" * 60)
    print(f"Profile: {name}")
    print(
        f"  wants genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']}, likes_acoustic={user_prefs.get('likes_acoustic', False)}"
    )
    print("-" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=k)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  (score {score:.2f})")
        print(f"   because: {explanation}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs from the catalog.\n")

    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs, k=5)


if __name__ == "__main__":
    main()
