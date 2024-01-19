from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime
from urllib.parse import urljoin

import humanize
import requests
from bs4 import BeautifulSoup
from cs50 import SQL
import yfinance as yf


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///game.db")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_companies():
    """Get relevant information for stocks in S&P 500"""
    # Send GET request to URL
    wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(wiki_url)

    if response.status_code == 200:
        # Find S&P 500 table
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        rows = table.find_all("tr")[1:]

        companies = []

        for row in rows:
            cells = row.find_all("td")

            # Extract ticker, company name, URL, and sector
            ticker = cells[0].text.strip()
            name = cells[1].text.strip()
            sector = cells[3].text.strip()
            hyperlink = cells[1].find("a")

            if hyperlink:
                company_url = link.get("href")
                absolute_url = f"https://en.wikipedia.org{company_url}"

            company = {
                "ticker": ticker,
                "name": name,
                "sector": sector,
                "url": absolute_url,
            }
            companies.append(company)
        return companies

    print(f"Failed to fetch the page. Status code: {response.status_code}")


def get_logo(wiki_url):
    """Get logo of company given its Wikipedia page"""
    # Parse the HTML content of the page
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find infobox where first image is assumed to be logo
    infobox = soup.find("table", {"class": "infobox"})
    if infobox:
        logo_tag = infobox.find("img")
        if logo_tag:
            image_link = urljoin(wiki_url, logo_tag["src"])
            return image_link
    return None


def create_database():
    """Retrieve necessary information of companies in S&P 500 and store in SQL database"""
    companies = get_companies()

    for company in companies:
        try:
            stock_ticker = yf.Ticker(company["ticker"])
            stock_logo = get_logo(company["url"])
            market_cap = round(stock_ticker.fast_info["marketCap"])
            db.execute(
                "INSERT INTO stocks (name, ticker, market_cap, sector, logo) VALUES(?, ?, ?, ?, ?)",
                company["name"],
                company["ticker"],
                market_cap,
                company["sector"],
                stock_logo,
            )
        except:
            print(f"Failed for {company['ticker']}")


def get_random_company():
    """Return random company from SQL database"""
    row = db.execute("SELECT * FROM stocks ORDER BY RANDOM() LIMIT 1")[0]
    company = {
        "ticker": row["ticker"],
        "market_cap": row["market_cap"],
        "logo": row["logo"],
    }
    return company


def check_guess(company1, company2):
    """Return correct answer for game logic"""
    if company1["market_cap"] > company2["market_cap"]:
        return "lower"
    return "higher"


def update_leaderboard(id, score):
    """Update leaderboard given a player's final score"""

    # Extract information from top 10 scores and player's username
    top_scores = db.execute("SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10")
    username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]

    # Insert score into leaderboard if there are less than 10 recorded scores or current score is greater than 10th score
    if score > 0:
        if len(top_scores) < 10 or score > top_scores[-1]["score"]:
            db.execute(
                "INSERT INTO leaderboard (id, username, score, date) VALUES (?, ?, ?, ?)",
                id,
                username,
                score,
                datetime.now().date(),
            )

            # Remove lowest score from leaderboard if there are 10 recorded scores
            if len(top_scores) == 10:
                lowest_score = top_scores[-1]["score"]
                db.execute(
                    "DELETE FROM leaderboard WHERE id = ? AND score = ?",
                    top_scores[-1]["id"],
                    lowest_score,
                )


def update_high_score(id, score):
    """Update high score of user if necessary"""
    high_score = db.execute("SELECT high_score FROM users WHERE id = ?", id)[0]["high_score"]
    if score > high_score:
        db.execute("UPDATE users SET high_score = ? WHERE id = ?", score, id)
        return score
    return high_score


def usd(value):
    """Format and humanize value as USD"""
    formatted_value = humanize.intword(value)
    return f"${formatted_value}"
