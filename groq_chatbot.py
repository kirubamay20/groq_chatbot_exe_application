
import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """
You are a helpful AI assistant.
Answer accurately and clearly.
Use examples when useful.
Format answers with Markdown-style text when appropriate.
"""


class GroqChatbotApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Groq AI Chatbot")
        self.root.geometry("850x650")
        self.root.minsize(600, 450)

        self.history = []
        self.events = queue.Queue()
        self.busy = False
        self.current_response = ""
        self.answer_start = "Assistant: "
        self.api_key = os.environ.get("GROQ_API_KEY", "").strip()

        if not self.api_key:
            self.api_key = simpledialog.askstring(
                "Groq API Key",
                "Enter your Groq API key:",
                show="*",
                parent=root
            ) or ""

        if not self.api_key.strip():
            messagebox.showerror(
                "API Key Required",
                "A Groq API key is required to use this application."
            )
            self.root.after(100, self.root.destroy)
            return

        self.api_key = self.api_key.strip()

        self.llm = ChatGroq(
            api_key=self.api_key,
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=2048,
            streaming=True,
            max_retries=2
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.llm

        self.build_ui()
        self.root.after(100, self.process_events)

    def build_ui(self):

        self.root.configure(bg="#F3F4F6")

        header = tk.Frame(self.root, bg="#172554", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Groq AI Chatbot",
            font=("Segoe UI", 19, "bold"),
            fg="white",
            bg="#172554"
        ).pack(side="left", padx=20, pady=15)

        tk.Button(
            header,
            text="New Chat",
            command=self.new_chat,
            font=("Segoe UI", 10),
            bg="#DBEAFE",
            fg="#172554",
            relief="flat",
            padx=12,
            pady=7
        ).pack(side="right", padx=18, pady=15)

        self.chat_area = tk.Text(
            self.root,
            wrap="word",
            font=("Segoe UI", 11),
            bg="white",
            fg="#1F2937",
            padx=18,
            pady=15,
            relief="flat",
            state="disabled"
        )
        self.chat_area.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(15, 8)
        )

        self.chat_area.tag_configure(
            "user",
            foreground="#1D4ED8",
            font=("Segoe UI", 11, "bold")
        )
        self.chat_area.tag_configure(
            "assistant",
            foreground="#047857",
            font=("Segoe UI", 11, "bold")
        )
        self.chat_area.tag_configure(
            "body",
            foreground="#1F2937",
            spacing1=3,
            spacing3=8
        )
        self.chat_area.tag_configure(
            "error",
            foreground="#B91C1C"
        )

        bottom = tk.Frame(self.root, bg="#F3F4F6")
        bottom.pack(fill="x", padx=15, pady=(0, 8))

        self.input_box = tk.Text(
            bottom,
            height=3,
            wrap="word",
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        self.input_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.input_box.bind("<Control-Return>", self.send_message)

        self.send_button = tk.Button(
            bottom,
            text="Send",
            command=self.send_message,
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=22,
            pady=12
        )
        self.send_button.pack(side="right")

        self.status = tk.Label(
            self.root,
            text=f"Ready | Model: {MODEL_NAME}",
            anchor="w",
            bg="#E5E7EB",
            fg="#374151",
            font=("Segoe UI", 9),
            padx=12,
            pady=6
        )
        self.status.pack(fill="x", side="bottom")

        self.append_text(
            "Groq AI Chatbot\n",
            "assistant"
        )
        self.append_text(
            "Hello! Ask me anything.\n\n",
            "body"
        )

    def append_text(self, text, tag="body"):

        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", text, tag)
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

    def send_message(self, event=None):

        if self.busy:
            return "break" if event else None

        message = self.input_box.get("1.0", "end-1c").strip()

        if not message:
            return "break" if event else None

        self.input_box.delete("1.0", "end")

        self.append_text("You: ", "user")
        self.append_text(message + "\n\n", "body")

        # Snapshot prior turns before adding the current question.
        previous_history = list(self.history)

        self.history.append(HumanMessage(content=message))

        self.busy = True
        self.send_button.configure(state="disabled")
        self.status.configure(text="Generating response...")

        self.append_text("Assistant: ", "assistant")
        self.current_response = ""

        threading.Thread(
            target=self.generate_response,
            args=(message, previous_history),
            daemon=True
        ).start()

        return "break" if event else None

    def generate_response(self, message, previous_history):

        try:
            for chunk in self.chain.stream({
                "history": previous_history[-20:],
                "input": message
            }):

                content = chunk.content

                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = "".join(
                        part.get("text", "")
                        for part in content
                        if isinstance(part, dict)
                        and part.get("type") == "text"
                    )
                else:
                    text = ""

                if text:
                    self.events.put(("token", text))

            self.events.put(("complete", None))

        except Exception as exc:
            # Do not display the API key or request headers.
            print("Groq request error:", type(exc).__name__, str(exc))
            self.events.put((
                "error",
                f"Request failed ({type(exc).__name__}). "
                "Check your API key, internet connection, model "
                "availability, and Groq usage limits."
            ))

    def process_events(self):

        try:
            while True:
                event, data = self.events.get_nowait()

                if event == "token":
                    self.current_response += data
                    self.append_text(data, "body")

                elif event == "complete":
                    if self.current_response:
                        self.history.append(
                            AIMessage(content=self.current_response)
                        )

                    self.append_text("\n\n", "body")
                    self.finish_request()

                elif event == "error":
                    self.append_text("\n" + data + "\n\n", "error")
                    self.finish_request()

        except queue.Empty:
            pass

        if self.root.winfo_exists():
            self.root.after(100, self.process_events)

    def finish_request(self):

        self.busy = False
        self.send_button.configure(state="normal")
        self.status.configure(text=f"Ready | Model: {MODEL_NAME}")
        self.input_box.focus_set()

    def new_chat(self):

        if self.busy:
            messagebox.showinfo(
                "Please wait",
                "Wait for the current response to finish before starting a new chat."
            )
            return

        self.history.clear()
        self.chat_area.configure(state="normal")
        self.chat_area.delete("1.0", "end")
        self.chat_area.configure(state="disabled")

        self.append_text("New conversation started.\n\n", "assistant")
        self.status.configure(text=f"Ready | Model: {MODEL_NAME}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GroqChatbotApp(root)
    root.mainloop()
