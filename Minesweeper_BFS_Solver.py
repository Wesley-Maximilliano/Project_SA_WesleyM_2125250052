import tkinter as tk
from tkinter import messagebox
import random
from collections import deque
import time
from tkinter.font import Font

class Minesweeper:
    def __init__(self, master, size=10, mines=10):
        self.master = master
        self.size = size
        self.mines = mines
        self.buttons = {}
        self.board = self.create_board()
        self.place_mines()
        self.update_numbers()
        self.colors = {
            1: "blue", 2: "green", 3: "red", 4: "purple",
            5: "maroon", 6: "turquoise", 7: "black", 8: "gray"
        }
        self.solve_queue = deque()
        self.solve_steps = deque()
        self.marked_mines = set()
        self.solve_speed = 1000  # Default speed in milliseconds
        self.custom_font = Font(family="Arial", size=14, weight="bold")
        self.create_widgets()
        self.create_control_buttons()
        self.create_log_box()

    def create_board(self):
        return [[0 for _ in range(self.size)] for _ in range(self.size)]

    def place_mines(self):
        mines_placed = 0
        while mines_placed < self.mines:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.board[x][y] == 0:
                self.board[x][y] = -1
                mines_placed += 1

    def update_numbers(self):
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == -1:
                    continue
                self.board[x][y] = self.count_adjacent_mines(x, y)

    def count_adjacent_mines(self, x, y):
        count = 0
        for i in range(max(0, x - 1), min(self.size, x + 2)):
            for j in range(max(0, y - 1), min(self.size, y + 2)):
                if self.board[i][j] == -1:
                    count += 1
        return count

    def create_widgets(self):
        for x in range(self.size):
            for y in range(self.size):
                button = tk.Button(self.master, width=3, height=1, font=self.custom_font, bg="#BDBDBD", relief=tk.RAISED, command=lambda x=x, y=y: self.on_click(x, y))
                button.bind("<Button-3>", lambda e, x=x, y=y: self.on_right_click(x, y))
                button.grid(row=x, column=y, padx=2, pady=2)
                self.buttons[(x, y)] = button

    def create_control_buttons(self):
        control_frame = tk.Frame(self.master, bg="#ADD8E6")
        control_frame.grid(row=self.size, column=0, columnspan=self.size, pady=10, padx=10)

        reset_button = tk.Button(control_frame, text="Reset", font=("Arial", 14, "bold"), bg="#FFD700", command=self.reset_game)
        reset_button.pack(side=tk.LEFT, padx=5)

        solve_button = tk.Button(control_frame, text="Solve", font=("Arial", 14, "bold"), bg="#90EE90", command=self.prepare_solve_game)
        solve_button.pack(side=tk.RIGHT, padx=5)

        speed_label = tk.Label(control_frame, text="Speed:", font=("Arial", 12), bg="#ADD8E6")
        speed_label.pack(side=tk.LEFT, padx=5)

        self.speed_slider = tk.Scale(control_frame, from_=100, to=1000, orient=tk.HORIZONTAL, bg="#ADD8E6", length=200, command=self.update_speed)
        self.speed_slider.set(self.solve_speed)
        self.speed_slider.pack(side=tk.LEFT, padx=5)

    def create_log_box(self):
        log_frame = tk.Frame(self.master, bg="#ADD8E6")
        log_frame.grid(row=self.size+1, column=0, columnspan=self.size, pady=10, padx=10)

        self.log_box = tk.Text(log_frame, width=50, height=10, bg="white", font=("Arial", 10))
        self.log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_frame, command=self.log_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_box.config(yscrollcommand=scrollbar.set)

    def update_speed(self, val):
        self.solve_speed = int(val)

    def reset_game(self):
        for button in self.buttons.values():
            button.destroy()
        self.__init__(self.master, self.size, self.mines)

    def prepare_solve_game(self):
        self.log_box.insert(tk.END, "Starting BFS algorithm...\n")
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == 0 and self.buttons[(x, y)]["state"] == tk.NORMAL:
                    self.solve_queue.append((x, y))
                    break
        self.solve_step()

    def solve_step(self):
        if not self.solve_steps and not self.solve_queue:
            for x in range(self.size):
                for y in range(self.size):
                    if self.board[x][y] != -1 and self.buttons[(x, y)]["state"] == tk.NORMAL:
                        self.reveal(x, y)
            if self.check_win():
                self.win_game()
            return

        if not self.solve_steps:
            x, y = self.solve_queue.popleft()
            if self.buttons[(x, y)]["state"] == tk.NORMAL:
                start_time = time.time()
                self.bfs(x, y)
                end_time = time.time()
                self.log_box.insert(tk.END, f"BFS executed in {end_time - start_time:.2f} seconds.\n")

        if self.solve_steps:
            cx, cy = self.solve_steps.popleft()
            if self.board[cx][cy] == -1:
                self.mark_bomb(cx, cy)
            elif self.buttons[(cx, cy)]["state"] == tk.NORMAL:
                self.reveal(cx, cy)

        self.master.after(self.solve_speed, self.solve_step)

    def bfs(self, x, y):
        queue = deque([(x, y)])
        visited = set()
        self.log_box.insert(tk.END, f"BFS starting from ({x}, {y})\n")

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            self.solve_steps.append((cx, cy))
            self.log_box.insert(tk.END, f"Visiting ({cx}, {cy})\n")
            if self.board[cx][cy] == 0:
                for i in range(max(0, cx - 1), min(self.size, cx + 2)):
                    for j in range(max(0, cy - 1), min(self.size, cy + 2)):
                        if (i, j) not in visited:
                            queue.append((i, j))

    def on_click(self, x, y):
        if self.board[x][y] == -1:
            self.game_over()
        else:
            self.reveal(x, y)
            if self.check_win():
                self.win_game()

    def on_right_click(self, x, y):
        button = self.buttons[(x, y)]
        if button["text"] == "F":
            button["text"] = ""
            button.config(bg="#BDBDBD", relief=tk.RAISED)
        else:
            button["text"] = "F"
            button.config(bg="#FFA500", relief=tk.SUNKEN)
            self.marked_mines.add((x, y))

    def mark_bomb(self, x, y):
        button = self.buttons[(x, y)]
        button.config(text="F", bg="#FFA500", relief=tk.SUNKEN)
        self.marked_mines.add((x, y))

    def reveal(self, x, y):
        if self.buttons[(x, y)]["state"] == tk.DISABLED:
            return
        if self.board[x][y] == 0:
            self.flood_fill(x, y)
        else:
            button = self.buttons[(x, y)]
            button.config(text=str(self.board[x][y]), state=tk.DISABLED, disabledforeground=self.colors.get(self.board[x][y], "black"), bg="white", relief=tk.SUNKEN)

    def flood_fill(self, x, y):
        queue = deque([(x, y)])
        visited = set()

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            button = self.buttons[(cx, cy)]
            button.config(text="", state=tk.DISABLED, bg="white", relief=tk.SUNKEN)

            if self.board[cx][cy] == 0:
                for i in range(max(0, cx - 1), min(self.size, cx + 2)):
                    for j in range(max(0, cy - 1), min(self.size, cy + 2)):
                        if (i, j) not in visited:
                            queue.append((i, j))
            else:
                button.config(text=str(self.board[cx][cy]), disabledforeground=self.colors.get(self.board[cx][cy], "black"))

    def game_over(self):
        for (x, y), button in self.buttons.items():
            if self.board[x][y] == -1:
                button.config(text="*", bg="red", relief=tk.SUNKEN)
        self.disable_buttons()
        messagebox.showinfo("Game Over", "You clicked on a mine! Game over.")

    def win_game(self):
        for (x, y), button in self.buttons.items():
            if self.board[x][y] == -1:
                button.config(text="F", bg="green", relief=tk.SUNKEN)
        self.disable_buttons()
        messagebox.showinfo("Congratulations", "You've won the game!")

    def disable_buttons(self):
        for button in self.buttons.values():
            button.config(state=tk.DISABLED)

    def check_win(self):
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] != -1 and self.buttons[(x, y)]["state"] == tk.NORMAL:
                    return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper BFS Solver")
    root.configure(bg="#ADD8E6")

    # Add padding to the main window
    padding_frame = tk.Frame(root, bg="#ADD8E6", padx=20, pady=20)
    padding_frame.pack(expand=True, fill=tk.BOTH)

    game = Minesweeper(padding_frame, size=10, mines=10)
    root.mainloop()
