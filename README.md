# Llama Server Launcher

This project provides a user-friendly graphical interface for managing and controlling the [llama-server](https://github.com/ggml-org/llama.cpp) with GGUF models. It allows you to easily configure, start, and stop the server process.

![Llama_server_ui](https://github.com/user-attachments/assets/1e35cd19-f816-4124-93f8-fad72e665111)


## Features

- Browse for the `llama-server` executable and GGUF model files.
- Set server parameters such as GPU layers, context size, host, port, and device.
- Preview the command line that will be executed to start the server.
- Save and load parameters for different models.
- Start and stop the server process with ease.
- Check the status of the running server.

## Requirements

- Python 3.x
- Tkinter (usually included with standard Python distributions)
- psutil library (`pip install psutil`)
- gguf_dump-v3.py script in the same directory as this UI script for model parameter extraction (available from [here](https://github.com/ggerganov/llama.cpp/blob/main/tools/gguf-dump/gguf_dump_v3.py))

## Installation

Clone or download this repository:

```bash
git clone https://github.com/hashms0a/Llama-Server-Launcher.git
cd Llama-Server-Launcher
pip install -r requirements.txt
```

## Usage

### Running the UI

Run the application from the command line:

```bash
python3 llama_server_UI.py 
```

### Configuration File

The script maintains configuration settings in an ini file named `llama_server_config.ini`. This includes paths to the selected server executable and the last used model.
