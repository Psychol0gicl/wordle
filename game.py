import sys
from multiprocessing import Pool, cpu_count
import os
import time
from collections import Counter, defaultdict
import math
from statistics import mean, median, mode, stdev

import numpy as np
GREEN_SQUARE = "\U0001F7E9"
YELLOW_SQUARE = "\U0001F7E8"
GREY_SQUARE = "\u2B1C"

RESULT_FOLDER = "results"
os.makedirs(RESULT_FOLDER, exist_ok=True)
class Game:
    def __init__(self):
        self.common_words = self.load_words("wordle-answers-alphabetical.txt")
        self.all_words  =self.load_words("valid-wordle-words.txt") 

        self.weights = np.array([self.weight_function(word) for word in self.all_words])
        total_weight = self.weights.sum()
        probabilities = self.weights / total_weight
        self.secret_word = np.random.choice(self.all_words, p=probabilities)
        # self.secret_word = "SHADE"
        # self.secret_word = "SOARE"
        # self.secret_word = "WRICK" # good for checking choosing words in the common word list
        # self.secret_word = "TANIA" # Causes errors, because yellow feedback is not working well.
        self.secret_word = self.secret_word.upper()
        # print(f"SHHH! Secret word for debugging: {self.secret_word}")
        self.check_letters_secret_word()
        # print(self.weight_function(self.secret_word))
        self.game_is_over = False
        self.guess_history = []
        self.game_result = ""
        # print(self.guess_history)

        # self.game_loop()
        pass

    def load_words(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            words = [line.strip().upper() for line in file if line.strip()]
        return words
    
    def check_game_over(self):
        if len(self.guess_history) == 6 and self.game_result == "":
            print("Game Over! You ran out of guesses.")
            self.game_is_over = True
            self.game_result = "L"
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
    
            print(f"{GREEN_SQUARE}"*5)
            print(f"You won! Amount of guesses: {self.get_guess_count()}")
            self.game_result = "W"
            self.game_is_over = True
            return None
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
            if feedback is not None:
                bot.receive_feedback(feedback)
                print(feedback+"\n" + "-"*25)



    def reset_game(self, new_word):
        self.game_is_over = False
        self.game_result = ""
        self.guess_history = []
        self.secret_word = new_word
        self.check_letters_secret_word()

        
    # def test_bot(self, word_list,bot_class, file_name = None):
    #     print(f"Testing bot: {bot_class.__name__}")

    #     results = {"W": 0, "L": 0}
    #     if file_name:
    #         sys.stdout = open(file_name, 'w', encoding='utf-8')


    #     for word in word_list:
    #         bot = bot_class(self, self.all_words, self.common_words)
    #         print(f"Testing word: {word} ")
    #         self.reset_game(word)
    #         self.game_loop_bot(bot)
    #         results[word] = self.get_guess_count()
    #         results[self.game_result] += 1
    #     print("Testing bot class: " + bot_class.__name__ + " complete.")
    #     return results
    

    def test_bot(self, word_list, bot_class, file_name=None):
        results = {"W": 0, "L": 0}
        total_start = time.time()  # Start total timer

        # os.makedirs(str(bot_class.__name__), exist_ok=True)
        folder_path = f"{RESULT_FOLDER}/{str(bot_class.__name__)}"
        os.makedirs(folder_path, exist_ok=True)  # creates folder_path and parents if not exist

        if file_name:
            sys.stdout = open(f"{folder_path}/{file_name}", 'w', encoding='utf-8')

        print(f"Testing bot: {bot_class.__name__}")



        for word in word_list:
            word_start = time.time()  # Start per-word timer

            bot = bot_class(self, self.all_words, self.common_words)
            print("\n" + "-"*50)
            print(f"Testing word: {word}")
            self.reset_game(word)
            self.game_loop_bot(bot)

            word_time = time.time() - word_start
            print(f"Time taken for '{word}': {word_time:.4f} seconds")

            results[word] = {
                "guesses": self.get_guess_count(),
                "time": word_time
            }
            results[self.game_result] += 1

        total_time = time.time() - total_start
        print(f"\nTotal time for {len(word_list)} words: {total_time:.2f} seconds")
        print("Testing bot class: " + bot_class.__name__ + " complete.")
        sys.stdout = open(f"{folder_path}/results_only.txt", 'w', encoding='utf-8')
        analyze_guess_data(results)

        # return results



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
            if chosen_word_score - word_plus_score[1] > chosen_word_score/10 and self.game.get_guess_count() <= 2:
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




class EntropyWordleBot(WordleBot):  
    def __init__(self, game, word_list, common_words):
        super().__init__(game, word_list, common_words)
        initial_entropy = math.log2(len(word_list))
        # print(f"Initial entropy: {initial_entropy}")




        
        
    def get_feedback(self, guess_word, secret_word):
        temp_letters_secret_word = {}
        for c in secret_word:
            temp_letters_secret_word[c] = temp_letters_secret_word.get(c, 0) + 1

        feedback = [f"{GREY_SQUARE}"] * 5

        # First pass: Green
        for i in range(5):
            if guess_word[i] == secret_word[i]:
                feedback[i] = GREEN_SQUARE
                temp_letters_secret_word[guess_word[i]] -= 1

        # Second pass: Yellow
        for i in range(5):
            if feedback[i] == GREEN_SQUARE:
                continue
            if guess_word[i] in temp_letters_secret_word and temp_letters_secret_word[guess_word[i]] > 0:
                feedback[i] = YELLOW_SQUARE
                temp_letters_secret_word[guess_word[i]] -= 1

        return ''.join(feedback)

    def compute_entropy(self, guess):
        feedback_counts = {}
        total = len(self.candidates)
        # print(f"Total words: {total}")

        for word in self.candidates:
            feedback = self.get_feedback(guess, word)
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1

        entropy = 0.0
        
        for count in feedback_counts.values():
            probability = count / total
            entropy -= probability * math.log2(probability)

        return entropy

    def choose_guess(self):
        top_guesses: list = []

        print("\nThe bot is making a guess...")
        if game.get_guess_count() == 0:
            # print(f"Candidates after choosing: {len(self.candidates)}")
            print("First guess by a human: SPEAR")

            return "SPEAR"
        best_word = ""
        best_entropy = -1
        
        entropy_list = []
        for word in self.candidates:
            entropy = self.compute_entropy(word)
            # if entropy > best_entropy:
            #     best_word = word
            #     best_entropy = entropy
            entropy_list.append((word, entropy))
        entropy_list.sort(key=lambda x: x[1], reverse=True)
        top_guesses.extend(entropy_list[:10])
        best_word, best_entropy = top_guesses[0]
        print(f"Initial guess by the bot: {best_word} with entropy: {best_entropy:.4f}")
        for word_plus_entropy in top_guesses[:10]:
            if best_entropy - word_plus_entropy[1] > best_entropy/10 and self.game.get_guess_count() <= 2:
                continue
            if word_plus_entropy[0] in self.common_words:
                best_word = word_plus_entropy[0]
                best_entropy = word_plus_entropy[-1]
                break

        print(f"Bot chose: {best_word} with entropy: {best_entropy:.4f}")
        print(f"Top ten guesses: {top_guesses}")
        return best_word        

    def receive_feedback(self, feedback):
        prior_entropy = math.log2(len(self.candidates))
        self.filter_candidates(self.guess_history[-1], feedback)
        posterior_entropy = math.log2(len(self.candidates)) if self.candidates else 0
        actual_info_gain = prior_entropy - posterior_entropy
        
        print(f"Guess: {self.guess_history[-1]}, Feedback: {feedback}, Actual Info Gain: {actual_info_gain:.4f} bits")
        print(f"Posterior entropy: {posterior_entropy}")



    



# def analyze_guess_data(guess_data):
#     print("")
#     print("-"*50)
#     print("")
#     print("-"*50)
#     print("")
#     print("-"*50)
#     print("RESULTS:")
#     if not guess_data:
#         print("No data to analyze.")

#         return

#     guess_counts = list(guess_data.values())

#     # Basic statistics
#     avg = mean(guess_counts)
#     med = median(guess_counts)
#     try:
#         mod = mode(guess_counts)
#     except:
#         mod = "No unique mode"
#     minimum = min(guess_counts)
#     maximum = max(guess_counts)
#     stddev = stdev(guess_counts) if len(guess_counts) > 1 else 0

#     print(f"Total words: {len(guess_data)}")
#     print(f"Mean guesses: {avg:.2f}")
#     print(f"Median guesses: {med}")
#     print(f"Mode guesses: {mod}")
#     print(f"Min guesses: {minimum}")
#     print(f"Max guesses: {maximum}")
#     print(f"Standard deviation: {stddev:.2f}")
#     print(f"Games won: {guess_data['W']}")
#     print(f"Win percentage: {guess_data['W']/len(guess_data)*100:.2f}%")
#     print(f"Games lost: {guess_data['L']}")

#     # Optional: histogram of frequencies
#     freq = Counter(guess_counts)
#     print("\nGuess count frequencies:")
#     for guess_num in sorted(freq):
#         print(f"{guess_num} guesses: {freq[guess_num]} word(s)")

def analyze_guess_data(guess_data):
    print("\n" + "-"*50 + "\n" + "-"*50 + "\n" + "-"*50)
    print("RESULTS:")

    if not guess_data:
        print("No data to analyze.")
        return

    # Extract valid entries, skip "W" and "L"
    guess_entries = [
        data for word, data in guess_data.items()
        if word not in ("W", "L") and isinstance(data, dict)
    ]

    if not guess_entries:
        print("No valid guess data to analyze.")
        return

    guess_counts = [entry["guesses"] for entry in guess_entries]
    time_taken = [entry["time"] for entry in guess_entries]

    # Guess statistics
    avg_guesses = mean(guess_counts)
    med_guesses = median(guess_counts)
    try:
        mod_guesses = mode(guess_counts)
    except:
        mod_guesses = "No unique mode"
    min_guesses = min(guess_counts)
    max_guesses = max(guess_counts)
    stddev_guesses = stdev(guess_counts) if len(guess_counts) > 1 else 0

    # Time statistics
    avg_time = mean(time_taken)
    med_time = median(time_taken)
    try:
        mod_time = mode(time_taken)
    except:
        mod_time = "No unique mode"
    min_time = min(time_taken)
    max_time = max(time_taken)
    stddev_time = stdev(time_taken) if len(time_taken) > 1 else 0
    total_time = sum(time_taken)

    # Win/loss
    wins = guess_data.get("W", 0)
    losses = guess_data.get("L", 0)
    total_words = len(guess_counts)

    # Output
    print(f"Total words: {total_words}")
    print(f"Games won: {wins}")
    print(f"Win percentage: {wins / total_words * 100:.2f}%")
    print(f"Games lost: {losses}")

    print("\nGuess Statistics:")
    print(f"Mean guesses: {avg_guesses:.2f}")
    print(f"Median guesses: {med_guesses}")
    print(f"Mode guesses: {mod_guesses}")
    print(f"Min guesses: {min_guesses}")
    print(f"Max guesses: {max_guesses}")
    # print(f"Standard deviation: {stddev_guesses:.2f}")

    freq = Counter(guess_counts)
    print("\nGuess count frequencies:")
    for guess_num in sorted(freq):
        print(f"{guess_num} guesses: {freq[guess_num]} word(s)")

    print("\nTime Statistics (seconds):")
    print(f"Total time: {total_time:.2f} seconds")
    if total_time > 60:
        print(f"Total time: {total_time/60:.2f} minutes")
    print(f"Mean time: {avg_time:.2f} seconds per guess")
    print(f"Median time: {med_time:.2f} seconds per guess")
    print(f"Mode time: {mod_time} seconds per guess")
    print(f"Min time: {min_time:.2f}")
    print(f"Max time: {max_time:.2f}")

    print("\n" + "-"*50 + "\n" + "-"*50 + "\n" + "-"*50)
    # print(f"Standard deviation: {stddev_time:.2f}")

    # Optional: histogram of frequencies



bot = WordleBot(game, game.all_words, game.common_words)
# game.game_loop_bot(bot)
# results = game.test_bot(game.all_words,WordleBot, "most_basic_bot_all_words.txt")
# results = game.test_bot(game.common_words, WordleBot, "most_basic_bot_common_words.txt")





EntropyBot = EntropyWordleBot(game, game.all_words, game.common_words)
# game.game_loop_bot(EntropyBot)

# results = game.test_bot(game.all_words,EntropyBot, "entropy_bot_all_words.txt")
results = game.test_bot(game.common_words, EntropyWordleBot, "entropy_bot_common_words.txt")
