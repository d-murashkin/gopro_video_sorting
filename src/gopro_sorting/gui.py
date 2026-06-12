from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .cli import run
from .config import AnalyzerConfig, default_output_dir, default_sample_data_dir


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("GoPro Video Sorting")
        self.geometry("680x260")

        self.input_dir_var = tk.StringVar(value=str(default_sample_data_dir()))
        self.output_dir_var = tk.StringVar(value=str(default_output_dir()))
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Input folder").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.input_dir_var, width=70).grid(row=1, column=0, sticky=tk.EW)
        ttk.Button(frame, text="Browse", command=self._pick_input).grid(row=1, column=1, padx=(8, 0))

        ttk.Label(frame, text="Output folder").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Entry(frame, textvariable=self.output_dir_var, width=70).grid(row=3, column=0, sticky=tk.EW)
        ttk.Button(frame, text="Browse", command=self._pick_output).grid(row=3, column=1, padx=(8, 0))

        ttk.Button(frame, text="Run analysis", command=self._run).grid(row=4, column=0, sticky=tk.W, pady=(16, 0))
        ttk.Label(frame, textvariable=self.status_var).grid(row=5, column=0, sticky=tk.W, pady=(12, 0))

        frame.columnconfigure(0, weight=1)

    def _pick_input(self) -> None:
        selected = filedialog.askdirectory(title="Choose input folder")
        if selected:
            self.input_dir_var.set(selected)

    def _pick_output(self) -> None:
        selected = filedialog.askdirectory(title="Choose output folder")
        if selected:
            self.output_dir_var.set(selected)

    def _run(self) -> None:
        input_dir = Path(self.input_dir_var.get())
        output_dir = Path(self.output_dir_var.get())
        if not input_dir.exists():
            messagebox.showerror("Missing input", "Input folder does not exist.")
            return

        self.status_var.set("Running...")
        self.update_idletasks()

        try:
            cfg = AnalyzerConfig(input_dir=input_dir, output_dir=output_dir)
            csv_path, json_path, summary_path, script_path = run(cfg)
            self.status_var.set(
                f"Done: {csv_path.name}, {json_path.name}, {summary_path.name}, {script_path.name}"
            )
            messagebox.showinfo("Completed", f"Results written to {output_dir}")
        except Exception as exc:  # pragma: no cover - GUI path
            self.status_var.set("Failed")
            messagebox.showerror("Error", str(exc))


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
