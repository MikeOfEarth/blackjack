# using https://www.deckofcardsapi.com/ as provided by Dylan Katina
# requests PIP install directions found online
import requests

class Player():
    
    def __init__(self):
        self.hand=[]
        self.chips=0
        self.bet=0
        self.hand_score=0
        self.bet=0
        self.busted=False
        self.blackjack=False
        self.stay=False

class Dealer(Player):
    
    def __init__(self):
        super().__init__()
        self.totalWin=False
        self.not_bust_counter=[]
        

class BlackJack():
    
    def __init__(self):
        self.deck_id=''
        self.player_list={}
        self.player_count=0
        self.deck_number=0
        self.play=True
        self.high_hand=None
        self.dealer=Dealer()
        self.current_player=0
        self.deck_remaining=0


    def setup(self):
        # this function runs once in the beginning of gameplay to create the deck and set player names and starting money
        print("")
        while True:
            initialize = input('Howdy partner, you ready to play some blackjack? Yes/No\t')
            if initialize == 'Yes' or initialize == 'yes':
                    while True:
                        players_num_ask = int(input('How many player\'s are joining?\t'))
                        if players_num_ask < 1:
                            print('At least one player must join')
                        elif players_num_ask >= 1:                            
                            print('Great!, we are just going to grab some info from each of the players\n')
                            for player_num in range(players_num_ask):
                                self.player_count+=1
                                player_name=input(f'What is player {self.player_count}\'s name?\t').title()
                                player_chips=int(input('And how much money in chips did you bring?\t$'))
                                self.player_list[player_name]=Player()
                                self.player_list[player_name].chips=player_chips
                            break
                    print(f"Great! {self.player_count} player(s) have joined the game.\n")
                    while self.deck_number == 0:
                        self.deck_number=int(input("Default BlackJack is played with 6 decks. How many would you like to play with today?\t"))
                    api_pull=requests.get(f'https://www.deckofcardsapi.com/api/deck/new/shuffle/?deck_count={self.deck_number}')
                    api_pull_converted=api_pull.json()
                    self.deck_id=api_pull_converted['deck_id']
                    print('Deck ready! Let\'s play!\n')
                    break                    
            elif initialize == 'No' or initialize == 'no':
                print('Welp, maybe next time, good luck out there.')
                break
            else:
                print('Whoops, wrong entry. Try again.\n')


    def take_bets(self):
        # this function takes bets (.bet) from available player funds (.chips)
        for player in self.player_list:
            still_betting=True
            print(f'{player}, you currently have ${self.player_list[player].chips}')
            while still_betting==True:                
                active_bet=int(input('How much do you want to bet on this round?\t$'))
                if active_bet<0:
                    print('Please make bet a positive number\n')
                elif active_bet==0:
                    print("Just playing for fun? That's fine but you won't win anything\n")
                    still_betting=False
                else:
                    if active_bet<=self.player_list[player].chips:
                        self.player_list[player].bet=active_bet
                        print(f"Awesome, {player} is in for ${self.player_list[player].bet}\n")
                        self.player_list[player].chips-=self.player_list[player].bet
                        still_betting=False
                    else:
                        print(f"Doesn't look like you have enough chips {player}.\n")
                        print(f"Please pick a bet for ${self.player_list[player].chips} or less.\n")
                    

    def reset(self,target):
        target.hand=[]
        target.busted=False
        target.blackjack=False
        target.stay=False
        target.hand_score=0

    def deal(self, dealt_player_num):
        # this function has been separated from hit to decrease the api pulls, setting up the first hand with only one and hopefully 
        # speeding up programmed play. Otherwise I would use this function nested for both deal and hit actions with different end values.        
        self.high_hand=0
        deal_value=0
        initial_deal=2+(dealt_player_num*2)
        api_pull=requests.get(f'https://www.deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={initial_deal}')
        api_pull_converted=api_pull.json()
        current_deal=api_pull_converted
        for player in self.player_list.keys():        
            self.current_player=player
            game.reset(self.player_list[player])
            self.player_list[player].hand.append(current_deal['cards'][deal_value])
            self.player_list[player].hand.append(current_deal['cards'][(deal_value+dealt_player_num)])
            game.count(self.player_list[player])
            deal_value+=1   
        self.current_player='Dealer'
        game.reset(self.dealer)
        self.dealer.hand.append(current_deal['cards'][deal_value])
        game.count(self.dealer)
        self.dealer.hand.append(current_deal['cards'][deal_value+dealt_player_num])
        deal_value+=1
        

    def count(self, target):
        # this method prints out player hands and calculates results
        print(f'{self.current_player}\'s hand...')
        target.norm_score=0
        target.ace_score=0
        for n in range(len(target.hand)):
            value=target.hand[n]['value']
            suit=target.hand[n]['suit']
            if value=='JACK' or value =='QUEEN' or value=='KING':
                target.norm_score+=10
                target.ace_score+=10
            elif value=='ACE':
                target.ace_score=target.ace_score+1
                target.norm_score+=11
            else:
                target.ace_score+=int(value)
                target.norm_score+=int(value)

            print(f'[{value} of {suit}]')
        
        if target.norm_score==21 or target.ace_score==21:
            print('BLACKJACK! Nice pull.\n')
            target.blackjack=True
            target.hand_score=21
            self.high_hand=target.hand_score
        else:
            if target.norm_score>21 and target.ace_score >21:
                target.hand_score=target.ace_score
                print(f'BUSTED. Better luck next time.\n')
                target.busted=True
            elif target.norm_score==target.ace_score:
                target.hand_score=target.norm_score
            elif target.norm_score > 21 and target.ace_score<=21:
                target.hand_score=target.ace_score
            elif target.norm_score <= 21:
                target.hand_score=target.norm_score
            print(f'For a total of {target.hand_score}\n')
        

    def hitter(self,target):
        # this method allows players to take a new card if not blackjack or busted and uses .counter to calculate results
        print(f'{self.current_player}\'s Turn...\n')
        self.count(target)
        while not target.busted and not target.blackjack and not target.stay:
            
            hit_ask=input(f'Does {self.current_player} want another card? Y/N\t')
            print("")
            if hit_ask=='Y' or hit_ask=='y':
                api_pull=requests.get(f'https://www.deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=1')
                api_pull_converted=api_pull.json()
                current_hit=api_pull_converted
                target.hand.append(current_hit['cards'][0])
                self.count(target)
            elif hit_ask=='N' or hit_ask=='n':
                target.stay=True
            else:
                print('Whoops, wrong entry. Try again.\n')
            
    def endTurn(self):
        # this method executes the dealer's final turn with casino hitting logic and tests if dealer hand beats all player hands
        self.dealer.totalWin=False
        self.dealer.not_bust_counter=[]
        print(f'{self.current_player}\'s Turn...\n')
        self.count(self.dealer)
        for player in self.player_list:
            if self.player_list[player].busted == False:
                self.dealer.not_bust_counter.append(1)
                if self.player_list[player].hand_score>self.high_hand:
                    self.high_hand=self.player_list[player].hand_score
        if self.dealer.hand_score>self.high_hand or len(self.dealer.not_bust_counter) == 0:
            self.dealer.totalWin=True
        while True:
            if not self.dealer.busted and not self.dealer.blackjack and not self.dealer.stay and not self.dealer.totalWin:
                if self.dealer.hand_score<=self.high_hand and self.dealer.hand_score<=16:
                    print('Dealer will hit...')
                    api_pull=requests.get(f'https://www.deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=1')
                    api_pull_converted=api_pull.json()
                    current_hit=api_pull_converted
                    self.dealer.hand.append(current_hit['cards'][0])
                    game.count(self.dealer)
                else:
                    self.dealer.stay=True
            else:
                break

    def payout(self, target, ratio, bet):
        # this method calculates proper returns to winners
        target.chips+=(bet*ratio)


    def winners(self):
        # this method works in tandem with the payout method to decide winners and proper returns to betting players
        if self.dealer.totalWin:
            print('Dealer takes all')
            for player in self.player_list:            
                print(f"{player} loses ${self.player_list[player].bet}")
            print("Better luck next hand\n")
        elif self.dealer.busted:
            for player in self.player_list:
                if self.player_list[player].busted:
                    print(f"{player} BUSTED and lost ${self.player_list[player].bet}. Better luck next hand!\n")
                elif self.player_list[player].blackjack:                         
                    print(f"{player} hit BLACKJACK while Dealer BUSTED. 3:1 payout on ${self.player_list[player].bet} for ${self.player_list[player].bet*3}\n")
                    game.payout(self.player_list[player],3,self.player_list[player].bet)
                else:
                    print(f"Dealer BUSTED! {player} wins 2:1 payout on ${self.player_list[player].bet} for ${self.player_list[player].bet*2}\n")
                    game.payout(self.player_list[player],2,self.player_list[player].bet)
        elif self.dealer.blackjack:
            for player in self.player_list:
                if self.player_list[player].blackjack:
                    print(f"{player}'s hand is a push from blackjack tie with dealer. Return ${self.player_list[player].bet}\n")
                    game.payout(self.player_list[player],1,self.player_list[player].bet)
                else:
                    print(f"Dealer hit BLACKJACK. {player} lost ${self.player_list[player].bet}. Better luck next hand!\n")                        
        else:
            for player in self.player_list:
                if self.player_list[player].blackjack:                         
                    print(f"{player} hit BLACKJACK! 3:1 payout on ${self.player_list[player].bet} for ${self.player_list[player].bet*3}\n")
                    game.payout(self.player_list[player],3,self.player_list[player].bet)
                elif self.player_list[player].busted:
                    print(f"{player} BUSTED and lost ${self.player_list[player].bet}. Better luck next hand!\n")
                elif self.player_list[player].hand_score<self.dealer.hand_score:
                    print(f"{player} was beat by dealer's hand and lost ${self.player_list[player].bet}. Better luck next hand!\n")
                elif self.player_list[player].hand_score>self.dealer.hand_score:                    
                    print(f"{player} beat dealer's hand! 2:1 payout on ${self.player_list[player].bet} for ${self.player_list[player].bet*2}\n")
                    game.payout(self.player_list[player],2,self.player_list[player].bet)
                else:
                    print(f"{player}'s hand is a push from tie with dealer. Return ${self.player_list[player].bet}")
                    game.payout(self.player_list[player],1,self.player_list[player].bet)

    def playBlackjack(self):
        # this method controls the flow of the game
        game.setup()
        while self.play:
            game.take_bets()
            game.deal(self.player_count)
            for player in self.player_list.keys():
                self.current_player=player
                game.hitter(self.player_list[player])
            self.current_player='Dealer'
            game.endTurn()
            game.winners()
            play=input('Would you like to play again? Y/N\t')
            if play=='Y' or play=='y':
                self.play=True
                print("")
            elif play=='N' or play=='n':
                self.play=False
                print('Thanks for playing.\n')
                for player in self.player_list:
                    print(f'{player} is leaving the table ${self.player_list[player].chips}')
                print('Please tip your dealer and cash out at the Cashiers booth.\n')
            else:
                print('Whoops, wrong entry. Try again.\n')

game=BlackJack()
game.playBlackjack()