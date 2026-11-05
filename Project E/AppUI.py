import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import Logic


class ApplicationUI:

    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor Workspace")
        self.root.geometry("1150x780")
        self.root.configure(bg="#11111b")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()

        self.setup_ui()

    def _configure_styles(self):
        self.style.configure(".", background="#11111b", foreground="#cdd6f4")
        self.style.configure("TFrame", background="#11111b")
        self.style.configure("Card.TFrame", background="#1e1e2e", borderwidth=0)
        self.style.configure("Header.TLabel", background="#11111b",
                             foreground="#cdd6f4", font=("Segoe UI", 16, "bold"))
        self.style.configure("SectionTitle.TLabel", background="#1e1e2e",
                             foreground="#89b4fa", font=("Segoe UI", 10, "bold"))
        self.style.configure("Action.TButton", background="#89b4fa",
                             foreground="#11111b", font=("Segoe UI", 10, "bold"),
                             borderwidth=0, focuscolor="none")
        self.style.map("Action.TButton", background=[("active", "#b4befe")])
        self.style.configure("Treeview", background="#1e1e2e",
                             fieldbackground="#1e1e2e", foreground="#cdd6f4",
                             font=("Segoe UI", 9), rowheight=28, borderwidth=0)
        self.style.configure("Treeview.Heading", background="#181825",
                             foreground="#89b4fa",
                             font=("Segoe UI", 9, "bold"), relief="flat")
        self.style.map("Treeview",
                       background=[("selected", "#45475a")],
                       foreground=[("selected", "#89b4fa")])

    # ---------------------------------------------------------------- layout
    def setup_ui(self):
        ttk.Label(self.root, text="System Monitor Workspace",
                  style="Header.TLabel").pack(anchor="w", padx=30, pady=(25, 12))

        self._build_input_section()

        grid = ttk.Frame(self.root, style="TFrame")
        grid.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        grid.columnconfigure(0, weight=1, uniform="equal")
        grid.columnconfigure(1, weight=1, uniform="equal")
        grid.rowconfigure(0, weight=1, uniform="equal")
        grid.rowconfigure(1, weight=1, uniform="equal")

        self._build_reminders_section(grid)
        self._build_text_section(grid)
        self._build_files_section(grid)

    def _build_input_section(self):
        outer = ttk.Frame(self.root, style="Card.TFrame")
        outer.pack(fill="x", padx=30, pady=10)

        inner = ttk.Frame(outer, style="Card.TFrame")
        inner.pack(fill="x", expand=True, padx=16, pady=16)

        self.user_input = tk.Text(
            inner, height=3, bg="#11111b", fg="#cdd6f4",
            insertbackground="#89b4fa", font=("Segoe UI", 10),
            bd=0, padx=14, pady=12,
            highlightthickness=1,
            highlightbackground="#313244",
            highlightcolor="#89b4fa",
            wrap="word",
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 15))

        ttk.Button(inner, text="Process Entry", style="Action.TButton",
                   command=self.on_process_click, cursor="hand2"
                   ).pack(side="right", ipady=10, ipadx=16)

    def _build_reminders_section(self, grid):
        frame = ttk.Frame(grid, style="Card.TFrame")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._section_header(frame, "🔔 ACTIVE REMINDERS")

        # IMPORTANT: pack the Delete button BEFORE the list container.
        # Tk packer allocates space in pack order; a later fill="both",
        # expand=True widget would otherwise consume all remaining height
        # and squeeze this button to zero pixels.
        ttk.Button(
            frame, text="Delete", style="Action.TButton",
            command=self.delete_selected_reminder,
            cursor="hand2", width=16,
        ).pack(side="bottom", anchor="e", padx=18, pady=(0, 18),
            ipady=10, ipadx=16)

        container = ttk.Frame(frame, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        self.reminder_entries = {}
        self.reminder_box = tk.Listbox(
            container, bg="#11111b", fg="#f38ba8",
            selectbackground="#45475a", selectforeground="#f38ba8",
            font=("Consolas", 10), bd=0, highlightthickness=0,
            activestyle="none",
        )
        scroll = ttk.Scrollbar(container, orient="vertical",
                            command=self.reminder_box.yview)
        self.reminder_box.configure(yscrollcommand=scroll.set)
        self.reminder_box.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
    def _build_text_section(self, grid):
        frame = ttk.Frame(grid, style="Card.TFrame")
        frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self._section_header(frame, "📋 FORMATTED PAYLOAD STREAM")

        container = ttk.Frame(frame, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.text_display = tk.Text(
            container, bg="#11111b", fg="#a6e3a1", font=("Consolas", 10),
            bd=0, highlightthickness=0, padx=14, pady=14,
            state="disabled", wrap="word",
        )
        scroll = ttk.Scrollbar(container, orient="vertical",
                               command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=scroll.set)
        self.text_display.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _build_files_section(self, grid):
        frame = ttk.Frame(grid, style="Card.TFrame")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self._section_header(frame, "📁 GENERATED ARCHIVE & DIRECTORIES")

        container = ttk.Frame(frame, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.file_tree = ttk.Treeview(
            container, columns=("Directory"), show="tree headings", style="Treeview"
        )
        self.file_tree.heading("#0", text="Filename/Object", anchor="w")
        self.file_tree.heading("Directory", text="Source Path Location", anchor="w")
        self.file_tree.column("#0", width=160, stretch=True)
        self.file_tree.column("Directory", width=220, stretch=True)

        scroll = ttk.Scrollbar(container, orient="vertical",
                               command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scroll.set)
        self.file_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _section_header(self, parent, title_text):
        ttk.Label(parent, text=title_text, style="SectionTitle.TLabel"
                  ).pack(anchor="w", padx=18, pady=(16, 12))

    # ---------------------------------------------------------- thread-safe UI
    def update_formatted_text(self, text_content):
        def _update():
            self.text_display.config(state="normal")
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert("1.0", text_content)
            self.text_display.config(state="disabled")
        self.root.after(0, _update)

    def add_reminder_display(self, reminder_time, task):
        def _add():
            label = f"🔔 [{reminder_time}] - {task.upper()}"
            self.reminder_box.insert(tk.END, label)
            self.reminder_entries[label] = (reminder_time, task)
        self.root.after(0, _add)

    def upsert_file_display(self, filepath):
        """Insert file into the tree, or update it if it already exists."""
        def _update():
            file_dir, filename = os.path.split(filepath)
            target = os.path.normcase(os.path.abspath(filepath))
            for item_id in self.file_tree.get_children(""):
                item = self.file_tree.item(item_id)
                candidate = os.path.normcase(
                    os.path.abspath(os.path.join(item["values"][0], item["text"]))
                )
                if candidate == target:
                    self.file_tree.item(item_id, text=filename, values=(file_dir,))
                    return
            self.file_tree.insert("", "end", text=filename, values=(file_dir,))
        self.root.after(0, _update)

    def delete_selected_reminder(self):
        selection = self.reminder_box.curselection()
        if not selection:
            messagebox.showinfo("Delete Reminder", "Select a reminder to delete.")
            return

        index = selection[0]
        label = self.reminder_box.get(index)
        reminder = self.reminder_entries.get(label)
        manager = getattr(self, "reminder_manager", None)

        if reminder is None or manager is None:
            messagebox.showerror("Delete Reminder",
                                 "Could not find the selected reminder in the scheduler.")
            return

        result = manager.remove_reminder(*reminder)
        if result.get("status") != "success":
            messagebox.showerror("Delete Reminder",
                                 result.get("message", "Could not delete the reminder."))
            return

        self.reminder_box.delete(index)
        del self.reminder_entries[label]

    def on_process_click(self):
        prompt = self.user_input.get("1.0", "end-1c").strip()
        if prompt:
            Logic.process_request(prompt, self)
            self.user_input.tag_add("sel", "1.0", "end-1c")
            self.user_input.focus_set()


def main():
    root = tk.Tk()
    ApplicationUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()