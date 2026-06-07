import getpass

class ATM:
    """A simple ATM model that stores and updates account balance."""

    def __init__(self, initial_balance=0.0, password="2580"):
        self._balance = float(initial_balance)
        self._password = str(password)

    def authenticate(self, password):
        return password == self._password

    def check_balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        self._balance += amount
        return self._balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount
        return self._balance


class ATMController:
    """Handles user interaction for the ATM simulation."""

    def __init__(self, atm):
        self.atm = atm

    def show_menu(self):
        print("\nATM Simulation")
        print("1. Check balance")
        print("2. Deposit money")
        print("3. Withdraw money")
        print("4. Quit")

    @staticmethod
    def get_float_input(prompt):
        user_input = input(prompt).strip()
        try:
            value = float(user_input)
        except ValueError:
            raise ValueError("Please enter a valid number.")
        return value

    def authenticate_user(self, max_attempts=3):
        attempts = max_attempts
        while attempts > 0:
            password = getpass.getpass("Enter ATM password: ")
            if self.atm.authenticate(password):
                print("Access granted. Welcome!")
                return True
            attempts -= 1
            print(f"Incorrect password. {attempts} attempt(s) left.")
        return False

    def run(self):
        print("Welcome to the ATM Simulation!")
        if not self.authenticate_user():
            print("Access denied. Exiting the ATM.")
            return

        while True:
            self.show_menu()
            choice = input("Please select an option (1-4): ").strip()

            if choice == "1":
                balance = self.atm.check_balance()
                print(f"Your current balance is: ${balance:.2f}")

            elif choice == "2":
                try:
                    amount = self.get_float_input("Enter deposit amount: $")
                    new_balance = self.atm.deposit(amount)
                    print(f"Deposit successful. New balance: ${new_balance:.2f}")
                except ValueError as exc:
                    print(f"Error: {exc}")

            elif choice == "3":
                try:
                    amount = self.get_float_input("Enter withdrawal amount: $")
                    new_balance = self.atm.withdraw(amount)
                    print(f"Withdrawal successful. New balance: ${new_balance:.2f}")
                except ValueError as exc:
                    print(f"Error: {exc}")

            elif choice == "4":
                print("Thank you for using the ATM Simulation. Goodbye!")
                break

            else:
                print("Invalid selection. Please choose 1, 2, 3, or 4.")


def main():
    atm = ATM(initial_balance=100.0)
    controller = ATMController(atm)
    controller.run()


if __name__ == "__main__":
    main()
