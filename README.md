# 💰 FortuneFaceoff
#### Video Demo 📹:  https://youtu.be/__BMU66nZ0k
#### Description 👁️‍🗨️: A stock-themed version of "The Higher Lower Game" based off the market capitalization of companies in the S&P 500

##### Game 🕹️:
The aim of the game is to achieve the highest possible score by consecutively indicating whether a particular company is worth more or less than another company. The game displays two stocks where the market cap of one stock is provided. The player must guess whether the other stock has a higher or lower market cap. If the player guesses correctly, the unknown market cap of the stock is revealed and the player continues the game. The next round will prompt the player to compare the market cap of the revealed stock to another random stock in the S&P 500. The player continues to play until they guess incorrectly.

##### Functionality 🧰:

1. ```helpers.py```
- Retrieves relevant information of stocks in the S&P 500 by webscraping a Wikipedia page with ```BeauitfulSoup``` (ex. name, ticker, sector, Wikipedia URL)
- Retrieves company logo by webscraping its Wikipedia page with ```BeautifulSoup```
- Retrieves market cap of each company using the ```yfinance``` library
- Stores and manages all the stock/company information using SQLite
- Provides ```get_random_company``` which randomly picks a company in the ```stocks``` SQL database
- Provides ```update_leaderboard``` which manages and updates a ```leaderboard``` SQL database which saves the top scores that players achieve
- Provides ```update_high_score``` which helps display and update a player's high score

2. ```app.py```
- Configures Flask application by handling requests, routing, and interacting with databases
- Enables users to register and log in/out to/from game with a unique username and hashed password
- Handles game logic and state (ex. updating score/high score, getting companies, resetting game state, updating leaderboard)
- Displays a unique game over screen depending on the player's final score and enables user to play again
- Contains route that allows users to view a leaderboard of the top 10 scores which is stored and updated in a ```leaderboard``` SQL database
- Contains route that allows users to view information of the companies in the S&P 500 ranked by market cap
- Contains route that allows users to change their password

3. ```templates```
- Contains ```layout.html``` which organizes the overall design of the web application
- Contains all the HTML files used to create the different components of the web application


4. ```static```
- Contains all the icons, images, and GIFs used throughout the HTML files in ```templates```

##### Dependencies 🖲️:
Make sure you have the following Python libraries installed:

- **BeautifulSoup**: Used for web scraping and parsing HTML and XML content.
- **Flask**: A lightweight web framework for Python.
- **Flask-Session**: An extension for Flask that adds support for server-side sessions.
- **cs50**: A library for Harvard's CS50 course, providing functions for user input validation, etc.
- **humanize**: A Python library for making data more human-readable.
- **requests**: A simple HTTP library for making HTTP requests.
- **yfinance**: A library for accessing financial data from Yahoo Finance.

All languages and frameworks used in this project include: Python, Flask, Jinja, JavaScript, HTML, CSS, Bootstrap.

#### Next Steps ⏭️:

Note that there are a lot of improvements that I want to make to this project. Super excited to build upon this prototype!:
- Completely rebuild the project using a MERN stack
- Build a dynamic frontend using JavaScript and React (prevent refreshing + add animations)
- Design a more appealing frontend to improve the UX
- Retrieve the stocks in the S&P 500 using some existing API
- Retrieve the logos of the companies using an API for higher quality and to improve reliability
- Deploy the web application on some host once the project is ready
