#!/usr/bin/env python3

import sys
import json
from typing import Dict, List, Optional, Union

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Error: tkinter is not installed. Please install it using:")
    print("For Ubuntu/Debian: sudo apt-get install python3-tk")
    print("For macOS: brew install python-tk")
    print("For Windows: It should be included with Python installation")
    sys.exit(1)

class NiobeAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Niobe Assistant Response Manager")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input fields
        ttk.Label(self.main_frame, text="Input Text:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_text = ttk.Entry(self.main_frame, width=60)
        self.input_text.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.description = tk.Text(self.main_frame, width=60, height=4)
        self.description.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Action Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.action_key = ttk.Entry(self.main_frame, width=60)
        self.action_key.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        self.add_button = ttk.Button(self.main_frame, text="Add Response", command=self.add_response)
        self.add_button.grid(row=3, column=1, pady=10)
        
        self.view_button = ttk.Button(self.main_frame, text="View All", command=self.view_responses)
        self.view_button.grid(row=3, column=2, pady=10)
        
        # Response list
        ttk.Label(self.main_frame, text="Recent Responses:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.response_list = tk.Text(self.main_frame, width=80, height=15)
        self.response_list.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Load existing responses
        self.load_responses()

    def load_responses(self):
        try:
            with open('niobe_training.txt', 'r', encoding='utf-8') as f:
                self.responses = f.read()
        except FileNotFoundError:
            self.responses = ""

    def save_responses(self):
        with open('niobe_training.txt', 'w', encoding='utf-8') as f:
            f.write(self.responses)

    def add_response(self):
        input_text = self.input_text.get().strip()
        description = self.description.get("1.0", tk.END).strip()
        action_key = self.action_key.get().strip()
        
        if not input_text or not description:
            messagebox.showerror("Error", "Input text and description are required!")
            return
        
        # Create response string with single newline
        response_str = f'input: {input_text}\noutput: {{"description": "{description}"'
        if action_key:
            response_str += f',"actionKey": "{action_key}"'
        response_str += '}\n'  # Add single newline after response
        
        # Add to responses
        self.responses += response_str
        
        # Save to file
        self.save_responses()
        
        # Clear fields
        self.input_text.delete(0, tk.END)
        self.description.delete("1.0", tk.END)
        self.action_key.delete(0, tk.END)
        
        # Update view
        self.view_responses()
        
        messagebox.showinfo("Success", "Response added successfully!")

    def view_responses(self):
        self.response_list.delete("1.0", tk.END)
        self.response_list.insert("1.0", self.responses)

def main():
    root = tk.Tk()
    app = NiobeAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
