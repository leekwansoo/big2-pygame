import pygame
import random
from enum import Enum
from typing import List, Tuple

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 768
CARD_WIDTH = 71
CARD_HEIGHT = 96
CARD_MARGIN = -25

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Suit(Enum):
    DIAMONDS = ("♦", RED, 0)
    CLUBS = ("♣", BLACK, 1)
    HEARTS = ("♥", RED, 2)
    SPADES = ("♠", BLACK, 3)
    
    def __lt__(self, other):
        return self.value[2] < other.value[2]
    
    def get_rank(self):
        return self.value[2]

class Rank(Enum):
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("J", 11)
    QUEEN = ("Q", 12)
    KING = ("K", 13)
    ACE = ("A", 14)
    TWO = ("2", 15)
    
    def __lt__(self, other):
        return self.value[1] < other.value[1]

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.selected = False
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
    
    def __str__(self):
        return f"{self.suit.value[0]}{self.rank.value[0]}"
    
    def __lt__(self, other):
        if self.rank == other.rank:
            return self.suit.get_rank() < other.suit.get_rank()
        return self.rank < other.rank
    
    def get_value(self):
        rank_value = self.rank.value[1]
        suit_value = self.suit.get_rank()
        return rank_value * 4 + suit_value

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Big 2 Card Game")
        try:
            self.font = pygame.font.SysFont('arial', 36)
            self.symbol_font = pygame.font.SysFont('arial', 48)
        except:
            self.font = pygame.font.Font(None, 36)
            self.symbol_font = pygame.font.Font(None, 48)
        self.initialize_game()
    
    def initialize_game(self):
        self.deck = []
        for suit in Suit:
            for rank in Rank:
                self.deck.append(Card(suit, rank))
        random.shuffle(self.deck)
        
        self.hands = [[] for _ in range(4)]
        for i in range(52):
            player_index = i // 13
            self.hands[player_index].append(self.deck[i])
        
        for hand in self.hands:
            hand.sort(key=lambda x: x.get_value())
        
        self.current_player = 0
        for i, hand in enumerate(self.hands):
            for card in hand:
                if card.suit == Suit.DIAMONDS and card.rank == Rank.THREE:
                    self.current_player = i
                    break
        
        self.last_play = []
        self.last_player = None
        self.game_started = False
    
    def is_straight(self, cards):
        if len(cards) != 5:
            return False
        sorted_cards = sorted(cards, key=lambda x: x.rank.value[1])
        for i in range(len(sorted_cards) - 1):
            if sorted_cards[i + 1].rank.value[1] - sorted_cards[i].rank.value[1] != 1:
                return False
        return True

    def is_flush(self, cards):
        if len(cards) != 5:
            return False
        first_suit = cards[0].suit
        return all(card.suit == first_suit for card in cards)

    def get_hand_type(self, cards):
        if len(cards) != 5:
            return 0
        
        is_flush = self.is_flush(cards)
        is_straight = self.is_straight(cards)
        
        if is_straight and is_flush:
            return 3  # Straight Flush
        elif is_flush:
            return 2  # Flush
        elif is_straight:
            return 1  # Straight
        return 0

    def compare_five_cards(self, current_cards, last_cards):
        current_type = self.get_hand_type(current_cards)
        last_type = self.get_hand_type(last_cards)
        
        if current_type != last_type:
            return current_type > last_type
            
        if current_type == 2:  # Flush
            if current_cards[0].suit == last_cards[0].suit:
                current_highest = max(current_cards, key=lambda x: x.rank.value[1])
                last_highest = max(last_cards, key=lambda x: x.rank.value[1])
                return current_highest.rank.value[1] > last_highest.rank.value[1]
            return current_cards[0].suit.get_rank() > last_cards[0].suit.get_rank()
        elif current_type == 1:  # Straight
            current_highest = max(current_cards, key=lambda x: x.rank.value[1])
            last_highest = max(last_cards, key=lambda x: x.rank.value[1])
            if current_highest.rank == last_highest.rank:
                return current_highest.suit.get_rank() > last_highest.suit.get_rank()
            return current_highest.rank.value[1] > last_highest.rank.value[1]
        
        return False

    def is_valid_play(self, cards):
        if not cards:
            return False
            
        if not self.game_started:
            has_diamond_three = any(
                card.suit == Suit.DIAMONDS and card.rank == Rank.THREE 
                for card in cards
            )
            if not has_diamond_three:
                print("첫 플레이어는 다이아몬드3을 포함해야 합니다!")
                return False
            self.game_started = True
            return True
            
        if not self.last_play:
            return True
            
        if len(cards) != len(self.last_play):
            print("이전 플레이와 같은 수의 카드를 내야 합니다!")
            return False
            
        if len(cards) == 1:
            return max(cards, key=lambda x: x.get_value()).get_value() > \
                   max(self.last_play, key=lambda x: x.get_value()).get_value()
        elif len(cards) == 2:
            if cards[0].rank != cards[1].rank:
                print("페어는 같은 숫자의 카드 2장이어야 합니다!")
                return False
            return max(cards, key=lambda x: x.get_value()).get_value() > \
                   max(self.last_play, key=lambda x: x.get_value()).get_value()
        elif len(cards) == 5:
            current_type = self.get_hand_type(cards)
            last_type = self.get_hand_type(self.last_play)
            
            if current_type == 0:
                print("유효하지 않은 5장 카드 조합입니다!")
                return False
                
            if last_type == 0:
                print("이전 플레이어의 카드 조합이 유효하지 않습니다!")
                return False
            
            return self.compare_five_cards(cards, self.last_play)
        
        return False

    def draw_card(self, card: Card, x: int, y: int):
        color = GREEN if card.selected else WHITE
        pygame.draw.rect(self.screen, color, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(self.screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
        
        rank_text = self.font.render(card.rank.value[0], True, BLACK)
        self.screen.blit(rank_text, (x + 5, y + 5))
        
        suit_color = card.suit.value[1]
        suit_text = self.symbol_font.render(card.suit.value[0], True, suit_color)
        suit_x = x + (CARD_WIDTH - suit_text.get_width()) // 2
        suit_y = y + (CARD_HEIGHT - suit_text.get_height()) // 2
        self.screen.blit(suit_text, (suit_x, suit_y))
        
        self.screen.blit(rank_text, (x + CARD_WIDTH - 20, y + CARD_HEIGHT - 25))

    def draw(self):
        self.screen.fill(WHITE)
        
        for i, hand in enumerate(self.hands):
            y = 150 + i * 150
            if i == self.current_player:
                text = self.font.render(f"Player {i+1} (Current)", True, BLUE)
            else:
                text = self.font.render(f"Player {i+1}", True, BLACK)
            self.screen.blit(text, (10, y - 30))
            
            total_width = (len(hand) - 1) * (CARD_WIDTH + CARD_MARGIN) + CARD_WIDTH
            start_x = (WINDOW_WIDTH - total_width) // 2
            
            for j, card in enumerate(hand):
                x = start_x + j * (CARD_WIDTH + CARD_MARGIN)
                card.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
                self.draw_card(card, x, y)
        
        if self.last_play:
            text = self.font.render("Last Play:", True, BLACK)
            self.screen.blit(text, (10, 50))
            for i, card in enumerate(self.last_play):
                x = 150 + i * (CARD_WIDTH + 10)
                self.draw_card(card, x, 50)
        
        pygame.draw.rect(self.screen, BLUE, (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 100, 80, 40))
        play_text = self.font.render("Play", True, WHITE)
        self.screen.blit(play_text, (WINDOW_WIDTH - 180, WINDOW_HEIGHT - 90))
        
        pygame.draw.rect(self.screen, RED, (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100, 80, 40))
        pass_text = self.font.render("Pass", True, WHITE)
        self.screen.blit(pass_text, (WINDOW_WIDTH - 80, WINDOW_HEIGHT - 90))
        
        pygame.display.flip()

    def handle_click(self, pos):
        x, y = pos
        current_hand = self.hands[self.current_player]
        
        for card in reversed(current_hand):
            if card.rect.collidepoint(x, y):
                card.selected = not card.selected
                return
        
        if WINDOW_WIDTH - 200 <= x <= WINDOW_WIDTH - 120 and WINDOW_HEIGHT - 100 <= y <= WINDOW_HEIGHT - 60:
            self.play_selected()
        elif WINDOW_WIDTH - 100 <= x <= WINDOW_WIDTH - 20 and WINDOW_HEIGHT - 100 <= y <= WINDOW_HEIGHT - 60:
            self.pass_turn()

    def play_selected(self):
        selected = [card for card in self.hands[self.current_player] if card.selected]
        
        if not self.is_valid_play(selected):
            return
        
        for card in selected:
            self.hands[self.current_player].remove(card)
            
        self.last_play = selected
        self.last_player = self.current_player
        
        if not self.hands[self.current_player]:
            print(f"Player {self.current_player + 1} wins!")
            pygame.quit()
            return
        
        self.current_player = (self.current_player + 1) % 4
        
        for hand in self.hands:
            for card in hand:
                card.selected = False

    def pass_turn(self):
        if not self.game_started:
            print("첫 플레이어는 패스할 수 없습니다!")
            return
            
        if not self.last_play:
            print("새로운 라운드의 첫 플레이어는 패스할 수 없습니다!")
            return
            
        self.current_player = (self.current_player + 1) % 4
        
        if self.current_player == self.last_player:
            self.last_play = []
            self.last_player = None
            print("새로운 라운드가 시작됩니다!")
        
        for hand in self.hands:
            for card in hand:
                card.selected = False

def main():
    game = Game()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
        
        game.draw()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()