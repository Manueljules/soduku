import tkinter as tk
from tkinter import messagebox
import random

# Create the main window
root = tk.Tk()
root.title("Simple Sudoku Game")
root.geometry("500x550")

# Store the entries (text boxes) where players type numbers
entries = []
# Store the solution for checking answers
solution = []
# Store the initial puzzle
puzzle = []

def generate_puzzle():
    """Generate a simple Sudoku puzzle"""
    # Create an empty 9x9 board (list of lists)
    board = [[0 for _ in range(9)] for _ in range(9)]
    
    # Fill the board with valid numbers
    for row in range(9):
        for col in range(9):
            # Try random numbers from 1 to 9
            for num in random.sample(range(1, 10), 9):
                # Check if the number is valid in this position
                if is_valid(board, row, col, num):
                    board[row][col] = num
                    break
    
    return board

def is_valid(board, row, col, num):
    """Check if placing 'num' at this position is valid"""
    # Check if number already exists in the same row
    if num in board[row]:
        return False
    
    # Check if number already exists in the same column
    if num in [board[i][col] for i in range(9)]:
        return False
    
    # Get the 3x3 box coordinates
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    
    # Check if number already exists in the same 3x3 box
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    
    return True

def create_puzzle_from_solution(sol):
    """Remove some numbers from the solution to create puzzle"""
    puzzle = [row[:] for row in sol]  # Copy the solution
    
    # Remove 40 numbers to create the puzzle
    cells_to_remove = random.sample(range(81), 40)
    for cell in cells_to_remove:
        row, col = cell // 9, cell % 9
        puzzle[row][col] = 0
    
    return puzzle

def start_game():
    """Initialize a new game"""
    global solution, puzzle
    
    # Generate a valid solution
    solution = generate_puzzle()
    
    # Create puzzle by removing numbers
    puzzle = create_puzzle_from_solution(solution)
    
    # Clear all entry boxes and fill with puzzle values
    for i in range(9):
        for j in range(9):
            entry = entries[i][j]
            entry.config(state='normal')  # Make editable
            entry.delete(0, tk.END)  # Clear the box
            
            # If puzzle has a number, show it and disable editing
            if puzzle[i][j] != 0:
                entry.insert(0, str(puzzle[i][j]))
                entry.config(state='readonly')  # Lock this box
                entry.config(bg='lightgray')  # Color for pre-filled cells
            else:
                entry.config(state='normal')  # Allow typing
                entry.config(bg='white')  # Reset color for empty cells

def check_solution():
    """Check if the player's solution is correct"""
    try:
        # Loop through all 9x9 cells
        for i in range(9):
            for j in range(9):
                # Get the number entered by the player
                user_input = entries[i][j].get()
                
                # Check if the cell is empty
                if user_input == '':
                    messagebox.showerror("Error", "Fill all cells!")
                    return
                
                # Convert to integer
                num = int(user_input)
                
                # Check if it matches the solution
                if num != solution[i][j]:
                    messagebox.showerror("Wrong!", "Some numbers are incorrect!")
                    return
        
        # If we reach here, all numbers are correct
        messagebox.showinfo("Success!", "You solved the Sudoku! 🎉")
    
    except ValueError:
        messagebox.showerror("Error", "Please enter only numbers 1-9!")

def validate_cells():
    """Check each cell and color it based on correctness"""
    for i in range(9):
        for j in range(9):
            entry = entries[i][j]
            if entry.cget('state') == 'readonly':
                continue  # Skip pre-filled cells
            
            user_input = entry.get()
            if user_input == '':
                entry.config(bg='white')  # Empty cell
            elif user_input.isdigit() and 1 <= int(user_input) <= 9:
                if int(user_input) == solution[i][j]:
                    entry.config(bg='lightgreen')  # Correct number
                else:
                    entry.config(bg='lightcoral')  # Wrong number
            else:
                entry.config(bg='white')  # Invalid input

def only_numbers(char):
    """Allow only numbers 1-9 to be typed"""
    return char.isdigit() and char in '123456789' or char == ''

# Create a frame for the grid
grid_frame = tk.Frame(root)
grid_frame.pack(pady=10)

# Validation function for input
vcmd = root.register(only_numbers)

# Create the 9x9 Sudoku grid (Entry boxes)
for i in range(9):
    row_entries = []
    for j in range(9):
        # Create a text box (Entry widget)
        entry = tk.Entry(
            grid_frame,
            width=4,
            font=('Arial', 14, 'bold'),
            justify='center',
            validate='key',
            validatecommand=(vcmd, '%S')
        )
        
        # Add borders to create 3x3 boxes
        padx = (5, 0) if j % 3 == 0 else (0, 0)
        pady = (5, 0) if i % 3 == 0 else (0, 0)
        entry.grid(row=i, column=j, padx=padx, pady=pady)
        
        row_entries.append(entry)
    entries.append(row_entries)

# Create button frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# New Game button
new_button = tk.Button(button_frame, text="New Game", command=start_game, bg='lightblue', width=12)
new_button.pack(side='left', padx=5)

# Check button
check_button = tk.Button(button_frame, text="Check", command=check_solution, bg='lightgreen', width=12)
check_button.pack(side='left', padx=5)

# Validate button
validate_button = tk.Button(button_frame, text="Validate", command=validate_cells, bg='yellow', width=12)
validate_button.pack(side='left', padx=5)

# Start the first game
start_game()

# Run the window
root.mainloop()
