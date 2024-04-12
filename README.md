# Hnefatafl

Hnefatafl originated in Scandinavia many centuries ago. It was developed from a Roman game called Ludus Latrunculorum. This game flourished until the arrival of chess. It was revived back in nineteenth century.

## Algorithm and approach

This project used minmax algorithm with alpha-beta pruning. The heuristic evaluation function considers king position, number of attackers and defenders remaining, how close it is to capture king etc. Based on the values provided by this function for all possible valid moves at a state, ai decides which move to commit.

## Rules
- Turn based board game.
- Two board sizes: 'large' - 11x11 and 'small' - 9x9.
- Center cell and four corner cells are called restricted cells.
- Excluding king, a-d count is 24-12 on large board and 16-8 on small board.
- All pieces except king can move any number of cells horizontally or vertically.
- King can move only one cell at a time.
- Only king can move to any of the restricted cells.
- Pieces, except king, can be captured by sandwitching them from both sides.
- Restricted cells can be used to sandwitch opponent.
- Only one opponent piece can be captured in single line with single move.
- Multiple pieces can be captured with a single move on cardinal points.
- To capture king, attackers need to sorround him on all four cardinal points.
- If king is captured, attackers win.
- If king escapes to any of the four corner cells, defenders win.
- If all attackers are captured, defenders win.

## Screenshots
![Screenshot (6)](https://github.com/JoeSzeles/Vikings-chess-Hnefatafl/blob/main/Screenshot%20(32).jpg)

![Screenshot (12)](https://github.com/JoeSzeles/Vikings-chess-Hnefatafl/blob/main/Screenshot%20(25).png)

![Screenshot (13)](https://github.com/JoeSzeles/Vikings-chess-Hnefatafl/blob/main/Screenshot%20(24).jpg)


curl -X POST -H "Authorization: Bearer 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" -H "Content-Type: application/json" -d '{"text": "YOUR_MESSAGE"}' https://api.openai.com/v1/completions


