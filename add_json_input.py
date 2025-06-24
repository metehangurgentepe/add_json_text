#!/usr/bin/env python3

import sys
import json
import uuid
from typing import Dict, List, Optional, Union
from datetime import datetime

# Import Supabase Python library
from supabase import create_client, Client

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

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class NiobeAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Niobe Assistant Response Manager")
        self.root.geometry("1000x700")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid to expand
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        
        # Input fields - Response section
        ttk.Label(self.main_frame, text="Response Information", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(self.main_frame, text="Input Text:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_text = ttk.Entry(self.main_frame, width=60)
        self.input_text.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.description = tk.Text(self.main_frame, width=60, height=4)
        self.description.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Action Key:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.action_key = ttk.Entry(self.main_frame, width=60)
        self.action_key.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Generate UUID button
        self.generate_uuid_button = ttk.Button(self.main_frame, text="Generate UUID", command=self.generate_uuid)
        self.generate_uuid_button.grid(row=3, column=3, padx=5)
        
        # Button information section
        ttk.Label(self.main_frame, text="Button Information", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        ttk.Label(self.main_frame, text="Button Title:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.button_title = ttk.Entry(self.main_frame, width=60)
        self.button_title.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Action Type:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.action_type = ttk.Combobox(self.main_frame, width=58, values=["url", "route", "phone", "app_store"])
        self.action_type.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Navigation Type:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.navigation_type = ttk.Combobox(self.main_frame, width=58, values=["push", "go", "pushReplacement"])
        self.navigation_type.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Action Value:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.action_value = ttk.Entry(self.main_frame, width=60)
        self.action_value.grid(row=8, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.main_frame, text="Button Order:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.button_order = ttk.Entry(self.main_frame, width=60)
        self.button_order.grid(row=9, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Save options section
        ttk.Label(self.main_frame, text="Save Options", font=("Arial", 12, "bold")).grid(row=10, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        # Checkboxes for save options
        self.save_to_file_var = tk.BooleanVar(value=True)
        self.save_to_file_checkbox = ttk.Checkbutton(self.main_frame, text="Save to niobe_training.txt", variable=self.save_to_file_var)
        self.save_to_file_checkbox.grid(row=11, column=0, sticky=tk.W, pady=5)
        
        self.save_to_db_var = tk.BooleanVar(value=True)
        self.save_to_db_checkbox = ttk.Checkbutton(self.main_frame, text="Save to ai_log.instructions", variable=self.save_to_db_var)
        self.save_to_db_checkbox.grid(row=11, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        self.add_button = ttk.Button(self.main_frame, text="Add Response & Button", command=self.add_response_and_button)
        self.add_button.grid(row=12, column=1, pady=10)
        
        self.view_button = ttk.Button(self.main_frame, text="View All", command=self.view_responses)
        self.view_button.grid(row=12, column=2, pady=10)
        
        self.test_button = ttk.Button(self.main_frame, text="Test Supabase", command=self.test_supabase_connection)
        self.test_button.grid(row=12, column=0, pady=10)
        
        # Response list
        ttk.Label(self.main_frame, text="Recent Responses:").grid(row=13, column=0, sticky=tk.W, pady=5)
        self.response_list = tk.Text(self.main_frame, width=80, height=15)
        self.response_list.grid(row=14, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Load existing responses
        self.load_responses()

    def generate_uuid(self):
        """Generate a random UUID and insert it into the action key field"""
        # Generate a 8-character UUID (first 8 characters of a full UUID)
        unique_id = uuid.uuid4().hex[:8]
        self.action_key.delete(0, tk.END)
        self.action_key.insert(0, unique_id)

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

    def add_response_and_button(self):
        input_text = self.input_text.get().strip()
        description = self.description.get("1.0", tk.END).strip()
        action_key = self.action_key.get().strip()
        
        # Button data
        button_title = self.button_title.get().strip()
        action_type = self.action_type.get()
        navigation_type = self.navigation_type.get()
        action_value = self.action_value.get().strip()
        button_order = self.button_order.get().strip()
        
        # Validate required fields
        if not input_text or not description:
            messagebox.showerror("Error", "Input text and description are required!")
            return
        
        # If no action key is provided, generate one
        if not action_key:
            action_key = uuid.uuid4().hex[:8]
            
        # Create response string with single newline
        response_str = f'input: {input_text}\noutput: {{"description": "{description}"'
        if action_key:
            response_str += f',"actionKey": "{action_key}"'
        response_str += '}\n'  # Add single newline after response
        
        # Add to responses
        self.responses += response_str
        
        # Save to file if option is selected
        if self.save_to_file_var.get():
            self.save_responses()
        elif self.save_to_db_var.get():
            # If only saving to DB, update the DB directly
            self.update_instructions_in_supabase()
        
        # Create button in Supabase if button fields are provided
        button_created = False
        button_message = ""
        
        if button_title or action_type or navigation_type or action_value:
            # Convert button_order to integer if provided
            order_value = None
            if button_order:
                try:
                    order_value = int(button_order)
                except ValueError:
                    messagebox.showerror("Error", "Button order must be a number!")
                    return
            
            # Create button data
            button_data = {
                "id": action_key,
                "title": button_title,
                "action_type": action_type if action_type else None,
                "navigation_type": navigation_type if navigation_type else None,
                "action_value": action_value if action_value else None,
                "order": order_value,
                "updated_at": datetime.now().isoformat()
            }
            
            # Send to Supabase
            button_created, button_message = self.create_button_in_supabase(button_data)
        
        # Clear fields
        self.input_text.delete(0, tk.END)
        self.description.delete("1.0", tk.END)
        self.action_key.delete(0, tk.END)
        self.button_title.delete(0, tk.END)
        self.action_type.set("")
        self.navigation_type.set("")
        self.action_value.delete(0, tk.END)
        self.button_order.delete(0, tk.END)
        
        # Update view
        self.view_responses()
        
        # Show success message
        success_message = "Response added successfully!"
        if self.save_to_file_var.get():
            success_message += "\nSaved to niobe_training.txt"
        if self.save_to_db_var.get():
            success_message += "\nSaved to ai_log.instructions table"
        if button_created:
            success_message += f"\n{button_message}"
        elif button_title or action_type or navigation_type or action_value:
            success_message += f"\nWarning: {button_message}"
        
        messagebox.showinfo("Success", success_message)

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
        """Fetch buttons from Supabase public.buttons table"""
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

    def view_responses(self):
        self.response_list.delete("1.0", tk.END)
        
        # Load local file content
        local_content = "=== LOCAL FILE (niobe_training.txt) ===\n"
        local_content += self.responses
        
        # Fetch from Supabase - AI Log Instructions
        supabase_instructions_content = "\n\n=== SUPABASE (ai_log.instructions) ===\n"
        supabase_instructions = self.fetch_instructions_from_supabase()
        supabase_instructions_content += supabase_instructions
        
        # Fetch from Supabase - Buttons
        supabase_buttons_content = "\n\n=== SUPABASE (public.buttons) ===\n"
        supabase_buttons = self.fetch_buttons_from_supabase()
        supabase_buttons_content += supabase_buttons
        
        # Combine and display all
        combined_content = local_content + supabase_instructions_content + supabase_buttons_content
        self.response_list.insert("1.0", combined_content)

def main():
    root = tk.Tk()
    app = NiobeAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
