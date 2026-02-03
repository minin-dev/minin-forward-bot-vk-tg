package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
)

func TestHandleSaveClient(t *testing.T) {
	tmpfile, err := os.CreateTemp("", "clients_test_*.json")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(tmpfile.Name())
	tmpfile.Close()

	originalClientsFile := clientsFile
	clientsFile = tmpfile.Name()
	defer func() { clientsFile = originalClientsFile }()

	os.WriteFile(clientsFile, []byte("[]"), 0644)

	clientData := ClientConfig{
		Name: "Test Bot",
		Env:  map[string]string{"TOKEN": "123"},
	}
	body, _ := json.Marshal(clientData)
	req, err := http.NewRequest("POST", "/api/clients", bytes.NewBuffer(body))
	if err != nil {
		t.Fatal(err)
	}
	rr := httptest.NewRecorder()

	handler := http.HandlerFunc(handleSaveClient)
	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	var resp Response
	if err := json.Unmarshal(rr.Body.Bytes(), &resp); err != nil {
		t.Errorf("Response body invalid json: %v", err)
	}

	if !resp.Success {
		t.Errorf("Response success is false: %v", resp.Error)
	}

	content, _ := os.ReadFile(clientsFile)
	var list []ClientConfig
	json.Unmarshal(content, &list)

	if len(list) != 1 {
		t.Errorf("Expected 1 client in file, got %d", len(list))
	}
	if list[0].Name != "Test Bot" {
		t.Errorf("Expected client name 'Test Bot', got '%s'", list[0].Name)
	}
}

func TestHandleListClients(t *testing.T) {
	originalRunCommand := runCommand
	runCommand = func(args ...string) (string, error) {
		if len(args) > 0 {
			if args[0] == "inspect" {
				return "running", nil
			}
			if args[0] == "stats" {
				return "0.00% / 10MiB", nil
			}
		}
		return "", nil
	}
	defer func() { runCommand = originalRunCommand }()

	tmpfile, err := os.CreateTemp("", "clients_list_test_*.json")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(tmpfile.Name())
	tmpfile.Close()

	originalClientsFile := clientsFile
	clientsFile = tmpfile.Name()
	defer func() { clientsFile = originalClientsFile }()

	testClients := []ClientConfig{
		{ID: "123", Name: "Existing Bot"},
	}
	data, _ := json.Marshal(testClients)
	os.WriteFile(clientsFile, data, 0644)

	req, _ := http.NewRequest("GET", "/api/clients", nil)
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handleListClients)
	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", rr.Code, http.StatusOK)
	}

	var resp Response
	if err := json.Unmarshal(rr.Body.Bytes(), &resp); err != nil {
		t.Errorf("Failed to unmarshal response: %v", err)
	}

	if !resp.Success {
		t.Errorf("Expected success")
	}
}
