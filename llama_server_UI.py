#!/usr/bin/env python3
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import configparser
import re
from pathlib import Path
import signal
import platform


class LlamaServerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Llama Server UI")
        self.root.geometry("700x550")
        self.root.resizable(True, True)

        # Configuration file
        self.config_file = "llama_server_config.ini"
        self.config = configparser.ConfigParser()
        
        # Default values
        self.llama_server_path = ""
        self.gguf_model_path = ""
        self.params_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parameters")
        
        # Server process tracking
        self.server_process = None
        
        # Ensure parameters folder exists
        if not os.path.exists(self.params_folder):
            os.makedirs(self.params_folder)
        
        # Load configuration if exists
        self.load_config()
        
        # Create the UI
        self.create_widgets()
        
    def load_config(self):
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            if "Settings" in self.config:
                settings = self.config["Settings"]
                self.llama_server_path = settings.get("llama_server_path", "")
                self.gguf_model_path = settings.get("gguf_model_path", "")
    
    def save_config(self):
        """Save configuration to file"""
        if "Settings" not in self.config:
            self.config["Settings"] = {}
        
        self.config["Settings"]["llama_server_path"] = self.llama_server_path
        self.config["Settings"]["gguf_model_path"] = self.gguf_model_path
        
        with open(self.config_file, "w") as f:
            self.config.write(f)
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Server Location Frame
        server_frame = ttk.LabelFrame(main_frame, text="Server Location", padding="10")
        server_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.server_path_var = tk.StringVar(value=self.llama_server_path)
        ttk.Label(server_frame, text="Llama Server Path:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(server_frame, textvariable=self.server_path_var, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(server_frame, text="Browse", command=self.browse_server).grid(row=0, column=2, padx=5, pady=5)
        
        # Model Frame
        model_frame = ttk.LabelFrame(main_frame, text="Model Settings", padding="10")
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.model_path_var = tk.StringVar(value=self.gguf_model_path)
        ttk.Label(model_frame, text="GGUF Model Path:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.model_path_var, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(model_frame, text="Browse", command=self.browse_model).grid(row=0, column=2, padx=5, pady=5)
        
        # Parameters Frame
        params_frame = ttk.LabelFrame(main_frame, text="Server Parameters", padding="10")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # GPU Layers
        self.gpu_layers_var = tk.StringVar(value="0")
        ttk.Label(params_frame, text="GPU Layers (ngl):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.gpu_layers_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Context Size
        self.context_size_var = tk.StringVar(value="2048")
        ttk.Label(params_frame, text="Context Size (c):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.context_size_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Host
        self.host_var = tk.StringVar(value="0.0.0.0")
        ttk.Label(params_frame, text="Host:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.host_var, width=15).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Port
        self.port_var = tk.StringVar(value="9000")
        ttk.Label(params_frame, text="Port:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.port_var, width=10).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Device
        self.device_var = tk.StringVar(value="Vulkan1")
        ttk.Label(params_frame, text="Device:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.device_var, width=15).grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Update Button
        ttk.Button(params_frame, text="Update from Model", command=self.update_from_model).grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        
        # Model Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="Model Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=8, width=60, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.config(state=tk.DISABLED)
        
        # Command Preview Frame
        preview_frame = ttk.LabelFrame(main_frame, text="Command Preview", padding="10")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=3, width=60, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_text.config(state=tk.DISABLED)
        
        # Preview Button
        ttk.Button(preview_frame, text="Preview Command", command=self.preview_command).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Action Buttons Frame
        actions_frame = ttk.Frame(main_frame, padding="10")
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status indicator for server running state
        self.server_status_var = tk.StringVar(value="Server Status: Not Running")
        self.status_label = ttk.Label(actions_frame, textvariable=self.server_status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        self.save_button = ttk.Button(actions_frame, text="Save Parameters", command=self.save_parameters)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(actions_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.RIGHT, padx=5)
        
        self.stop_button = ttk.Button(actions_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5)
        
        # Update the command preview when any parameter changes
        self.server_path_var.trace_add("write", lambda *args: self.update_command_preview())
        self.model_path_var.trace_add("write", lambda *args: self.update_command_preview())
        self.gpu_layers_var.trace_add("write", lambda *args: self.update_command_preview())
        self.context_size_var.trace_add("write", lambda *args: self.update_command_preview())
        self.host_var.trace_add("write", lambda *args: self.update_command_preview())
        self.port_var.trace_add("write", lambda *args: self.update_command_preview())
        self.device_var.trace_add("write", lambda *args: self.update_command_preview())
    
    def browse_server(self):
        """Browse for llama-server executable"""
        path = filedialog.askopenfilename(title="Select llama-server executable")
        if path:
            self.llama_server_path = path
            self.server_path_var.set(path)
            self.save_config()
            self.update_command_preview()
    
    def browse_model(self):
        """Browse for GGUF model file"""
        path = filedialog.askopenfilename(
            title="Select GGUF Model",
            filetypes=[("GGUF Files", "*.gguf"), ("All Files", "*.*")]
        )
        if path:
            self.gguf_model_path = path
            self.model_path_var.set(path)
            self.save_config()
            self.load_model_parameters()
            self.update_model_info()
            self.update_command_preview()
    
    def update_model_info(self):
        """Update the model information text area"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        if os.path.exists(self.gguf_model_path):
            model_name = os.path.basename(self.gguf_model_path)
            model_size = os.path.getsize(self.gguf_model_path) / (1024 * 1024 * 1024)  # Size in GB
            
            info_text = f"Model: {model_name}\n"
            info_text += f"Size: {model_size:.2f} GB\n"
            
            if self.context_size_var.get():
                info_text += f"Context Length: {self.context_size_var.get()} tokens\n"
            
            if self.gpu_layers_var.get():
                info_text += f"GPU Layers: {self.gpu_layers_var.get()}\n"
            
            self.info_text.insert(tk.END, info_text)
        else:
            self.info_text.insert(tk.END, "No model loaded.")
        
        self.info_text.config(state=tk.DISABLED)
    
    def update_from_model(self):
        """Update parameters from model using gguf_dump-v3.py script"""
        if not os.path.exists(self.gguf_model_path):
            messagebox.showerror("Error", "Please select a GGUF model file first.")
            return
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gguf_dump-v3.py")
        
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "gguf_dump-v3.py script not found in the same directory.")
            return
        
        try:
            # Run the gguf_dump-v3.py script to extract parameters
            result = subprocess.run(
                ["python", script_path, self.gguf_model_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout + result.stderr
            
            # Extract block_count and context_length using regex
            block_count_match = re.search(r'block_count\s*=\s*(\d+)', output)
            context_length_match = re.search(r'context_length\s*=\s*(\d+)', output)
            
            if block_count_match and context_length_match:
                block_count = int(block_count_match.group(1))
                context_length = int(context_length_match.group(1))
                
                # Set values in the UI (add 1 to block_count as per requirements)
                self.gpu_layers_var.set(str(block_count + 1))
                self.context_size_var.set(str(context_length))
                
                messagebox.showinfo("Success", f"Updated parameters from model:\nGPU Layers: {block_count + 1}\nContext Size: {context_length}")
                self.update_model_info()
                self.update_command_preview()
            else:
                messagebox.showerror("Error", "Failed to extract parameters from model output.")
        
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to run gguf_dump-v3.py: {str(e)}\n{e.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def get_params_filename(self):
        """Get the parameters filename based on the model name"""
        if not self.gguf_model_path:
            return None
        
        model_name = os.path.basename(self.gguf_model_path)
        return os.path.join(self.params_folder, f"{model_name}.json")
    
    def load_model_parameters(self):
        """Load parameters for the selected model if they exist"""
        params_file = self.get_params_filename()
        
        if params_file and os.path.exists(params_file):
            try:
                with open(params_file, 'r') as f:
                    params = json.load(f)
                
                # Update UI with loaded parameters
                self.gpu_layers_var.set(str(params.get("gpu_layers", "0")))
                self.context_size_var.set(str(params.get("context_size", "2048")))
                self.host_var.set(params.get("host", "0.0.0.0"))
                self.port_var.set(str(params.get("port", "9000")))
                self.device_var.set(params.get("device", "Vulkan1"))
                
                messagebox.showinfo("Parameters Loaded", f"Loaded saved parameters for {os.path.basename(self.gguf_model_path)}")
                self.update_command_preview()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load parameters: {str(e)}")
    
    def save_parameters(self):
        """Save the current parameters for the loaded model"""
        if not self.gguf_model_path:
            messagebox.showerror("Error", "Please select a GGUF model file first.")
            return
        
        params_file = self.get_params_filename()
        
        if not params_file:
            return
        
        try:
            # Prepare parameters dictionary
            params = {
                "gpu_layers": int(self.gpu_layers_var.get() or 0),
                "context_size": int(self.context_size_var.get() or 2048),
                "host": self.host_var.get(),
                "port": int(self.port_var.get() or 9000),
                "device": self.device_var.get()
            }
            
            # Save to file
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=4)
            
            messagebox.showinfo("Parameters Saved", f"Parameters saved for {os.path.basename(self.gguf_model_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save parameters: {str(e)}")
    
    def build_command(self):
        """Build the command that will be executed to start the server"""
        if not self.llama_server_path or not self.gguf_model_path:
            return []
        
        # Build command
        cmd = [
            self.llama_server_path,
            "-m", self.gguf_model_path,
            "-ngl", self.gpu_layers_var.get(),
            "-c", self.context_size_var.get(),
            "--port", self.port_var.get(),
            "--device", self.device_var.get(),
            "--host", self.host_var.get()
        ]
        
        return cmd
        
    def update_command_preview(self):
        """Update the command preview text area"""
        cmd = self.build_command()
        
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        if cmd:
            # For clarity in display, replace long paths with shorter ones if needed
            display_cmd = cmd.copy()
            if os.path.exists(self.gguf_model_path):
                model_name = os.path.basename(self.gguf_model_path)
                model_idx = display_cmd.index(self.gguf_model_path)
                display_cmd[model_idx] = f".../{model_name}"
            
            command_str = " ".join(display_cmd)
            self.preview_text.insert(tk.END, command_str)
        else:
            self.preview_text.insert(tk.END, "Please select server executable and model file.")
        
        self.preview_text.config(state=tk.DISABLED)
    
    def preview_command(self):
        """Show the full command in a popup dialog for easy copying"""
        cmd = self.build_command()
        
        if not cmd:
            messagebox.showinfo("Command Preview", "Please select server executable and model file.")
            return
        
        command_str = " ".join(cmd)
        
        # Create a dialog to show the command
        preview_dialog = tk.Toplevel(self.root)
        preview_dialog.title("Command Preview")
        preview_dialog.geometry("600x200")
        
        # Make dialog modal
        preview_dialog.grab_set()
        
        # Add text area with command
        cmd_text = tk.Text(preview_dialog, wrap=tk.WORD)
        cmd_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        cmd_text.insert(tk.END, command_str)
        
        # Make it read-only
        cmd_text.config(state=tk.NORMAL)
        
        # Add Copy button
        def copy_to_clipboard():
            preview_dialog.clipboard_clear()
            preview_dialog.clipboard_append(command_str)
            messagebox.showinfo("Copied", "Command copied to clipboard.")
        
        button_frame = ttk.Frame(preview_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=preview_dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def start_server(self):
        """Start the llama-server with the specified parameters"""
        if not os.path.exists(self.llama_server_path):
            messagebox.showerror("Error", "Please select a valid llama-server executable.")
            return
        
        if not os.path.exists(self.gguf_model_path):
            messagebox.showerror("Error", "Please select a valid GGUF model file.")
            return
        
        # Check if server is already running
        if self.server_process and self.server_process.poll() is None:
            messagebox.showinfo("Server Running", "The server is already running.")
            return
        
        try:
            # Get command
            cmd = self.build_command()
            
            # Display command
            command_str = " ".join(cmd)
            info_msg = f"Starting server with command:\n\n{command_str}\n\nContinue?"
            if not messagebox.askyesno("Confirm Start", info_msg):
                return
            
            # Save parameters before starting
            self.save_parameters()
            
            # Start server in a new process
            self.server_process = subprocess.Popen(cmd)
            
            # Update UI state
            self.update_server_status(True)
            
            messagebox.showinfo("Server Started", "Llama Server has been started.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        """Stop the running server process"""
        if not self.server_process or self.server_process.poll() is not None:
            messagebox.showinfo("Server Not Running", "No server is currently running.")
            self.update_server_status(False)
            return
        
        try:
            # Confirm before stopping
            if not messagebox.askyesno("Confirm Stop", "Are you sure you want to stop the server?"):
                return
            
            # Platform-specific process termination
            if platform.system() == "Windows":
                # Windows requires specific handling
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.server_process.pid)])
            else:
                # Unix-like systems can use os.kill
                os.kill(self.server_process.pid, signal.SIGTERM)
                # Give it a moment to shut down gracefully
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # If it doesn't shut down gracefully, force it
                    os.kill(self.server_process.pid, signal.SIGKILL)
            
            # Update UI state
            self.update_server_status(False)
            
            messagebox.showinfo("Server Stopped", "Llama Server has been stopped.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
            # Check if the process is actually still running
            if self.server_process.poll() is not None:
                self.update_server_status(False)
    
    def update_server_status(self, running):
        """Update the UI to reflect the server's running state"""
        if running:
            self.server_status_var.set("Server Status: Running")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.server_status_var.set("Server Status: Not Running")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.server_process = None


if __name__ == "__main__":
    root = tk.Tk()
    app = LlamaServerUI(root)
    root.mainloop()
