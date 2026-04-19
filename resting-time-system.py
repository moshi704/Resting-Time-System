#!/usr/bin/env python3
"""
Resting Time System - Enhanced Professional Edition
A comprehensive break enforcement system with advanced analytics and health tracking.
Classical Design by Professional Standards - Version 2.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
import platform
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import math


class RestingTimeSystem:
    """Main application class for the Enhanced Resting Time System"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Resting Time System - Professional Edition")
        self.root.geometry("1200x800")
        
        # Classical color scheme - inspired by traditional design
        self.colors = {
            'bg_primary': '#f5f5f0',      # Warm ivory
            'bg_secondary': '#ffffff',     # Pure white
            'bg_card': '#fafaf8',         # Subtle cream
            'accent_primary': '#2c5f2d',   # Classic forest green
            'accent_secondary': '#8b4513', # Saddle brown
            'text_primary': '#2b2b2b',    # Rich charcoal
            'text_secondary': '#5a5a5a',  # Medium gray
            'text_muted': '#888888',      # Light gray
            'success': '#2e7d32',         # Forest green
            'warning': '#d84315',         # Burnt sienna
            'danger': '#c62828',          # Deep red
            'border': '#d4d4ca',          # Soft taupe
            'shadow': '#00000015'         # Subtle shadow
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Application state
        self.config_file = Path.home() / ".resting_time_config.json"
        self.sessions_file = Path.home() / ".resting_time_sessions.json"
        self.trash_file = Path.home() / ".resting_time_trash.json"
        self.load_configuration()
        
        # Enhanced session state
        self.session_active = False
        self.session_paused = False
        self.in_break = False
        self.timer_thread = None
        self.break_window = None
        self.remaining_work_time = 0
        self.remaining_break_time = 0
        self.total_session_time = 0
        self.pause_start_time = None
        self.total_pause_time = 0
        
        # Analytics tracking
        self.current_session_data = {}
        
        # Setup UI
        self.setup_classical_styles()
        self.create_main_interface()
        self.load_session_history()
        
        # Window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_configuration(self):
        """Load user configuration from file"""
        default_config = {
            "strict_mode": False,
            "default_total_minutes": 120,
            "default_work_minutes": 25,
            "default_break_minutes": 5,
            "sound_notifications": True,
            "auto_start_work": True,
            "show_motivational_quotes": True,
            "compliance_target": 85.0
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            
    def save_configuration(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def load_session_history(self):
        """Load session history from file"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
            except Exception as e:
                print(f"Error loading sessions: {e}")
                self.sessions = []
        else:
            self.sessions = []
            
        self.update_session_list()
        self.update_analytics()
        
    def save_session(self, session_data):
        """Save a session to history"""
        self.sessions.insert(0, session_data)
        self.sessions = self.sessions[:100]  # Keep last 100 sessions
        
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")
            
    def calculate_compliance_rate(self):
        """Calculate overall compliance rate from session history"""
        if not self.sessions:
            return 0.0
            
        total_sessions = len(self.sessions)
        completed_sessions = sum(1 for s in self.sessions if s.get('completed', False))
        
        # Factor in break compliance
        total_breaks_taken = sum(s.get('breaks_taken', 0) for s in self.sessions)
        total_breaks_scheduled = sum(s.get('breaks_scheduled', 0) for s in self.sessions)
        
        if total_breaks_scheduled > 0:
            break_compliance = (total_breaks_taken / total_breaks_scheduled) * 100
        else:
            break_compliance = 0
            
        session_completion_rate = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        
        # Weighted average: 60% session completion, 40% break compliance
        overall_compliance = (session_completion_rate * 0.6) + (break_compliance * 0.4)
        
        return min(100.0, max(0.0, overall_compliance))
        
    def get_health_advice(self):
        """Generate personalized health advice based on user's compliance and patterns"""
        compliance = self.calculate_compliance_rate()
        
        if compliance >= 90:
            advice_category = "Excellent"
            advice = (
                "Outstanding commitment to your health! Your consistency is remarkable.\n\n"
                "Continue this excellent routine, and consider these enhancements:\n"
                "• Incorporate brief stretching exercises during breaks\n"
                "• Practice the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds\n"
                "• Stay hydrated - keep water nearby during work sessions"
            )
        elif compliance >= 75:
            advice_category = "Very Good"
            advice = (
                "Great work maintaining your health routine! You're doing well.\n\n"
                "To reach the next level:\n"
                "• Try to complete all scheduled breaks\n"
                "• Ensure you're fully stepping away from your screen during breaks\n"
                "• Consider enabling Strict Mode to prevent skipping breaks"
            )
        elif compliance >= 60:
            advice_category = "Good Start"
            advice = (
                "You're building a solid foundation. Keep it up!\n\n"
                "Recommendations to improve:\n"
                "• Set realistic work intervals that match your workflow\n"
                "• Use breaks for eye exercises and light movement\n"
                "• Track your most productive times and schedule sessions accordingly"
            )
        elif compliance >= 40:
            advice_category = "Needs Improvement"
            advice = (
                "Your health deserves more attention. Let's work on consistency.\n\n"
                "Important steps:\n"
                "• Start with shorter work intervals (15-20 minutes)\n"
                "• Enable notifications to remind you of breaks\n"
                "• Remember: breaks are not interruptions, they're investments in your health\n"
                "• Consider the long-term health consequences of prolonged screen time"
            )
        else:
            advice_category = "Urgent Attention Needed"
            advice = (
                "Your current pattern is concerning for your health.\n\n"
                "Please prioritize:\n"
                "• Set achievable goals - even 2-3 completed sessions per day helps\n"
                "• Enable Strict Mode to enforce necessary breaks\n"
                "• Consult with a healthcare professional about ergonomics\n"
                "• Remember: eye strain and posture problems are cumulative and serious"
            )
            
        return advice_category, advice
        
    def setup_classical_styles(self):
        """Configure classical design styles inspired by timeless design principles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure classical frame styles
        style.configure("TFrame", background=self.colors['bg_primary'])
        style.configure("Card.TFrame", 
                       background=self.colors['bg_card'],
                       relief="flat",
                       borderwidth=1)
        
        # Classical label styles with serif-inspired fonts
        style.configure("TLabel",
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=("Georgia", 10))
        
        style.configure("Title.TLabel",
                       background=self.colors['bg_primary'],
                       foreground=self.colors['accent_primary'],
                       font=("Georgia", 28, "bold"))
        
        style.configure("Subtitle.TLabel",
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_secondary'],
                       font=("Georgia", 12, "italic"))
        
        style.configure("CardTitle.TLabel",
                       background=self.colors['bg_card'],
                       foreground=self.colors['accent_secondary'],
                       font=("Georgia", 16, "bold"))
        
        style.configure("Timer.TLabel",
                       background=self.colors['bg_card'],
                       foreground=self.colors['accent_primary'],
                       font=("Georgia", 56, "bold"))
        
        style.configure("Status.TLabel",
                       background=self.colors['bg_card'],
                       foreground=self.colors['success'],
                       font=("Georgia", 14, "bold"))
        
        style.configure("Compliance.TLabel",
                       background=self.colors['bg_card'],
                       foreground=self.colors['accent_primary'],
                       font=("Georgia", 24, "bold"))
        
        # Classical button styles
        style.configure("Primary.TButton",
                       background=self.colors['accent_primary'],
                       foreground='white',
                       font=("Georgia", 11, "bold"),
                       borderwidth=0,
                       focuscolor="none",
                       padding=(24, 14))
        
        style.map("Primary.TButton",
                 background=[("active", self.colors['success']), ("disabled", self.colors['text_muted'])])
        
        style.configure("Secondary.TButton",
                       background=self.colors['accent_secondary'],
                       foreground='white',
                       font=("Georgia", 10),
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 12))
        
        style.map("Secondary.TButton",
                 background=[("active", "#6d3710")])
        
        style.configure("Danger.TButton",
                       background=self.colors['danger'],
                       foreground='white',
                       font=("Georgia", 11, "bold"),
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 12))
        
        style.map("Danger.TButton",
                 background=[("active", "#a31e1e")])
        
        style.configure("Accent.TButton",
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['accent_primary'],
                       font=("Georgia", 10),
                       borderwidth=1,
                       relief="solid",
                       focuscolor="none",
                       padding=(16, 10))
        
        # Entry styles
        style.configure("TEntry",
                       fieldbackground=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=2,
                       relief="solid",
                       insertcolor=self.colors['accent_primary'])
        
        # Progressbar classical style
        style.configure("Classical.Horizontal.TProgressbar",
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['border'],
                       borderwidth=1,
                       thickness=24)
        
    def create_main_interface(self):
        """Creating the main user interface with classical design"""
        # Main container with elegant padding
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Elegant header with classical typography
        header_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Title with classical serif font
        title_label = ttk.Label(header_frame,
                               text="Resting Time System",
                               style="Title.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Subtitle with italic emphasis
        subtitle_label = ttk.Label(header_frame,
                                   text="Professional Health Management",
                                   style="Subtitle.TLabel")
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0), pady=(12, 0))
        
        # Navigation buttons with classical spacing
        nav_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        nav_frame.pack(side=tk.RIGHT)
        
        analytics_btn = ttk.Button(nav_frame,
                                   text="📊 Analytics",
                                   style="Accent.TButton",
                                   command=self.open_analytics)
        analytics_btn.pack(side=tk.LEFT, padx=5)
        
        settings_btn = ttk.Button(nav_frame,
                                  text="⚙ Settings",
                                  style="Accent.TButton",
                                  command=self.open_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Content area with classical grid
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Main content (wider for classical proportions)
        left_column = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Right column - Session history with elegant width
        right_column = tk.Frame(content_frame, bg=self.colors['bg_primary'], width=400)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_column.pack_propagate(False)
        
        # Setup card with classical borders
        self.setup_card = self.create_setup_card(left_column)
        self.setup_card.pack(fill=tk.X, pady=(0, 20))
        
        # Timer card (hidden initially)
        self.timer_card = self.create_timer_card(left_column)
        
        # Session history card with compliance tracking
        self.create_history_card(right_column)
        
    def create_classical_card(self, parent, title=None):
        card_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        
        # Card with subtle shadow effect
        card = tk.Frame(card_container,
                       bg=self.colors['bg_card'],
                       highlightbackground=self.colors['border'],
                       highlightthickness=2,
                       relief="flat")
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        inner_frame = tk.Frame(card, bg=self.colors['bg_card'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        if title:
            title_label = ttk.Label(inner_frame,
                                   text=title,
                                   style="CardTitle.TLabel")
            title_label.pack(anchor=tk.W, pady=(0, 20))
            
        return card_container, inner_frame
        
    def create_setup_card(self, parent):
        card_container, inner_frame = self.create_classical_card(parent, "Commence New Session")
        
        # Input grid with classical spacing
        input_frame = tk.Frame(inner_frame, bg=self.colors['bg_card'])
        input_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Configure grid weights for elegant proportions
        for i in range(3):
            input_frame.columnconfigure(i, weight=1, uniform="inputs")
        
        # Total duration
        self.create_input_field(input_frame, "Total Duration (minutes)", 
                               self.config['default_total_minutes'], 0)
        
        # Work interval
        self.create_input_field(input_frame, "Work Interval (minutes)",
                               self.config['default_work_minutes'], 1)
        
        # Break duration
        self.create_input_field(input_frame, "Break Duration (minutes)",
                               self.config['default_break_minutes'], 2)
        
        # Start button with classical styling
        start_btn = ttk.Button(inner_frame,
                              text="Begin Session",
                              style="Primary.TButton",
                              command=self.start_session)
        start_btn.pack(fill=tk.X, pady=(10, 0))
        
        return card_container
        
    def create_input_field(self, parent, label_text, default_value, column):
        """Create a classical input field with elegant styling"""
        container = tk.Frame(parent, bg=self.colors['bg_card'])
        container.grid(row=0, column=column, padx=10, sticky="ew")
        
        label = tk.Label(container,
                        text=label_text,
                        bg=self.colors['bg_card'],
                        fg=self.colors['text_secondary'],
                        font=("Georgia", 9))
        label.pack(anchor=tk.W, pady=(0, 8))
        
        entry = ttk.Entry(container, width=15, font=("Georgia", 12))
        entry.insert(0, str(default_value))
        entry.pack(fill=tk.X)
        
        # Store reference based on column
        if column == 0:
            self.total_entry = entry
        elif column == 1:
            self.work_entry = entry
        elif column == 2:
            self.break_entry = entry
            
    def create_timer_card(self, parent):
        """Create the active timer card with pause functionality"""
        card_container, inner_frame = self.create_classical_card(parent)
        
        # Header with status and controls
        header_frame = tk.Frame(inner_frame, bg=self.colors['bg_card'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        self.status_label = ttk.Label(header_frame,
                                     text="SESSION IN PROGRESS",
                                     style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = tk.Frame(header_frame, bg=self.colors['bg_card'])
        controls_frame.pack(side=tk.RIGHT)
        
        self.pause_btn = ttk.Button(controls_frame,
                                    text="⏸ Pause",
                                    style="Secondary.TButton",
                                    command=self.toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(controls_frame,
                                   text="■ Stop",
                                   style="Danger.TButton",
                                   command=self.stop_session)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Timer display with classical typography
        timer_container = tk.Frame(inner_frame, bg=self.colors['bg_card'])
        timer_container.pack(fill=tk.BOTH, expand=True)
        
        self.timer_display = ttk.Label(timer_container,
                                      text="25:00",
                                      style="Timer.TLabel")
        self.timer_display.pack(pady=(20, 15))
        
        self.phase_label = tk.Label(timer_container,
                                   text="Work Phase",
                                   bg=self.colors['bg_card'],
                                   fg=self.colors['text_secondary'],
                                   font=("Georgia", 12, "italic"))
        self.phase_label.pack(pady=(0, 20))
        
        self.global_status = tk.Label(timer_container,
                                     text="Total Session Remaining: 120:00",
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text_secondary'],
                                     font=("Georgia", 11))
        self.global_status.pack()
        
        # Pause indicator
        self.pause_indicator = tk.Label(timer_container,
                                       text="⏸ PAUSED",
                                       bg=self.colors['bg_card'],
                                       fg=self.colors['warning'],
                                       font=("Georgia", 16, "bold"))
        
        return card_container
        
    def create_history_card(self, parent):
        """Create the session history card with compliance tracking"""
        card_container, inner_frame = self.create_classical_card(parent, "Session History")
        
        # Compliance rate display
        compliance_frame = tk.Frame(inner_frame, 
                                   bg="#f0f4f0",
                                   highlightbackground=self.colors['border'],
                                   highlightthickness=1)
        compliance_frame.pack(fill=tk.X, pady=(0, 20))
        
        compliance_inner = tk.Frame(compliance_frame, bg=self.colors['bg_secondary'])
        compliance_inner.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(compliance_inner,
                text="Compliance Rate",
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_secondary'],
                font=("Georgia", 10)).pack()
        
        self.compliance_label = ttk.Label(compliance_inner,
                                         text="0.0%",
                                         style="Compliance.TLabel")
        self.compliance_label.pack(pady=(5, 10))
        
        # Progress bar
        self.compliance_progress = ttk.Progressbar(compliance_inner,
                                                  style="Classical.Horizontal.TProgressbar",
                                                  length=300,
                                                  mode='determinate')
        self.compliance_progress.pack(fill=tk.X)
        
        # Health status
        self.health_status_label = tk.Label(compliance_inner,
                                           text="Building healthy habits...",
                                           bg=self.colors['bg_secondary'],
                                           fg=self.colors['text_secondary'],
                                           font=("Georgia", 9, "italic"))
        self.health_status_label.pack(pady=(8, 0))
        
        # History management buttons
        history_controls = tk.Frame(inner_frame, bg=self.colors['bg_card'])
        history_controls.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(history_controls,
                  text="🗑 Clear History",
                  style="Accent.TButton",
                  command=self.manage_history).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(history_controls,
                  text="💡 Health Advice",
                  style="Accent.TButton",
                  command=self.show_health_advice).pack(side=tk.LEFT, padx=2)
        
        # Scrollable session list
        list_container = tk.Frame(inner_frame, bg=self.colors['bg_card'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(list_container,
                          bg=self.colors['bg_card'],
                          highlightthickness=0,
                          height=350)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        
        self.sessions_frame = tk.Frame(canvas, bg=self.colors['bg_card'])
        self.sessions_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.sessions_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return card_container
        
    def update_session_list(self):
        """Update session history display with completion status"""
        for widget in self.sessions_frame.winfo_children():
            widget.destroy()
            
        if not self.sessions:
            no_sessions = tk.Label(self.sessions_frame,
                                  text="No sessions recorded yet.\nBegin your health journey today!",
                                  bg=self.colors['bg_card'],
                                  fg=self.colors['text_muted'],
                                  font=("Georgia", 10, "italic"),
                                  justify=tk.CENTER)
            no_sessions.pack(pady=40)
            return
            
        for idx, session in enumerate(self.sessions[:15]):
            session_frame = tk.Frame(self.sessions_frame,
                                    bg=self.colors['bg_secondary'],
                                    highlightbackground=self.colors['border'],
                                    highlightthickness=1)
            session_frame.pack(fill=tk.X, pady=(0, 8), padx=2)
            
            inner = tk.Frame(session_frame, bg=self.colors['bg_secondary'])
            inner.pack(fill=tk.X, padx=15, pady=12)
            
            # Date and status
            header_frame = tk.Frame(inner, bg=self.colors['bg_secondary'])
            header_frame.pack(fill=tk.X)
            
            date_label = tk.Label(header_frame,
                                 text=session.get('date', 'Unknown'),
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_primary'],
                                 font=("Georgia", 10, "bold"))
            date_label.pack(side=tk.LEFT)
            
            # Status badge
            completed = session.get('completed', False)
            status_color = self.colors['success'] if completed else self.colors['warning']
            status_text = "✓ Complete" if completed else "⚠ Incomplete"
            
            status_label = tk.Label(header_frame,
                                   text=status_text,
                                   bg=self.colors['bg_secondary'],
                                   fg=status_color,
                                   font=("Georgia", 9, "bold"))
            status_label.pack(side=tk.RIGHT)
            
            # Session details
            duration = session.get('total_minutes', 0)
            cycles = session.get('cycles_completed', 0)
            breaks_taken = session.get('breaks_taken', 0)
            breaks_scheduled = session.get('breaks_scheduled', 0)
            
            details = f"{duration} min session • {cycles} cycles • {breaks_taken}/{breaks_scheduled} breaks"
            
            details_label = tk.Label(inner,
                                    text=details,
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_secondary'],
                                    font=("Georgia", 9))
            details_label.pack(anchor=tk.W, pady=(5, 0))
            
    def manage_history(self):
        """Manage session history - clear options"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage History")
        dialog.geometry("500x300")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        container = tk.Frame(dialog, bg=self.colors['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(container,
                        text="History Management",
                        bg=self.colors['bg_primary'],
                        fg=self.colors['accent_primary'],
                        font=("Georgia", 18, "bold"))
        title.pack(pady=(0, 20))
        
        info = tk.Label(container,
                       text=f"You have {len(self.sessions)} recorded sessions.\n"
                            "Choose how to manage your history:",
                       bg=self.colors['bg_primary'],
                       fg=self.colors['text_primary'],
                       font=("Georgia", 10),
                       justify=tk.CENTER)
        info.pack(pady=(0, 30))
        
        def move_to_trash():
            if messagebox.askyesno("Move to Recycle Bin",
                                  "Move all session history to recycle bin?\n"
                                  "You can restore it later if needed."):
                try:
                    # Save to trash file
                    trash_data = {
                        'deleted_date': datetime.now().isoformat(),
                        'sessions': self.sessions
                    }
                    with open(self.trash_file, 'w') as f:
                        json.dump(trash_data, f, indent=2)
                    
                    self.sessions = []
                    self.save_session({})  # Clear main file
                    self.sessions = []
                    self.update_session_list()
                    self.update_analytics()
                    messagebox.showinfo("Success", "History moved to recycle bin.")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not move to trash: {e}")
        
        def delete_permanently():
            if messagebox.askyesno("Permanent Deletion",
                                  "Permanently delete ALL session history?\n"
                                  "This action CANNOT be undone!",
                                  icon='warning'):
                if messagebox.askyesno("Final Confirmation",
                                      "Are you absolutely sure?\n"
                                      "This will erase all your progress data permanently.",
                                      icon='warning'):
                    self.sessions = []
                    try:
                        if self.sessions_file.exists():
                            os.remove(self.sessions_file)
                        messagebox.showinfo("Deleted", "All history permanently deleted.")
                        self.update_session_list()
                        self.update_analytics()
                        dialog.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not delete: {e}")
        
        def restore_from_trash():
            if self.trash_file.exists():
                try:
                    with open(self.trash_file, 'r') as f:
                        trash_data = json.load(f)
                    
                    if messagebox.askyesno("Restore History",
                                          f"Restore {len(trash_data.get('sessions', []))} sessions from recycle bin?"):
                        self.sessions = trash_data.get('sessions', [])
                        self.save_session({})
                        self.sessions = trash_data.get('sessions', [])
                        os.remove(self.trash_file)
                        self.update_session_list()
                        self.update_analytics()
                        messagebox.showinfo("Restored", "History restored successfully!")
                        dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not restore: {e}")
            else:
                messagebox.showinfo("Empty", "Recycle bin is empty.")
        
        # Buttons
        ttk.Button(container,
                  text="🗑 Move to Recycle Bin",
                  style="Secondary.TButton",
                  command=move_to_trash).pack(fill=tk.X, pady=5)
        
        ttk.Button(container,
                  text="♻ Restore from Recycle Bin",
                  style="Accent.TButton",
                  command=restore_from_trash).pack(fill=tk.X, pady=5)
        
        ttk.Button(container,
                  text="⚠ Delete Permanently",
                  style="Danger.TButton",
                  command=delete_permanently).pack(fill=tk.X, pady=5)
        
        ttk.Button(container,
                  text="Cancel",
                  style="Accent.TButton",
                  command=dialog.destroy).pack(fill=tk.X, pady=(20, 0))
        
    def show_health_advice(self):
        """Display personalized health advice"""
        category, advice = self.get_health_advice()
        compliance = self.calculate_compliance_rate()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Health Advice")
        dialog.geometry("600x500")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        
        container = tk.Frame(dialog, bg=self.colors['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Title
        title = tk.Label(container,
                        text="📋 Personalized Health Advice",
                        bg=self.colors['bg_primary'],
                        fg=self.colors['accent_primary'],
                        font=("Georgia", 20, "bold"))
        title.pack(pady=(0, 20))
        
        # Compliance display
        compliance_frame = tk.Frame(container,
                                   bg=self.colors['bg_secondary'],
                                   highlightbackground=self.colors['border'],
                                   highlightthickness=2)
        compliance_frame.pack(fill=tk.X, pady=(0, 20))
        
        comp_inner = tk.Frame(compliance_frame, bg=self.colors['bg_secondary'])
        comp_inner.pack(padx=20, pady=15)
        
        tk.Label(comp_inner,
                text=f"Current Status: {category}",
                bg=self.colors['bg_secondary'],
                fg=self.colors['accent_secondary'],
                font=("Georgia", 14, "bold")).pack()
        
        tk.Label(comp_inner,
                text=f"Compliance Rate: {compliance:.1f}%",
                bg=self.colors['bg_secondary'],
                fg=self.colors['accent_primary'],
                font=("Georgia", 16, "bold")).pack(pady=5)
        
        # Advice text
        advice_frame = tk.Frame(container, bg=self.colors['bg_card'],
                               highlightbackground=self.colors['border'],
                               highlightthickness=1)
        advice_frame.pack(fill=tk.BOTH, expand=True)
        
        advice_text = tk.Text(advice_frame,
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_primary'],
                             font=("Georgia", 11),
                             wrap=tk.WORD,
                             relief="flat",
                             padx=20,
                             pady=20)
        advice_text.pack(fill=tk.BOTH, expand=True)
        advice_text.insert("1.0", advice)
        advice_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(container,
                  text="Close",
                  style="Primary.TButton",
                  command=dialog.destroy).pack(fill=tk.X, pady=(20, 0))
        
    def update_analytics(self):
        """Update analytics display"""
        compliance = self.calculate_compliance_rate()
        self.compliance_label.config(text=f"{compliance:.1f}%")
        self.compliance_progress['value'] = compliance
        
        # Update health status
        if compliance >= 90:
            status = "Excellent health habits! 🌟"
            color = self.colors['success']
        elif compliance >= 75:
            status = "Very good progress! 👍"
            color = self.colors['accent_primary']
        elif compliance >= 60:
            status = "Good start, keep going! 💪"
            color = self.colors['accent_secondary']
        elif compliance >= 40:
            status = "Needs improvement 📈"
            color = self.colors['warning']
        else:
            status = "Please prioritize your health ⚠"
            color = self.colors['danger']
            
        self.health_status_label.config(text=status, fg=color)
        
    def open_analytics(self):
        """Open analytics window with health predictions"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Health Analytics")
        dialog.geometry("900x700")
        dialog.configure(bg=self.colors['bg_primary'])
        
        container = tk.Frame(dialog, bg=self.colors['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Title
        title = tk.Label(container,
                        text="📊 Health Analytics & Predictions",
                        bg=self.colors['bg_primary'],
                        fg=self.colors['accent_primary'],
                        font=("Georgia", 22, "bold"))
        title.pack(pady=(0, 30))
        
        # Stats grid
        stats_frame = tk.Frame(container, bg=self.colors['bg_primary'])
        stats_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Calculate stats
        total_sessions = len(self.sessions)
        completed = sum(1 for s in self.sessions if s.get('completed', False))
        total_minutes = sum(s.get('total_minutes', 0) for s in self.sessions if s.get('completed', False))
        total_breaks = sum(s.get('breaks_taken', 0) for s in self.sessions)
        
        stats = [
            ("Total Sessions", total_sessions, "📅"),
            ("Completed", completed, "✓"),
            ("Total Hours", f"{total_minutes/60:.1f}", "⏱"),
            ("Breaks Taken", total_breaks, "☕")
        ]
        
        for idx, (label, value, icon) in enumerate(stats):
            stat_card = tk.Frame(stats_frame,
                                bg=self.colors['bg_card'],
                                highlightbackground=self.colors['border'],
                                highlightthickness=1)
            stat_card.grid(row=0, column=idx, padx=10, sticky="ew")
            stats_frame.columnconfigure(idx, weight=1)
            
            inner = tk.Frame(stat_card, bg=self.colors['bg_card'])
            inner.pack(padx=20, pady=20)
            
            tk.Label(inner,
                    text=icon,
                    bg=self.colors['bg_card'],
                    font=("Arial", 24)).pack()
            
            tk.Label(inner,
                    text=str(value),
                    bg=self.colors['bg_card'],
                    fg=self.colors['accent_primary'],
                    font=("Georgia", 20, "bold")).pack()
            
            tk.Label(inner,
                    text=label,
                    bg=self.colors['bg_card'],
                    fg=self.colors['text_secondary'],
                    font=("Georgia", 9)).pack()
        
        # Health prediction graph
        graph_frame = tk.Frame(container,
                              bg=self.colors['bg_card'],
                              highlightbackground=self.colors['border'],
                              highlightthickness=2)
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_health_graph(graph_frame)
        
        # Recommendations
        rec_frame = tk.Frame(container,
                            bg=self.colors['bg_secondary'],
                            highlightbackground=self.colors['border'],
                            highlightthickness=1)
        rec_frame.pack(fill=tk.X, pady=(20, 0))
        
        rec_inner = tk.Frame(rec_frame, bg=self.colors['bg_secondary'])
        rec_inner.pack(padx=20, pady=15)
        
        tk.Label(rec_inner,
                text="💡 Optimal Session Configuration for Your Health:",
                bg=self.colors['bg_secondary'],
                fg=self.colors['accent_secondary'],
                font=("Georgia", 12, "bold")).pack(anchor=tk.W)
        
        recommendations = (
            "• Work Interval: 25-30 minutes (optimal for focus and eye health)\n"
            "• Break Duration: 5-7 minutes (sufficient for eye rest and movement)\n"
            "• Total Session: 90-120 minutes (prevents prolonged static posture)\n"
            "• Daily Goal: 4-5 complete sessions (builds sustainable habits)"
        )
        
        tk.Label(rec_inner,
                text=recommendations,
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=("Georgia", 10),
                justify=tk.LEFT).pack(anchor=tk.W, pady=(10, 0))
        
    def create_health_graph(self, parent):
        """Create a simple health improvement graph"""
        canvas_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        tk.Label(canvas_frame,
                text="Daily Health Improvement Projection (30 Days)",
                bg=self.colors['bg_card'],
                fg=self.colors['accent_primary'],
                font=("Georgia", 14, "bold")).pack(pady=(0, 15))
        
        canvas = tk.Canvas(canvas_frame,
                          bg=self.colors['bg_secondary'],
                          highlightthickness=0,
                          height=300)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw axes
        margin = 40
        width = 750
        height = 280
        
        # Y-axis
        canvas.create_line(margin, margin, margin, height - margin,
                          fill=self.colors['text_secondary'], width=2)
        # X-axis
        canvas.create_line(margin, height - margin, width - margin, height - margin,
                          fill=self.colors['text_secondary'], width=2)
        
        # Labels
        canvas.create_text(20, margin, text="100%", anchor="e",
                          fill=self.colors['text_secondary'], font=("Georgia", 9))
        canvas.create_text(20, height - margin, text="0%", anchor="e",
                          fill=self.colors['text_secondary'], font=("Georgia", 9))
        
        # Time labels
        for i, label in enumerate(["Day 5", "Day 10", "Day 15", "Day 20", "Day 25", "Day 30"]):
            x = margin + ((i + 1) * 5 / 30) * (width - 2 * margin)
            canvas.create_text(x, height - margin + 20, text=label,
                              fill=self.colors['text_secondary'], font=("Georgia", 9))
        
        # Current compliance
        current_compliance = self.calculate_compliance_rate()
        
        # Project improvement curve
        points = []
        for day in range(31):
            x = margin + (day / 30) * (width - 2 * margin)
            
            # Realistic improvement curve
            if day == 0:
                improvement = current_compliance
            else:
                # Logarithmic improvement curve
                max_improvement = min(95, current_compliance + 30)
                improvement = current_compliance + (max_improvement - current_compliance) * (1 - math.exp(-day/12))
            
            y = height - margin - ((height - 2 * margin) * improvement / 100)
            points.extend([x, y])
        
        # Draw projection line
        canvas.create_line(points, fill=self.colors['accent_primary'],
                          width=3, smooth=True)
        
        # Draw current point
        if len(points) >= 2:
            canvas.create_oval(points[0] - 5, points[1] - 5,
                             points[0] + 5, points[1] + 5,
                             fill=self.colors['danger'], outline=self.colors['danger'])
            canvas.create_text(points[0], points[1] - 15,
                             text=f"You are here\n{current_compliance:.1f}%",
                             fill=self.colors['danger'],
                             font=("Georgia", 9, "bold"))
        
        # Legend
        legend_frame = tk.Frame(canvas_frame, bg=self.colors['bg_card'])
        legend_frame.pack(pady=(15, 0))
        
        tk.Label(legend_frame,
                text="📈 Based on consistent usage, you can expect significant health improvements in 4 weeks",
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary'],
                font=("Georgia", 9, "italic")).pack()
        
    def start_session(self):
        """Start a new work/break session"""
        try:
            total_minutes = int(self.total_entry.get())
            work_minutes = int(self.work_entry.get())
            break_minutes = int(self.break_entry.get())
            
            if total_minutes <= 0 or work_minutes <= 0 or break_minutes <= 0:
                messagebox.showerror("Invalid Input",
                                   "All values must be positive numbers.")
                return
                
            if work_minutes >= total_minutes:
                messagebox.showerror("Invalid Input",
                                   "Work interval must be less than total duration.")
                return
                
        except ValueError:
            messagebox.showerror("Invalid Input",
                               "Please enter valid numbers for all fields.")
            return
            
        # Initialize session data
        self.session_start_time = datetime.now()
        self.total_session_time = total_minutes * 60
        self.work_interval = work_minutes * 60
        self.break_interval = break_minutes * 60
        self.remaining_work_time = work_minutes * 60
        self.session_total = total_minutes
        self.session_work = work_minutes
        self.session_break = break_minutes
        self.completed_cycles = 0
        self.breaks_taken = 0
        self.breaks_scheduled = math.ceil(total_minutes / work_minutes)
        self.session_paused = False
        self.total_pause_time = 0
        
        # Track session data
        self.current_session_data = {
            'start_time': self.session_start_time.isoformat(),
            'date': self.session_start_time.strftime("%b %d, %Y - %I:%M %p"),
            'total_minutes': total_minutes,
            'work_minutes': work_minutes,
            'break_minutes': break_minutes,
            'breaks_scheduled': self.breaks_scheduled
        }
        
        # Update UI
        self.session_active = True
        self.setup_card.pack_forget()
        self.timer_card.pack(fill=tk.X)
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()
        
        messagebox.showinfo("Session Commenced",
                          f"Your {total_minutes}-minute session has begun.\n\n"
                          f"Work: {work_minutes} min | Break: {break_minutes} min\n"
                          f"Scheduled breaks: {self.breaks_scheduled}")
        
    def toggle_pause(self):
        """Pause or resume the session"""
        if not self.session_active:
            return
            
        if self.in_break and self.config.get('strict_mode', False):
            messagebox.showwarning("Cannot Pause",
                                 "Cannot pause during break in Strict Mode.")
            return
            
        self.session_paused = not self.session_paused
        
        if self.session_paused:
            self.pause_start_time = time.time()
            self.pause_btn.config(text="▶ Resume")
            self.pause_indicator.pack(pady=15)
            self.status_label.config(text="SESSION PAUSED")
        else:
            if self.pause_start_time:
                self.total_pause_time += time.time() - self.pause_start_time
            self.pause_btn.config(text="⏸ Pause")
            self.pause_indicator.pack_forget()
            self.status_label.config(text="SESSION IN PROGRESS")
            
    def run_timer(self):
        """Main timer loop with pause support"""
        while self.session_active and self.total_session_time > 0:
            if not self.session_paused:
                if not self.in_break:
                    # Work period
                    if self.remaining_work_time > 0:
                        self.remaining_work_time -= 1
                        self.total_session_time -= 1
                        self.update_timer_display()
                    else:
                        # Time for a break
                        self.start_break()
                else:
                    # Break period
                    if self.remaining_break_time > 0:
                        self.remaining_break_time -= 1
                        self.update_break_display()
                    else:
                        # Break is over
                        self.end_break()
                        
            time.sleep(1)
            
        # Session completed
        if self.session_active:
            self.root.after(0, self.complete_session)
            
    def update_timer_display(self):
        """Update the main timer display"""
        work_mins, work_secs = divmod(self.remaining_work_time, 60)
        total_mins, total_secs = divmod(self.total_session_time, 60)
        
        self.root.after(0, lambda: self.timer_display.config(
            text=f"{work_mins:02d}:{work_secs:02d}"))
        self.root.after(0, lambda: self.global_status.config(
            text=f"Total Session Remaining: {total_mins:02d}:{total_secs:02d}"))
        self.root.after(0, lambda: self.phase_label.config(
            text="Work Phase"))
            
    def start_break(self):
        """Initiate a break period"""
        self.in_break = True
        self.remaining_break_time = self.break_interval
        self.completed_cycles += 1
        self.breaks_taken += 1
        
        # Create fullscreen break overlay
        self.root.after(0, self.create_break_overlay)
        
    def create_break_overlay(self):
        """Create the fullscreen break overlay window with classical design"""
        self.break_window = tk.Toplevel(self.root)
        self.break_window.title("Break Time")
        self.break_window.configure(bg=self.colors['bg_primary'])
        
        # Make fullscreen and always on top
        self.break_window.attributes('-fullscreen', True)
        self.break_window.attributes('-topmost', True)
        
        # Disable close in strict mode
        if self.config.get('strict_mode', False):
            self.break_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
        # Center content with classical design
        content_frame = tk.Frame(self.break_window, bg=self.colors['bg_primary'])
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title with classical typography
        title = tk.Label(content_frame,
                        text="Time for Rest",
                        font=("Georgia", 72, "bold"),
                        fg=self.colors['accent_primary'],
                        bg=self.colors['bg_primary'])
        title.pack(pady=(0, 20))
        
        # Decorative line
        line_frame = tk.Frame(content_frame, bg=self.colors['accent_secondary'], height=3)
        line_frame.pack(fill=tk.X, padx=100, pady=(0, 30))
        
        # Subtitle
        subtitle = tk.Label(content_frame,
                           text="Please step away from your screen.\nRest your eyes and move your body.",
                           font=("Georgia", 18),
                           fg=self.colors['text_secondary'],
                           bg=self.colors['bg_primary'],
                           justify=tk.CENTER)
        subtitle.pack(pady=(0, 50))
        
        # Timer with elegant styling
        self.break_timer_label = tk.Label(content_frame,
                                         text="05:00",
                                         font=("Georgia", 80, "bold"),
                                         fg=self.colors['accent_secondary'],
                                         bg=self.colors['bg_primary'])
        self.break_timer_label.pack(pady=(0, 50))
        
        # Break activity suggestions
        tips = [
            "• Look at something 20 feet away",
            "• Do gentle neck and shoulder rolls",
            "• Take a short walk",
            "• Stay hydrated"
        ]
        
        tips_frame = tk.Frame(content_frame, bg=self.colors['bg_card'],
                             highlightbackground=self.colors['border'],
                             highlightthickness=1)
        tips_frame.pack(pady=(0, 40))
        
        tips_inner = tk.Frame(tips_frame, bg=self.colors['bg_card'])
        tips_inner.pack(padx=40, pady=20)
        
        for tip in tips:
            tk.Label(tips_inner,
                    text=tip,
                    bg=self.colors['bg_card'],
                    fg=self.colors['text_primary'],
                    font=("Georgia", 12),
                    justify=tk.LEFT).pack(anchor=tk.W, pady=2)
        
        # Strict mode warning or skip button
        if self.config.get('strict_mode', False):
            warning = tk.Label(content_frame,
                             text="⚠ Strict Mode Active\nYou must complete this break for your health",
                             font=("Georgia", 12, "bold"),
                             fg=self.colors['danger'],
                             bg=self.colors['bg_primary'],
                             justify=tk.CENTER)
            warning.pack()
        else:
            skip_btn = ttk.Button(content_frame,
                                text="Skip Break (Not Recommended)",
                                style="Secondary.TButton",
                                command=self.skip_break)
            skip_btn.pack()
            
    def update_break_display(self):
        """Update break timer display"""
        mins, secs = divmod(self.remaining_break_time, 60)
        if self.break_timer_label:
            self.root.after(0, lambda: self.break_timer_label.config(
                text=f"{mins:02d}:{secs:02d}"))
                
    def skip_break(self):
        """Skip the current break (only in non-strict mode)"""
        if not self.config.get('strict_mode', False):
            self.end_break()
            
    def end_break(self):
        """End the break period and notify user"""
        self.in_break = False
        self.remaining_work_time = self.work_interval
        
        # Close break window
        if self.break_window:
            self.root.after(0, self.break_window.destroy)
            self.break_window = None
            
        # Notify user that break has ended
        if platform.system() == 'Windows':
            try:
                # Windows notification
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast("Break Ended",
                                 "Your break is complete. Time to resume work!",
                                 duration=5,
                                 threaded=True)
            except:
                pass
        
        # Show system messagebox as fallback
        self.root.after(0, lambda: messagebox.showinfo(
            "Break Complete",
            "Your break has ended.\nTime to resume your session!",
            parent=self.root))
            
    def stop_session(self):
        """Stop the current session"""
        if self.config.get('strict_mode', False) and self.in_break:
            messagebox.showwarning("Strict Mode Active",
                                 "Cannot stop session during break in Strict Mode.")
            return
            
        if messagebox.askyesno("Stop Session",
                             "Are you sure you want to stop this session?\n"
                             "It will be marked as incomplete."):
            self.session_active = False
            
            # Calculate session stats
            time_elapsed = self.session_total * 60 - self.total_session_time
            minutes_elapsed = time_elapsed / 60
            
            # Save incomplete session
            session_data = self.current_session_data.copy()
            session_data.update({
                'end_time': datetime.now().isoformat(),
                'completed': False,
                'cycles_completed': self.completed_cycles,
                'breaks_taken': self.breaks_taken,
                'breaks_scheduled': self.breaks_scheduled,
                'minutes_completed': int(minutes_elapsed),
                'pause_time': int(self.total_pause_time)
            })
            self.save_session(session_data)
            
            # Clean up
            if self.break_window:
                self.break_window.destroy()
                self.break_window = None
                
            # Reset UI
            self.timer_card.pack_forget()
            self.setup_card.pack(fill=tk.X, pady=(0, 20))
            self.update_session_list()
            self.update_analytics()
            
    def complete_session(self):
        """Handle session completion"""
        self.session_active = False
        
        # Save completed session
        session_data = self.current_session_data.copy()
        session_data.update({
            'end_time': datetime.now().isoformat(),
            'completed': True,
            'cycles_completed': self.completed_cycles,
            'breaks_taken': self.breaks_taken,
            'breaks_scheduled': self.breaks_scheduled,
            'minutes_completed': self.session_total,
            'pause_time': int(self.total_pause_time)
        })
        self.save_session(session_data)
        
        # Celebratory message
        messagebox.showinfo("Session Complete! 🎉",
                          f"Congratulations on completing your {self.session_total}-minute session!\n\n"
                          f"✓ Cycles completed: {self.completed_cycles}\n"
                          f"✓ Breaks taken: {self.breaks_taken}/{self.breaks_scheduled}\n"
                          f"✓ Total pause time: {int(self.total_pause_time/60)} minutes\n\n"
                          f"Your health journey continues!")
        
        # Reset UI
        self.timer_card.pack_forget()
        self.setup_card.pack(fill=tk.X, pady=(0, 20))
        self.update_session_list()
        self.update_analytics()
        
    def open_settings(self):
        """Open enhanced settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("700x650")
        settings_window.configure(bg=self.colors['bg_primary'])
        settings_window.transient(self.root)
        
        # Main container
        container = tk.Frame(settings_window, bg=self.colors['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Title
        title = tk.Label(container,
                        text="System Preferences",
                        bg=self.colors['bg_primary'],
                        fg=self.colors['accent_primary'],
                        font=("Georgia", 24, "bold"))
        title.pack(anchor=tk.W, pady=(0, 10))
        
        subtitle = tk.Label(container,
                           text="Customize your health management experience",
                           bg=self.colors['bg_primary'],
                           fg=self.colors['text_secondary'],
                           font=("Georgia", 11, "italic"))
        subtitle.pack(anchor=tk.W, pady=(0, 30))
        
        # Scrollable content
        canvas = tk.Canvas(container, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=600)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Strict mode section
        self.create_settings_section(scrollable_frame, "Strict Break Mode",
                                     "When enabled, breaks cannot be skipped and sessions cannot be stopped during breaks.",
                                     "strict_mode")
        
        # Sound notifications
        self.create_settings_section(scrollable_frame, "Sound Notifications",
                                     "Enable sound alerts for break start and end.",
                                     "sound_notifications")
        
        # Auto-start work
        self.create_settings_section(scrollable_frame, "Auto-Resume Work",
                                     "Automatically start work period after break ends.",
                                     "auto_start_work")
        
        # Motivational quotes
        self.create_settings_section(scrollable_frame, "Motivational Messages",
                                     "Show health tips and motivational quotes during breaks.",
                                     "show_motivational_quotes")
        
        # Default preferences
        defaults_frame = tk.Frame(scrollable_frame,
                                 bg=self.colors['bg_card'],
                                 highlightbackground=self.colors['border'],
                                 highlightthickness=1)
        defaults_frame.pack(fill=tk.X, pady=(0, 20))
        
        defaults_inner = tk.Frame(defaults_frame, bg=self.colors['bg_card'])
        defaults_inner.pack(fill=tk.X, padx=25, pady=20)
        
        tk.Label(defaults_inner,
                text="Default Session Configuration",
                bg=self.colors['bg_card'],
                fg=self.colors['accent_secondary'],
                font=("Georgia", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(defaults_inner,
                text="Set your preferred default durations for new sessions.",
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary'],
                font=("Georgia", 9)).pack(anchor=tk.W, pady=(0, 15))
        
        # Input fields
        fields_frame = tk.Frame(defaults_inner, bg=self.colors['bg_card'])
        fields_frame.pack(fill=tk.X, pady=(0, 15))
        
        total_default = self.create_setting_input(fields_frame, "Default Total Minutes",
                                                  self.config['default_total_minutes'], 0)
        work_default = self.create_setting_input(fields_frame, "Default Work Minutes",
                                                 self.config['default_work_minutes'], 1)
        break_default = self.create_setting_input(fields_frame, "Default Break Minutes",
                                                  self.config['default_break_minutes'], 2)
        
        def save_defaults():
            try:
                self.config['default_total_minutes'] = int(total_default.get())
                self.config['default_work_minutes'] = int(work_default.get())
                self.config['default_break_minutes'] = int(break_default.get())
                self.save_configuration()
                
                # Update main UI
                self.total_entry.delete(0, tk.END)
                self.total_entry.insert(0, str(self.config['default_total_minutes']))
                self.work_entry.delete(0, tk.END)
                self.work_entry.insert(0, str(self.config['default_work_minutes']))
                self.break_entry.delete(0, tk.END)
                self.break_entry.insert(0, str(self.config['default_break_minutes']))
                
                messagebox.showinfo("Settings Saved", "Your preferences have been updated.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.")
        
        ttk.Button(defaults_inner,
                  text="Save Configuration",
                  style="Primary.TButton",
                  command=save_defaults).pack(fill=tk.X)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_settings_section(self, parent, title, description, config_key):
        """Create a settings section with toggle"""
        section_frame = tk.Frame(parent,
                                bg=self.colors['bg_card'],
                                highlightbackground=self.colors['border'],
                                highlightthickness=1)
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        inner = tk.Frame(section_frame, bg=self.colors['bg_card'])
        inner.pack(fill=tk.X, padx=25, pady=20)
        
        # Title
        tk.Label(inner,
                text=title,
                bg=self.colors['bg_card'],
                fg=self.colors['accent_primary'],
                font=("Georgia", 13, "bold")).pack(anchor=tk.W)
        
        # Description
        tk.Label(inner,
                text=description,
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary'],
                font=("Georgia", 9),
                wraplength=520,
                justify=tk.LEFT).pack(anchor=tk.W, pady=(5, 15))
        
        # Toggle button
        current_state = self.config.get(config_key, False)
        status_text = "Enabled" if current_state else "Disabled"
        status_color = self.colors['success'] if current_state else self.colors['text_muted']
        
        status_label = tk.Label(inner,
                               text=f"Status: {status_text}",
                               bg=self.colors['bg_card'],
                               fg=status_color,
                               font=("Georgia", 10, "bold"))
        status_label.pack(anchor=tk.W, pady=(0, 10))
        
        def toggle():
            self.config[config_key] = not self.config[config_key]
            self.save_configuration()
            new_state = self.config[config_key]
            status_label.config(
                text=f"Status: {'Enabled' if new_state else 'Disabled'}",
                fg=self.colors['success'] if new_state else self.colors['text_muted']
            )
            toggle_btn.config(
                text=f"Disable {title}" if new_state else f"Enable {title}"
            )
        
        toggle_btn = ttk.Button(inner,
                               text=f"Disable {title}" if current_state else f"Enable {title}",
                               style="Secondary.TButton",
                               command=toggle)
        toggle_btn.pack(anchor=tk.W)
        
    def create_setting_input(self, parent, label_text, default_value, row):
        """Create a setting input field"""
        tk.Label(parent,
                text=label_text,
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary'],
                font=("Georgia", 9)).grid(row=row, column=0, sticky=tk.W, pady=8)
        
        entry = ttk.Entry(parent, width=15, font=("Georgia", 10))
        entry.insert(0, str(default_value))
        entry.grid(row=row, column=1, sticky=tk.W, padx=(20, 0))
        
        return entry
        
    def on_closing(self):
        """Handle window close event"""
        if self.session_active:
            if messagebox.askyesno("Session Active",
                                 "A session is currently active.\n"
                                 "Closing will stop it and mark it as incomplete.\n\n"
                                 "Do you want to exit?"):
                self.session_active = False
                if self.break_window:
                    self.break_window.destroy()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = RestingTimeSystem()
    app.run()