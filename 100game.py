import tkinter as tk
import random
import sys
import ast
import time

class HundredsGame:
    def __init__(self, grid_size=5, numbers_list=None):
        if numbers_list is None or len(numbers_list) != grid_size*grid_size:
            numbers_list = random.sample(range(1, grid_size*grid_size + 1), grid_size*grid_size)
        self.grid_size = grid_size if grid_size <= 10 else 10
        self.root = tk.Tk()
        self.root.title("Find: 1")
        self.root.resizable(False, False)

        self.numbers_list = numbers_list
        self.number_to_find = 1
        self.button_height = 2  # Height in text units
        self.button_width = 4   # Width in text units
        self.button_font = ('Arial', 12)  # Font for the button text

        self.buttons = {}  # Track buttons to update them

        self.initiate_grid()

        self.start_time = time.time()
        self.root.mainloop()

    def button_command(self, number):
        if number == self.number_to_find:
            print(f"Found number: {number}")
            self.number_to_find += 1
            self.root.title(f"Find: {self.number_to_find}")
            if number == self.grid_size*self.grid_size:
                end_time = time.time()
                elapsed_time = end_time - self.start_time
                minutes, seconds = divmod(elapsed_time, 60)
                if minutes > 0:
                    print(f"Found {grid_size*grid_size} in {int(minutes)} minutes and {int(seconds)} seconds!")
                else:
                    print(f"Found {grid_size*grid_size} in {int(seconds)} seconds!")
                self.root.quit()
            self.update_grid()
        else:
            print(f"Wrong number: {number}")
    def initiate_grid(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                number = self.numbers_list[row*self.grid_size + col]
                button = tk.Button(self.root, text=str(number), width=self.button_width, 
                                   height=self.button_height, font=self.button_font, 
                                   command=lambda n=number: self.button_command(n))
                button.grid(row=row, column=col, padx=1, pady=1)
                self.buttons[(row, col)] = button

    def update_grid(self):
        for idx, number in enumerate(self.numbers_list):
            row, col = divmod(idx, self.grid_size)
            button = self.buttons[(row, col)]
            if number >= self.number_to_find:
                button.config(text=str(number), command=lambda n=number: self.button_command(n))
            else:
                button.config(text=' ')

# Create and start the game
if __name__ == "__main__":
    grid_size = 3
    if len(sys.argv) > 1:
        grid_size = int(sys.argv[1])
    if len(sys.argv) > 2:
        numbers_list = ast.literal_eval(sys.argv[2])
        game = HundredsGame(grid_size, numbers_list)
    else:
        game = HundredsGame(grid_size)