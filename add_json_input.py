#!/usr/bin/env python3

import sys
import json
import uuid
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime

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
            headers = {
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json",
                "Prefer": "return=representation",
                "Accept-Profile": "ai_log",
                "Content-Profile": "ai_log"
            }
            
            # Check if a record exists
            check_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/instructions?select=id",
                headers=headers
            )
            
            data = {"instructions": self.responses}
            
            if check_response.status_code == 200 and check_response.json():
                # Update existing record
                record_id = check_response.json()[0]['id']
                response = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/instructions?id=eq.{record_id}",
                    headers=headers,
                    json=data
                )
            else:
                # Insert new record
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/instructions",
                    headers=headers,
                    json=data
                )
            
            if response.status_code in (200, 201, 204):
                return True, "Instructions updated in Supabase!"
            else:
                return False, f"Failed to update instructions: {response.text}"
                
        except Exception as e:
            return False, f"Error updating instructions: {str(e)}"

    def create_button_in_supabase(self, button_data):
        """Create a new button record in Supabase"""
        try:
            headers = {
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/button",
                headers=headers,
                json=button_data
            )
            
            if response.status_code in (200, 201):
                return True, "Button created successfully in Supabase!"
            else:
                return False, f"Failed to create button: {response.text}"
                
        except Exception as e:
            return False, f"Error creating button: {str(e)}"

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

    def test_all_schemas_and_tables(self):
        """Test different schemas and table names to find the instructions"""
        test_configs = [
            # (schema, table_name, description)
            ("public", "instructions", "Public schema - instructions table"),
            ("ai_log", "instructions", "AI_log schema - instructions table"),
            ("public", "ai_log_instructions", "Public schema - ai_log_instructions table"),
            ("public", "instruction", "Public schema - instruction table (singular)"),
            ("ai_log", "instruction", "AI_log schema - instruction table (singular)"),
        ]
        
        results = []
        
        for schema, table_name, description in test_configs:
            try:
                if schema == "public":
                    headers = {
                        "apikey": SUPABASE_KEY,
                        "Content-Type": "application/json"
                    }
                else:
                    headers = {
                        "apikey": SUPABASE_KEY,
                        "Content-Type": "application/json",
                        "Accept-Profile": schema,
                        "Content-Profile": schema
                    }
                
                response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/{table_name}",
                    headers=headers
                )
                
                result = f"{description}: Status {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    result += f" - Found {len(data)} records"
                    if data:
                        # Show first record structure
                        first_record = data[0]
                        result += f" - Sample keys: {list(first_record.keys())}"
                else:
                    result += f" - Error: {response.text[:100]}"
                    
                results.append(result)
                print(result)
                
            except Exception as e:
                result = f"{description}: Exception - {str(e)}"
                results.append(result)
                print(result)
        
        return "\n".join(results)

    def debug_ai_log_instructions(self):
        """Debug specifically the ai_log.instructions table with detailed logging"""
        print("\n=== DEBUGGING AI_LOG.INSTRUCTIONS TABLE ===")
        
        # Test with different header combinations
        test_cases = [
            {
                "name": "With Accept-Profile and Content-Profile",
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json",
                    "Accept-Profile": "ai_log",
                    "Content-Profile": "ai_log"
                }
            },
            {
                "name": "With only Accept-Profile", 
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json",
                    "Accept-Profile": "ai_log"
                }
            },
            {
                "name": "With Authorization header",
                "headers": {
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Accept-Profile": "ai_log"
                }
            },
            {
                "name": "Public schema (default)",
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json"
                }
            }
        ]
        
        results = []
        
        for case in test_cases:
            print(f"\n--- Testing: {case['name']} ---")
            try:
                # Test the exact URL and headers we're using
                url = f"{SUPABASE_URL}/rest/v1/instructions"
                print(f"URL: {url}")
                print(f"Headers: {case['headers']}")
                
                response = requests.get(url, headers=case['headers'])
                
                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                print(f"Response Text: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Number of records: {len(data)}")
                    if data:
                        print(f"First record: {data[0]}")
                        # Check if instructions column exists
                        if 'instructions' in data[0]:
                            instructions_content = data[0]['instructions']
                            print(f"Instructions content length: {len(str(instructions_content))}")
                            print(f"Instructions preview: {str(instructions_content)[:200]}...")
                
                result = f"{case['name']}: Status {response.status_code}, Records: {len(response.json()) if response.status_code == 200 else 'N/A'}"
                results.append(result)
                
            except Exception as e:
                error_msg = f"{case['name']}: Exception - {str(e)}"
                print(error_msg)
                results.append(error_msg)
        
        return "\n".join(results)

    def list_all_tables_in_schema(self):
        """List all tables in ai_log schema"""
        print("\n=== LISTING ALL TABLES IN AI_LOG SCHEMA ===")
        
        try:
            headers = {
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json",
                "Accept-Profile": "ai_log"
            }
            
            # Try to get schema information
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/",
                headers=headers
            )
            
            print(f"Schema info response: {response.status_code}")
            print(f"Response: {response.text}")
            
        except Exception as e:
            print(f"Error listing tables: {str(e)}")

    def try_different_instructions_queries(self):
        """Try different ways to query the instructions table"""
        print("\n=== TRYING DIFFERENT INSTRUCTIONS QUERIES ===")
        
        queries = [
            ("No filters", ""),
            ("Select all columns", "?select=*"),
            ("Select instructions only", "?select=instructions"),
            ("Order by id", "?select=*&order=id"),
            ("Order by created_at desc", "?select=*&order=created_at.desc"),
            ("Limit 10", "?select=*&limit=10"),
            ("With count", "?select=*&limit=1"),
        ]
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
            "Accept-Profile": "ai_log"
        }
        
        results = []
        
        for description, query_params in queries:
            try:
                url = f"{SUPABASE_URL}/rest/v1/instructions{query_params}"
                print(f"\n--- {description} ---")
                print(f"URL: {url}")
                
                response = requests.get(url, headers=headers)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    result = f"{description}: {len(data)} records"
                    if data:
                        result += f" - Sample: {str(data[0])[:100]}..."
                else:
                    result = f"{description}: Error {response.status_code}"
                
                results.append(result)
                
            except Exception as e:
                error_msg = f"{description}: Exception - {str(e)}"
                print(error_msg)
                results.append(error_msg)
        
        return results

    def test_supabase_connection(self):
        """Test Supabase connection and check table structure"""
        print("=== TESTING ALL POSSIBLE SCHEMAS AND TABLES ===")
        all_results = self.test_all_schemas_and_tables()
        
        print("\n=== LISTING TABLES ===")
        self.list_all_tables_in_schema()
        
        print("\n=== TRYING DIFFERENT QUERIES ===")
        query_results = self.try_different_instructions_queries()
        
        print("\n=== DETAILED AI_LOG.INSTRUCTIONS DEBUG ===")
        debug_results = self.debug_ai_log_instructions()
        
        combined_results = all_results + "\n\n" + "\n".join(query_results) + "\n\n" + debug_results
        messagebox.showinfo("Supabase Test Results", combined_results)
        return combined_results

    def fetch_instructions_from_supabase(self):
        """Fetch instructions from Supabase - try multiple approaches"""
        
        # Try different approaches to access ai_log.instructions
        approaches = [
            {
                "name": "Public schema - instructions table",
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json"
                },
                "url": f"{SUPABASE_URL}/rest/v1/instructions"
            },
            {
                "name": "AI_log schema with Accept-Profile",
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json",
                    "Accept-Profile": "ai_log"
                },
                "url": f"{SUPABASE_URL}/rest/v1/instructions"
            },
            {
                "name": "Public schema - ai_log_instructions table",
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json"
                },
                "url": f"{SUPABASE_URL}/rest/v1/ai_log_instructions"
            },
            {
                "name": "URL with schema parameter",
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json"
                },
                "url": f"{SUPABASE_URL}/rest/v1/instructions?schema=ai_log"
            },
            {
                "name": "RPC call approach",
                "headers": {
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json"
                },
                "url": f"{SUPABASE_URL}/rest/v1/rpc/get_ai_log_instructions"
            }
        ]
        
        for approach in approaches:
            try:
                print(f"\nTrying: {approach['name']}")
                print(f"URL: {approach['url']}")
                
                response = requests.get(
                    f"{approach['url']}?select=instructions&order=created_at.desc&limit=1",
                    headers=approach['headers']
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        instructions_content = data[0].get('instructions', '')
                        if instructions_content:
                            print(f"SUCCESS with {approach['name']}!")
                            return f"[SUCCESS: {approach['name']}]\n{instructions_content}"
                        else:
                            print(f"Empty instructions in {approach['name']}")
                    else:
                        print(f"No records in {approach['name']}")
                else:
                    print(f"Error {response.status_code} in {approach['name']}")
                    
            except Exception as e:
                print(f"Exception in {approach['name']}: {str(e)}")
        
        # If none worked, return error message
        return "Could not fetch instructions from any schema/table combination. Tried:\n" + \
               "\n".join([f"- {a['name']}" for a in approaches]) + \
               "\n\nCheck if ai_log schema exists and has proper permissions."

    def fetch_buttons_from_supabase(self):
        """Fetch buttons from Supabase public.buttons table"""
        try:
            headers = {
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/button?select=*&order=created_at.desc",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    buttons_text = ""
                    for button in data:
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
                    return "No buttons found in public.buttons table."
            else:
                return f"Error fetching buttons (Status: {response.status_code}): {response.text}"
                
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
