import random
import sys

print('ROCK, PAPER, SCISSORS')

moves: dict[str,str] = {'rock': "🪨", 'paper': "📜", 'scissors': "✂️"}
moves_list: list[str] = list(moves.keys())

while True:
    print()
    print('Enter your move: (rock, paper, scissors)')
    player_move = input().lower().strip()
    if player_move == 'quit':
        sys.exit()
    if player_move not in moves:
        print('Invalid move. Try again.')
        continue

    computer_move: str = random.choice(moves_list)

    print(f'You played {moves[player_move]}, computer played {moves[computer_move]}.')

    result: int = (moves_list.index(player_move) - moves_list.index(computer_move)) % 3

    if result == 0:
        print('It\'s a tie!')
    elif result == 1:
        print('You win!')
    else:
        print('You lose!')