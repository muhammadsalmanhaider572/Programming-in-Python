import random

def roll_dice():
    """Roll two dice and return the results."""
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    return die1, die2

def main():
    """Main function to run the dice rolling game."""
    print("Welcome to the Dice Rolling Game!")
    print("-" * 40)
    
    while True:
        # Roll the dice
        die1, die2 = roll_dice()
        total = die1 + die2
        
        # Display results
        print(f"\nDie 1: {die1}")
        print(f"Die 2: {die2}")
        print(f"Total: {total}")
        
        # Ask if user wants to roll again
        while True:
            response = input("\nWould you like to roll again? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                break
            elif response in ['no', 'n']:
                print("\nThanks for playing! Goodbye!")
                return
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()
