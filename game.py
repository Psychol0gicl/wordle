import sys
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


    def test_bot_optimized(self, word_list, bot_class, file_name=None):
        results = {"W": 0, "L": 0}
        total_start = time.time()
        
        folder_path = f"{RESULT_FOLDER}/{str(bot_class.__name__)}"
        os.makedirs(folder_path, exist_ok=True)
        
        if file_name:
            sys.stdout = open(f"{folder_path}/{file_name}", 'w', encoding='utf-8')
        
        print(f"Testing bot: {bot_class.__name__}")
        
        # Create bot instance ONCE before the loop
        print("Initializing bot (this may take a few minutes for optimized bots)...")
        init_start = time.time()
        bot = bot_class(self, self.all_words, self.common_words)
        init_time = time.time() - init_start
        print(f"Bot initialization completed in {init_time:.2f} seconds")
        
        for word in word_list:
            word_start = time.time()
            
            print("\n" + "-"*50)
            print(f"Testing word: {word}")
            
            # Reset the game state
            self.reset_game(word)
            
            # Reset the bot state for new game (but keep precomputed data)
            bot.reset_for_new_game()
            
            # Run the game
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
        print(f"Average time per word: {(total_time-init_time)/len(word_list):.4f} seconds")
        print("Testing bot class: " + bot_class.__name__ + " complete.")
        
        sys.stdout = open(f"{folder_path}/results_only.txt", 'w', encoding='utf-8')
        analyze_guess_data(results)




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
    

    def reset_for_new_game(self):
        """Reset bot state for a new game while keeping precomputed data"""
        self.candidates = self.all_words[:]  # Reset to full word list
        self.guess_history = []              # Clear guess history
        # Keep self.feedback_cache - this is the expensive precomputed data!
        
        # Clear LRU cache to avoid stale data
        if hasattr(self, '_compute_entropy_cached'):
            self._compute_entropy_cached.cache_clear()




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



class OptimizedEntropyWordleBot(EntropyWordleBot):  
    def __init__(self, game, word_list, common_words):
        super().__init__(game, word_list, common_words)
        # Precompute feedback patterns for all word pairs (one-time cost)
        self.feedback_cache = {}
        self._precompute_feedback_patterns()
        
    # def _precompute_feedback_patterns(self):
    #     """Precompute all possible feedback patterns between word pairs"""
    #     print("Precomputing feedback patterns... (one-time setup)")
    #     for i, guess in enumerate(self.all_words):
    #         if i % 500 == 0:
    #             print(f"Progress: {i}/{len(self.all_words)}")
    #         for secret in self.all_words:
    #             self.feedback_cache[(guess, secret)] = self._get_feedback_fast(guess, secret)
    def _precompute_feedback_patterns(self):
        """Only precompute patterns we actually need"""
        print("Smart precomputing feedback patterns...")
        
        # Strategy 1: Only guess_words × answer_words (not guess × guess)
        total_combinations = len(self.all_words) * len(self.common_words)
        processed = 0
        
        for guess in self.all_words:  # All possible guesses (~12k)
            for secret in self.common_words:  # Only possible answers (~2.3k)
                self.feedback_cache[(guess, secret)] = self._get_feedback_fast(guess, secret)
                processed += 1
                
                # Progress tracking
                if processed % 1000000 == 0:
                    progress = (processed / total_combinations) * 100
                    print(f"Progress: {processed:,}/{total_combinations:,} ({progress:.1f}%)")
        
        print(f"Precomputed {processed:,} feedback patterns")
    
    def _get_feedback_fast(self, guess_word, secret_word):
        """Optimized feedback calculation using list operations"""
        temp_counts = [0] * 26  # a-z
        for c in secret_word:
            temp_counts[ord(c) - ord('A')] += 1
        
        feedback = [2] * 5  # 0=green, 1=yellow, 2=gray
        
        # First pass: Green
        for i in range(5):
            if guess_word[i] == secret_word[i]:
                feedback[i] = 0
                temp_counts[ord(guess_word[i]) - ord('A')] -= 1
        
        # Second pass: Yellow
        for i in range(5):
            if feedback[i] == 0:  # already green
                continue
            char_idx = ord(guess_word[i]) - ord('A')
            if temp_counts[char_idx] > 0:
                feedback[i] = 1
                temp_counts[char_idx] -= 1
        
        # Convert to string format
        symbols = [GREEN_SQUARE, YELLOW_SQUARE, GREY_SQUARE]
        return ''.join(symbols[f] for f in feedback)
    
    def get_feedback(self, guess_word, secret_word):
        """Use precomputed feedback if available"""
        if (guess_word, secret_word) in self.feedback_cache:
            return self.feedback_cache[(guess_word, secret_word)]
        return self._get_feedback_fast(guess_word, secret_word)
    
    @lru_cache(maxsize=1024)
    def _compute_entropy_cached(self, guess, candidates_tuple):
        """Cached entropy computation"""
        feedback_counts = defaultdict(int)
        
        for word in candidates_tuple:
            feedback = self.get_feedback(guess, word)
            feedback_counts[feedback] += 1
        
        total = len(candidates_tuple)
        entropy = 0.0
        
        for count in feedback_counts.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def compute_entropy(self, guess):
        """Compute entropy with caching"""
        # Convert candidates to tuple for hashing
        candidates_tuple = tuple(self.candidates)
        return self._compute_entropy_cached(guess, candidates_tuple)
    
    def _get_candidate_pool(self):
        """Smart candidate selection - consider common words and remaining candidates"""
        if len(self.candidates) <= 50:
            # If few candidates left, only consider remaining words
            return self.candidates[:]
        elif len(self.candidates) <= 200:
            # Medium set: consider candidates + some common words
            pool = set(self.candidates)
            pool.update(w for w in self.common_words[:100] if w in self.all_words)
            return list(pool)
        else:
            # Large set: broader search including common words
            pool = set(self.candidates[:min(len(self.candidates), 300)])
            pool.update(w for w in self.common_words[:200] if w in self.all_words)
            return list(pool)
    
    def choose_guess(self):
        print("\nThe bot is making a guess...")
        
        if self.game.get_guess_count() == 0:
            print("First guess: SOARE (optimal starting word)")
            return "SOARE"  # Proven optimal first guess
        
        # Smart candidate pool selection
        candidate_pool = self._get_candidate_pool()
        
        print(f"Evaluating {len(candidate_pool)} potential guesses from {len(self.candidates)} remaining candidates...")
        
        # Parallel entropy calculation (if you want to add multiprocessing)
        entropy_list = []
        
        # Progress tracking for long calculations
        total_words = len(candidate_pool)
        for i, word in enumerate(candidate_pool):
            if i % max(1, total_words // 10) == 0:
                print(f"Progress: {i+1}/{total_words}")
            
            entropy = self.compute_entropy(word)
            entropy_list.append((word, entropy))
        
        entropy_list.sort(key=lambda x: x[1], reverse=True)
        
        # Apply common word preference with stricter criteria
        best_word, best_entropy = entropy_list[0]
        print(f"Top entropy choice: {best_word} with entropy: {best_entropy:.4f}")
        
        # Only prefer common words if entropy loss is small
        for word, entropy in entropy_list[:5]:  # Only check top 5
            if best_entropy - entropy < 0.01:  # 1% max loss
                best_word, best_entropy = word, entropy
                print(f"Chose common word: {best_word} with entropy: {best_entropy:.4f}")
                break
            entropy_loss = (best_entropy - entropy) / best_entropy
            if entropy_loss <= 0.05 and word in self.common_words:  # 5% max loss
                best_word, best_entropy = word, entropy
                print(f"Chose common word: {best_word} with entropy: {best_entropy:.4f}")
                break
        
        print(f"Top 5 guesses: {[(w, f'{e:.3f}') for w, e in entropy_list[:5]]}")
        return best_word


class FastEntropyWordleBot(EntropyWordleBot):
    """Ultra-fast version using approximation techniques"""
    
    def __init__(self, game, word_list, common_words):
        super().__init__(game, word_list, common_words)
        self.entropy_cache = {}
        
    def _sample_candidates(self, sample_size=100):
        """Sample candidates for approximate entropy calculation"""
        if len(self.candidates) <= sample_size:
            return self.candidates
        
        # Always include some high-frequency words in sample
        import random
        common_in_candidates = [w for w in self.candidates if w in self.common_words]
        sample = common_in_candidates[:sample_size//3]
        
        remaining_sample = sample_size - len(sample)
        if remaining_sample > 0:
            other_candidates = [w for w in self.candidates if w not in sample]
            sample.extend(random.sample(other_candidates, 
                                      min(remaining_sample, len(other_candidates))))
        
        return sample
    
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


class HybridOptimizedEntropyWordleBot(OptimizedEntropyWordleBot):
    def __init__(self, game, word_list, common_words):
        super().__init__(game, word_list, common_words)
        self.feedback_cache = {}
        # Precompute only the most common patterns
        self._precompute_common_patterns()
        
    def _precompute_common_patterns(self):
        """Precompute patterns for most likely guesses and answers"""
        print("Precomputing common feedback patterns...")
        
        # Top opening guesses (these will be used frequently)
        common_openers = ['SOARE', 'SLATE', 'CRANE', 'ADIEU', 'AUDIO', 'OUIJA', 'ARISE', 'RAISE']
        
        # Precompute opener × all possible answers
        for opener in common_openers:
            if opener in self.all_words:
                for secret in self.common_words:
                    self.feedback_cache[(opener, secret)] = self._get_feedback_fast(opener, secret)
        
        # Precompute common_words × common_words (likely late-game scenarios)
        for guess in self.common_words[:500]:  # Top 500 most common
            for secret in self.common_words:
                self.feedback_cache[(guess, secret)] = self._get_feedback_fast(guess, secret)
        
        print(f"Precomputed {len(self.feedback_cache):,} common patterns")
        
    def get_feedback(self, guess_word, secret_word):
        """Use cache if available, compute otherwise"""
        cache_key = (guess_word, secret_word)
        
        if cache_key not in self.feedback_cache:
            # Compute on demand for uncommon patterns
            self.feedback_cache[cache_key] = self._get_feedback_fast(guess_word, secret_word)
        
        return self.feedback_cache[cache_key]


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



game: Game = Game()
# results = game.test_bot_optimized(game.common_words, WordleBot, "most_basic_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, EntropyWordleBot, "entropy_bot_common_words.txt")
results = game.test_bot_optimized(game.common_words, OptimizedEntropyWordleBot, "optimized_entropy_bot_common_words.txt")
results = game.test_bot_optimized(game.common_words, HybridOptimizedEntropyWordleBot, "hybrid_optimized_entropy_bot_common_words.txt")
results = game.test_bot_optimized(game.common_words, FastEntropyWordleBot, "fast_entropy_bot_common_words.txt")

