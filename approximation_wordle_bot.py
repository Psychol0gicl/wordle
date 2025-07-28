import math
from wordle_game import GREY_SQUARE, YELLOW_SQUARE, GREEN_SQUARE
from wordle_bot import WordleBot
from entropy_wordle_bot import EntropyWordleBot

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