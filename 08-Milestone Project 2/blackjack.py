#You must use OOP and classes in some portion of your game. You can not just use functions in your game. Use classes to help you define the Deck and the Player's hand. There are many right ways to do this, so explore it well!

import random

suits = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five':5, 'Six':6, 'Seven':7, 'Eight':8, 'Nine':9, 'Ten':10, 'Jack':10,
         'Queen':10, 'King':10, 'Ace':11}


class Deck():
    def __init__(self):
        self.deck = []
        for rank in ranks:
            for suit in suits:
                self.deck.append([rank, suit])
        
    def shuffle(self):
        random.shuffle(self.deck)
    def drawCard(self):
        return self.deck.pop()
    pass
class Hand():
    def __init__(self):
        self.cards = []

    def takeCard(self, card):
        self.cards.append(card)

    def value(self):
        sum = 0
        for card in self.cards:
            sum += values[card[0]]
        return sum

    def busts(self, deck):
        for card in self.cards:
            deck.append(self.cards.pop)

    def busts(self):
        return self.value() > 21

    def hit(self, deck):
        self.takeCard(deck.drawCard())

    def stand(self):
        return self.value()

    def __str__(self):
        str = ""
        for card in self.cards:
            str += "[] " + " ".join(card) + "\n "
        return str

class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance
    
    def deposit(self, amount):
        self.balance += amount
        return "Deposit Accepted"

    def withdraw(self, amount):
        if(amount <= self.balance):
            self.balance -= amount
            return "Withdraw Accepted"
        else:
            return "Withdraw Declined, Insufficent funds"

    def __str__(self):
        return f"Account owner: {self.owner} \nAccount balance: {self.balance}"

class CasinoBalance:
    def __init__(self, chips):
        self.chips = chips

    def deposit(self, amount):
        self.chips += amount
        return "Deposit Accepted"

    def withdraw(self, amount):
        if(amount <= self.chips):
            self.chips -= amount
            return "Withdraw Accepted"
        else:
            return "Withdraw Declined, Insufficent funds"
# Money
# Stand or Hit
# Betting amount



# Game logic
while(True):
    print("Welcome, to the Streaks Casino")

    playerBank = Account('Igrachut',100)
    casinoBank = CasinoBalance(0)

    print("Your balance: ", playerBank.balance)
    buyingChips = True # True represents if the user is still buying chips
    while buyingChips:
        try:
            chipBuyingCount = int(input("How many chips do you need to purchase? (number): "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if chipBuyingCount <= 0:
            print("Chip amount must be greater than zero.")
            continue

        withdrawResponse = playerBank.withdraw(chipBuyingCount)
        if(withdrawResponse == "Withdraw Accepted"):
            casinoBank.deposit(chipBuyingCount)
            buyingChips = False
        elif(withdrawResponse.startswith("Withdraw Declined")):
            print("Transaction didn't go through:")
            print(withdrawResponse)

    print(f"You have {casinoBank.chips} chips")

    bettingChips = True
    while bettingChips:
        try:
            betAmount = int(input("Betting amount (number): "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if betAmount <= 0:
            print("Your bet must be greater than zero.")
            continue

        withdrawResponse = casinoBank.withdraw(betAmount)
        if withdrawResponse == "Withdraw Accepted":
            pot = betAmount
            bettingChips = False
        elif(withdrawResponse.startswith("Withdraw Declined")):
            print("You don't have enough chips!")

    tableDeck = Deck()
    tableDeck.shuffle()

    playerHand = Hand()
    playerHand.takeCard(tableDeck.drawCard())
    playerHand.takeCard(tableDeck.drawCard())

    dealerHand = Hand()
    dealerHand.takeCard(tableDeck.drawCard())
    dealerHand.takeCard(tableDeck.drawCard())

    print("Dealer's cards: ")
    print("[]", ' '.join(dealerHand.cards[0]))
    print("[]", "HIDDEN CARD")

    print("Your cards: ")
    print(playerHand)

    if playerHand.value() == 21 or dealerHand.value() == 21:
        print("Dealer's Hand:\n", dealerHand, "Points: ", dealerHand.value())
        print("Player's Hand:\n", playerHand, "Points: ", playerHand.value())
        if playerHand.value() == dealerHand.value():
            print("Push!")
            casinoBank.deposit(pot)
        elif playerHand.value() == 21:
            print("Blackjack! You win!")
            playerBank.deposit(pot * 2)
            casinoBank.deposit(pot)
        else:
            print("Dealer wins!")
    else:
        playing = True
        while playing:
            hitOrStand_answer = input("Do you HIT (H) or STAND (S): (H/S): ").strip().upper()

            if hitOrStand_answer == 'H':
                playerHand.hit(tableDeck)
                print("Your cards: ")
                print(playerHand)

                if playerHand.busts():
                    print("You busted! Dealer wins.")
                    playing = False
            elif hitOrStand_answer == 'S':
                playing = False
            else:
                print("Please enter H or S.")

        if not playerHand.busts():
            while dealerHand.value() < 17:
                dealerHand.takeCard(tableDeck.drawCard())

            print("Dealer's Hand:\n", dealerHand, "Points: ", dealerHand.value())
            print("Player's Hand:\n", playerHand, "Points: ", playerHand.value())

            if dealerHand.value() > 21:
                print("Dealer busts! You win!")
                playerBank.deposit(pot * 2)
                casinoBank.deposit(pot)
            elif dealerHand.value() > playerHand.value():
                print("Dealer wins!")
            elif dealerHand.value() < playerHand.value():
                print("You win!")
                playerBank.deposit(pot * 2)
                casinoBank.deposit(pot)
            else:
                print("Push!")
                casinoBank.deposit(pot)

    print(f"Your final balance is: {playerBank.balance}")
    playAgain = input("Do you want to play again? (Y/N): ").strip().upper()
    if playAgain != 'Y':
        print("Thanks for playing at Streaks Casino!")
        break