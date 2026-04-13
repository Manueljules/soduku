# ================================================================
# Sudoku Game — DSA Demo
# Data Structures used: HashMap, Set, Stack, Linked List, Queue
# No built-in arrays used for core game logic
# ================================================================


# ── 1. NODE ──────────────────────────────────────────────────────
# A single unit used by LinkedList, Stack, and Queue.
# Each node holds a value and a pointer to the next node.
class Node:
    def __init__(self, val):
        self.val  = val   # the data stored in this node
        self.next = None  # pointer to the next node (None = end of chain)


# ── 2. LINKED LIST ───────────────────────────────────────────────
# A chain of nodes where each node points to the next.
# Used here to store the list of empty cells for the solver.
class LinkedList:
    def __init__(self):
        self.head = None  # start of the chain; None means the list is empty

    def append(self, val):
        # Add a new node at the END of the list
        new = Node(val)
        if not self.head:
            # List is empty — new node becomes the head
            self.head = new
        else:
            # Walk to the last node, then attach the new node
            cur = self.head
            while cur.next:      # keep moving until there is no next node
                cur = cur.next
            cur.next = new       # attach new node at the end


# ── 3. STACK (LIFO) ──────────────────────────────────────────────
# Last In, First Out — like a stack of plates.
# Used here to remember every move so the player can undo.
class Stack:
    def __init__(self):
        self.top = None   # the most recently pushed node

    def push(self, val):
        # Add a new node ON TOP of the stack
        n = Node(val)
        n.next = self.top  # new node points to the old top
        self.top = n       # new node is now the top

    def pop(self):
        # Remove and return the TOP node's value
        if not self.top:
            return None          # stack is empty, nothing to pop
        val = self.top.val
        self.top = self.top.next # move top down to the next node
        return val

    def is_empty(self):
        return self.top is None  # True if no nodes exist


# ── 4. QUEUE (FIFO) ──────────────────────────────────────────────
# First In, First Out — like a queue at a shop.
# Used here to store and replay the solver's steps in order.
class Queue:
    def __init__(self):
        self.head = None  # front of the queue (next to be removed)
        self.tail = None  # back of the queue  (last added)

    def enqueue(self, val):
        # Add a new node to the BACK of the queue
        n = Node(val)
        if not self.tail:
            # Queue is empty — node is both head and tail
            self.head = self.tail = n
        else:
            self.tail.next = n  # attach after current tail
            self.tail = n       # update tail to the new node

    def dequeue(self):
        # Remove and return the FRONT node's value
        if not self.head:
            return None              # queue is empty
        val = self.head.val
        self.head = self.head.next   # move head forward
        if not self.head:
            self.tail = None         # queue is now empty; reset tail too
        return val

    def is_empty(self):
        return self.head is None     # True if no nodes exist


# ── 5. HASHMAP ───────────────────────────────────────────────────
# Key-value store that allows O(1) lookup, insert, and delete.
# Used here to store the board: key = (row, col), value = digit.
class HashMap:
    def __init__(self):
        self._data = {}  # internal Python dict powers constant-time operations

    def set(self, key, val):
        # Insert or update a key-value pair
        self._data[key] = val

    def get(self, key):
        # Return the value for a key, or None if the key doesn't exist
        return self._data.get(key)

    def has(self, key):
        # Return True if the key exists
        return key in self._data

    def delete(self, key):
        # Remove a key (safe — does nothing if key is missing)
        self._data.pop(key, None)

    def items(self):
        # Return all key-value pairs (used when iterating the board)
        return self._data.items()


# ================================================================
# GAME DATA
# ================================================================

# board  — HashMap storing the current digit at each cell (row, col)
# givens — HashMap marking cells that came with the puzzle (read-only)
# undo_stack — Stack recording every player move for undo support
board      = HashMap()
givens     = HashMap()
undo_stack = Stack()

# Constraint Sets — one Set per row, column, and 3x3 box (27 sets total).
# Each Set holds the digits already placed in that group.
# Checking membership in a Set is O(1), much faster than scanning.
row_sets = [set() for _ in range(9)]  # row_sets[r] = digits used in row r
col_sets = [set() for _ in range(9)]  # col_sets[c] = digits used in col c
box_sets = [set() for _ in range(9)]  # box_sets[b] = digits used in box b


# ── Helper: box index ────────────────────────────────────────────
def box_index(r, c):
    # Map a (row, col) position to one of the 9 box indices (0-8).
    # The grid is divided into 3 rows of boxes x 3 cols of boxes.
    # Example: (0,0)->0, (0,3)->1, (3,0)->3, (4,4)->4
    return (r // 3) * 3 + (c // 3)


# ── Helper: validity check ───────────────────────────────────────
def can_place(r, c, v):
    # Return True only if digit v does NOT already appear in
    # the same row, same column, or same 3x3 box — all O(1) checks.
    return (v not in row_sets[r] and
            v not in col_sets[c] and
            v not in box_sets[box_index(r, c)])


# ── Helper: add digit to all three constraint Sets ───────────────
def add_to_sets(r, c, v):
    # When a digit is placed, register it in its row, col, and box Sets
    # so future validity checks know it is taken.
    row_sets[r].add(v)
    col_sets[c].add(v)
    box_sets[box_index(r, c)].add(v)


# ── Helper: remove digit from all three constraint Sets ──────────
def remove_from_sets(r, c, v):
    # When a digit is erased or undone, free it from its row, col, and box Sets.
    # discard() is used instead of remove() so it won't raise an error if missing.
    row_sets[r].discard(v)
    col_sets[c].discard(v)
    box_sets[box_index(r, c)].discard(v)


# ================================================================
# BOARD DISPLAY
# ================================================================

def print_board():
    # Print the 9x9 grid with thick borders separating the 3x3 boxes.
    # Empty cells are shown as dots.
    print("\n  +-------+-------+-------+")
    for r in range(9):
        row = "  | "
        for c in range(9):
            val = board.get((r, c))           # look up cell value in HashMap
            row += (str(val) if val else ".") + " "
            if c == 2 or c == 5:             # draw vertical box divider
                row += "| "
        print(row + "|")
        if r == 2 or r == 5:                 # draw horizontal box divider
            print("  +-------+-------+-------+")
    print("  +-------+-------+-------+")


# ================================================================
# LOAD PUZZLE
# ================================================================

def load_puzzle():
    # A classic beginner Sudoku puzzle.
    # 0 means the cell is empty (player must fill it in).
    puzzle = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],
        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],
        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9],
    ]
    for r in range(9):
        for c in range(9):
            if puzzle[r][c]:                      # skip empty cells (0)
                v = puzzle[r][c]
                board.set((r, c), v)              # store in HashMap
                givens.set((r, c), True)          # mark as a given (read-only)
                add_to_sets(r, c, v)              # register in constraint Sets


# ================================================================
# PLACE A DIGIT
# ================================================================

def place(r, c, v):
    # Try to place digit v at position (r, c).

    # Block edits to given (pre-filled) cells
    if givens.has((r, c)):
        print("  Cannot change a given cell.")
        return

    # Validate the digit range
    if not (1 <= v <= 9):
        print("  Enter a digit 1-9.")
        return

    # If there is already a digit here, temporarily remove it from
    # the Sets so the conflict check is not affected by the old value
    old = board.get((r, c))
    if old:
        remove_from_sets(r, c, old)

    # Check if placing v here would break any Sudoku rule
    if not can_place(r, c, v):
        print(f"  Conflict! {v} already used in this row/col/box.")
        # Restore the old value's Set membership since we didn't place anything
        if old:
            add_to_sets(r, c, old)
        return

    # Place the digit: update HashMap and constraint Sets
    board.set((r, c), v)
    add_to_sets(r, c, v)

    # Push this move onto the undo Stack so it can be reversed later.
    # We store the old value too so undo knows what to restore.
    undo_stack.push((r, c, old, v))
    print(f"  Placed {v} at ({r+1},{c+1})")


# ================================================================
# UNDO LAST MOVE
# ================================================================

def undo():
    # Pop the most recent move from the Stack (LIFO order)
    move = undo_stack.pop()
    if not move:
        print("  Nothing to undo.")
        return

    r, c, old, val = move

    # Remove the digit that was placed
    remove_from_sets(r, c, val)

    # Restore the previous value (if there was one) or clear the cell
    if old:
        board.set((r, c), old)   # put the old digit back
        add_to_sets(r, c, old)
    else:
        board.delete((r, c))     # cell was empty before — clear it again

    print(f"  Undone move at ({r+1},{c+1})")


# ================================================================
# AUTO SOLVER  —  Backtracking Algorithm
# ================================================================

def solve():
    # Step 1: Build a LinkedList of all empty cell positions.
    # The solver will walk this list node by node.
    empty_cells = LinkedList()
    for r in range(9):
        for c in range(9):
            if not board.has((r, c)):
                empty_cells.append((r, c))  # add empty cell to the chain

    # Step 2: Make local copies of the constraint Sets so the solver
    # can freely add/remove digits without touching the real board state.
    rs = [set(s) for s in row_sets]  # copy of row constraint Sets
    cs = [set(s) for s in col_sets]  # copy of col constraint Sets
    bs = [set(s) for s in box_sets]  # copy of box constraint Sets

    # Local working HashMap to track the solver's placements
    work = HashMap()
    for (r, c), v in board.items():
        work.set((r, c), v)

    # Queue to record every successful placement in FIFO order.
    # After solving, we replay these steps to update the real board.
    steps = Queue()

    # Step 3: Recursive backtracking function.
    # It receives the current LinkedList node (pointing to an empty cell).
    def bt(node):
        if not node:
            # All empty cells have been filled — puzzle is solved!
            return True

        r, c = node.val  # get the (row, col) of this empty cell

        # Try every digit from 1 to 9
        for v in range(1, 10):
            # Check if v is valid in this row, col, and box
            if v not in rs[r] and v not in cs[c] and v not in bs[box_index(r, c)]:

                # Tentatively place v
                rs[r].add(v); cs[c].add(v); bs[box_index(r, c)].add(v)
                work.set((r, c), v)
                steps.enqueue((r, c, v))  # record this step in the Queue

                # Recurse to the next empty cell in the LinkedList
                if bt(node.next):
                    return True  # solution found — stop trying

                # Backtrack: this path did not work, undo the placement
                rs[r].discard(v); cs[c].discard(v); bs[box_index(r, c)].discard(v)
                work.delete((r, c))

        return False  # no digit worked — signal the caller to backtrack

    # Run the solver starting from the first empty cell in the LinkedList
    if not bt(empty_cells.head):
        print("  No solution found.")
        return

    # Step 4: Replay the successful steps from the Queue onto the real board.
    # dequeue() gives us each step in the order they were placed (FIFO).
    while not steps.is_empty():
        r, c, v = steps.dequeue()
        board.set((r, c), v)       # update the real HashMap
        add_to_sets(r, c, v)       # update the real constraint Sets

    print("  Puzzle solved!")


# ================================================================
# WIN CHECK
# ================================================================

def check_win():
    # The puzzle is complete when every cell in the HashMap has a value.
    for r in range(9):
        for c in range(9):
            if not board.has((r, c)):
                return False  # found an empty cell — not done yet
    print("\n  Congratulations! Puzzle complete!")
    return True


# ================================================================
# MAIN LOOP
# ================================================================

def main():
    print("\n  SUDOKU - DSA Demo")
    print("  Data Structures: HashMap, Set, Stack, LinkedList, Queue")
    print("  Commands: place <row> <col> <digit>  |  undo  |  solve  |  quit")

    load_puzzle()   # fill the board with the starting puzzle
    print_board()   # show the initial state

    while True:
        # Read and split the player's command into tokens
        cmd = input("\n> ").strip().lower().split()
        if not cmd:
            continue  # ignore blank input

        if cmd[0] == "quit":
            print("  Bye!")
            break

        elif cmd[0] == "undo":
            undo()
            print_board()

        elif cmd[0] == "solve":
            solve()
            print_board()

        elif cmd[0] == "place" and len(cmd) == 4:
            try:
                # Convert to 0-based indices (player types 1-9)
                r, c, v = int(cmd[1]) - 1, int(cmd[2]) - 1, int(cmd[3])
                if 0 <= r <= 8 and 0 <= c <= 8:
                    place(r, c, v)
                    print_board()
                    check_win()
                else:
                    print("  Row and col must be 1-9.")
            except ValueError:
                print("  Usage: place <row> <col> <digit>")

        else:
            print("  Commands: place <row> <col> <digit>  |  undo  |  solve  |  quit")


main()
