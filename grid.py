import random

class Grid:
    def __init__(self, size):
        self.size = size
        self.grid = [['X' for _ in range(size)] for _ in range(size)]
        self.hidden_grid = self._hidden_grid()
        self.revealed_cells = set()

    def _hidden_grid(self):
        num_pairs = (self.size * self.size) // 2
        numbers = list(range(num_pairs)) * 2
        random.shuffle(numbers)

        hidden_grid = []
        for i in range(self.size):
            row = [numbers.pop() for _ in range(self.size)]
            hidden_grid.append(row)
        
        return hidden_grid

    # Checks if a cell is already open 
    def is_revealed(self, cell):
        try:
            row, col = self._parse_cell(cell)
            return (row, col) in self.revealed_cells
        except:
            return False

    def reveal_cell(self, cell):  
        row, col = self._parse_cell(cell)
        # Return the value even if already revealed so the UI can see it
        if (row, col) not in self.revealed_cells:
            self.grid[row][col] = self.hidden_grid[row][col]
            self.revealed_cells.add((row, col))
        return self.hidden_grid[row][col]

    def hide_cell(self, cell):
        row, col = self._parse_cell(cell)
        if (row, col) not in self.revealed_cells:
            return
        self.grid[row][col] = 'X'
        self.revealed_cells.remove((row, col))

    def check_match(self, cell1, cell2):
        row1, col1 = self._parse_cell(cell1)
        row2, col2 = self._parse_cell(cell2)
        return self.hidden_grid[row1][col1] == self.hidden_grid[row2][col2]

    def is_completed(self):
        return len(self.revealed_cells) == self.size * self.size

    def _parse_cell(self, cell):
        # Parses "A0" to (0, 0)
        row = int(cell[1:])
        col = ord(cell[0].upper()) - ord('A')
        return row, col

    # Helper for the UI to convert (0,0) back to "A0"
    def get_coords_str(self, row, col):
        return f"{chr(65 + col)}{row}"