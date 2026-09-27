from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import random
import os

app = Flask(__name__)
app.secret_key = "soundle-secret-key"


# -----------------------------
# LOAD ARTISTS
# -----------------------------

def load_artists():
    path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "artists.json"
    )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def find_artist(name):
    artists = load_artists()

    for artist in artists:
        if artist["name"].lower() == name.lower():
            return artist

    return None


# -----------------------------
# HOME / FIRST PAGE
# -----------------------------

@app.route("/")
def home():

    artists = load_artists()

    # Only choose a new artist when starting a new game
    mystery_artist = random.choice(artists)

    session["answer"] = mystery_artist["name"]
    session["guesses"] = []

    # Random hint from that artist
    hint = random.choice(mystery_artist["hints"])

    return render_template(
        "index.html",
        hint=hint
    )


# -----------------------------
# FIRST GUESS
# -----------------------------

@app.route("/first-guess", methods=["POST"])
def first_guess():

    guess = request.form.get("artist", "").strip()

    if not guess:
        return redirect(url_for("home"))

    artist = find_artist(guess)

    if artist is None:
        return redirect(url_for("home"))

    session["guesses"] = [artist["name"]]

    # CORRECT ON FIRST GUESS
    if artist["name"].lower() == session["answer"].lower():

        session["score"] = 100

        return redirect(url_for("result"))

    # WRONG → GAME PAGE
    return redirect(url_for("game"))


# -----------------------------
# GAME PAGE
# -----------------------------

@app.route("/game")
def game():

    if "answer" not in session:
        return redirect(url_for("home"))

    answer = find_artist(session["answer"])

    guess_data = []

    for guess_name in session.get("guesses", []):

        guessed_artist = find_artist(guess_name)

        if guessed_artist:

            comparison = compare_artists(
                guessed_artist,
                answer
            )

            guess_data.append({
                "artist": guessed_artist,
                "comparison": comparison
            })

    attempts = len(session.get("guesses", []))

    attempts_left = 5 - attempts

    return render_template(
        "game.html",
        guesses=guess_data,
        attempts_left=attempts_left
    )


# -----------------------------
# NEXT GUESS
# -----------------------------

@app.route("/guess", methods=["POST"])
def make_guess():

    guess = request.form.get("artist", "").strip()

    if not guess:
        return redirect(url_for("game"))

    guessed_artist = find_artist(guess)

    if guessed_artist is None:
        return redirect(url_for("game"))

    guesses = session.get("guesses", [])

    # Maximum 5 guesses
    if len(guesses) >= 5:
        return redirect(url_for("result"))

    # Store official artist name
    guesses.append(guessed_artist["name"])

    session["guesses"] = guesses

    # Correct answer
    if guessed_artist["name"].lower() == session["answer"].lower():

        # More points for fewer guesses
        session["score"] = (6 - len(guesses)) * 20

        return redirect(url_for("result"))

    # Five guesses used
    if len(guesses) >= 5:

        session["score"] = 0

        return redirect(url_for("result"))

    return redirect(url_for("game"))


# -----------------------------
# COMPARE ARTISTS
# -----------------------------

def compare_artists(guess, answer):

    year_difference = abs(
        guess["debut_year"] - answer["debut_year"]
    )

    popularity_difference = abs(
        guess["popularity"] - answer["popularity"]
    )

    return {

        "genre":
            "correct"
            if guess["genre"] == answer["genre"]
            else "wrong",

        "country":
            "correct"
            if guess["country"] == answer["country"]
            else "wrong",

        "debut_year":
            "correct"
            if guess["debut_year"] == answer["debut_year"]
            else "close"
            if year_difference <= 5
            else "wrong",

        "artist_type":
            "correct"
            if guess["artist_type"] == answer["artist_type"]
            else "wrong",

        "popularity":
            "correct"
            if guess["popularity"] == answer["popularity"]
            else "close"
            if popularity_difference <= 10
            else "wrong"
    }


# -----------------------------
# RESULT PAGE
# -----------------------------

@app.route("/result")
def result():

    if "answer" not in session:
        return redirect(url_for("home"))

    answer = find_artist(session["answer"])

    guesses = session.get("guesses", [])

    won = any(
        guess.lower() == session["answer"].lower()
        for guess in guesses
    )

    score = session.get("score", 0)

    return render_template(
        "result.html",
        answer=answer,
        won=won,
        guesses=len(guesses),
        score=score
    )


# -----------------------------
# AUTOCOMPLETE API
# -----------------------------

@app.route("/artists")
def artists_api():

    artists = load_artists()

    return jsonify([
        artist["name"]
        for artist in artists
    ])

# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)