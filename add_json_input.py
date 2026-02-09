#!/usr/bin/env python3

import sys
import json
import uuid
from typing import Dict, List, Optional, Union
from datetime import datetime
import ssl

# Import Supabase Python library
from supabase import create_client, Client
import httpx

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Error: tkinter is not installed. Please install it using:")
    print("For Ubuntu/Debian: sudo apt-get install python3-tk")
    print("For macOS: brew install python-tk")
    print("For Windows: It should be included with Python installation")
    sys.exit(1)

SUPABASE_URL = "https://mobil.manisa.bel.tr"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaXNzIjoic3VwYWJhc2UiLCJpYXQiOjE3MTQ5NzUyMDAsImV4cCI6MTg3Mjc0MTYwMH0.eQqXgsJCuribSyEFPTZ5vP3ibSXtXRmMonaKrHFMZ8Y"

# SSL doğrulamasını devre dışı bırakmak için warnings'i bastır
import warnings
import urllib3
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# httpx'in varsayılan Client sınıfını override et
original_httpx_client = httpx.Client

class InsecureClient(httpx.Client):
    def __init__(self, *args, **kwargs):
        kwargs['verify'] = False
        super().__init__(*args, **kwargs)

# httpx.Client'ı override et
httpx.Client = InsecureClient

# Supabase client'ı oluştur (artık otomatik olarak SSL doğrulaması devre dışı)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class NiobeAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Niobe Assistant Multiple Response Manager")
        self.root.geometry("1200x800")
        
        # Initialize current responses list for the current input
        self.current_responses = []
        
        # Create main frame with scrollbar
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Main content frame
        self.main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid to expand
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_responses()

    def setup_ui(self):
        row = 0
        
        # Input text section
        ttk.Label(self.main_frame, text="Input Text", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        row += 1
        
        ttk.Label(self.main_frame, text="Input Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.input_text = ttk.Entry(self.main_frame, width=80)
        self.input_text.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        # Response creation section
        ttk.Label(self.main_frame, text="Add New Response", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(20, 5))
        row += 1
        
        ttk.Label(self.main_frame, text="Description:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.description = tk.Text(self.main_frame, width=60, height=3)
        self.description.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        ttk.Label(self.main_frame, text="Action Key:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.action_key = ttk.Entry(self.main_frame, width=60)
        self.action_key.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Generate UUID button
        self.generate_uuid_button = ttk.Button(self.main_frame, text="Generate UUID", command=self.generate_uuid)
        self.generate_uuid_button.grid(row=row, column=2, padx=(5, 0))
        row += 1
        
        # Button information section
        ttk.Label(self.main_frame, text="Button Information (Optional)", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        row += 1
        
        ttk.Label(self.main_frame, text="Button Title:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.button_title = ttk.Entry(self.main_frame, width=60)
        self.button_title.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        ttk.Label(self.main_frame, text="Action Type:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.action_type = ttk.Combobox(self.main_frame, width=58, values=["url", "route", "phone", "app_store"])
        self.action_type.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        ttk.Label(self.main_frame, text="Navigation Type:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.navigation_type = ttk.Combobox(self.main_frame, width=58, values=["push", "go", "pushReplacement"])
        self.navigation_type.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        ttk.Label(self.main_frame, text="Action Value:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.action_value = ttk.Entry(self.main_frame, width=60)
        self.action_value.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        ttk.Label(self.main_frame, text="Button Order:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.button_order = ttk.Entry(self.main_frame, width=60)
        self.button_order.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        # Response management buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.add_response_button = ttk.Button(button_frame, text="Add Response to List", command=self.add_response_to_list)
        self.add_response_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_response_button = ttk.Button(button_frame, text="Clear Response Fields", command=self.clear_response_fields)
        self.clear_response_button.pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Current responses list
        ttk.Label(self.main_frame, text="Current Responses for this Input", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(20, 5))
        row += 1
        
        # Response list with scrollbar
        list_frame = ttk.Frame(self.main_frame)
        list_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        
        self.response_listbox = tk.Listbox(list_frame, height=6)
        self.response_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.response_listbox.yview)
        list_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.response_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Bind double-click to edit response
        self.response_listbox.bind("<Double-Button-1>", self.edit_selected_response)
        row += 1
        
        # Response list management buttons
        list_button_frame = ttk.Frame(self.main_frame)
        list_button_frame.grid(row=row, column=0, columnspan=3, pady=5)
        
        self.edit_response_button = ttk.Button(list_button_frame, text="Edit Selected", command=self.edit_selected_response)
        self.edit_response_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_response_button = ttk.Button(list_button_frame, text="Remove Selected", command=self.remove_selected_response)
        self.remove_response_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_all_button = ttk.Button(list_button_frame, text="Clear All Responses", command=self.clear_all_responses)
        self.clear_all_button.pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Save options section
        ttk.Label(self.main_frame, text="Save Options", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(20, 5))
        row += 1
        
        # Checkboxes for save options
        save_options_frame = ttk.Frame(self.main_frame)
        save_options_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.save_to_file_var = tk.BooleanVar(value=True)
        self.save_to_file_checkbox = ttk.Checkbutton(save_options_frame, text="Save to niobe_training.txt", variable=self.save_to_file_var)
        self.save_to_file_checkbox.pack(side=tk.LEFT, padx=(0, 20))
        
        self.save_to_db_var = tk.BooleanVar(value=True)
        self.save_to_db_checkbox = ttk.Checkbutton(save_options_frame, text="Save to ai_log.instructions", variable=self.save_to_db_var)
        self.save_to_db_checkbox.pack(side=tk.LEFT)
        row += 1
        
        # Final action buttons
        final_button_frame = ttk.Frame(self.main_frame)
        final_button_frame.grid(row=row, column=0, columnspan=3, pady=15)
        
        self.save_final_button = ttk.Button(final_button_frame, text="Save All Responses", command=self.save_all_responses)
        self.save_final_button.pack(side=tk.LEFT, padx=5)
        
        self.view_button = ttk.Button(final_button_frame, text="View All Training Data", command=self.view_responses)
        self.view_button.pack(side=tk.LEFT, padx=5)
        
        self.test_button = ttk.Button(final_button_frame, text="Test Supabase", command=self.test_supabase_connection)
        self.test_button.pack(side=tk.LEFT, padx=5)

        self.export_sql_button = ttk.Button(final_button_frame, text="Export Buttons as SQL", command=self.export_buttons_as_sql)
        self.export_sql_button.pack(side=tk.LEFT, padx=5)

        self.new_input_button = ttk.Button(final_button_frame, text="New Input", command=self.start_new_input)
        self.new_input_button.pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Training data view
        ttk.Label(self.main_frame, text="Training Data Preview", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(20, 5))
        row += 1
        
        self.training_data_text = tk.Text(self.main_frame, width=80, height=15)
        self.training_data_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Add scrollbar to training data text
        training_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.training_data_text.yview)
        training_scrollbar.grid(row=row, column=3, sticky=(tk.N, tk.S), pady=5)
        self.training_data_text.configure(yscrollcommand=training_scrollbar.set)

    def generate_uuid(self):
        """Generate a random UUID and insert it into the action key field"""
        unique_id = uuid.uuid4().hex[:8]
        self.action_key.delete(0, tk.END)
        self.action_key.insert(0, unique_id)

    def add_response_to_list(self):
        """Add current response fields to the responses list"""
        description = self.description.get("1.0", tk.END).strip()
        action_key = self.action_key.get().strip()
        
        if not description:
            messagebox.showerror("Error", "Description is required!")
            return
        
        # If no action key is provided, generate one
        if not action_key:
            action_key = uuid.uuid4().hex[:8]
            self.action_key.delete(0, tk.END)
            self.action_key.insert(0, action_key)
        
        # Create response object
        response_obj = {
            "description": description,
            "actionKey": action_key
        }
        
        # Create button object if button fields are provided
        button_obj = None
        button_title = self.button_title.get().strip()
        action_type = self.action_type.get()
        navigation_type = self.navigation_type.get()
        action_value = self.action_value.get().strip()
        button_order = self.button_order.get().strip()
        
        if button_title or action_type or navigation_type or action_value:
            order_value = None
            if button_order:
                try:
                    order_value = int(button_order)
                except ValueError:
                    messagebox.showerror("Error", "Button order must be a number!")
                    return
            
            button_obj = {
                "id": action_key,
                "title": button_title,
                "action_type": action_type if action_type else None,
                "navigation_type": navigation_type if navigation_type else None,
                "action_value": action_value if action_value else None,
                "order": order_value,
                "updated_at": datetime.now().isoformat()
            }
        
        # Add to current responses
        self.current_responses.append({
            "response": response_obj,
            "button": button_obj
        })
        
        # Update listbox
        self.update_response_listbox()
        
        # Clear fields for next response
        self.clear_response_fields()
        
        messagebox.showinfo("Success", f"Response added to list! Total responses: {len(self.current_responses)}")

    def clear_response_fields(self):
        """Clear all response input fields"""
        self.description.delete("1.0", tk.END)
        self.action_key.delete(0, tk.END)
        self.button_title.delete(0, tk.END)
        self.action_type.set("")
        self.navigation_type.set("")
        self.action_value.delete(0, tk.END)
        self.button_order.delete(0, tk.END)

    def update_response_listbox(self):
        """Update the response listbox with current responses"""
        self.response_listbox.delete(0, tk.END)
        for i, item in enumerate(self.current_responses):
            response = item["response"]
            button = item["button"]
            display_text = f"{i+1}. {response['description'][:50]}{'...' if len(response['description']) > 50 else ''}"
            if button and button.get("title"):
                display_text += f" [Button: {button['title']}]"
            display_text += f" (Key: {response['actionKey']})"
            self.response_listbox.insert(tk.END, display_text)

    def edit_selected_response(self, event=None):
        """Edit the selected response"""
        selection = self.response_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a response to edit.")
            return
        
        index = selection[0]
        if index >= len(self.current_responses):
            return
        
        item = self.current_responses[index]
        response = item["response"]
        button = item["button"]
        
        # Fill fields with selected response data
        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", response["description"])
        
        self.action_key.delete(0, tk.END)
        self.action_key.insert(0, response["actionKey"])
        
        if button:
            self.button_title.delete(0, tk.END)
            if button.get("title"):
                self.button_title.insert(0, button["title"])
            
            self.action_type.set(button.get("action_type", ""))
            self.navigation_type.set(button.get("navigation_type", ""))
            
            self.action_value.delete(0, tk.END)
            if button.get("action_value"):
                self.action_value.insert(0, button["action_value"])
            
            self.button_order.delete(0, tk.END)
            if button.get("order") is not None:
                self.button_order.insert(0, str(button["order"]))
        else:
            self.clear_response_fields()
            self.description.insert("1.0", response["description"])
            self.action_key.insert(0, response["actionKey"])
        
        # Remove the item from list so it can be re-added after editing
        self.current_responses.pop(index)
        self.update_response_listbox()
        
        messagebox.showinfo("Edit Mode", "Response loaded for editing. Make changes and click 'Add Response to List' when done.")

    def remove_selected_response(self):
        """Remove the selected response from the list"""
        selection = self.response_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a response to remove.")
            return
        
        index = selection[0]
        if index >= len(self.current_responses):
            return
        
        # Confirm removal
        response = self.current_responses[index]["response"]
        if messagebox.askyesno("Confirm", f"Remove response: {response['description'][:50]}...?"):
            self.current_responses.pop(index)
            self.update_response_listbox()
            messagebox.showinfo("Success", "Response removed from list.")

    def clear_all_responses(self):
        """Clear all responses from the current list"""
        if not self.current_responses:
            messagebox.showinfo("Info", "No responses to clear.")
            return
        
        if messagebox.askyesno("Confirm", f"Clear all {len(self.current_responses)} responses?"):
            self.current_responses.clear()
            self.update_response_listbox()
            messagebox.showinfo("Success", "All responses cleared.")

    def start_new_input(self):
        """Start a new input session"""
        if self.current_responses:
            if not messagebox.askyesno("Confirm", "You have unsaved responses. Continue with new input?"):
                return
        
        self.input_text.delete(0, tk.END)
        self.current_responses.clear()
        self.update_response_listbox()
        self.clear_response_fields()
        messagebox.showinfo("Success", "Ready for new input.")

    def save_all_responses(self):
        """Save all current responses as a single training entry"""
        input_text = self.input_text.get().strip()
        
        if not input_text:
            messagebox.showerror("Error", "Input text is required!")
            return
        
        if not self.current_responses:
            messagebox.showerror("Error", "No responses to save! Add at least one response.")
            return
        
        # Create output array
        output_array = []
        buttons_to_create = []
        
        for item in self.current_responses:
            output_array.append(item["response"])
            if item["button"]:
                buttons_to_create.append(item["button"])
        
        # Create response string in the required format
        if len(output_array) == 1:
            # Single response format
            response_str = f'input: {input_text}\noutput: {json.dumps(output_array[0], ensure_ascii=False)}\n'
        else:
            # Multiple responses format
            response_str = f'input: {input_text}\noutput: {json.dumps(output_array, ensure_ascii=False)}\n'
        
        # Add to responses
        self.responses += response_str
        
        # Save to file if option is selected
        saved_to_file = False
        saved_to_db = False
        
        if self.save_to_file_var.get():
            self.save_responses()
            saved_to_file = True
        
        if self.save_to_db_var.get():
            success, message = self.update_instructions_in_supabase()
            if success:
                saved_to_db = True
        
        # Create buttons in Supabase
        buttons_created = 0
        button_errors = []
        
        for button_data in buttons_to_create:
            success, message = self.create_button_in_supabase(button_data)
            if success:
                buttons_created += 1
            else:
                button_errors.append(f"Button {button_data['id']}: {message}")
        
        # Update view
        self.view_responses()
        
        # Show success message
        success_parts = []
        success_parts.append(f"Saved {len(self.current_responses)} responses for input: '{input_text}'")
        
        if saved_to_file:
            success_parts.append("✓ Saved to niobe_training.txt")
        if saved_to_db:
            success_parts.append("✓ Saved to ai_log.instructions table")
        if buttons_created > 0:
            success_parts.append(f"✓ Created {buttons_created} buttons in Supabase")
        if button_errors:
            success_parts.append(f"⚠ {len(button_errors)} button creation errors")
        
        success_message = "\n".join(success_parts)
        
        if button_errors:
            success_message += "\n\nButton errors:\n" + "\n".join(button_errors[:3])
            if len(button_errors) > 3:
                success_message += f"\n... and {len(button_errors) - 3} more errors"
        
        messagebox.showinfo("Save Complete", success_message)
        
        # Clear current session
        self.current_responses.clear()
        self.update_response_listbox()
        self.input_text.delete(0, tk.END)

    def load_responses(self):
        try:
            with open('niobe_training.txt', 'r', encoding='utf-8') as f:
                self.responses = f.read()
        except FileNotFoundError:
            self.responses = ""

    def save_responses(self):
        with open('niobe_training.txt', 'w', encoding='utf-8') as f:
            f.write(self.responses)
        
        # If database saving is enabled, update ai_log.instructions
        if self.save_to_db_var.get():
            self.update_instructions_in_supabase()

    def update_instructions_in_supabase(self):
        """Update the instructions column in ai_log.instructions table"""
        try:
            print("Checking for existing instructions record...")
            
            # Try to get existing record from ai_log schema
            try:
                # Use schema parameter for ai_log schema
                check_response = supabase.schema("ai_log").table("instructions").select("id").execute()
                print(f"Check response: {check_response}")
                
                data = {"instructions": self.responses}
                
                if check_response.data and len(check_response.data) > 0:
                    # Update existing record
                    record_id = check_response.data[0]['id']
                    print(f"Updating existing record with ID: {record_id}")
                    response = supabase.schema("ai_log").table("instructions").update(data).eq("id", record_id).execute()
                else:
                    # Insert new record
                    print("Inserting new record")
                    response = supabase.schema("ai_log").table("instructions").insert(data).execute()
                
                print(f"Final response: {response}")
                
                if response.data is not None:
                    return True, "Instructions updated in Supabase!"
                else:
                    error_message = f"Failed to update instructions: {response}"
                    return False, error_message
                    
            except Exception as schema_error:
                print(f"ai_log schema failed: {schema_error}")
                # Fallback to public schema
                print("Trying public schema...")
                
                check_response = supabase.table("instructions").select("id").execute()
                print(f"Public schema check response: {check_response}")
                
                data = {"instructions": self.responses}
                
                if check_response.data and len(check_response.data) > 0:
                    # Update existing record
                    record_id = check_response.data[0]['id']
                    print(f"Updating existing record with ID: {record_id}")
                    response = supabase.table("instructions").update(data).eq("id", record_id).execute()
                else:
                    # Insert new record
                    print("Inserting new record")
                    response = supabase.table("instructions").insert(data).execute()
                
                print(f"Final response: {response}")
                
                if response.data is not None:
                    return True, "Instructions updated in Supabase (public schema)!"
                else:
                    error_message = f"Failed to update instructions: {response}"
                    return False, error_message
                
        except Exception as e:
            print(f"Exception in update_instructions_in_supabase: {str(e)}")
            return False, f"Error updating instructions: {str(e)}"

    def create_button_in_supabase(self, button_data):
        """Create a new button record in Supabase"""
        try:
            print(f"Attempting to create button with Supabase Python library")
            print(f"Button data: {button_data}")
            
            # Try to insert button using Supabase Python library
            response = supabase.table("button").insert(button_data).execute()
            
            print(f"Response: {response}")
            
            if response.data is not None and len(response.data) > 0:
                return True, "Button created successfully in Supabase!"
            else:
                error_message = f"Failed to create button: {response}"
                # Check if it's an RLS error
                if hasattr(response, 'error') and response.error:
                    error_str = str(response.error)
                    if "row-level security" in error_str.lower() or "42501" in error_str:
                        error_message += "\n\nSUGGESTION: Check Supabase RLS policies for the 'button' table. You may need to:"
                        error_message += "\n1. Disable RLS on the button table, or"
                        error_message += "\n2. Create appropriate RLS policies that allow INSERT operations"
                        error_message += "\n3. Ensure the service role key has proper permissions"
                return False, error_message
                
        except Exception as e:
            error_message = f"Error creating button: {str(e)}"
            if "row-level security" in str(e).lower() or "42501" in str(e):
                error_message += "\n\nSUGGESTION: Check Supabase RLS policies for the 'button' table."
            return False, error_message

    def test_supabase_connection(self):
        """Test Supabase connection using Python library"""
        try:
            print("=== TESTING SUPABASE CONNECTION ===")
            
            # Test basic connection
            response = supabase.table("button").select("id").limit(1).execute()
            
            results = f"Connection test: {'SUCCESS' if response.data is not None else 'FAILED'}\n"
            results += f"Response: {response}\n\n"
            
            # Test instructions table in different schemas
            results += "=== TESTING INSTRUCTIONS ACCESS ===\n"
            
            try:
                ai_log_response = supabase.schema("ai_log").table("instructions").select("id").limit(1).execute()
                results += f"ai_log.instructions: {'SUCCESS' if ai_log_response.data is not None else 'FAILED'}\n"
                if ai_log_response.data:
                    results += f"Records found: {len(ai_log_response.data)}\n"
            except Exception as e:
                results += f"ai_log.instructions: ERROR - {str(e)}\n"
            
            try:
                public_response = supabase.table("instructions").select("id").limit(1).execute()
                results += f"public.instructions: {'SUCCESS' if public_response.data is not None else 'FAILED'}\n"
                if public_response.data:
                    results += f"Records found: {len(public_response.data)}\n"
            except Exception as e:
                results += f"public.instructions: ERROR - {str(e)}\n"
            
            # Test button table
            results += "\n=== TESTING BUTTON ACCESS ===\n"
            try:
                button_response = supabase.table("button").select("id").limit(1).execute()
                results += f"public.button: {'SUCCESS' if button_response.data is not None else 'FAILED'}\n"
                if button_response.data:
                    results += f"Records found: {len(button_response.data)}\n"
            except Exception as e:
                results += f"public.button: ERROR - {str(e)}\n"
            
            messagebox.showinfo("Supabase Test Results", results)
            return results
            
        except Exception as e:
            error_msg = f"Error testing Supabase connection: {str(e)}"
            messagebox.showerror("Connection Error", error_msg)
            return error_msg

    def fetch_instructions_from_supabase(self):
        """Fetch instructions from Supabase - try multiple approaches"""
        
        # Try different approaches to access instructions
        approaches = [
            ("AI_log schema", lambda: supabase.schema("ai_log").table("instructions")),
            ("Public schema", lambda: supabase.table("instructions")),
            ("ai_log_instructions table", lambda: supabase.table("ai_log_instructions"))
        ]
        
        for approach_name, table_func in approaches:
            try:
                print(f"\nTrying: {approach_name}")
                
                # Build the query
                response = table_func().select("instructions").order("created_at", desc=True).limit(1).execute()
                
                print(f"Response: {response}")
                
                if response.data is not None and len(response.data) > 0:
                    instructions_content = response.data[0].get('instructions', '')
                    if instructions_content:
                        print(f"SUCCESS with {approach_name}!")
                        return f"[SUCCESS: {approach_name}]\n{instructions_content}"
                    else:
                        print(f"Empty instructions in {approach_name}")
                else:
                    print(f"No records in {approach_name}")
                    
            except Exception as e:
                print(f"Exception in {approach_name}: {str(e)}")
        
        # If none worked, return error message
        return "Could not fetch instructions from any schema/table combination. Tried:\n" + \
               "\n".join([f"- {name}" for name, _ in approaches]) + \
               "\n\nCheck if ai_log schema exists and has proper permissions."

    def fetch_buttons_from_supabase(self):
        """Fetch buttons from Supabase public.button table"""
        try:
            # First try with order by created_at, then fallback to no ordering
            try:
                response = supabase.table("button").select("*").order("created_at", desc=True).execute()
            except:
                # Fallback: no ordering
                response = supabase.table("button").select("*").execute()
            
            print(f"Fetch buttons response: {response}")
            
            if response.data is not None:
                if len(response.data) > 0:
                    buttons_text = ""
                    for button in response.data:
                        buttons_text += f"ID: {button.get('id', 'N/A')}\n"
                        buttons_text += f"Title: {button.get('title', 'N/A')}\n"
                        buttons_text += f"Action Type: {button.get('action_type', 'N/A')}\n"
                        buttons_text += f"Navigation Type: {button.get('navigation_type', 'N/A')}\n"
                        buttons_text += f"Action Value: {button.get('action_value', 'N/A')}\n"
                        buttons_text += f"Order: {button.get('order', 'N/A')}\n"
                        buttons_text += f"Created: {button.get('created_at', 'N/A')}\n"
                        buttons_text += "-" * 50 + "\n"
                    return buttons_text
                else:
                    return "No buttons found in public.button table."
            else:
                error_message = f"Error fetching buttons: {response}"
                if hasattr(response, 'error') and response.error:
                    error_message += f" - Error details: {response.error}"
                return error_message
                
        except Exception as e:
            return f"Error connecting to Supabase for buttons: {str(e)}"

    def export_buttons_as_sql(self):
        """Export current buttons as SQL INSERT statements"""
        if not self.current_responses:
            messagebox.showinfo("Info", "No buttons to export. Add responses with buttons first.")
            return

        # Collect all buttons
        buttons_to_export = []
        for item in self.current_responses:
            if item["button"]:
                buttons_to_export.append(item["button"])

        if not buttons_to_export:
            messagebox.showinfo("Info", "No buttons found in current responses.")
            return

        # Generate SQL INSERT statements
        sql_statements = "-- SQL INSERT statements for buttons\n"
        sql_statements += "-- Copy and paste these into your SQL editor\n\n"

        for button in buttons_to_export:
            # Escape single quotes in strings
            def escape_sql(value):
                if value is None:
                    return "NULL"
                elif isinstance(value, str):
                    return f"'{value.replace("'", "''")}'"
                elif isinstance(value, (int, float)):
                    return str(value)
                else:
                    return f"'{str(value)}'"

            sql_statements += f"""INSERT INTO public.button (id, title, action_type, navigation_type, action_value, "order", updated_at)
VALUES (
    {escape_sql(button.get('id'))},
    {escape_sql(button.get('title'))},
    {escape_sql(button.get('action_type'))},
    {escape_sql(button.get('navigation_type'))},
    {escape_sql(button.get('action_value'))},
    {escape_sql(button.get('order'))},
    {escape_sql(button.get('updated_at'))}
);

"""

        # Save to file
        sql_filename = "buttons_export.sql"
        try:
            with open(sql_filename, 'w', encoding='utf-8') as f:
                f.write(sql_statements)

            # Also display in training data text area
            self.training_data_text.delete("1.0", tk.END)
            self.training_data_text.insert("1.0", sql_statements)

            messagebox.showinfo(
                "Export Successful",
                f"Exported {len(buttons_to_export)} buttons to {sql_filename}\n\n"
                f"SQL statements are also displayed in the preview area below.\n\n"
                f"You can now copy and paste them into your SQL editor."
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save SQL file: {str(e)}")

    def view_responses(self):
        self.training_data_text.delete("1.0", tk.END)

        # Load local file content
        local_content = "=== LOCAL FILE (niobe_training.txt) ===\n"
        local_content += self.responses

        # Fetch from Supabase - AI Log Instructions
        supabase_instructions_content = "\n\n=== SUPABASE (ai_log.instructions) ===\n"
        supabase_instructions = self.fetch_instructions_from_supabase()
        supabase_instructions_content += supabase_instructions

        # Fetch from Supabase - Buttons
        supabase_buttons_content = "\n\n=== SUPABASE (public.button) ===\n"
        supabase_buttons = self.fetch_buttons_from_supabase()
        supabase_buttons_content += supabase_buttons

        # Combine and display all
        combined_content = local_content + supabase_instructions_content + supabase_buttons_content
        self.training_data_text.insert("1.0", combined_content)

def main():
    root = tk.Tk()
    app = NiobeAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
