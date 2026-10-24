# Groq AI Chatbot — Windows EXE Build Guide

This guide explains how to run the LangChain + Groq desktop chatbot and package it as a Windows `.exe`.

## What you need

- A Windows 10 or Windows 11 computer
- Python 3.10 or newer (64-bit recommended)
- An internet connection
- A Groq API key: https://console.groq.com/keys

> **Important:** Google Colab runs Linux, so use a Windows computer to build a native Windows `.exe` with PyInstaller.

## 1. Install Python

1. Download Python for Windows: https://www.python.org/downloads/windows/
2. Run the installer.
3. Enable **Add Python to PATH** if the installer shows that option.
4. Finish installation.

Open Command Prompt and check Python:

```bat
py --version
```

If the `py` command is unavailable, reinstall Python and ensure it is added to PATH.

## 2. Create the project folder

Create a folder called `GroqChatbot`, for example:

```text
C:\Users\YourUser\GroqChatbot
```

Inside that folder, save the desktop chatbot code in a file named:

```text
groq_chatbot.py
```

Use the complete `groq_chatbot.py` code provided with this guide. Do not name the file `tkinter.py`, `gradio.py`, or `langchain_groq.py`, because those names can conflict with Python packages.

## 3. Open Command Prompt in the project folder

In File Explorer, open the `GroqChatbot` folder. Click the address bar, type `cmd`, and press Enter.

Install the dependencies:

```bat
py -m pip install --upgrade pip
py -m pip install -U langchain-core langchain-groq pyinstaller
```

## 4. Run and test the Python app first

Run:

```bat
py groq_chatbot.py
```

The app should open a desktop window and ask for your Groq API key.

1. Create or copy your API key from https://console.groq.com/keys.
2. Enter it into the app's password prompt.
3. Ask a test question.
4. Confirm that the app returns a response.

The app needs internet access because the language model is hosted by Groq.

### Troubleshooting before packaging

- **Invalid API key / 401:** Check the key and make sure it has not been revoked.
- **Rate limit / 429:** Check your Groq account's usage and rate limits.
- **Model unavailable:** Check the current model list at https://console.groq.com/docs/models and update `MODEL_NAME` in the Python file if needed.
- **Missing module:** Rerun the dependency installation command.
- **No window appears:** Run the Python script from Command Prompt so error messages remain visible.

## 5. Build the Windows executable

Once the Python app works, run this command in the same project folder:

```bat
py -m PyInstaller --noconfirm --clean --onefile --windowed --name GroqAIChatbot groq_chatbot.py
```

Wait until PyInstaller completes. The executable should be created at:

```text
GroqChatbot\dist\GroqAIChatbot.exe
```

The folder structure will look similar to:

```text
GroqChatbot/
├── groq_chatbot.py
├── build/
├── dist/
│   └── GroqAIChatbot.exe
└── GroqAIChatbot.spec
```

PyInstaller may create additional files or folders. That is normal.

## 6. Launch the EXE

1. Open the `dist` folder.
2. Double-click `GroqAIChatbot.exe`.
3. Enter your Groq API key when prompted.
4. Test a few questions and start a new chat.

You can copy `GroqAIChatbot.exe` to another compatible Windows computer. Test it on the destination computer before distributing it. The destination computer needs internet access and a valid Groq API key.

## 7. Rebuild after changing the code

Save your changes to `groq_chatbot.py`, then run the PyInstaller command again:

```bat
py -m PyInstaller --noconfirm --clean --onefile --windowed --name GroqAIChatbot groq_chatbot.py
```

The updated executable will be placed in `dist`.

## Security and usage notes

- Never publish your Groq API key or commit it to a public repository.
- This app asks for the key at launch and holds it in memory; it does not intentionally save the key to disk.
- Anyone who uses the app must provide their own valid API key unless you deliberately build a different credential-management design.
- The executable is not an offline AI model. Prompts are sent to Groq's API for processing.
- A one-file executable can take a little time to start because it extracts bundled components.
- Windows security software may warn about a newly built, unsigned executable. Only run builds you created or otherwise trust.

## Official links

- Groq API keys: https://console.groq.com/keys
- Groq model documentation: https://console.groq.com/docs/models
- Python for Windows: https://www.python.org/downloads/windows/
- PyInstaller documentation: https://pyinstaller.org/en/stable/

## Quick command checklist

Run these commands from the project folder, in order:

```bat
py --version
py -m pip install --upgrade pip
py -m pip install -U langchain-core langchain-groq pyinstaller
py groq_chatbot.py
py -m PyInstaller --noconfirm --clean --onefile --windowed --name GroqAIChatbot groq_chatbot.py
```

Your output executable should be:

```text
dist\GroqAIChatbot.exe
```
