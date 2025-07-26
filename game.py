import numpy as np
GREEN_SQUARE = "\U0001F7E9"
YELLOW_SQUARE = "\U0001F7E8"
GREY_SQUARE = "\u2B1C"

class Game:
    def __init__(self):
        self.common_words = self.load_words("wordle-answers-alphabetical.txt")
        self.all_words  =self.load_words("valid-wordle-words.txt") 

        self.weights = np.array([self.weight_function(word) for word in self.all_words])
        total_weight = self.weights.sum()
        probabilities = self.weights / total_weight
        self.secret_word = np.random.choice(self.all_words, p=probabilities)
        self.secret_word = "SOARE"
        self.secret_word = "TANIA" # Causes errors, because yellow feedback is not working well.
        self.secret_word = self.secret_word.upper()
        print(self.weight_function(self.secret_word))
        self.game_is_over = False
        self.guess_history = []
        print(self.guess_history)

        # self.game_loop()
        pass

    def load_words(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            words = [line.strip().upper() for line in file if line.strip()]
        return words
    
    def check_game_over(self):
        if len(self.guess_history) == 6:
            self.game_is_over = True
        return self.game_is_over
    

    
    def weight_function(self,word):
        if word in self.common_words:
            return 25
        else:
            return 1



    # def guess(self,word):
    #     word = word.upper()
    #     if len(word) != 5:
    #         print("Word must be 5 letters long.")
    #         return 0
    #     if word not in self.all_words:
    #         print("Word not in word list.")
    #         return 0
        
    #     for i in range(5):
    #         if word[i] == self.secret_word[i]:
    #             print(GREEN_SQUARE, end="")
    #         elif word[i] in self.secret_word:
    #             print(YELLOW_SQUARE, end="")
    #         else:
    #             print(GREY_SQUARE, end="")
    #     print("")
    #     if word == self.secret_word:
    #         return -1
    #     return 1

    def guess(self,word):
        word = word.upper()
        if len(word) != 5:
            print("Word must be 5 letters long.")
            return
        if word not in self.all_words:
            print("Word not in word list.")
            return
        feedback = ""
        self.guess_history.append(word)
        if word == self.secret_word:
            self.game_is_over = True
        self.check_game_over()
        
        for i in range(5):
            if word[i] == self.secret_word[i]:
                # print(GREEN_SQUARE, end="")
                feedback += GREEN_SQUARE 
            elif word[i] in self.secret_word:   
                # print(YELLOW_SQUARE, end="")
                amount_of_yellow = 0
                for j in range(5):
                    if word[i] == self.secret_word[j] and word[j] != self.secret_word[j]:
                        amount_of_yellow += 1
                # print(f"amount_of_yellow: {amount_of_yellow}")
                
                in_loop = False
                for j in range(amount_of_yellow):
                    in_loop = True
                    
                    # print(YELLOW_SQUARE, end="")
                    feedback += YELLOW_SQUARE 
                    amount_of_yellow -= 1
                if amount_of_yellow == 0 and in_loop == False:
                    # print(GREY_SQUARE, end="")
                    feedback += GREY_SQUARE

            else:
                # print(GREY_SQUARE, end="")
                feedback += GREY_SQUARE
        return feedback

    # np.random.shuffle(all_words)


    def game_loop(self):
        while(True):
            if self.check_game_over():
                return
            guess = input("Enter your guess: \n")
            guess = guess.upper()
            feedback = self.guess(guess)
            if feedback is not None:
                print(feedback)

    def game_loop_bot(self, bot):
        while(True):
            if self.check_game_over():
                return
            guess = bot.choose_guess()

            guess = guess.upper()
            bot.guess_history.append(guess)

            feedback = self.guess(guess)
            bot.receive_feedback(feedback)
            if feedback is not None:
                print(feedback)

game = Game()
# game.game_loop()


class WordleBot:
    def __init__(self, game, word_list):
        self.game = game
        self.all_words = word_list[:]
        # print(len(self.all_words))
        self.candidates = word_list[:]
        self.guess_history = []
        pass



    def choose_guess(self):
        from collections import Counter

        letter_counts = Counter(''.join(self.candidates))
        scored = [(word, sum(letter_counts[c] for c in set(word))) for word in self.candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        print(scored[:10])
        word_plus_score = scored[0]
        return word_plus_score[0]
    
    def filter_candidates(self, guess, feedback):
        def valid(word):

            matched = [False] * 5
            for i in range(5): # handling green
                if feedback[i] == GREEN_SQUARE:
                    if word[i] != guess[i]:
                        return False
                    matched[i] = True

            for i in range(5):
                if feedback[i] == YELLOW_SQUARE:
                    if guess[i] not in word:
                        return False
                    if word[i] == guess[i]:
                        return False
                    # Must check that there's an unmatched occurrence
                    found = False
                    for j in range(5):
                        if not matched[j] and word[j] == guess[i] and guess[j] != word[j]:
                            matched[j] = True
                            found = True
                            break
                    if not found:
                        return False

            # Third pass: handle black/gray
            for i in range(5):
                if feedback[i] not in {GREEN_SQUARE, YELLOW_SQUARE}:
                    # Count how many times guess[i] occurs in feedback as G/Y
                    allowed_count = sum(1 for j in range(5) if guess[j] == guess[i] and feedback[j] in {GREEN_SQUARE, YELLOW_SQUARE})
                    if word.count(guess[i]) > allowed_count:
                        return False

            return True

        self.candidates = [word for word in self.candidates if valid(word)]
        # print("SOARE" in self.candidates)
        # print(len(self.candidates))


    def receive_feedback(self, feedback):
        self.filter_candidates(self.guess_history[-1], feedback)
    

bot = WordleBot(game, game.all_words)
# print(bot.choose_guess())

game.game_loop_bot(bot)