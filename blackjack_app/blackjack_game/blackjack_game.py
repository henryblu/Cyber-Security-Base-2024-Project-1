import random

# Define card values
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 6, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

class BlackjackGame:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []

    def create_deck(self):
        deck = []
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = list(card_values.keys())
        for suit in suits:
            for rank in ranks:
                deck.append((rank, suit))
        random.shuffle(deck)
        return deck

    def deal_card(self):
        return self.deck.pop()

    def initial_deal(self):
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]

    def calculate_hand_value(self, hand):
        value = 0
        num_aces = 0
        for card, suit in hand:
            value += card_values[card]
            if card == 'A':
                num_aces += 1
        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1
        return value

    def player_hit(self):
        self.player_hand.append(self.deal_card())

    def dealer_turn(self):
        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deal_card())

    def is_bust(self, hand):
        return self.calculate_hand_value(hand) > 21
    
    def is_blackjack(self):
        return self.calculate_hand_value(self.player_hand) == 21 and len(self.player_hand) == 2

    def get_winner(self):
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        if self.is_bust(self.player_hand):
            return 'Dealer'
        elif self.is_bust(self.dealer_hand):
            return 'Player'
        elif player_value > dealer_value:
            return 'Player'
        elif dealer_value >= player_value:
            return 'Dealer'
        else:
            return None

    def reset(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []