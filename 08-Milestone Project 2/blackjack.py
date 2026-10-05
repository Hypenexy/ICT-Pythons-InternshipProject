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

    def hit():
        # self.cards append from deck
        # Take card
        pass

    def stand():
        pass

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

    # Create & shuffle the deck, deal two cards to each player
    tableDeck = Deck()

    tableDeck.shuffle()

    # print(tableDeck.deck)

    playerHand = Hand()

    playerHand.takeCard(tableDeck.drawCard())
    playerHand.takeCard(tableDeck.drawCard())
    tableDeck.deck.pop()

    dealerHand = Hand()
    dealerHand.takeCard(tableDeck.drawCard())
    dealerHand.takeCard(tableDeck.drawCard())


    
        
    # Set up the Player's chips
    print("Your balance: ", playerBank.balance)
    buyingChips = True # True represents if the user is still buying chips
    while(buyingChips):
        chipBuyingCount = int(input("How many chips do you need to purchase? (number): "))
        withdrawResponse = playerBank.withdraw(chipBuyingCount)
        if(withdrawResponse == "Withdraw Accepted"):
            casinoBank.deposit(chipBuyingCount)
            buyingChips = False
        elif(withdrawResponse.startswith("Withdraw Declined")):
            print("Transaction didn't go through:")
            print(withdrawResponse)

    print(f"You have {casinoBank.chips} chips")

    # Prompt the Player for their bet
    bettingChips = True # True represents if the user is still betting chips
    while(bettingChips):
        chipBuyingCount = int(input("Betting amount (number): "))
        withdrawResponse = casinoBank.withdraw(chipBuyingCount)
        if(withdrawResponse == "Withdraw Accepted"):
            casinoBank.deposit(chipBuyingCount)
            bettingChips = False
        elif(withdrawResponse.startswith("Withdraw Declined")):
            print("You don't have enough chips!")

    
    # Show cards (but keep one dealer card hidden)
    playing = True
    
    while playing:  # recall this variable from our hit_or_stand function

        hitOrStand_answer = input("Do you HIT (H) or STAND (S): (H/S): ")
        # Prompt for Player to Hit or Stand
        
        print("Dealer's cards: ")
        card_i = 0
        for card in dealerHand.cards:
            if(card_i < len(dealerHand.cards)-1):
                print("[]", ' '.join(card))
            card_i += 1
        
        print("[]", "HIDDEN CARD")

        # Show cards (but keep one dealer card hidden)

        print("Your cards: ")
        print(playerHand)
        
        # If player's hand exceeds 21, run player_busts() and break out of loop

        if(playerHand.value() > 21):
            playerHand.busts(deck=tableDeck)
            break

        while(dealerHand.value() <= 17):
            dealerHand.takeCard(tableDeck.drawCard())

        print("Dealer's Hand:\n", dealerHand)

        print("Player's Hand:\n", playerHand)
        
        # If Player hasn't busted, play Dealer's hand until Dealer reaches 17
        
        
            # Show all cards
        
            # Run different winning scenarios
            
        
        # Inform Player of their chips total 
        
        # Ask to play again

            #break