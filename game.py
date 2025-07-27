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
        # self.secret_word = "VAUNT"
        # self.secret_word = "SOARE"
        # self.secret_word = "WRICK" # good for checking choosing words in the common word list
        # self.secret_word = "TANIA" # Causes errors, because yellow feedback is not working well.
        self.secret_word = self.secret_word.upper()
        print(f"SHHH! Secret word for debugging: {self.secret_word}")
        self.check_letters_secret_word()
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
    
    def get_guess_count(self):
        return len(self.guess_history)

    def check_letters_secret_word(self):
        self.secret_word_letters = {}
        for c in self.secret_word:
            self.secret_word_letters[c] = self.secret_word_letters.get(c, 0) + 1




    

    
    def weight_function(self,word):
        if word in self.common_words:
            return 25
        else:
            return 1








    def guess(self, guess_word):
        guess_word = guess_word.upper()
        if len(guess_word) != 5:
            print("Word must be 5 letters long.")
            return
        if guess_word not in self.all_words:
            print("Word not in word list.")
            return
        feedback = ""
        self.guess_history.append(guess_word)
        if guess_word == self.secret_word:

            print(f"\nYou won! Amount of guesses: {self.get_guess_count()}")
            self.game_is_over = True
        self.check_game_over()

        temp_letters_word = {}
        for c in guess_word:
            temp_letters_word[c] = temp_letters_word.get(c, 0) + 1
        

        temp_letters_secret_word  =self.secret_word_letters.copy()
        # print(f"Letters guess word: {temp_letters_word}")
        # print(f"Letters secret word: {temp_letters_secret_word}")
        # feedback = f"{GREY_SQUARE*5}" 
        feedback = ['⬜'] * 5
        for i in range(5):
            if guess_word[i] == self.secret_word[i]:
                feedback[i] = GREEN_SQUARE
                temp_letters_secret_word[guess_word[i]] -= 1

        # Second pass: Handle YELLOW_SQUARE
        for i in range(5):
            if feedback[i] == GREEN_SQUARE:
                continue
            if guess_word[i] in temp_letters_secret_word and temp_letters_secret_word[guess_word[i]] > 0:
                feedback[i] = YELLOW_SQUARE
                temp_letters_secret_word[guess_word[i]] -= 1
            


        # print(f"Letters guess word after adjusting {temp_letters_word}")
        # print(f"Letters secret word after adjusting: {temp_letters_secret_word}")

                





        feedback_str = ''.join(feedback)

        return feedback_str



    def game_loop(self):
        while(True):
            if self.check_game_over():
                print("Game over!")
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
    def __init__(self, game, word_list, common_words):
        self.game = game
        self.all_words = word_list[:]
        self.common_words = common_words[:]
        # print(len(self.all_words))
        self.candidates = word_list[:]
        self.guess_history = []
        pass



    def choose_guess(self):
        from collections import Counter

        letter_counts = Counter(''.join(self.candidates))
        scored = [(word, sum(letter_counts[c] for c in set(word))) for word in self.candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_word_plus_score = scored[0]
        chosen_word = top_word_plus_score[0]
        chosen_word_score = top_word_plus_score[1]
        print(f"The bot originally chose: {chosen_word} ")
        print(f"The top ten guesses and scores: {scored[:10]}")
        for word_plus_score in scored[:10]:
            if chosen_word_score - word_plus_score[1] > chosen_word_score/10 and self.game.get_guess_count <= 2:
                continue
            if word_plus_score[0] in self.common_words:
                chosen_word = word_plus_score[0]
                break

        # return "AAPAS"
        print(f"The bot finally chose: {chosen_word} ")


        return chosen_word 
    
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
    

bot = WordleBot(game, game.all_words, game.common_words)
# print(bot.choose_guess())

game.game_loop_bot(bot)