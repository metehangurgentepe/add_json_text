# Niobe Assistant Response & Button Manager

This application helps you manage responses for a chat assistant and create corresponding buttons in Supabase. The application can save responses to a local file and/or to your Supabase database.

## Features

- Create responses with input text, description, and action keys
- Generate random UUIDs for action keys
- Create buttons in Supabase with customizable:
  - Button titles
  - Action types (url, route, phone, app_store)
  - Navigation types (push, go, pushReplacement)
  - Action values
  - Button order
- Save responses to local file (niobe_training.txt)
- Save responses to Supabase database (ai_log.instructions table)
- View all responses in a scrollable text area

## Setup

1. Make sure you have Python 3.x installed
2. Install required dependencies:

```bash
pip install requests
```

3. Configure your Supabase credentials:
   - Open `add_json_input.py`
   - Replace the placeholder values for `SUPABASE_URL` and `SUPABASE_KEY` with your actual Supabase project URL and API key

## Running the Application

```bash
python add_json_input.py
```

## How to Use

1. Enter response information:
   - Input Text: The text input that triggers this response
   - Description: The description or content of the response
   - Action Key: A unique identifier for this response (can be auto-generated)

2. Enter button information (optional):
   - Button Title: The text displayed on the button
   - Action Type: Select from url, route, phone, or app_store
   - Navigation Type: Select from push, go, or pushReplacement
   - Action Value: The specific value for the action (URL, route name, etc.)
   - Button Order: Numeric order of the button in the UI

3. Choose save options:
   - Save to niobe_training.txt: Save responses to local file
   - Save to ai_log.instructions: Save responses to Supabase database

4. Click "Add Response & Button" to save the response and create the button

5. Click "View All" to refresh the view of all responses

## File Structure

- `add_json_input.py`: Main application file
- `niobe_training.txt`: File where responses are stored locally

## Supabase Table Structure

This application works with two Supabase tables:

### Button Table

```sql
create table public.button (
  created_at timestamp with time zone not null default now(),
  title text null,
  action_type public.button_action_type null,
  navigation_type public.button_navigation_type null,
  action_value text null,
  "order" integer null,
  updated_at timestamp with time zone null default now(),
  id text not null,
  constraint button_pkey primary key (id)
) tablespace pg_default;
```

Where `button_action_type` and `button_navigation_type` are enums in your Supabase database.

### Instructions Table

```sql
create table ai_log.instructions (
  id integer primary key generated always as identity,
  instructions text null,
  created_at timestamp with time zone not null default now()
)
```

The application will update the `instructions` column with the content from niobe_training.txt. 