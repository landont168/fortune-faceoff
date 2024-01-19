"""
FortuneFaceoff
Landon T.
Kitchener, Canada
"""

import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    apology,
    login_required,
    usd,
    get_random_company,
    check_guess,
    update_leaderboard,
    update_high_score,
)

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///game.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user with username and password"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Get list of existing usernames
        usernames = [
            row["username"] for row in db.execute("SELECT username FROM users")
        ]

        # Validate username
        if not username:
            return apology("invalid username")
        elif username in usernames:
            return apology("username already exists")

        # Validate password
        if not password or not confirmation:
            return apology("invalid passwords")
        elif password != confirmation:
            return apology("passwords do not match")

        # Insert new user and password into users database
        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash
        )
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/game", methods=["GET", "POST"])
@login_required
def game():
    """Handle game logic and player guesses"""

    # Set up game and retrieve player ID
    game_state = session.get("game", {})
    id = session["user_id"]

    # Update player's high score if necessary
    current_score = game_state.get("score", 0)
    high_score = update_high_score(id, current_score)

    # Update game depending on correct or incorrect player guess
    if request.method == "POST":
        guess = request.form.get("guess")
        companies = game_state["companies"]

        # Guessed correctly - update score and game for next round
        if guess == check_guess(companies[0], companies[1]):
            current_score += 1
            session["game"]["score"] = current_score
            session["game"]["companies"] = [companies[1], get_random_company()]
            correct = True

        # Guessed incorrectly - reset game state and update leaderboard if needed
        else:
            final_score = game_state["score"]
            del game_state["companies"]
            game_state["score"] = 0
            correct = False
            update_leaderboard(id, final_score)

        # Display result
        return render_template(
            "result.html",
            company1=companies[0],
            company2=companies[1],
            score=current_score,
            high_score=high_score,
            correct=correct,
        )

    # Setup initial or concurrent game state
    else:
        if "companies" not in game_state:
            companies = [get_random_company() for _ in range(2)]
            session["game"] = {"score": 0, "companies": companies}
        else:
            companies = game_state["companies"]

        return render_template(
            "game.html",
            company1=companies[0],
            company2=companies[1],
            score=current_score,
            high_score=high_score,
        )


@app.route("/game_over/<int:score>")
@login_required
def game_over(score):
    """Displays appropriate game over screen"""
    if score > 15:
        gif = "winnie.gif"
        message = "Wow, great job!"
    elif score > 5:
        gif = "wow.gif"
        message = "Not bad! Keep going!"
    elif score > 0:
        gif = "minion.gif"
        message = "We both know you can do better!"
    else:
        gif = "speechless.gif"
        message = "Come on! Try again..."
    return render_template("game_over.html", score=score, gif=gif, message=message)


@app.route("/leaderboard")
@login_required
def leaderboard():
    """Display leaderboard table"""
    leaderboard_info = db.execute(
        "SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10"
    )
    return render_template("leaderboard.html", leaderboard=leaderboard_info)


@app.route("/sp500")
@login_required
def sp500():
    """Display information about the S&P 500"""
    companies = db.execute("SELECT * FROM stocks ORDER BY market_cap DESC")
    return render_template("sp500.html", companies=companies)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Allower user to update password"""
    if request.method == "POST":
        current_pw = request.form.get("password")
        new_pw = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Get actual current password
        user_id = session["user_id"]
        user_info = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

        if not check_password_hash(user_info["hash"], current_pw):
            return apology("incorrect current password")

        # Validate new password
        if not new_pw or not confirmation:
            return apology("invalid passwords")
        elif new_pw != confirmation:
            return apology("passwords do not match")
        if new_pw == current_pw:
            return apology("please pick a new password")

        # Change password
        hash_new_pw = generate_password_hash(new_pw)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash_new_pw, user_id)

        # Redirect to home page
        return redirect("/")

    else:
        return render_template("account.html")
