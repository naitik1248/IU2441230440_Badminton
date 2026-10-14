"""
Naitik Parmar - Badminton Match Performance Analyzer

A Tkinter desktop application for maintaining badminton match records,
calculating performance statistics, filtering/searching records, and
generating Matplotlib visual reports.

Run:
    python main.py

Dependencies:
    pip install pandas numpy matplotlib
"""

import csv
import uuid
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from storage import load_matches, save_matches, update_match, delete_match
from validation import validate_match, normalize_match
from analytics import (
    matches_dataframe,
    calculate_statistics,
    opponent_summary,
    event_summary,
    recent_form,
    export_dataframe,
)

PLAYER_NAME = "Naitik Parmar"
APP_TITLE = "Naitik Parmar | Badminton Performance Analyzer"


class BadmintonApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1250x760")
        self.minsize(1050, 680)
        self.configure(bg="#eef3f8")

        self.matches = load_matches()
        self.selected_id = None

        self._configure_style()
        self._build_header()
        self._build_notebook()
        self.refresh_all()

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#eef3f8")
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background="#eef3f8", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#1f4e78", foreground="white",
                        font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", background="#1f4e78", foreground="#dceeff",
                        font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="white", foreground="#1f4e78",
                        font=("Segoe UI", 10, "bold"))
        style.configure("Stat.TLabel", background="white", foreground="#1f4e78",
                        font=("Segoe UI", 22, "bold"))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TNotebook", background="#eef3f8")
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_header(self):
        header = tk.Frame(self, bg="#1f4e78", height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="BADMINTON PERFORMANCE ANALYZER",
                 bg="#1f4e78", fg="white", font=("Segoe UI", 21, "bold")).pack(
                     anchor="w", padx=25, pady=(16, 0))
        tk.Label(header, text=f"Player: {PLAYER_NAME}  •  Sports & Fitness  •  Match Records & Performance Analysis",
                 bg="#1f4e78", fg="#dceeff", font=("Segoe UI", 10)).pack(
                     anchor="w", padx=27, pady=(2, 0))

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.dashboard_tab = ttk.Frame(self.notebook)
        self.records_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.help_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="  Dashboard  ")
        self.notebook.add(self.records_tab, text="  Match Records  ")
        self.notebook.add(self.analysis_tab, text="  Performance Analysis  ")
        self.notebook.add(self.help_tab, text="  About / Help  ")

        self._build_dashboard()
        self._build_records()
        self._build_analysis()
        self._build_help()

    def _stat_card(self, parent, title, variable):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=14)
        frame.pack(side="left", fill="both", expand=True, padx=5)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(frame, textvariable=variable, style="Stat.TLabel").pack(anchor="w", pady=(6, 0))
        return frame

    def _build_dashboard(self):
        top = ttk.Frame(self.dashboard_tab)
        top.pack(fill="x", pady=(5, 10))

        self.var_total = tk.StringVar(value="0")
        self.var_wins = tk.StringVar(value="0")
        self.var_losses = tk.StringVar(value="0")
        self.var_rate = tk.StringVar(value="0%")
        self._stat_card(top, "TOTAL MATCHES", self.var_total)
        self._stat_card(top, "WINS", self.var_wins)
        self._stat_card(top, "LOSSES", self.var_losses)
        self._stat_card(top, "WIN RATE", self.var_rate)

        lower = ttk.Frame(self.dashboard_tab)
        lower.pack(fill="both", expand=True)

        left = ttk.Frame(lower, style="Card.TFrame", padding=16)
        left.pack(side="left", fill="both", expand=True, padx=(5, 8))

        ttk.Label(left, text="Player Snapshot", style="CardTitle.TLabel").pack(anchor="w")
        self.snapshot_text = tk.Text(left, height=16, width=50, bg="white",
                                     fg="#263238", relief="flat", font=("Segoe UI", 11))
        self.snapshot_text.pack(fill="both", expand=True, pady=10)
        self.snapshot_text.configure(state="disabled")

        right = ttk.Frame(lower, style="Card.TFrame", padding=12)
        right.pack(side="right", fill="both", expand=True, padx=(8, 5))
        ttk.Label(right, text="Win / Loss Overview", style="CardTitle.TLabel").pack(anchor="w")
        self.dashboard_fig = Figure(figsize=(5.4, 3.8), dpi=100)
        self.dashboard_ax = self.dashboard_fig.add_subplot(111)
        self.dashboard_canvas = FigureCanvasTkAgg(self.dashboard_fig, master=right)
        self.dashboard_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_records(self):
        container = ttk.Frame(self.records_tab)
        container.pack(fill="both", expand=True)

        form = ttk.Frame(container, style="Card.TFrame", padding=14)
        form.pack(fill="x", pady=(5, 10))

        fields = [
            ("Date (YYYY-MM-DD)", "date"),
            ("Opponent", "opponent"),
            ("Event / Tournament", "event"),
            ("Points For", "points_for"),
            ("Points Against", "points_against"),
            ("Notes", "notes"),
        ]
        self.form_vars = {key: tk.StringVar() for _, key in fields}
        self.form_vars["result"] = tk.StringVar(value="Win")

        for i, (label, key) in enumerate(fields):
            row, col = divmod(i, 3)
            ttk.Label(form, text=label).grid(row=row * 2, column=col, sticky="w",
                                             padx=8, pady=(2, 2))
            ttk.Entry(form, textvariable=self.form_vars[key], width=30).grid(
                row=row * 2 + 1, column=col, sticky="ew", padx=8, pady=(0, 7))
        ttk.Label(form, text="Result").grid(row=0, column=3, sticky="w", padx=8)
        ttk.Combobox(form, textvariable=self.form_vars["result"],
                     values=["Win", "Loss"], state="readonly", width=27).grid(
                         row=1, column=3, sticky="ew", padx=8)

        for col in range(4):
            form.columnconfigure(col, weight=1)

        buttons = ttk.Frame(form, style="Card.TFrame")
        buttons.grid(row=2, column=3, sticky="e", padx=8, pady=(5, 0))
        ttk.Button(buttons, text="Add Match", command=self.add_match,
                   style="Accent.TButton").pack(side="left", padx=3)
        ttk.Button(buttons, text="Update Selected", command=self.update_selected).pack(side="left", padx=3)
        ttk.Button(buttons, text="Clear", command=self.clear_form).pack(side="left", padx=3)
        ttk.Button(buttons, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=3)

        searchbar = ttk.Frame(container)
        searchbar.pack(fill="x", pady=(0, 8))
        ttk.Label(searchbar, text="Search / Filter:").pack(side="left", padx=(6, 6))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(searchbar, textvariable=self.search_var, width=45)
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self.populate_tree())
        ttk.Button(searchbar, text="Export CSV", command=self.export_csv).pack(side="right", padx=6)

        table_frame = ttk.Frame(container)
        table_frame.pack(fill="both", expand=True)

        columns = ("date", "opponent", "event", "result", "score", "margin", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "date": "Date", "opponent": "Opponent", "event": "Event",
            "result": "Result", "score": "Score", "margin": "Margin", "notes": "Notes"
        }
        widths = {"date": 105, "opponent": 160, "event": 190, "result": 80,
                  "score": 90, "margin": 80, "notes": 260}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center" if col in {"date","result","score","margin"} else "w")

        self.tree.tag_configure("win", background="#eaf7ea")
        self.tree.tag_configure("loss", background="#fff0f0")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    def _build_analysis(self):
        controls = ttk.Frame(self.analysis_tab)
        controls.pack(fill="x", pady=5)
        ttk.Button(controls, text="Refresh Analysis", command=self.refresh_all).pack(side="left", padx=5)
        ttk.Button(controls, text="Export Analysis CSV", command=self.export_csv).pack(side="left", padx=5)

        charts = ttk.Frame(self.analysis_tab)
        charts.pack(fill="both", expand=True)

        left = ttk.Frame(charts, style="Card.TFrame", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(5, 6))
        ttk.Label(left, text="Scoring Performance by Match", style="CardTitle.TLabel").pack(anchor="w")
        self.trend_fig = Figure(figsize=(6, 4.5), dpi=100)
        self.trend_ax = self.trend_fig.add_subplot(111)
        self.trend_canvas = FigureCanvasTkAgg(self.trend_fig, master=left)
        self.trend_canvas.get_tk_widget().pack(fill="both", expand=True)

        right = ttk.Frame(charts, style="Card.TFrame", padding=10)
        right.pack(side="right", fill="both", expand=True, padx=(6, 5))
        ttk.Label(right, text="Opponent Win Rate", style="CardTitle.TLabel").pack(anchor="w")
        self.opp_fig = Figure(figsize=(6, 4.5), dpi=100)
        self.opp_ax = self.opp_fig.add_subplot(111)
        self.opp_canvas = FigureCanvasTkAgg(self.opp_fig, master=right)
        self.opp_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_help(self):
        frame = ttk.Frame(self.help_tab, style="Card.TFrame", padding=24)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        text = (
            f"{APP_TITLE}\\n\\n"
            f"Project Owner: {PLAYER_NAME}\\n"
            "Domain: Sports & Fitness\\n\\n"
            "Purpose\\n"
            "This application maintains badminton match records and provides performance analysis "
            "for a player or club. It supports match entry, search/filtering, updating and deletion, "
            "automatic win/loss statistics, opponent analysis, CSV export and visual reports.\\n\\n"
            "Technical requirements covered\\n"
            "• Python functions and data structures\\n"
            "• Persistent file handling using JSON\\n"
            "• Pandas DataFrame for structured match analysis and CSV export\\n"
            "• NumPy arrays for numerical statistics\\n"
            "• Tkinter GUI with multiple tabs\\n"
            "• Matplotlib visualizations: win/loss and scoring/opponent charts\\n"
            "• Input validation and exception handling\\n"
            "• Modular design: storage.py, validation.py, analytics.py and main.py\\n\\n"
            "How to use\\n"
            "1. Open Match Records.\\n"
            "2. Enter date, opponent, event, result and score.\\n"
            "3. Click Add Match.\\n"
            "4. Use Search / Filter to find records.\\n"
            "5. Select a record to update or delete it.\\n"
            "6. Open Performance Analysis for charts.\\n"
            "7. Use Export CSV to save a spreadsheet-compatible report.\\n\\n"
            "Storage\\n"
            "Match data is automatically stored in matches.json in the same folder as the application."
        )
        box = tk.Text(frame, bg="white", relief="flat", wrap="word",
                      font=("Segoe UI", 11), padx=15, pady=15)
        box.pack(fill="both", expand=True)
        box.insert("1.0", text)
        box.configure(state="disabled")

    def refresh_all(self):
        self.matches = load_matches()
        self.populate_tree()
        self.update_dashboard()
        self.update_charts()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        df = matches_dataframe(self.matches)
        if query and not df.empty:
            mask = df.astype(str).apply(
                lambda col: col.str.lower().str.contains(query, na=False)
            ).any(axis=1)
            df = df[mask]

        for _, row in df.iterrows():
            margin = int(row["points_for"]) - int(row["points_against"])
            score = f'{int(row["points_for"])} - {int(row["points_against"])}'
            tag = "win" if row["result"] == "Win" else "loss"
            self.tree.insert("", "end", iid=str(row["id"]),
                             values=(row["date"], row["opponent"], row["event"],
                                     row["result"], score, margin, row["notes"]),
                             tags=(tag,))

    def get_form_data(self):
        data = {key: var.get() for key, var in self.form_vars.items()}
        data["id"] = self.selected_id or str(uuid.uuid4())
        return data

    def add_match(self):
        try:
            data = normalize_match(self.get_form_data())
            ok, error = validate_match(data)
            if not ok:
                messagebox.showerror("Validation Error", error)
                return
            self.matches.append(data)
            save_matches(self.matches)
            self.clear_form()
            self.refresh_all()
            messagebox.showinfo("Saved", "Match record added successfully.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Error", f"Could not save match:\\n{exc}")

    def update_selected(self):
        if not self.selected_id:
            messagebox.showwarning("Select Match", "Select a match record first.")
            return
        try:
            data = normalize_match(self.get_form_data())
            ok, error = validate_match(data)
            if not ok:
                messagebox.showerror("Validation Error", error)
                return
            self.matches = update_match(self.selected_id, data)
            self.clear_form()
            self.refresh_all()
            messagebox.showinfo("Updated", "Match record updated successfully.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Error", f"Could not update match:\\n{exc}")

    def delete_selected(self):
        if not self.selected_id:
            messagebox.showwarning("Select Match", "Select a match record first.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete the selected match record?"):
            return
        try:
            self.matches = delete_match(self.selected_id)
            self.clear_form()
            self.refresh_all()
        except OSError as exc:
            messagebox.showerror("Error", f"Could not delete match:\\n{exc}")

    def on_tree_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        match_id = selected[0]
        match = next((m for m in self.matches if str(m.get("id")) == str(match_id)), None)
        if not match:
            return
        self.selected_id = match_id
        for key in self.form_vars:
            self.form_vars[key].set(str(match.get(key, "")))

    def clear_form(self):
        self.selected_id = None
        defaults = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "opponent": "",
            "event": "",
            "result": "Win",
            "points_for": "",
            "points_against": "",
            "notes": "",
        }
        for key, value in defaults.items():
            self.form_vars[key].set(value)
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def update_dashboard(self):
        stats = calculate_statistics(self.matches)
        self.var_total.set(str(stats["total"]))
        self.var_wins.set(str(stats["wins"]))
        self.var_losses.set(str(stats["losses"]))
        self.var_rate.set(f'{stats["win_rate"]}%')

        self.snapshot_text.configure(state="normal")
        self.snapshot_text.delete("1.0", "end")
        snapshot = (
            f"Player: {PLAYER_NAME}\\n\\n"
            f"Total matches: {stats['total']}\\n"
            f"Wins: {stats['wins']}\\n"
            f"Losses: {stats['losses']}\\n"
            f"Win rate: {stats['win_rate']}%\\n\\n"
            f"Points scored: {stats['points_for']}\\n"
            f"Points conceded: {stats['points_against']}\\n"
            f"Average points scored: {stats['avg_for']}\\n"
            f"Average points conceded: {stats['avg_against']}\\n"
            f"Best score margin: +{stats['best_margin']}\\n"
            f"Worst score margin: {stats['worst_margin']}\\n\\n"
            f"Recent form: {recent_form(self.matches)}"
        )
        self.snapshot_text.insert("1.0", snapshot)
        self.snapshot_text.configure(state="disabled")

    def update_charts(self):
        # Dashboard win/loss chart
        self.dashboard_ax.clear()
        stats = calculate_statistics(self.matches)
        labels = ["Wins", "Losses"]
        values = [stats["wins"], stats["losses"]]
        bars = self.dashboard_ax.bar(labels, values)
        self.dashboard_ax.set_title("Match Results")
        self.dashboard_ax.set_ylabel("Number of Matches")
        self.dashboard_ax.grid(axis="y", alpha=0.25)
        for bar, value in zip(bars, values):
            self.dashboard_ax.text(bar.get_x() + bar.get_width()/2,
                                    value + 0.05, str(value),
                                    ha="center", va="bottom", fontweight="bold")
        self.dashboard_fig.tight_layout()
        self.dashboard_canvas.draw()

        # Scoring trend chart
        self.trend_ax.clear()
        df = matches_dataframe(self.matches).sort_values("date")
        if not df.empty:
            x = range(1, len(df) + 1)
            self.trend_ax.plot(x, df["points_for"], marker="o", label="Points For")
            self.trend_ax.plot(x, df["points_against"], marker="o", label="Points Against")
            self.trend_ax.set_xticks(list(x))
            self.trend_ax.set_xlabel("Match Sequence (Oldest → Newest)")
            self.trend_ax.set_ylabel("Points")
            self.trend_ax.legend()
            self.trend_ax.grid(alpha=0.25)
        else:
            self.trend_ax.text(0.5, 0.5, "Add match records to view scoring trends.",
                               ha="center", va="center", transform=self.trend_ax.transAxes)
        self.trend_ax.set_title("Scoring Performance by Match")
        self.trend_fig.tight_layout()
        self.trend_canvas.draw()

        # Opponent win-rate chart
        self.opp_ax.clear()
        opp = opponent_summary(self.matches)
        if not opp.empty:
            plot_df = opp.head(8).sort_values("win_rate")
            self.opp_ax.barh(plot_df["opponent"], plot_df["win_rate"])
            self.opp_ax.set_xlim(0, 100)
            self.opp_ax.set_xlabel("Win Rate (%)")
            self.opp_ax.set_title("Best Opponent Win Rates")
            self.opp_ax.grid(axis="x", alpha=0.25)
        else:
            self.opp_ax.text(0.5, 0.5, "Add match records to view opponent analysis.",
                             ha="center", va="center", transform=self.opp_ax.transAxes)
        self.opp_fig.tight_layout()
        self.opp_canvas.draw()

    def export_csv(self):
        df = export_dataframe(self.matches)
        if df.empty:
            messagebox.showwarning("No Data", "There are no match records to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Match Report",
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            df.to_csv(path, index=False)
            messagebox.showinfo("Export Complete", f"Report saved to:\\n{path}")
        except OSError as exc:
            messagebox.showerror("Export Error", f"Could not export report:\\n{exc}")


def main():
    app = BadmintonApp()
    app.clear_form()
    app.mainloop()


if __name__ == "__main__":
    main()
