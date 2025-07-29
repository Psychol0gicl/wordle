import numpy as np
from wordle_game import WordleGame
from wordle_bot import WordleBot
from entropy_wordle_bot import EntropyWordleBot
from optimized_entropy_wordle_bot import OptimizedEntropyWordleBot, HybridOptimizedEntropyWordleBot, CachedEntropyWordleBot, NonGreedyCachedEntropyWordleBot
from approximation_wordle_bot import FastEntropyWordleBot
from optimized_entropy_wordle_bot import setup_entropy_cache, check_and_setup_entropy_cache    

print("+" *50 + "\n" + "Welcome to Wordle Bot Tester" + "\n" + "+" *50 + "\n")
game: WordleGame = WordleGame()
check_and_setup_entropy_cache(game.all_words, game.common_words)  

# results = game.test_bot_optimized(game.common_words, WordleBot, "most_basic_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, EntropyWordleBot, "entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, OptimizedEntropyWordleBot, "optimized_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, HybridOptimizedEntropyWordleBot, "hybrid_optimized_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, FastEntropyWordleBot, "fast_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words,CachedEntropyWordleBot , "cached_entropy_bot_common_words.txt")

# results = game.test_bot_optimized_x_words(game.common_words,x=100, bot_class=CachedEntropyWordleBot , file_name= "cached_entropy_bot_common_words.txt")

# results = game.test_bot_optimized_x_words(game.common_words,x=100,  bot_class=CachedEntropyWordleBot , file_name= "cached_entropy_bot_common_words.txt")
# results = game.test_bot_optimized_x_words(game.common_words,x=100,  bot_class=NonGreedyCachedEntropyWordleBot, file_name= "non_greedy_cached_entropy_bot_common_words.txt")
print("Testing bots completed.")


# TODO: #4 Make non-greedy bot faster   
# TODO: #5 Fix random seed initialization 
# TODO: #6 Add UI for better bot testing
# TODO: #7 Add a function for testing every bot on a single word 


secret_word = "SAPPY"
bot = CachedEntropyWordleBot(game, game.all_words, game.common_words)
game.let_bot_guess_a_word(bot=bot, word=secret_word)
game.reset_game(secret_word)
bot = NonGreedyCachedEntropyWordleBot(game, game.all_words, game.common_words)
game.let_bot_guess_a_word(bot=bot, word=secret_word)
game.reset_game(secret_word )



