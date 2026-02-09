package main

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/google/uuid"
)

const (
	SUPABASE_URL = "https://mobil.manisa.bel.tr"
	SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaXNzIjoic3VwYWJhc2UiLCJpYXQiOjE3MTQ5NzUyMDAsImV4cCI6MTg3Mjc0MTYwMH0.eQqXgsJCuribSyEFPTZ5vP3ibSXtXRmMonaKrHFMZ8Y"
)

type Button struct {
	ID             string    `json:"id"`
	Title          string    `json:"title"`
	ActionType     string    `json:"action_type"`
	NavigationType string    `json:"navigation_type"`
	ActionValue    string    `json:"action_value"`
	Order          *int      `json:"order"`
	UpdatedAt      time.Time `json:"updated_at"`
}

type Response struct {
	Description string `json:"description"`
	ActionKey   string `json:"actionKey"`
}

type TrainingData struct {
	Input  string      `json:"input"`
	Output interface{} `json:"output"`
}

type TrainingEntry struct {
	Input       string `json:"input"`
	Description string `json:"description"`
	ActionKey   string `json:"action_key"`
}

var templates *template.Template

func init() {
	templates = template.Must(template.ParseGlob("templates/*.html"))
}

func main() {
	// Static files
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	// Routes
	http.HandleFunc("/", homeHandler)
	http.HandleFunc("/add-button", addButtonHandler)
	http.HandleFunc("/save-to-supabase", saveToSupabaseHandler)
	http.HandleFunc("/add-training", addTrainingHandler)
	http.HandleFunc("/save-training-to-file", saveTrainingToFileHandler)
	http.HandleFunc("/save-training-to-supabase", saveTrainingToSupabaseHandler)
	http.HandleFunc("/upload-training-file-to-supabase", uploadTrainingFileToSupabaseHandler)
	http.HandleFunc("/generate-sql", generateSQLHandler)
	http.HandleFunc("/api/buttons", buttonsAPIHandler)

	fmt.Println("Server starting on http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
	templates.ExecuteTemplate(w, "index.html", nil)
}

func addButtonHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Debug: log content type and headers
	log.Printf("=== Button Form Submission ===")
	log.Printf("Content-Type: %s\n", r.Header.Get("Content-Type"))
	log.Printf("Content-Length: %s\n", r.Header.Get("Content-Length"))

	// FIRST: Try to parse as multipart form (what browser sends for FormData)
	err := r.ParseMultipartForm(10 << 20) // 10 MB max
	if err != nil {
		// If multipart fails, try regular form (application/x-www-form-urlencoded)
		log.Printf("ParseMultipartForm failed: %v, trying ParseForm...\n", err)
		if err := r.ParseForm(); err != nil {
			log.Printf("ParseForm also failed: %v\n", err)
			http.Error(w, "Error parsing form", http.StatusBadRequest)
			return
		}
	}

	// Debug: log all form values from ALL sources
	log.Printf("r.Form (combined): %v\n", r.Form)
	log.Printf("r.PostForm (body only): %v\n", r.PostForm)
	if r.MultipartForm != nil {
		log.Printf("r.MultipartForm.Value: %v\n", r.MultipartForm.Value)
	}

	// Get values
	id := r.FormValue("id")
	title := r.FormValue("title")
	actionType := r.FormValue("action_type")
	navigationType := r.FormValue("navigation_type")
	actionValue := r.FormValue("action_value")
	orderStr := r.FormValue("order")

	log.Printf("Parsed values: id=%q, title=%q, action_type=%q, navigation_type=%q, action_value=%q, order=%q\n",
		id, title, actionType, navigationType, actionValue, orderStr)

	// Create button
	button := Button{
		ID:             id,
		Title:          title,
		ActionType:     actionType,
		NavigationType: navigationType,
		ActionValue:    actionValue,
		UpdatedAt:      time.Now(),
	}

	// Handle order (optional field)
	if orderStr != "" {
		var order int
		fmt.Sscanf(orderStr, "%d", &order)
		button.Order = &order
	}

	// Generate UUID if not provided
	if button.ID == "" {
		button.ID = uuid.New().String()[:8]
		log.Printf("Generated UUID: %s\n", button.ID)
	}

	log.Printf("Final button object: %+v\n", button)
	log.Printf("=== End Button Form ===\n")

	// Return JSON response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"button":  button,
		"message": "Button created successfully",
	})
}

func generateSQLHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var button Button
	if err := json.NewDecoder(r.Body).Decode(&button); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	sql := generateButtonSQL(button)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"sql": sql,
	})
}

func buttonsAPIHandler(w http.ResponseWriter, r *http.Request) {
	// This would connect to Supabase in production
	// For now, just return empty array
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode([]Button{})
}

func saveToSupabaseHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var button Button
	if err := json.NewDecoder(r.Body).Decode(&button); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Save to Supabase
	err := saveButtonToSupabase(button)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "Button saved to Supabase successfully",
	})
}

func saveButtonToSupabase(button Button) error {
	// Create HTTP client with SSL verification disabled
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	// Prepare button data for Supabase
	buttonData := map[string]interface{}{
		"id":           button.ID,
		"title":        button.Title,
		"action_value": button.ActionValue,
		"updated_at":   button.UpdatedAt.Format(time.RFC3339),
	}

	// Only add action_type if it's not empty (it's an enum)
	if button.ActionType != "" {
		buttonData["action_type"] = button.ActionType
	}

	// Only add navigation_type if it's not empty
	if button.NavigationType != "" {
		buttonData["navigation_type"] = button.NavigationType
	}

	if button.Order != nil {
		buttonData["order"] = *button.Order
	}

	jsonData, err := json.Marshal(buttonData)
	if err != nil {
		return fmt.Errorf("failed to marshal button data: %v", err)
	}

	// Make request to Supabase
	url := fmt.Sprintf("%s/rest/v1/button", SUPABASE_URL)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("apikey", SUPABASE_KEY)
	req.Header.Set("Authorization", "Bearer "+SUPABASE_KEY)
	req.Header.Set("Prefer", "return=representation")

	// Send request
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	// Read response body
	body, _ := io.ReadAll(resp.Body)

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		return fmt.Errorf("supabase error (status %d): %s", resp.StatusCode, string(body))
	}

	return nil
}

func generateButtonSQL(button Button) string {
	orderValue := "NULL"
	if button.Order != nil {
		orderValue = fmt.Sprintf("%d", *button.Order)
	}

	// Format timestamp correctly
	timestamp := button.UpdatedAt.Format("2006-01-02 15:04:05.000000")

	sql := fmt.Sprintf(`INSERT INTO public.button (id, title, action_type, navigation_type, action_value, "order", updated_at)
VALUES (
    '%s',
    '%s',
    '%s',
    '%s',
    '%s',
    %s,
    '%s'::timestamp
);`,
		escapeSQLString(button.ID),
		escapeSQLString(button.Title),
		escapeSQLString(button.ActionType),
		escapeSQLString(button.NavigationType),
		escapeSQLString(button.ActionValue),
		orderValue,
		timestamp,
	)

	return sql
}

func addTrainingHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse form data (supports both multipart and url-encoded)
	err := r.ParseMultipartForm(10 << 20) // 10 MB max
	if err != nil {
		// Try regular form parsing
		if err := r.ParseForm(); err != nil {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"success": false,
				"error":   "Error parsing form",
			})
			return
		}
	}

	input := r.FormValue("input")
	description := r.FormValue("description")
	actionKey := r.FormValue("action_key")

	if input == "" || description == "" || actionKey == "" {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   "All fields are required",
		})
		return
	}

	// Create training entry
	entry := TrainingEntry{
		Input:       input,
		Description: description,
		ActionKey:   actionKey,
	}

	// Format as niobe_training.txt format
	trainingText := fmt.Sprintf("input: %s\noutput: {\"description\": \"%s\", \"actionKey\": \"%s\"}\n",
		entry.Input,
		escapeSQLString(entry.Description),
		entry.ActionKey,
	)

	// STEP 1: Append to niobe_training.txt file
	file, err := os.OpenFile("niobe_training.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to open file: %v", err),
		})
		return
	}

	if _, err := file.WriteString(trainingText); err != nil {
		file.Close()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to write to file: %v", err),
		})
		return
	}
	file.Close()

	log.Printf("Training data appended to niobe_training.txt\n")

	// STEP 2: Read entire file and upload to Supabase (id=1)
	fileContent, err := os.ReadFile("niobe_training.txt")
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to read file for Supabase upload: %v", err),
		})
		return
	}

	// Upload to Supabase
	err = replaceInstructionsInSupabase(string(fileContent))
	if err != nil {
		log.Printf("Warning: Failed to update Supabase: %v\n", err)
		// Don't fail the request, file was saved successfully
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": true,
			"entry":   entry,
			"message": "Training data saved to file, but Supabase update failed: " + err.Error(),
		})
		return
	}

	log.Printf("Training data uploaded to Supabase (ID=1)\n")

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"entry":   entry,
		"message": "Training data saved to niobe_training.txt and uploaded to Supabase (ID=1)",
	})
}

func saveTrainingToFileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var data struct {
		TrainingText string `json:"training_text"`
	}

	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Append to niobe_training.txt file
	file, err := os.OpenFile("niobe_training.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to open file: %v", err),
		})
		return
	}
	defer file.Close()

	if _, err := file.WriteString(data.TrainingText); err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to write to file: %v", err),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "Training data saved to niobe_training.txt",
	})
}

func saveTrainingToSupabaseHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var data struct {
		TrainingText string `json:"training_text"`
	}

	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// First, append to file
	file, err := os.OpenFile("niobe_training.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to open file: %v", err),
		})
		return
	}

	if _, err := file.WriteString(data.TrainingText); err != nil {
		file.Close()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to write to file: %v", err),
		})
		return
	}
	file.Close()

	// Then, APPEND to Supabase instructions (ID=1)
	err = appendToInstructionsInSupabase(data.TrainingText)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "Training data saved to both niobe_training.txt and Supabase ai_log.instructions (appended)",
	})
}

func uploadTrainingFileToSupabaseHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Read the entire niobe_training.txt file
	fileContent, err := os.ReadFile("niobe_training.txt")
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to read niobe_training.txt: %v", err),
		})
		return
	}

	// Upload to Supabase - REPLACE existing content, don't append
	err = replaceInstructionsInSupabase(string(fileContent))
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "niobe_training.txt file uploaded to Supabase ai_log.instructions",
	})
}

func appendToInstructionsInSupabase(newTrainingText string) error {
	// Create HTTP client with SSL verification disabled
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	// First, fetch the current instructions from ID=1
	getURL := fmt.Sprintf("%s/rest/v1/instructions?id=eq.1&select=instructions", SUPABASE_URL)
	getReq, err := http.NewRequest("GET", getURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create GET request: %v", err)
	}

	getReq.Header.Set("apikey", SUPABASE_KEY)
	getReq.Header.Set("Authorization", "Bearer "+SUPABASE_KEY)
	getReq.Header.Set("Accept-Profile", "ai_log")
	getReq.Header.Set("Content-Profile", "ai_log")

	getResp, err := client.Do(getReq)
	if err != nil {
		return fmt.Errorf("failed to fetch existing instructions: %v", err)
	}
	defer getResp.Body.Close()

	getBody, _ := io.ReadAll(getResp.Body)
	log.Printf("GET response status: %d, body: %s\n", getResp.StatusCode, string(getBody))

	// Parse the response
	var existingRecords []map[string]interface{}
	if err := json.Unmarshal(getBody, &existingRecords); err != nil {
		return fmt.Errorf("failed to parse existing instructions: %v", err)
	}

	var currentInstructions string
	if len(existingRecords) > 0 {
		currentInstructions, _ = existingRecords[0]["instructions"].(string)
		log.Printf("Current instructions length: %d bytes\n", len(currentInstructions))
	} else {
		return fmt.Errorf("no record found with ID=1 in ai_log.instructions")
	}

	// Append new training text to existing instructions
	updatedInstructions := currentInstructions + newTrainingText

	log.Printf("Appending %d bytes to existing instructions, new total: %d bytes\n",
		len(newTrainingText), len(updatedInstructions))

	// Prepare update data
	instructionsData := map[string]interface{}{
		"instructions": updatedInstructions,
	}

	jsonData, err := json.Marshal(instructionsData)
	if err != nil {
		return fmt.Errorf("failed to marshal instructions data: %v", err)
	}

	// Update the record with ID=1
	updateURL := fmt.Sprintf("%s/rest/v1/instructions?id=eq.1", SUPABASE_URL)
	updateReq, err := http.NewRequest("PATCH", updateURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create PATCH request: %v", err)
	}

	updateReq.Header.Set("Content-Type", "application/json")
	updateReq.Header.Set("apikey", SUPABASE_KEY)
	updateReq.Header.Set("Authorization", "Bearer "+SUPABASE_KEY)
	updateReq.Header.Set("Prefer", "return=representation")
	updateReq.Header.Set("Accept-Profile", "ai_log")
	updateReq.Header.Set("Content-Profile", "ai_log")

	updateResp, err := client.Do(updateReq)
	if err != nil {
		return fmt.Errorf("failed to send PATCH request: %v", err)
	}
	defer updateResp.Body.Close()

	updateBody, _ := io.ReadAll(updateResp.Body)
	log.Printf("PATCH response status: %d, body: %s\n", updateResp.StatusCode, string(updateBody))

	if updateResp.StatusCode != http.StatusOK && updateResp.StatusCode != http.StatusNoContent {
		return fmt.Errorf("update failed (status %d): %s", updateResp.StatusCode, string(updateBody))
	}

	log.Println("Successfully appended to instructions record (ID=1)")
	return nil
}

func replaceInstructionsInSupabase(fullContent string) error {
	// Create HTTP client with SSL verification disabled
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	// Prepare data - instructions as plain text string
	instructionsData := map[string]interface{}{
		"instructions": fullContent,
	}

	jsonData, err := json.Marshal(instructionsData)
	if err != nil {
		return fmt.Errorf("failed to marshal instructions data: %v", err)
	}

	log.Printf("Uploading to Supabase, content length: %d bytes\n", len(fullContent))

	// Directly update ID=1 (don't insert new records)
	updateURL := fmt.Sprintf("%s/rest/v1/instructions?id=eq.1", SUPABASE_URL)
	log.Printf("Updating record with ID=1 at %s\n", updateURL)

	updateReq, err := http.NewRequest("PATCH", updateURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create PATCH request: %v", err)
	}

	updateReq.Header.Set("Content-Type", "application/json")
	updateReq.Header.Set("apikey", SUPABASE_KEY)
	updateReq.Header.Set("Authorization", "Bearer "+SUPABASE_KEY)
	updateReq.Header.Set("Prefer", "return=representation")
	updateReq.Header.Set("Accept-Profile", "ai_log")
	updateReq.Header.Set("Content-Profile", "ai_log")

	updateResp, err := client.Do(updateReq)
	if err != nil {
		return fmt.Errorf("failed to send PATCH request: %v", err)
	}
	defer updateResp.Body.Close()

	updateBody, _ := io.ReadAll(updateResp.Body)
	log.Printf("PATCH response status: %d, body: %s\n", updateResp.StatusCode, string(updateBody))

	if updateResp.StatusCode != http.StatusOK && updateResp.StatusCode != http.StatusNoContent {
		return fmt.Errorf("update failed (status %d): %s", updateResp.StatusCode, string(updateBody))
	}

	log.Println("Successfully updated instructions record (ID=1)")
	return nil
}

func saveInstructionsToSupabase(trainingText string) error {
	// Create HTTP client with SSL verification disabled
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	// First, fetch existing instructions
	getURL := fmt.Sprintf("%s/rest/v1/instructions?select=id,instructions&order=id.desc&limit=1", SUPABASE_URL)
	getReq, err := http.NewRequest("GET", getURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create GET request: %v", err)
	}

	getReq.Header.Set("apikey", SUPABASE_KEY)
	getReq.Header.Set("Authorization", "Bearer "+SUPABASE_KEY)
	getReq.Header.Set("Accept-Profile", "ai_log")
	getReq.Header.Set("Content-Profile", "ai_log")

	getResp, err := client.Do(getReq)
	if err != nil {
		return fmt.Errorf("failed to fetch existing instructions: %v", err)
	}
	defer getResp.Body.Close()

	getBody, _ := io.ReadAll(getResp.Body)

	// Debug log
	log.Printf("Supabase GET response (append mode) status: %d, body: %s\n", getResp.StatusCode, string(getBody))

	var existingRecords []map[string]interface{}
	if err := json.Unmarshal(getBody, &existingRecords); err != nil {
		// Check if it's an error response
		var errorObj map[string]interface{}
		if err2 := json.Unmarshal(getBody, &errorObj); err2 == nil && errorObj["error"] != nil {
			return fmt.Errorf("supabase API error: %v", errorObj)
		}
		return fmt.Errorf("failed to parse existing records: %v, response body: %s", err, string(getBody))
	}

	// Prepare new instructions text
	var newInstructions string
	if len(existingRecords) > 0 {
		// Append to existing instructions
		existingInstructions, _ := existingRecords[0]["instructions"].(string)
		newInstructions = existingInstructions + trainingText
	} else {
		// First entry
		newInstructions = trainingText
	}

	// Prepare data
	instructionsData := map[string]interface{}{
		"instructions": newInstructions,
	}

	jsonData, err := json.Marshal(instructionsData)
	if err != nil {
		return fmt.Errorf("failed to marshal instructions data: %v", err)
	}

	// Update or insert
	var req *http.Request
	if len(existingRecords) > 0 {
		// Update existing record
		recordID := existingRecords[0]["id"]
		url := fmt.Sprintf("%s/rest/v1/instructions?id=eq.%v", SUPABASE_URL, recordID)
		req, err = http.NewRequest("PATCH", url, bytes.NewBuffer(jsonData))
	} else {
		// Insert new record
		url := fmt.Sprintf("%s/rest/v1/instructions", SUPABASE_URL)
		req, err = http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	}

	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("apikey", SUPABASE_KEY)
	req.Header.Set("Authorization", "Bearer "+SUPABASE_KEY)
	req.Header.Set("Prefer", "return=representation")

	// Send request
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	// Read response body
	body, _ := io.ReadAll(resp.Body)

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusOK {
		return fmt.Errorf("supabase error (status %d): %s", resp.StatusCode, string(body))
	}

	return nil
}

func escapeSQLString(s string) string {
	// Simple escape - replace single quotes with two single quotes
	result := ""
	for _, char := range s {
		if char == '\'' {
			result += "''"
		} else {
			result += string(char)
		}
	}
	return result
}
