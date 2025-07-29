import pickle
import json
import os
import hashlib
import time
import math
from wordle_game import GREY_SQUARE, YELLOW_SQUARE, GREEN_SQUARE, to_fancy, WordleGame
from wordle_bot import WordleBot
from entropy_wordle_bot import EntropyWordleBot
from functools import lru_cache
from collections import Counter, defaultdict

MAX_ENTROPY_LOSS_FOR_COMMON_WORDS = 0.2
class OptimizedEntropyWordleBot(EntropyWordleBot):  

    def __init__(self, game: WordleGame, word_list, common_words):
        super().__init__(game, word_list, common_words)
        # Precompute feedback patterns for all word pairs (one-time cost)
        self.feedback_cache = {}
        self._precompute_feedback_patterns()
        
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
        print("The bot is making a guess...")
        
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
        #     if i % max(1, total_words // 10) == 0:
        #         print(f"Progress: {i+1}/{total_words}")
            
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
            if entropy_loss <= MAX_ENTROPY_LOSS_FOR_COMMON_WORDS and word in self.common_words:  # 5% max loss
                best_word, best_entropy = word, entropy
                print(f"Chose common word: {best_word} with entropy: {best_entropy:.4f}")
                break
        
        print(f"Top 5 guesses: {[(w, f'{e:.3f}') for w, e in entropy_list[:5]]}")
        return best_word



class HybridOptimizedEntropyWordleBot(OptimizedEntropyWordleBot):
    def __init__(self, game: WordleGame, word_list, common_words):
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




class EntropyPrecomputeSystem:
    """System for precomputing and caching entropy values"""
    
    def __init__(self, all_words, common_words, cache_dir="entropy_cache"):
        self.all_words = all_words
        self.common_words = common_words
        self.cache_dir = cache_dir
        self.feedback_cache = {}
        self.entropy_cache = {}
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate unique hash for this word set combination
        self.word_set_hash = self._generate_word_set_hash()
        self.cache_file = os.path.join(cache_dir, f"entropy_cache_{self.word_set_hash}.pkl")
        self.metadata_file = os.path.join(cache_dir, f"metadata_{self.word_set_hash}.json")
    
    def _generate_word_set_hash(self):
        """Generate unique hash for current word lists"""
        combined = ''.join(sorted(self.all_words)) + ''.join(sorted(self.common_words))
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _get_feedback_fast(self, guess_word, secret_word):
        """Fast feedback calculation"""
        temp_counts = [0] * 26
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
            if feedback[i] == 0:
                continue
            char_idx = ord(guess_word[i]) - ord('A')
            if temp_counts[char_idx] > 0:
                feedback[i] = 1
                temp_counts[char_idx] -= 1
        
        # Convert to compact string (using single chars instead of emojis)
        symbols = ['G', 'Y', 'B']  # Green, Yellow, Black
        return ''.join(symbols[f] for f in feedback)
    
    def _precompute_feedback_patterns(self):
        """Precompute feedback patterns"""
        print("Precomputing feedback patterns...")
        total = len(self.all_words) * len(self.common_words)
        processed = 0
        
        for guess in self.all_words:
            for secret in self.common_words:
                self.feedback_cache[(guess, secret)] = self._get_feedback_fast(guess, secret)
                processed += 1
                
                if processed % 100000 == 0:
                    progress = (processed / total) * 100
                    print(f"Feedback progress: {processed:,}/{total:,} ({progress:.1f}%)")
        
        print(f"Precomputed {processed:,} feedback patterns")
    
    def _compute_entropy_for_candidates(self, guess, candidates):
        """Compute entropy for a specific guess against candidate set"""
        feedback_counts = defaultdict(int)
        
        for secret in candidates:
            if (guess, secret) in self.feedback_cache:
                feedback = self.feedback_cache[(guess, secret)]
            else:
                feedback = self._get_feedback_fast(guess, secret)
            feedback_counts[feedback] += 1
        
        total = len(candidates)
        entropy = 0.0
        
        for count in feedback_counts.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def precompute_all_entropy_values(self):
        """Precompute entropy for all meaningful game states"""
        print("Starting comprehensive entropy precomputation...")
        
        # First, precompute feedback patterns
        if not self.feedback_cache:
            self._precompute_feedback_patterns()
        
        # Generate all meaningful candidate sets to precompute
        candidate_sets = self._generate_candidate_sets()
        
        print(f"Precomputing entropy for {len(candidate_sets)} different game states...")
        
        total_computations = 0
        for candidates_tuple in candidate_sets:
            candidates = list(candidates_tuple)
            
            # For each candidate set, compute entropy for relevant guesses
            guess_pool = self._get_relevant_guesses(candidates)
            
            for guess in guess_pool:
                cache_key = (guess, candidates_tuple)
                if cache_key not in self.entropy_cache:
                    entropy = self._compute_entropy_for_candidates(guess, candidates)
                    self.entropy_cache[cache_key] = entropy
                    total_computations += 1
                    
                    if total_computations % 10000 == 0:
                        print(f"Entropy computations: {total_computations:,}")
        
        print(f"Precomputed {total_computations:,} entropy values")
    
    def _generate_candidate_sets(self):
        """Generate representative candidate sets for different game states"""
        candidate_sets = set()
        
        # Full word list (game start)
        candidate_sets.add(tuple(self.common_words))
        
        # Simulate various game states by filtering with common patterns
        common_first_guesses = ['SOARE', 'SLATE', 'CRANE', 'ADIEU', 'RAISE', 'SPEAR']
        common_patterns = ['GBBBB', 'YBBBB', 'BYBBB', 'BBGBB', 'BBBBY', 'GYBBG', 'YGBBY']
        
        for first_guess in common_first_guesses:
            if first_guess not in self.all_words:
                continue
                
            for pattern in common_patterns:
                # Simulate filtering after this guess/pattern combination
                filtered_candidates = []
                for candidate in self.common_words:
                    if self._get_feedback_fast(first_guess, candidate).replace('G', 'G').replace('Y', 'Y').replace('B', 'B') == pattern:
                        filtered_candidates.append(candidate)
                
                if 2 <= len(filtered_candidates) <= 500:  # Only meaningful sizes
                    candidate_sets.add(tuple(filtered_candidates))
        
        # Add some random smaller sets
        import random
        for size in [3, 5, 10, 20, 50, 100]:
            for _ in range(10):  # 10 random sets of each size
                random_candidates = tuple(random.sample(self.common_words, min(size, len(self.common_words))))
                candidate_sets.add(random_candidates)
        
        return list(candidate_sets)
    
    def _get_relevant_guesses(self, candidates):
        """Get relevant guesses for a candidate set"""
        if len(candidates) <= 20:
            # Late game: only consider remaining candidates
            return candidates
        elif len(candidates) <= 100:
            # Mid game: candidates + some common words
            relevant = set(candidates)
            relevant.update([w for w in self.all_words[:500] if w in self.all_words])
            return list(relevant)
        else:
            # Early game: broader selection
            return self.all_words[:1000]  # Top 1000 words
    
    def save_cache(self):
        """Save precomputed entropy values to disk"""
        cache_data = {
            'entropy_cache': dict(self.entropy_cache),
            'feedback_cache': dict(self.feedback_cache),
            'word_set_hash': self.word_set_hash
        }
        
        metadata = {
            'num_all_words': len(self.all_words),
            'num_common_words': len(self.common_words),
            'num_entropy_entries': len(self.entropy_cache),
            'num_feedback_entries': len(self.feedback_cache),
            'created_time': time.time(),
            'word_set_hash': self.word_set_hash
        }
        
        # Save binary cache
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Save human-readable metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Cache saved to {self.cache_file}")
        print(f"Metadata saved to {self.metadata_file}")
        print(f"Cache contains {len(self.entropy_cache):,} entropy values")
    
    def load_cache(self):
        """Load precomputed entropy values from disk"""
        if not os.path.exists(self.cache_file):
            print(f"Cache file not found: {self.cache_file}")
            return False
        
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Verify this cache matches our word lists
            if cache_data['word_set_hash'] != self.word_set_hash:
                print("Cache was created with different word lists - ignoring")
                return False
            
            self.entropy_cache = cache_data['entropy_cache']
            self.feedback_cache = cache_data['feedback_cache']
            
            print(f"Loaded cache with {len(self.entropy_cache):,} entropy values")
            print(f"Loaded cache with {len(self.feedback_cache):,} feedback patterns")
            return True
            
        except Exception as e:
            print(f"Error loading cache: {e}")
            return False

# class CachedEntropyWordleBot(EntropyWordleBot):
#     """Bot that uses precomputed entropy cache"""
    
#     # Class-level cache shared across all instances
#     _entropy_system = None
#     _cache_loaded = False
    
#     def __init__(self, game, word_list, common_words):
#         super().__init__(game, word_list, common_words)
        
#         # Initialize shared entropy system
#         if CachedEntropyWordleBot._entropy_system is None:
#             CachedEntropyWordleBot._entropy_system = EntropyPrecomputeSystem(
#                 word_list, common_words
#             )
        
#         # Load cache if not already loaded
#         if not CachedEntropyWordleBot._cache_loaded:
#             cache_loaded = CachedEntropyWordleBot._entropy_system.load_cache()
#             if not cache_loaded:
#                 print("No cache found - bot will compute entropy on demand")
#             CachedEntropyWordleBot._cache_loaded = True
        
#         self.entropy_system = CachedEntropyWordleBot._entropy_system
    
#     def get_feedback(self, guess_word, secret_word):
#         """Use cached feedback if available"""
#         cache_key = (guess_word, secret_word)
#         if cache_key in self.entropy_system.feedback_cache:
#             return self.entropy_system.feedback_cache[cache_key]
        
#         # Fall back to computation
#         return self.entropy_system._get_feedback_fast(guess_word, secret_word)
    
#     def compute_entropy(self, guess):
#         """Use cached entropy if available, compute otherwise"""
#         candidates_tuple = tuple(self.candidates)
#         cache_key = (guess, candidates_tuple)
        
#         if cache_key in self.entropy_system.entropy_cache:
#             return self.entropy_system.entropy_cache[cache_key]
        
#         # Fall back to computation
#         return self.entropy_system._compute_entropy_for_candidates(guess, self.candidates)
    
#     def reset_for_new_game(self):
#         """Reset bot state while keeping shared cache"""
#         self.candidates = self.all_words[:]
#         self.guess_history = []
    
#     @classmethod
#     def create_cache(cls, word_list, common_words):
#         """Class method to create and save entropy cache"""
#         print("Creating comprehensive entropy cache...")
#         system = EntropyPrecomputeSystem(word_list, common_words)
#         system.precompute_all_entropy_values()
#         system.save_cache()
#         print("Cache creation complete!")



class CachedEntropyWordleBot(EntropyWordleBot):  # Inherit from EntropyWordleBot directly
    """Bot that uses precomputed entropy cache"""
    
    # Class-level cache shared across all instances
    _entropy_system = None
    _cache_loaded = False
    
    def __init__(self, game: WordleGame, word_list, common_words):
        # Call EntropyWordleBot.__init__ directly, skip OptimizedEntropyWordleBot
        print("Calculating letter frequencies...")
        letter_counts = Counter(letter for word in word_list for letter in set(word))
        total_letters = sum(letter_counts.values())

        # Normalize to get letter frequencies
        self.letter_frequency = {letter: count / total_letters for letter, count in letter_counts.items()}

        # Step 2: Create a fake frequency score for each word based on its unique letters
        def word_score(word):
            return sum(self.letter_frequency.get(ch, 0) for ch in set(word))

        # Step 3: Sort common_words by descending score
        self.common_words = sorted(common_words, key=word_score, reverse=True)
        # print("Common words sorted by score:", self.common_words[:100])
        EntropyWordleBot.__init__(self, game, word_list, common_words)
        
        # Initialize shared entropy system
        if CachedEntropyWordleBot._entropy_system is None:
            CachedEntropyWordleBot._entropy_system = EntropyPrecomputeSystem(
                word_list, common_words
            )
        
        # Load cache if not already loaded
        if not CachedEntropyWordleBot._cache_loaded:
            cache_loaded = CachedEntropyWordleBot._entropy_system.load_cache()
            if not cache_loaded:
                print("No cache found - bot will compute entropy on demand")
            CachedEntropyWordleBot._cache_loaded = True
        
        self.entropy_system = CachedEntropyWordleBot._entropy_system
    
    def get_feedback(self, guess_word, secret_word):
        """Use cached feedback if available"""
        cache_key = (guess_word, secret_word)
        if cache_key in self.entropy_system.feedback_cache:
            return self.entropy_system.feedback_cache[cache_key]
        
        # Fall back to computation using optimized method
        return self._get_feedback_fast(guess_word, secret_word)
    
    def _get_feedback_fast(self, guess_word, secret_word):
        """Copy the optimized feedback calculation from OptimizedEntropyWordleBot"""
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
    
    def compute_entropy(self, guess):
        """Use cached entropy if available, compute otherwise"""
        candidates_tuple = tuple(self.candidates)
        cache_key = (guess, candidates_tuple)
        
        if cache_key in self.entropy_system.entropy_cache:
            return self.entropy_system.entropy_cache[cache_key]
        
        # Fall back to computation
        return self.entropy_system._compute_entropy_for_candidates(guess, self.candidates)
    
    def _get_candidate_pool(self):
        """Copy smart candidate selection from OptimizedEntropyWordleBot"""
        if len(self.candidates) <= 50:
            return self.candidates[:]
        elif len(self.candidates) <= 200:
            pool = set(self.candidates)
            print("Updating candidate pool: Adding 100 common words...")
            print(self.common_words[:100])
            pool.update(w for w in self.common_words[:100] if w in self.all_words)
            return list(pool)
        else:
            pool = set(self.candidates[:min(len(self.candidates), 300)])
            pool.update(w for w in self.common_words[:200] if w in self.all_words)
            return list(pool)
    
    def choose_guess(self):
        """Copy the optimized choose_guess logic"""
        print("The bot is making a guess...")
        
        if self.game.get_guess_count() == 0:
            # print("First guess: SOARE (optimal starting word)")
            print(f"First guess: {to_fancy('SOARE')} (optimal starting word)")
            return "SOARE"
        
        candidate_pool = self._get_candidate_pool()
        print(f"Evaluating {len(candidate_pool)} potential guesses from {len(self.candidates)} remaining candidates...")
        
        entropy_list = []
        total_words = len(candidate_pool)
        
        for i, word in enumerate(candidate_pool):
            # if i % max(1, total_words // 10) == 0:
            #     print(f"Progress: {i+1}/{total_words}")
            
            entropy = self.compute_entropy(word)
            entropy_list.append((word, entropy))
        
        entropy_list.sort(key=lambda x: x[1], reverse=True)
        
        best_word, best_entropy = entropy_list[0]
        print(f"Top 5 guesses: {[(w, f'{e:.3f}') for w, e in entropy_list[:5]]}")
        print(f"Top entropy choice: {to_fancy(best_word)} with entropy: {best_entropy:.4f}")
        
        # Apply common word preference
        for word, entropy in entropy_list[:5]:
            if best_entropy - entropy < 0.01:
                entropy_loss = 0
            else:
                entropy_loss = (best_entropy - entropy) / best_entropy
            # print(f"Entropy loss: {entropy_loss:.4f}")
            if entropy_loss <= MAX_ENTROPY_LOSS_FOR_COMMON_WORDS and word in self.common_words:
                best_word, best_entropy = word, entropy
                print(f"Ended up choosing COMMON word: {to_fancy(best_word)} with entropy: {best_entropy:.4f}")
                break
        
        return best_word
    
    def reset_for_new_game(self):
        """Reset bot state while keeping shared cache"""
        self.candidates = self.all_words[:]
        self.guess_history = []
    
    @classmethod
    def create_cache(cls, word_list, common_words):
        """Class method to create and save entropy cache"""
        print("Creating comprehensive entropy cache...")
        system = EntropyPrecomputeSystem(word_list, common_words)
        system.precompute_all_entropy_values()
        system.save_cache()
        print("Cache creation complete!")

class NonGreedyCachedEntropyWordleBot(CachedEntropyWordleBot):
        def choose_guess(self):
            """Improved strategy: balances entropy vs. greedy answer guessing"""
            print("The bot is making a guess...")

            if self.game.get_guess_count() == 0:
                print(f"First guess: {to_fancy('SOARE')} (optimal starting word)")
                return "SOARE"

            num_candidates = len(self.candidates)
            print(f"{num_candidates} candidate words remaining.")

            # Use full word list as guess pool for entropy, especially when many candidates remain
            use_full_word_list = num_candidates > 3
            guess_pool = self.all_words if use_full_word_list else self.candidates

            # Prioritize common words when entropy is close
            entropy_list = []
            for word in guess_pool:
                entropy = self.compute_entropy(word)
                entropy_list.append((word, entropy))

            entropy_list.sort(key=lambda x: x[1], reverse=True)

            best_word, best_entropy = entropy_list[0]
            print(f"Top 5 guesses: {[(w, f'{e:.3f}') for w, e in entropy_list[:5]]}")
            print(f"Top entropy choice: {to_fancy(best_word)} with entropy: {best_entropy:.4f}")

            # If we're still in exploration mode, prefer a high-entropy guess even if not a valid candidate
            if self.game.get_guess_count() <= 2:
                print(f"Guess count low, choosing the word with highest entropy: {to_fancy(best_word)} with entropy: {best_entropy:.4f}")
                return best_word    
            if use_full_word_list:
                for word, entropy in entropy_list[:10]:
                    entropy_loss = (best_entropy - entropy) / best_entropy 
                    if entropy_loss < 0.001:
                        entropy_loss = 0
                    if word in self.common_words and entropy_loss < MAX_ENTROPY_LOSS_FOR_COMMON_WORDS: 
                        print(f"Using common exploratory word: {to_fancy(word)} with entropy: {entropy:.4f}")
                        return word
                return best_word
            else:
                print(f"Few candidates left, going through them all to pick a common word...")
                for word, entropy in entropy_list[:10]:
                    if word in self.common_words:
                        print(f"Using common word: {to_fancy(word)} with entropy: {entropy:.4f}")
                        return word
                # In exploitation mode: just guess from remaining candidates
            return best_word


# Usage example
def setup_entropy_cache(all_words, common_words):
    """One-time setup to create entropy cache"""
    print("Setting up entropy cache (this will take 3-5 minutes)...")
    CachedEntropyWordleBot.create_cache(all_words, common_words)
    print("Setup complete! Future bot instances will load instantly.")



def check_and_setup_entropy_cache(all_words, common_words, cache_dir="entropy_cache"):
    """Check if entropy cache exists, create it only if needed"""
    
    # Generate the same hash that EntropyPrecomputeSystem uses
    def generate_word_set_hash(all_words, common_words):
        combined = ''.join(sorted(all_words)) + ''.join(sorted(common_words))
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    word_set_hash = generate_word_set_hash(all_words, common_words)
    cache_file = os.path.join(cache_dir, f"entropy_cache_{word_set_hash}.pkl")
    metadata_file = os.path.join(cache_dir, f"metadata_{word_set_hash}.json")
    
    # Check if cache already exists
    if os.path.exists(cache_file) and os.path.exists(metadata_file):
        print(f"Entropy cache found: {cache_file}")
        
        # Optional: Show cache info
        try:
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            print(f"Cache contains {metadata.get('num_entropy_entries', 'unknown'):,} entropy values")
            print(f"Cache contains {metadata.get('num_feedback_entries', 'unknown'):,} feedback patterns")
            print("Skipping cache creation.")
        except:
            print("Cache exists but metadata unreadable - proceeding anyway.")
        
        return True
    else:
        print("Entropy cache not found - creating new cache...")
        print("This will take approximately 2 minutes...")
        
        # Import here to avoid circular imports
        setup_entropy_cache(all_words, common_words)
        print("Cache creation complete!")
        return False


# Example usage in your code:
"""
# One-time setup (run this once):
setup_entropy_cache(all_words, common_words)

# Then use the cached bot:  
bot = CachedEntropyWordleBot(game, all_words, common_words)
# Bot loads instantly and has precomputed entropy for most game states!
"""