"""
Reusable UI Components for Speed Demon
"""

import customtkinter as ctk
from typing import Optional, Callable, Dict, Any
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ProcessCard(ctk.CTkFrame):
    """Modern process card component"""
    
    def __init__(self, parent, process_data: Dict[str, Any], 
                 on_optimize: Callable, on_details: Callable, **kwargs):
        super().__init__(parent, corner_radius=12, **kwargs)
        
        self.process_data = process_data
        self.on_optimize = on_optimize
        self.on_details = on_details
        self.is_optimized = process_data.get('is_optimized', False)
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=12)
        
        # Left section - Icon and info
        left_frame = ctk.CTkFrame(container, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Process icon placeholder
        icon_frame = ctk.CTkFrame(left_frame, width=48, height=48, corner_radius=12)
        icon_frame.pack(side="left", padx=(0, 15))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text="⚡", font=("Segoe UI", 20))
        icon_label.pack(expand=True)
        
        # Process info
        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Process name
        name_label = ctk.CTkLabel(
            info_frame,
            text=self.process_data['name'],
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Stats
        stats_text = f"CPU: {self.process_data['cpu_percent']:.1f}% | RAM: {self.process_data['memory_mb']:.0f} MB"
        stats_label = ctk.CTkLabel(
            info_frame,
            text=stats_text,
            font=("Segoe UI", 11),
            text_color="#888888",
            anchor="w"
        )
        stats_label.pack(anchor="w", pady=(2, 0))
        
        # Right section - Boost and actions
        right_frame = ctk.CTkFrame(container, fg_color="transparent")
        right_frame.pack(side="right")
        
        # Boost display
        if self.is_optimized:
            boost_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
            boost_frame.pack(side="left", padx=(0, 15))
            
            boost_label = ctk.CTkLabel(
                boost_frame,
                text=f"+{self.process_data.get('boost', 0)}%",
                font=("Segoe UI", 20, "bold"),
                text_color="#00ff88"
            )
            boost_label.pack()
            
            boost_text = ctk.CTkLabel(
                boost_frame,
                text="BOOST",
                font=("Segoe UI", 9),
                text_color="#00ff88"
            )
            boost_text.pack()
        
        # Action buttons
        action_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        # Optimize button
        optimize_btn = ctk.CTkButton(
            action_frame,
            text="✓ Optimized" if self.is_optimized else "Optimize",
            width=100,
            height=32,
            corner_radius=16,
            fg_color="#00ff88" if self.is_optimized else "#0084ff",
            hover_color="#00cc66" if self.is_optimized else "#0066cc",
            font=("Segoe UI", 12),
            command=lambda: self.on_optimize(self.process_data['pid']),
            state="disabled" if self.is_optimized else "normal"
        )
        optimize_btn.pack(pady=(0, 5))
        
        # Details button
        details_btn = ctk.CTkButton(
            action_frame,
            text="Details",
            width=100,
            height=28,
            corner_radius=14,
            fg_color="transparent",
            border_width=1,
            border_color="#333333",
            hover_color="#2a2a2a",
            font=("Segoe UI", 11),
            command=lambda: self.on_details(self.process_data['pid'])
        )
        details_btn.pack()
    
    def update_data(self, process_data: Dict[str, Any]):
        """Update process data and refresh display"""
        self.process_data = process_data
        self.is_optimized = process_data.get('is_optimized', False)
        # Recreate widgets with new data
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()


class PerformanceChart(ctk.CTkFrame):
    """Real-time performance chart component"""
    
    def __init__(self, parent, title: str, color: str = "#00ff88", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.color = color
        self.data = []
        self.max_points = 50
        
        self._create_chart()
    
    def _create_chart(self):
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(4, 2), dpi=80)
        self.fig.patch.set_facecolor('#1e1e1e')
        self.ax.set_facecolor('#1e1e1e')
        
        # Style the plot
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color('#333333')
        self.ax.spines['left'].set_color('#333333')
        self.ax.tick_params(colors='#666666', labelsize=8)
        self.ax.grid(True, alpha=0.1, color='#333333')
        
        # Initial empty plot
        self.line, = self.ax.plot([], [], color=self.color, linewidth=2)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, self.max_points)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def update_data(self, value: float):
        """Add new data point and update chart"""
        self.data.append(value)
        if len(self.data) > self.max_points:
            self.data.pop(0)
        
        # Update plot
        x = list(range(len(self.data)))
        self.line.set_data(x, self.data)
        
        # Adjust x-axis
        if len(self.data) > 1:
            self.ax.set_xlim(0, len(self.data) - 1)
        
        # Redraw
        self.canvas.draw_idle()


class StatCard(ctk.CTkFrame):
    """Statistics display card"""
    
    def __init__(self, parent, title: str, value: str = "0", 
                 subtitle: str = "", color: str = "#00ff88", **kwargs):
        super().__init__(parent, corner_radius=12, **kwargs)
        
        self.title = title
        self.color = color
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 11),
            text_color="#888888"
        )
        title_label.pack(pady=(15, 5))
        
        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Segoe UI", 28, "bold"),
            text_color=color
        )
        self.value_label.pack()
        
        # Subtitle
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=("Segoe UI", 10),
                text_color="#666666"
            )
            subtitle_label.pack(pady=(0, 15))
    
    def update_value(self, value: str, subtitle: str = None):
        """Update displayed value"""
        self.value_label.configure(text=value)
        if subtitle is not None:
            # Update subtitle if provided
            pass


class SearchBar(ctk.CTkFrame):
    """Modern search bar component"""
    
    def __init__(self, parent, on_search: Callable, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_search = on_search
        
        # Search container
        search_frame = ctk.CTkFrame(self, corner_radius=20, height=40)
        search_frame.pack(fill="x")
        search_frame.pack_propagate(False)
        
        # Search icon
        icon_label = ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Segoe UI", 14),
            width=40
        )
        icon_label.pack(side="left")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search processes...",
            border_width=0,
            fg_color="transparent",
            font=("Segoe UI", 12)
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search)
    
    def _on_search(self, event):
        """Handle search input"""
        query = self.search_entry.get()
        self.on_search(query)


class NotificationBanner(ctk.CTkFrame):
    """Notification banner component"""
    
    def __init__(self, parent, message: str, type: str = "info", **kwargs):
        super().__init__(parent, corner_radius=8, height=40, **kwargs)
        self.pack_propagate(False)
        
        # Set color based on type
        colors = {
            'info': '#0084ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff4444'
        }
        
        self.configure(fg_color=colors.get(type, colors['info']))
        
        # Icon
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        icon_label = ctk.CTkLabel(
            self,
            text=icons.get(type, icons['info']),
            font=("Segoe UI", 14)
        )
        icon_label.pack(side="left", padx=(15, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=("Segoe UI", 12)
        )
        message_label.pack(side="left", fill="x", expand=True)
        
        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="×",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color="rgba(255,255,255,0.1)",
            font=("Segoe UI", 18),
            command=self.destroy
        )
        close_btn.pack(side="right", padx=(10, 10))
    
    def show(self, duration: int = 3000):
        """Show notification for specified duration"""
        self.pack(fill="x", padx=20, pady=(10, 0))
        if duration > 0:
            self.after(duration, self.destroy)