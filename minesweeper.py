import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        empty_set = set()

        if self.count == 0:
            return empty_set
        if self.count == len(self.cells): #there are as many mines as there are cells
            return self.cells
        return empty_set

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        empty_set = set()
        
        if self.count == 0: #no mines
            return self.cells
        #else:
        return empty_set

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if cell[0] <= 7 and cell[1] <= 7:
            self.safes.add(cell)
            for sentence in self.knowledge:
                sentence.mark_safe(cell)
        else:
            print("ERROR ---------------")

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #1: mark cell as a move
        self.moves_made.add(cell)
        #2: mark cell as safe
        self.mark_safe(cell)
        
        #3: update knowledge base by finding neighboring cells of 'cell'
        row = cell[0]
        column = cell[1]
        potential_neighboring_cells = [(row-1, column-1), (row-1, column), (row, column-1), (row+1, column+1), (row+1, column), (row, column+1), (row-1, column+1), (row+1, column-1)]
        neighboring_cells = []
        for potential_cell in potential_neighboring_cells:
            if potential_cell[0] >= 0 and potential_cell[0] <= self.height and potential_cell[1] >= 0 and potential_cell[1] <= self.width:
                if potential_cell[0] <= 7 and potential_cell[1] <= 7:
                    neighboring_cells.append(potential_cell) 
        sentence = Sentence(neighboring_cells, count) 
        self.knowledge.append(sentence)
        #4: Mark additional cells as mines or as safe if possible
        knowledge_temp = self.knowledge.copy() # to check against the current class representation of knowledge
        self.update_knowledge_base()
        #5 Add new senences
        while not self.knowledge == knowledge_temp:
            knowledge_temp = self.knowledge
            self.update_knowledge_base() # update knowledge until all possible inferences are drawn and given to knowledge base through the update_knowledge_base function

    
    def update_knowledge_base(self):
        if len(self.mines) > 0:
            for mine in self.mines:
                self.mark_mine(mine)
        if len(self.safes) > 0:
            for safe_cell in self.safes:
                self.mark_safe(safe_cell)
        if not len(self.knowledge) == 0: # if knowledge not empty
            for sentence in self.knowledge:
                #concatenate lists using new known info about mines and safe locations  
                self.safes = self.safes.union(sentence.known_safes())
                self.mines = self.mines.union(sentence.known_mines())
        #subtraction inference
        new_knowledge_list = []
        for larger_set in self.knowledge:
            for subset in self.knowledge:
                # if set1 = count1 and set2 = count2 where set1 is a subset of set2, set2 - set1 = count2 - count1
                if subset.cells.issubset(larger_set.cells) and not subset == larger_set:
                    new_sentence_cells = larger_set.cells-subset.cells
                    new_sentence_mine_count = larger_set.count - subset.count
                    new_sentence = Sentence(new_sentence_cells, new_sentence_mine_count)
                    new_knowledge_list.append(new_sentence)
        for sentence in new_knowledge_list:
            if not sentence in self.knowledge: #avoid duplicates for efficiency
                self.knowledge.append(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if not len(self.safes) == 0: # no need to check if there are no safe moves
            for cell in self.safes:
                if not cell in self.moves_made:
                    return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        candidates = []
        for row in range(self.height):
            for column in range(self.width):
                if not (row, column) in self.moves_made and not (row, column) in self.mines:
                    candidates.append((row, column)) 
        if candidates: # are not empty
            random_move = random.choice(candidates)
            return random_move
        else:
            print("Candidates empty")

