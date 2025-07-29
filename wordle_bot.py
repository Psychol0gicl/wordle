from wordle_game import GREY_SQUARE, YELLOW_SQUARE, GREEN_SQUARE, to_fancy
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
                chosen_word_score = word_plus_score[1]
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
        print(f"Guess: {to_fancy(self.guess_history[-1])}, Feedback: {feedback}")
        self.filter_candidates(self.guess_history[-1], feedback)
    

    def reset_for_new_game(self):
        """Reset bot state for a new game while keeping precomputed data"""
        self.candidates = self.all_words[:]  # Reset to full word list
        self.guess_history = []              # Clear guess history
        # Keep self.feedback_cache - this is the expensive precomputed data!
        
        # Clear LRU cache to avoid stale data
        if hasattr(self, '_compute_entropy_cached'):
            self._compute_entropy_cached.cache_clear()