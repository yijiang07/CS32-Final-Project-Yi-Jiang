This file is to introduce what we have done for the FP Design assignment and the progress that has been made on the project:

Our overall project idea is the create a Python implementation of the classic game of Connect 4. While this version of the game runs like how the game Connect 4 runs, we do plan on adding more features for later versions of the project, including but not limited to AI opponent implementation, potential graphics, etc.

Below is the building of the core game logic of Connect 4:
- Creating the board.
- Accepting player input.
- Taking the player input and put their resepctive piece into whichever column    was selected.
- check for wins.
- check for draws.

Data Structures:
- We used a 2D list to represent the board:
- Each position on the 2D list of lists represents a specific value:
    - "." = empty space
    - "X" = piece for Player X
    - "0" = piece for Player 0

Future addons:
- Score Tracking System
- Single-player vs AI/computer
- Improve Board interface
- Make user experience better



Testing:
- We have a test file that tests:
    - horizontal wins
    - vertical wins
    - diagonal wins
    - finding the next open row


