import random


def play_game():
    """Play one round of the number guessing game."""
    secret_number = random.randint(1, 100)
    guesses = 0

    print("\nI have selected a number between 1 and 100.")
    print("Try to guess it!")

    while True:
        guess_input = input("Enter your guess: ").strip()
        if not guess_input.isdigit():
            print("Please enter a valid whole number between 1 and 100.")
            continue

        guess = int(guess_input)
        if guess < 1 or guess > 100:
            print("Your guess must be between 1 and 100.")
            continue

        guesses += 1
        if guess < secret_number:
            print("Too low. Try again.")
        elif guess > secret_number:
            print("Too high. Try again.")
        else:
            print(f"Congratulations! You guessed the number in {guesses} guess{'es' if guesses != 1 else ''}.")
            break


def main():
    """Main function for starting the game."""
    print("Welcome to the Number Guessing Game!")
    while True:
        play_game()
        play_again = input("Do you want to play again? (yes/no): ").strip().lower()
        if play_again in ("no", "n"):
            print("Thanks for playing. Goodbye!")
            break
        if play_again not in ("yes", "y"):
            print("I'll take that as a no. Exiting the game.")
            break


if __name__ == "__main__":
    main()
