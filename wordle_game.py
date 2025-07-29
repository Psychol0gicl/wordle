import sys
import json
from datetime import datetime
from functools import lru_cache
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
class WordleGame:
    def __init__(self):
        # self.common_words = self.load_words("wordle-answers-alphabetical.txt")
        self.common_words = self.load_words_json("word-data.json")

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
        self.feedback_history = []
        self.game_result = ""
        # print(self.guess_history)

        # self.game_loop()
        pass

    def load_words_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        words = [word.upper() for word in data["common"]]
        return words
    
    import json


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
            feedback = f"{GREEN_SQUARE*5}"
            self.feedback_history.append(feedback)
            # print(feedback)

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
            self.feedback_history.append(feedback)
            # if feedback is not None:
            #     print(feedback)

    def game_loop_bot(self, bot):
        while(True):
            if self.check_game_over():
                return
            guess = bot.choose_guess()

            guess = guess.upper()
            bot.guess_history.append(guess)

            feedback = self.guess(guess)
            if feedback is not None:
                self.feedback_history.append(feedback)
                bot.receive_feedback(feedback)
                # print(feedback+"\n" + "-"*25)
                print("-"*10)

    def set_secret_word(self, word):
        self.secret_word = word
        self.check_letters_secret_word()

    def let_bot_guess_a_word(self, bot, word = None):


        print(f"\nBot: {bot.__class__.__name__} guessing the word: {word}")
        if word is None:
            print("Please provide a word to guess.")
            return
        self.set_secret_word(word)
        while(True):
            if self.check_game_over():
                break
            guess = bot.choose_guess()

            guess = guess.upper()
            bot.guess_history.append(guess)

            feedback = self.guess(guess)
            if feedback is not None:
                self.feedback_history.append(feedback)
                bot.receive_feedback(feedback)
                # print(feedback+"\n" + "-"*25)
                print("-"*10)
        print("\n" + "=" * 35 + "\nHistory:")
        for i  in range(self.get_guess_count()):
            print(f"Guess: {to_fancy(self.guess_history[i])}, Feedback: {self.feedback_history[i]}")
        print("=" * 35)


    def reset_game(self, new_word):
        self.game_is_over = False
        self.game_result = ""
        self.guess_history = []
        self.feedback_history = []
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
    
    def print_guess_history(self):
        print("\n" + "=" * 35 + "\nHistory:")
        for i  in range(self.get_guess_count()):
            print(f"Guess: {to_fancy(self.guess_history[i])}, Feedback: {self.feedback_history[i]}")
        print("=" * 35)

    def test_bot(self, word_list, bot_class, file_name=None):
        results = {"W": 0, "L": 0}
        total_start = time.time()  # Start total timer

        # os.makedirs(str(bot_class.__name__), exist_ok=True)
        folder_path = f"{RESULT_FOLDER}/{str(bot_class.__name__)}"
        os.makedirs(folder_path, exist_ok=True)  # creates folder_path and parents if not exist
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = f"{folder_path}/{timestamp}"
        os.makedirs(folder_path, exist_ok=True)

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



    def test_bot_optimized_x_words(self, word_list, bot_class, x: int = 500, file_name=None):
        # RANDOM_SEED = 42
        # np.random.seed(RANDOM_SEED)
        results = {"W": 0, "L": 0}
        total_start = time.time()
        
        folder_path = f"{RESULT_FOLDER}/{str(bot_class.__name__)}"
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_path = f"{folder_path}/{timestamp}"
        os.makedirs(folder_path, exist_ok=True)
        
        if file_name:
            filename_without_ext = os.path.splitext(os.path.basename(file_name))[0]
            sys.stdout = open(f"{folder_path}/{filename_without_ext}_{str(x)}_words.txt", 'w', encoding='utf-8')
        
        print(f"Testing bot: {bot_class.__name__}")
        
        # Create bot instance ONCE before the loop
        print("Initializing bot (this may take a few minutes for optimized bots)...")
        init_start = time.time()
        bot = bot_class(self, self.all_words, self.common_words)
        init_time = time.time() - init_start
        print(f"Bot initialization completed in {init_time:.2f} seconds")

        np.random.shuffle(word_list)
        if x < 0:
            word_list_x_words = word_list
        else:
            word_list_x_words = word_list[:x]

        
        for word in word_list_x_words:
            word_start = time.time()
            
            print("\n" + "-"*100)
            print(f"___ Testing word: {to_fancy(word )} ___\n")

            
            # Reset the game state
            self.reset_game(word)
            
            # Reset the bot state for new game (but keep precomputed data)
            bot.reset_for_new_game()
            
            # Run the game
            self.game_loop_bot(bot)

            self.print_guess_history()
            word_time = time.time() - word_start
            print(f"Time taken for '{word}': {word_time:.4f} seconds")
            
            results[word] = {
                "guesses": self.get_guess_count(),
                "time": word_time
            }
            results[self.game_result] += 1
        
        total_time = time.time() - total_start
        print(f"\nTotal time for {len(word_list)} words: {total_time:.2f} seconds")
        print(f"Average time per word: {(total_time-init_time)/len(word_list):.4f} seconds")
        print("Testing bot class: " + bot_class.__name__ + " complete.")
        
        sys.stdout = open(f"{folder_path}/results_only_{str(x)}_words.txt", 'w', encoding='utf-8')
        analyze_guess_data(results)



    def test_every_bot_on_a_single_word(self, secret_word, bot_classes, file_name: str = None): 
        if file_name:

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_path = f"{RESULT_FOLDER}/single_word_tests/{secret_word}"
            os.makedirs(folder_path, exist_ok=True)
            file_name_without_ext = os.path.splitext(os.path.basename(file_name))[0]
            file_name = f"{folder_path}/{file_name_without_ext}_{timestamp}.txt"
            sys.stdout = open(file_name, 'w', encoding='utf-8')
        self.set_secret_word(secret_word)
        for bot_class in bot_classes:
            print(f"Testing bot: {bot_class.__name__}")
            print(f"___ Testing word: {to_fancy(secret_word )} ___\n")
            bot = bot_class(self, self.all_words, self.common_words)
            self.game_loop_bot(bot)
            self.print_guess_history()
            self.reset_game(secret_word)
            print("Testing bot class: " + bot_class.__name__ + " complete.")
            print("\n" + "-"*100)



    def compute_entropy_fast(self, guess):
        """Fast approximate entropy using sampling"""
        sample = self._sample_candidates()
        
        feedback_counts = defaultdict(int)
        for word in sample:
            feedback = self.get_feedback(guess, word)
            feedback_counts[feedback] += 1
        
        total = len(sample)
        entropy = 0.0
        
        for count in feedback_counts.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def choose_guess(self):
        if self.game.get_guess_count() == 0:
            return "SOARE"
        
        # Use hybrid approach: exact calculation for small sets, sampling for large
        if len(self.candidates) <= 20:
            # Use exact calculation
            return super().choose_guess() if hasattr(super(), 'choose_guess') else self.candidates[0]
        
        # Use sampling for speed
        candidate_pool = self._get_candidate_pool() if hasattr(self, '_get_candidate_pool') else self.candidates[:50]
        
        best_word = ""
        best_entropy = -1
        
        for word in candidate_pool:
            entropy = self.compute_entropy_fast(word)
            if entropy > best_entropy:
                best_word = word
                best_entropy = entropy
        
        return best_word




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
    sys.stdout = sys.__stdout__
    # print(f"Standard deviation: {stddev_time:.2f}")

    # Optional: histogram of frequencies


def to_fancy(text):
    if sys.stdout is sys.__stdout__:
        return text

    fancy_map = {
        'A': '𝘼', 'B': '𝘽', 'C': '𝘾', 'D': '𝘿', 'E': '𝙀',
        'F': '𝙁', 'G': '𝙂', 'H': '𝙃', 'I': '𝙄', 'J': '𝙅',
        'K': '𝙆', 'L': '𝙇', 'M': '𝙈', 'N': '𝙉', 'O': '𝙊',
        'P': '𝙋', 'Q': '𝙌', 'R': '𝙍', 'S': '𝙎', 'T': '𝙏',
        'U': '𝙐', 'V': '𝙑', 'W': '𝙒', 'X': '𝙓', 'Y': '𝙔', 'Z': '𝙕'
    }
    return ''.join(fancy_map.get(c.upper(), c) for c in text)



# TODO: #2 Test Hybrid Bot
# TODO: #1 Add common word list filter in the Optimized Bot
# TODO: #3 Add a etnropy precompute system
