import math
from wordle_game import GREY_SQUARE, YELLOW_SQUARE, GREEN_SQUARE, to_fancy
from wordle_bot import WordleBot


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
        if self.game.get_guess_count() == 0:
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
        
        print(f"\nGuess: {to_fancy(self.guess_history[-1])}, Feedback: {feedback}\nActual Info Gain: {actual_info_gain:.4f} bits")
        print(f"Posterior entropy: {posterior_entropy}")