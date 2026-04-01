// Copyright (c) 2023 [Eiztrips]
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"
)

// --- Configuration ---
var (
	Port             = getEnv("PORT", "8080")
	AdminUser        = getEnv("ADMIN_USERNAME", "admin")
	AdminPass        = getEnv("ADMIN_PASSWORD", "admin")
	ApiBase          = getEnv("API_BASE", "/api")
	ImageName        = getEnv("IMAGE_NAME", "minin-bot-client:latest")
	NetworkName      = getEnv("NETWORK_NAME", "minin-bot-network")
	MaxLoginAttempts = 5
	BlockDuration    = 15 * time.Minute
)

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

// --- Structs ---
type ClientConfig struct {
	ID        string            `json:"id"`
	Name      string            `json:"name"`
	Env       map[string]string `json:"env"`
	Status    string            `json:"status"`
	Stats     string            `json:"stats"`
	Container string            `json:"container_id,omitempty"`
	Logs      string            `json:"logs,omitempty"`
}

type Response struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// --- Store ---
var (
	clientsFile   = "clients.json"
	clientsLock   sync.RWMutex
	loginAttempts = make(map[string]int)
	blockedIPs    = make(map[string]time.Time)
	loginLock     sync.Mutex
)

// --- Helpers ---

func jsonResponse(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(Response{Success: true, Data: data})
}

func errorResponse(w http.ResponseWriter, msg string, code int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(Response{Success: false, Error: msg})
}

func getIP(r *http.Request) string {
	ip := r.Header.Get("X-Forwarded-For")
	if ip == "" {
		ip = r.RemoteAddr
	}
	if comma := strings.Index(ip, ","); comma != -1 {
		ip = ip[:comma]
	}
	host, _, err := net.SplitHostPort(ip)
	if err == nil {
		return host
	}
	return strings.TrimSpace(ip)
}

func authMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ip := getIP(r)

		loginLock.Lock()
		if blockTime, ok := blockedIPs[ip]; ok {
			if time.Now().Before(blockTime) {
				loginLock.Unlock()
				errorResponse(w, "Too many login attempts. Please try again later.", http.StatusTooManyRequests)
				return
			}
			delete(blockedIPs, ip)
			delete(loginAttempts, ip)
		}
		loginLock.Unlock()

		user, pass, ok := r.BasicAuth()
		if !ok || user != AdminUser || pass != AdminPass {
			loginLock.Lock()
			loginAttempts[ip]++
			if loginAttempts[ip] >= MaxLoginAttempts {
				blockedIPs[ip] = time.Now().Add(BlockDuration)
				log.Printf("Blocked IP %s due to too many failed login attempts", ip)
			}
			loginLock.Unlock()

			w.Header().Set("WWW-Authenticate", `Basic realm="Restricted"`)
			time.Sleep(1 * time.Second)
			errorResponse(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		loginLock.Lock()
		if loginAttempts[ip] > 0 {
			delete(loginAttempts, ip)
		}
		loginLock.Unlock()

		next(w, r)
	}
}

var runCommand = func(args ...string) (string, error) {
	cmd := exec.Command("docker", args...)
	out, err := cmd.CombinedOutput()
	if err != nil {
		return string(out), fmt.Errorf("cmd error: %v, output: %s", err, string(out))
	}
	return string(out), err
}

func getContainerStatus(name string) (string, string, string) {
	out, err := runCommand("inspect", "--format", "{{.State.Status}}", "minin-client-"+name)
	status := strings.TrimSpace(out)
	if err != nil || status == "" {
		return "stopped", "", ""
	}

	statsOut, _ := runCommand("stats", "--no-stream", "--format", "{{.CPUPerc}} / {{.MemUsage}}", "minin-client-"+name)
	stats := strings.TrimSpace(statsOut)

	idOut, _ := runCommand("inspect", "--format", "{{.Id}}", "minin-client-"+name)

	return status, stats, strings.TrimSpace(idOut)
}

func getContainerLogs(name string, tail string, since string) (string, error) {
	args := []string{"logs", "-t"} // -t adds timestamps
	if since != "" {
		args = append(args, "--since", since)
	}
	if tail != "" {
		args = append(args, "--tail", tail)
	} else if since == "" {
		args = append(args, "--tail", "100")
	}
	args = append(args, "minin-client-"+name)
	
	out, err := runCommand(args...)
	if err != nil {
		return "", err
	}
	return out, nil
}

func startClientContainer(c *ClientConfig) error {
	runCommand("rm", "-f", "minin-client-"+c.ID)

	args := []string{"run", "-d", "--name", "minin-client-" + c.ID, "--network", NetworkName, "--restart=unless-stopped"}
	for k, v := range c.Env {
		args = append(args, "-e", fmt.Sprintf("%s=%s", k, v))
	}
	args = append(args, ImageName)

	_, err := runCommand(args...)
	return err
}

func stopClientContainer(id string) error {
	_, err := runCommand("stop", "minin-client-"+id)
	return err
}

// --- Handlers ---

func handleLogin(w http.ResponseWriter, r *http.Request) {
	jsonResponse(w, "Logged in")
}

func handleLogs(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	tail := r.URL.Query().Get("tail")
	since := r.URL.Query().Get("since")
	if id == "" {
		errorResponse(w, "Missing id", 400)
		return
	}

	logs, err := getContainerLogs(id, tail, since)
	if err != nil {
		errorResponse(w, "Failed to get logs: "+err.Error(), 500)
		return
	}

	jsonResponse(w, logs)
}

func handleListClients(w http.ResponseWriter, r *http.Request) {
	clientsLock.RLock()
	defer clientsLock.RUnlock()

	data, err := os.ReadFile(clientsFile)
	var list []ClientConfig
	if err == nil {
		json.Unmarshal(data, &list)
	} else {
		list = []ClientConfig{}
	}

	for i := range list {
		s, stats, cid := getContainerStatus(list[i].ID)
		list[i].Status = s
		list[i].Stats = stats
		list[i].Container = cid
	}

	jsonResponse(w, list)
}

func handleSaveClient(w http.ResponseWriter, r *http.Request) {
	var c ClientConfig
	if err := json.NewDecoder(r.Body).Decode(&c); err != nil {
		errorResponse(w, "Invalid body", 400)
		return
	}

	if c.ID == "" {
		c.ID = fmt.Sprintf("%d", time.Now().Unix())
	}

	clientsLock.Lock()
	defer clientsLock.Unlock()

	data, _ := os.ReadFile(clientsFile)
	var list []ClientConfig
	json.Unmarshal(data, &list)

	found := false
	for i, existing := range list {
		if existing.ID == c.ID {
			list[i] = c
			found = true
			break
		}
	}
	if !found {
		list = append(list, c)
	}

	out, _ := json.MarshalIndent(list, "", "  ")
	os.WriteFile(clientsFile, out, 0644)

	jsonResponse(w, c)
}

func handleAction(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	action := r.URL.Query().Get("action")

	if id == "" {
		errorResponse(w, "Missing id", 400)
		return
	}

	clientsLock.RLock()
	data, _ := os.ReadFile(clientsFile)
	var list []ClientConfig
	json.Unmarshal(data, &list)
	var target *ClientConfig
	for i := range list {
		if list[i].ID == id {
			target = &list[i]
			break
		}
	}
	clientsLock.RUnlock()

	if target == nil {
		errorResponse(w, "Client not found", 404)
		return
	}

	var err error
	switch action {
	case "start":
		err = startClientContainer(target)
	case "stop":
		err = stopClientContainer(id)
	case "delete":
		stopClientContainer(id)
		runCommand("rm", "minin-client-"+id)
		clientsLock.Lock()
		newValue := []ClientConfig{}
		for _, item := range list {
			if item.ID != id {
				newValue = append(newValue, item)
			}
		}
		out, _ := json.MarshalIndent(newValue, "", "  ")
		os.WriteFile(clientsFile, out, 0644)
		clientsLock.Unlock()
	default:
		errorResponse(w, "Unknown action", 400)
		return
	}

	if err != nil {
		errorResponse(w, err.Error(), 500)
		return
	}

	jsonResponse(w, "OK")
}

func main() {
	if _, err := runCommand("version"); err != nil {
		log.Println("Warning: Docker not found. Dashboard will not be able to manage containers.")
	}

	mux := http.NewServeMux()

	mux.HandleFunc(ApiBase+"/login", authMiddleware(handleLogin))
	mux.HandleFunc(ApiBase+"/clients", authMiddleware(handleListClients))
	mux.HandleFunc(ApiBase+"/save", authMiddleware(handleSaveClient))
	mux.HandleFunc(ApiBase+"/action", authMiddleware(handleAction))
	mux.HandleFunc(ApiBase+"/logs", authMiddleware(handleLogs))

	// Serve config.js dynamically for the frontend
	mux.HandleFunc("/config.js", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/javascript")
		fmt.Fprintf(w, "const API_BASE = '%s';", ApiBase)
	})

	fs := http.FileServer(http.Dir("./static"))
	mux.Handle("/", fs)

	portStr := Port
	if !strings.HasPrefix(portStr, ":") {
		portStr = ":" + portStr
	}

	log.Printf("Starting dashboard on %s", portStr)
	log.Fatal(http.ListenAndServe(portStr, mux))
}
