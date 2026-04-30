# CS32-Final-Project---Yi-Jiang
Final Project for CS32

- Project Title: CS32 Final Project: Connect 4

- Motivation: I decided to create a Connect 4 game that allows a player to
              either play another player or the computer because I thought that
              it implements the tools and code that we have learned in class
              very well--specifically loops, arrays, conditionals, and networking
              between servers. I also think it might be interesting to implement
              a computer that makes the perfect move everytime/offer the player the
              computer difficulty that they want to play. Since Connect 4 is a solved
              game, this perfect move choice by the computer is possible. Furthermore,
              I think Connect 4 itself is a relatively intuitive game, and would be easy
              for users to play.

- Build Status: In progress

- Code Style: PEP 8

- Screenshots: N/A

- Tech/Framework Used: In progress

- Features: The program will have functionality for the Connect 4 Game,
            allow playing against the computer as well as another player,
            will keep track of how many wins each player has, and give the
            players an option to play again, etc.

- Code Examples: In progress

- Installation: N/A

- API Reference: N/A

- Tests: In progress

- How to use:
---

## Requirements

- Python 3.6 or higher
- Flask (`pip install flask`)
- No other external packages required


### Mode 1: Terminal — Local Two-Player (This is a primitive version and isn't the final version of our project. Feel free to ignore.)

Both players share one keyboard on one machine. No browser or network needed.

Files needed: `c4.py`

Run:

```bash
python3 c4.py
```

Players alternate entering a column number (1–7) when prompted. The game detects wins and draws automatically.

---

### Mode 2: Terminal — Networked Two-Player (This is also a primitive version and isn't the final version of our project. Feel free to ignore.)

Two players connect over a network, each using their own terminal. The two terminals communicate over a TCP socket connection.

Files needed: `c4.py`, `c4server.py`, `c4client.py`

Terminal 1 — Player X (hosts the game):

```bash
python3 c4server.py
```

The server will print `CONNECT 4 SERVER STARTED` and wait for Player O to connect.

Terminal 2 — Player O (joins the game):

```bash
python3 c4client.py
```

Once connected, the game begins automatically. Players type a column number (1–7) on their respective terminals. After each game, Player X is prompted `Play again? (y/n)` — scores persist across rounds within the session.

> If Player O is on a different machine, open `c4client.py` and change the `HOST` variable at the top from `"127.0.0.1"` to Player X's local IP address. Player X's IP can be found by running `ipconfig` (Windows) or `ifconfig` / `ip addr` (Mac/Linux).

---

### Mode 3: Browser — Networked Two-Player (This mode is a part of our final submission)

The same two-player networked game, but each player uses a browser with enhanced UI instead of a terminal. Each player runs their own Flask app which hosts a visual game board with a real Connect 4 look — blue board, red and yellow coins, drop animations.

Files needed: `c4.py`, `c4web_server.py`, `c4web_client.py`, `templates/board.html`

Step 1 — Player X starts the server:

```bash
python3 c4web_server.py
```

You will see:

"[TCP] Listening on 0.0.0.0:65432 for Player O...
[WEB] Open http://localhost:5000 in your browser (Player X)

Running on http://0.0.0.0:5000"

If you are running this in GitHub Codespaces, a pop-up will appear in the bottom-right corner of VS Code saying "Your application running on port 5000 is available." Click "Open in Browser". Use the forwarded URL that Codespaces provides via the pop-up.

Player X's board will load in the browser and show a status message indicating it is waiting for Player O. The board is inactive until Player O joins.

Step 2 — Player O connects:

In a second terminal, run:

```bash
python3 c4web_client.py
```

In Codespaces, a second pop-up will appear for port 5001. Click "Open in Browser" to open Player O's board in a new tab or window.

> If Player O is on a different machine**, open `c4web_client.py` and change the `SERVER_HOST` variable at the top from `"127.0.0.1"` to Player X's local IP address before running.

Step 3 — Play:

Once both browsers are open, the game starts automatically. Each player sees their own board and takes turns clicking a column button (1–7) to drop their coin.

- Player X plays red coins and always goes first.
- Player O plays yellow coins.
- After a win or draw, Player X's screen shows a Play Again and End Session button. Player X decides whether to continue. Scores are tracked across rounds within the session.

---
Mode 4: Browser — Impossible Mode (AI Opponent) (This is also part of our final submission)

A single human player faces a perfect AI opponent in the browser. The AI plays as Player X using Minimax with Alpha-Beta Pruning, which is the algorithm that initially solved Connect 4 in 1988. It searches 8 moves ahead and plays optimally every turn. Since Connect 4 is a mathematically solved game, with perfect play the first player (X) always wins, hence why we called it "Impossible Model". The AI's opening move is always the center column, which is the provably optimal first move.

Files needed: `c4.py`, `c4ai.py`, `c4web_ai_server.py`, `templates/board_ai.html`

Step 1 — Start the AI server:

```bash
python3 c4web_ai_server.py
```

You will see:

[WEB] Impossible Mode → http://localhost:5002

Running on http://0.0.0.0:5002

If you are in GitHub Codespaces, a pop-up will appear saying "Your application running on port 5002 is available." Click "Open in Browser". As with the other modes, use the Codespaces forwarded URL from the pop-up.

Note that only one terminal and one browser window are needed for this mode. No second player or second terminal is required. It's just going to be you against the AI.

Step 2 — Click Play vs. AI on the start screen:

When the browser opens, you will land on a dark start screen with a single card: Play vs. AI. Click it to begin. The screen will confirm that you are playing as Player O (yellow coins) and the AI is Player X (red coins).

Step 3 — Play:

The AI moves first automatically. While it is computing, you will see a pulsing "AI is thinking..." message. The first move is instant (always center column). Subsequent moves typically respond in under a second.

- Click any column button (1–7) to drop your yellow coin.
- The AI responds immediately after your move.
- After a game ends, Play Again resets the board and starts a new round with scores preserved. End Session closes out the game.


One Final Note:

All modes require `c4.py` in the same directory. The browser AI mode additionally requires `c4ai.py`.



- Contribute: We used Claude for assistance with portions of this project. We wrote prompts to help write the html files for the board, instructing it to use the Flask library to design a board and coins according to our specifications and the rules of Connect 4. We also leveraged Claude to write a Minimax Algorithm with Alpha-Beta Pruning, which we knew was the algorithm developed in 1988 by James Dow Allen and Victor Allis to solve the game for the player going first. We also leveraged Claude when we recognized we were uncertain as to the language we should use to connect our networked game logic to a locally hosted website, which assisted with some parts of c4web_client.py and c4web_server.py. We also used Claude to help debug network synchronization. Essentially, we had an issue with the server file in the networked game sending all messages to the client, and the client relying on this information being sent to update the board. What this meant was that if the server player (Player X) won first, the game would end immediately on the server, clear the board, but exit out of the game loop before the client file could be notified the game was over. We fixed this synchronization issue by recognizing that we had to make sure the client file read a few moves ahead and that there was enough of a lag between the two game files such that the client file wouldn't be timed out of the game before it could read a move tht told it the game was over. Claude also assisted with organizing our thoughts to write as thorough instructions as possible for the How to Use section.

- Credits: N/A

- License: N/A
