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

---

## How to Use

### Mode 1: Terminal — Local Two-Player

Both players share one keyboard on one machine. No browser or network needed.

**Files needed:** `c4.py`

Run:

```bash
python3 c4.py
```

Players alternate entering a column number (1–7) when prompted. The game detects wins and draws automatically.

---

### Mode 2: Terminal — Networked Two-Player

Two players connect over a network, each using their own terminal. The two terminals communicate over a TCP socket connection.

**Files needed:** `c4.py`, `c4server.py`, `c4client.py`

#### Terminal 1 — Player X (hosts the game):

```bash
python3 c4server.py
```

The server will print `CONNECT 4 SERVER STARTED` and wait for Player O to connect.

#### Terminal 2 — Player O (joins the game):

```bash
python3 c4client.py
```

Once connected, the game begins automatically. Players type a column number (1–7) on their respective terminals. After each game, Player X is prompted `Play again? (y/n)` — scores persist across rounds within the session.

> **If Player O is on a different machine**, open `c4client.py` and change the `HOST` variable at the top from `"127.0.0.1"` to Player X's local IP address. Player X's IP can be found by running `ipconfig` (Windows) or `ifconfig` / `ip addr` (Mac/Linux).

---

### Mode 3: Browser — Networked Two-Player

The same two-player networked game, but each player uses a browser instead of a terminal. Each player runs their own Flask app which hosts a visual game board with a real Connect 4 look — blue board, red and yellow coins, drop animations.

**Files needed:** `c4.py`, `c4web_server.py`, `c4web_client.py`, `templates/board.html`

#### Step 1 — Player X starts the server:

```bash
python3 c4web_server.py
```

You will see:

- Contribute: N/A

- Credits: N/A

- License: N/A
