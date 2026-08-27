class BankAccount:
    def __init__(self, initial_balance):
        self.balance = initial_balance

    def deposit(self, amount):
        if amount < 0:
            print("No negative deposits.")
            return
        self.balance += amount
        print(f"Deposited {amount}. New balance: {self.balance}")

    def withdraw(self, amount):
        if amount < 0:
            print("No negative withdrawals.")
            return
        if amount > self.balance:
            print("Insufficient funds")
            return
        self.balance -= amount
        print(f"Withdrew {amount}. New balance: {self.balance}")

    def check_balance(self):
        print(f"Current balance: {self.balance}")


if __name__ == "__main__":
    acc = BankAccount(100)
    acc.deposit(50)
    acc.withdraw(30)
    acc.check_balance()
