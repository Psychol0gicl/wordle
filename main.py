import numpy as np
import sys

from wordle_game import WordleGame
from wordle_bot import WordleBot
from entropy_wordle_bot import EntropyWordleBot
from optimized_entropy_wordle_bot import OptimizedEntropyWordleBot, HybridOptimizedEntropyWordleBot, CachedEntropyWordleBot, NonGreedyCachedEntropyWordleBot 
from approximation_wordle_bot import FastEntropyWordleBot
from optimized_entropy_wordle_bot import setup_entropy_cache, check_and_setup_entropy_cache, check_and_setup_letter_frequency_cache    

print("+" *50 + "\n" + "Welcome to Wordle Bot Tester" + "\n" + "+" *50 + "\n")
game: WordleGame = WordleGame()
check_and_setup_entropy_cache(game.all_words, game.common_words)  
check_and_setup_letter_frequency_cache(game.all_words)

# results = game.test_bot_optimized(game.common_words, WordleBot, "most_basic_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, EntropyWordleBot, "entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, OptimizedEntropyWordleBot, "optimized_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, HybridOptimizedEntropyWordleBot, "hybrid_optimized_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words, FastEntropyWordleBot, "fast_entropy_bot_common_words.txt")
# results = game.test_bot_optimized(game.common_words,CachedEntropyWordleBot , "cached_entropy_bot_common_words.txt")

# results = game.test_bot_optimized_x_words(game.common_words,x=100, bot_class=CachedEntropyWordleBot , file_name= "cached_entropy_bot_common_words.txt")

# results = game.test_bot_optimized_x_words(game.common_words,x=100,  bot_class=CachedEntropyWordleBot , file_name= "cached_entropy_bot_common_words.txt")
# results = game.test_bot_optimized_x_words(game.common_words,x=100,  bot_class=NonGreedyCachedEntropyWordleBot, file_name= "non_greedy_cached_entropy_bot_common_words.txt")


def test_all_words_on_all_bots():
    print(f"Testing bots on {len(game.common_words)} words. This will take a while (probably). Please wait.")
    print(f"Results will be saved into separate for each word, progress will be written into the console.")
    bot_classes = [WordleBot, EntropyWordleBot, FastEntropyWordleBot, CachedEntropyWordleBot, NonGreedyCachedEntropyWordleBot]
    words = game.common_words
    i = 0

    for word in words:
        if i % 300 == 1:
            tmp = sys.stdout
            sys.stdout = sys.__stdout__
            print(f"Progress: {i+1}/{len(words)}")
            sys.stdout = tmp    
            

        i += 1
        game.test_every_bot_on_a_single_word(word, bot_classes, file_name="every_bot_on_a_single_word.txt")
        # game.test_every_bot_on_a_single_word(word, bot_classes)

test_all_words_on_all_bots()

sys.stdout = sys.__stdout__
print("Testing bots completed.")