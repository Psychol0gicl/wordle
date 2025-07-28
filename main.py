
from wordle_game import WordleGame
from wordle_bot import WordleBot
from entropy_wordle_bot import EntropyWordleBot
from optimized_entropy_wordle_bot import OptimizedEntropyWordleBot, HybridOptimizedEntropyWordleBot, CachedEntropyWordleBot, NonGreedyCachedEntropyWordleBot
from approximation_wordle_bot import FastEntropyWordleBot
from optimized_entropy_wordle_bot import setup_entropy_cache, check_and_setup_entropy_cache    


game: WordleGame = WordleGame()
check_and_setup_entropy_cache(game.all_words, game.common_words)  

# results = game.test_bot_optimized(game.common_words, WordleBot, "most_basic_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, EntropyWordleBot, "entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, OptimizedEntropyWordleBot, "optimized_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, HybridOptimizedEntropyWordleBot, "hybrid_optimized_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, FastEntropyWordleBot, "fast_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words,CachedEntropyWordleBot , "cached_entropy_bot_common_words.txt")

# results = game.test_bot_optimized_x_words(game.common_words,x=100, bot_class=CachedEntropyWordleBot , file_name= "cached_entropy_bot_common_words.txt")
random_seed = 42
results = game.test_bot_optimized_x_words(game.common_words,x=100, random_seed=random_seed, bot_class=CachedEntropyWordleBot , file_name= "cached_entropy_bot_common_words.txt")
results = game.test_bot_optimized_x_words(game.common_words,x=100, random_seed=random_seed, bot_class=NonGreedyCachedEntropyWordleBot, file_name= "non_greedy_cached_entropy_bot_common_words.txt")
print("Testing bots completed.")