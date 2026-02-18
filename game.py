import tkinter as tk
from tkinter import messagebox
import random
from grid import Grid

class MemoryGameUI:
    def __init__(self, root, size=4):
        self.root = root
        self.size = size
        self.root.title("Brain Buster Pro")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

       
       #Logic Setup 
        self.game_logic = Grid(size)
        self.buttons = {}
        self.first_selection = None 
        self.is_processing = False 
        self.guesses = 0
        
        
        self.matched_cells = set() # Cells that are paired and done
        self.hint_cells = set()    # Cells revealed by "Reveal One"

        self.setup_ui_structure()
        self.start_new_game()

    def setup_ui_structure(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.grid_frame = tk.Frame(main_frame, bg="#d9d9d9", bd=2, relief="groove")
        self.grid_frame.pack(side="left", expand=True, fill="both", padx=(0, 20))

        self.control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.control_frame.pack(side="right", fill="y")

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            self.grid_frame, 
            textvariable=self.status_var, 
            font=("Helvetica", 12), 
            bg="#d9d9d9", 
            fg="#333"
        )
        self.status_label.grid(row=0, column=0, columnspan=self.size, pady=10, sticky="ew")

        lbl_title = tk.Label(self.control_frame, text="Controls", font=("Helvetica", 14, "bold"), bg="#f0f0f0")
        lbl_title.pack(pady=(0, 20))

        self.btn_peek = tk.Button(self.control_frame, text="Reveal One\n(Cost: 2 Guesses)", 
                                  bg="#ffcc00", command=self.option_reveal_one)
        self.btn_peek.pack(fill="x", pady=5, ipady=5)

        self.btn_giveup = tk.Button(self.control_frame, text="Give Up", 
                                    bg="#ff9999", command=self.option_give_up)
        self.btn_giveup.pack(fill="x", pady=5, ipady=5)

        self.btn_reset = tk.Button(self.control_frame, text="New Game", 
                                   bg="#99ccff", command=self.start_new_game)
        self.btn_reset.pack(fill="x", pady=20, ipady=5)

        self.score_label = tk.Label(self.control_frame, text="Guesses: 0", font=("Helvetica", 12), bg="#f0f0f0")
        self.score_label.pack(side="bottom", pady=20)

    def start_new_game(self):
        self.game_logic = Grid(self.size)
        self.guesses = 0
        self.first_selection = None
        self.is_processing = False
        self.matched_cells = set()
        self.hint_cells = set()
        self.update_score()
        self.status_var.set("New Game Started. Good Luck!")

        for widget in self.grid_frame.winfo_children():
            if widget != self.status_label:
                widget.destroy()

        self.buttons = {}
        for r in range(self.size):
            for c in range(self.size):
                btn = tk.Button(
                    self.grid_frame, 
                    text="?", 
                    font=("Arial", 18, "bold"),
                    width=4, 
                    height=2,
                    bg="white",
                    relief="raised",
                    command=lambda row=r, col=c: self.on_card_click(row, col)
                )
                btn.grid(row=r+1, column=c, padx=4, pady=4)
                self.buttons[(r, c)] = btn

    
    # Gameplay Logic 
    def on_card_click(self, row, col):
        if self.is_processing: return
        
         
        # allow clicking Hint cards 
        if (row, col) in self.matched_cells:
            return

        # Don't allow clicking the exact same card twice
        if self.first_selection == (row, col):
            return

        cell_str = self.game_logic.get_coords_str(row, col)
        
        # Visual Reveal
        val = self.game_logic.reveal_cell(cell_str)
        self.buttons[(row, col)].config(text=str(val), bg="#e6e6e6", relief="sunken")

        if self.first_selection is None:
            self.first_selection = (row, col)
            self.status_var.set("Select a second card...")
        else:
            self.guesses += 1
            self.update_score()
            r1, c1 = self.first_selection
            cell1_str = self.game_logic.get_coords_str(r1, c1)

            if self.game_logic.check_match(cell1_str, cell_str):
                # MATCH!
                self.status_var.set("It's a Match!")
                self.highlight_match(row, col, r1, c1)
                
                # Add to matched set so they become unclickable
                self.matched_cells.add((row, col))
                self.matched_cells.add((r1, c1))
                self.first_selection = None
                
                if len(self.matched_cells) == self.size * self.size:
                    messagebox.showinfo("Winner", f"You won in {self.guesses} guesses!")
            else:
                # NO MATCH
                self.status_var.set("Not a match...")
                self.is_processing = True
                self.highlight_mismatch(row, col, r1, c1)
                self.root.after(1000, lambda: self.hide_cards(row, col, r1, c1))

    def option_reveal_one(self):
        if self.is_processing: return
        
        # Find hidden cells (that aren't already hints or matched)
        available = []
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) not in self.matched_cells and (r, c) not in self.hint_cells:
                    available.append((r, c))
        
        if not available:
            return

        r, c = random.choice(available)
        cell_str = self.game_logic.get_coords_str(r, c)
        
        val = self.game_logic.reveal_cell(cell_str)
        
        # Mark as hint, turn yellow, but keep normal state so it can be clicked
        self.hint_cells.add((r, c))
        self.buttons[(r, c)].config(text=str(val), bg="#fffacd", relief="sunken", state="normal") 
        
        self.guesses += 2
        self.update_score()
        self.status_var.set("Hint revealed! You can now match it.")

    def option_give_up(self):
        self.status_var.set("Game Over.")
        for r in range(self.size):
            for c in range(self.size):
                cell_str = self.game_logic.get_coords_str(r, c)
                val = self.game_logic.reveal_cell(cell_str)
                self.buttons[(r, c)].config(text=str(val), bg="#ffcccc", state="disabled")
        self.is_processing = True

    def highlight_match(self, r1, c1, r2, c2):
        self.buttons[(r1, c1)].config(bg="#90EE90", state="disabled") 
        self.buttons[(r2, c2)].config(bg="#90EE90", state="disabled")

    def highlight_mismatch(self, r1, c1, r2, c2):
        self.buttons[(r1, c1)].config(bg="#FF7F7F") 
        self.buttons[(r2, c2)].config(bg="#FF7F7F")

    def hide_cards(self, r1, c1, r2, c2):
        cell1_str = self.game_logic.get_coords_str(r1, c1)
        cell2_str = self.game_logic.get_coords_str(r2, c2)
        
        # Only hide if it's NOT a hint card
        if (r1, c1) not in self.hint_cells:
            self.game_logic.hide_cell(cell1_str)
            self.buttons[(r1, c1)].config(text="?", bg="white", relief="raised")
        else:
            # If it is a hint, revert color to yellow (hint color) instead of red
            self.buttons[(r1, c1)].config(bg="#fffacd", relief="sunken")

        if (r2, c2) not in self.hint_cells:
            self.game_logic.hide_cell(cell2_str)
            self.buttons[(r2, c2)].config(text="?", bg="white", relief="raised")
        else:
            self.buttons[(r2, c2)].config(bg="#fffacd", relief="sunken")
        
        self.first_selection = None
        self.is_processing = False
        self.status_var.set("Try again.")

    def update_score(self):
        self.score_label.config(text=f"Guesses: {self.guesses}")

def main():
    root = tk.Tk()
    game = MemoryGameUI(root, size=4)
    root.mainloop()

if __name__ == "__main__":
    main()