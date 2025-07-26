import numpy as np
GREEN_SQUARE = "\U0001F7E9"
YELLOW_SQUARE = "\U0001F7E8"
GREY_SQUARE = "\u2B1C"

class Game:
    def __init__(self):
        self.common_words = self.load_words("wordle-answers-alphabetical.txt")
        self.all_words  =self.load_words("valid-wordle-words.txt") 

        self.weights = np.array([self.weight_function(word) for word in self.all_words])
        total_weight = self.weights.sum()
        probabilities = self.weights / total_weight
        self.secret_word = np.random.choice(self.all_words, p=probabilities)
        self.secret_word = "SOARE"
        print(self.weight_function(self.secret_word))
        self.game_loop()
        pass

    def load_words(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            words = [line.strip().upper() for line in file if line.strip()]
        return words
    

    
    def weight_function(self,word):
        if word in self.common_words:
            return 25
        else:
            return 1



    def guess(self,word):
        word = word.upper()
        if len(word) != 5:
            print("Word must be 5 letters long.")
            return 0
        if word not in self.all_words:
            print("Word not in word list.")
            return 0
        
        for i in range(5):
            if word[i] == self.secret_word[i]:
                print(GREEN_SQUARE, end="")
            elif word[i] in self.secret_word:
                print(YELLOW_SQUARE, end="")
            else:
                print(GREY_SQUARE, end="")
        print("")
        if word == self.secret_word:
            return -1
        return 1

    # np.random.shuffle(all_words)


    def game_loop(self):
        i = 0
        while(True):
            if i >= 6:
                print("You lose.")
                break

            guess = input("Enter your guess: \n")
            guess = guess.upper()
            r = self.guess(guess)
            if r < 0:
                print("You win!")
                break
            i += r 


game = Game()

