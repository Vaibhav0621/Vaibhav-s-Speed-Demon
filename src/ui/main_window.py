"""
Main Window for Speed Demon
"""

import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox 
from typing import Dict, List, Optional
import threading
import queue
from loguru import logger
from datetime import datetime
import psutil
from pathlib import Path

from src.ui.components import ProcessCard, PerformanceChart, StatCard, SearchBar, NotificationBanner
from src.ui.styles import SpeedDemonTheme
from src.core.monitor import ProcessMonitor
from src.core.optimizer import SystemOptimizer
from src.core.profiler import PerformanceProfiler
from src.utils.config import ConfigManager
from src.utils.helpers import format_bytes, format_time, is_admin, request_admin

class SpeedDemonApp(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Check admin privileges
        if not is_admin():
            self.show_admin_prompt()
        
        # Initialize components
        self.config = ConfigManager()
        self.monitor = ProcessMonitor(refresh_interval=5.0)
        self.optimizer = SystemOptimizer()
        self.profiler = PerformanceProfiler()
        self.update_counter = 0
        # UI state
        self.process_cards: Dict[int, ProcessCard] = {}
        self.update_queue = queue.Queue()
        self.search_query = ""
        self.current_view = "dashboard"  # dashboard, processes, settings
        
        # Configure window
        self.title("Vaibhav's Speed Demon - Universal Accelerator")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Apply theme
        SpeedDemonTheme.apply_theme(self.config.get('ui.theme', 'dark'))
        
        # Set window icon (if available)
        try:
            self.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Create UI
        self._create_ui()

        self._setup_keyboard_shortcuts()
        
        # Start monitoring
        self.monitor.add_callback(self._on_process_update)
        self.monitor.start_monitoring()
        
        # Start UI update loop
        self.after(500, self._process_updates)
        
        # Bind window events
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        from src.core.game_detector import GameDetector
        self.game_detector = GameDetector()
        self.game_mode_auto = False
        self.detected_games = []

        from src.core.scheduler import OptimizationScheduler
        self.scheduler = OptimizationScheduler(self.optimizer, self.monitor)
        self.scheduler.add_callback(self._on_schedule_executed)
        
        from src.core.game_detector import GameDetector
        from src.core.network_optimizer import NetworkOptimizer
        from src.core.scheduler import OptimizationScheduler
        from src.core.profile_manager import ProfileManager
    
        self.game_detector = GameDetector()
        self.network_optimizer = NetworkOptimizer()
        self.scheduler = OptimizationScheduler(self.optimizer, self.monitor)
        self.profile_manager = ProfileManager(self.optimizer, self.config)
    
        # Feature states
        self.game_mode_auto = False
        self.detected_games = []
        self.scheduler.start()

    def show_admin_prompt(self):
        """Show admin privileges prompt"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Administrator Required")
        dialog.geometry("400x200")
        dialog.transient(self)
        
        # Message
        message = ctk.CTkLabel(
            dialog,
            text="Speed Demon requires administrator privileges\nfor full functionality.",
            font=("Segoe UI", 14)
        )
        message.pack(pady=30)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack()
        
        restart_btn = ctk.CTkButton(
            button_frame,
            text="Restart as Admin",
            command=lambda: request_admin() or self.destroy()
        )
        restart_btn.pack(side="left", padx=10)
        
        continue_btn = ctk.CTkButton(
            button_frame,
            text="Continue (Limited)",
            fg_color="transparent",
            border_width=1,
            command=dialog.destroy
        )
        continue_btn.pack(side="left")
    
    def _create_ui(self):
        """Create the main UI layout"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self._create_sidebar()
        
        # Content area
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # Create views
        self._create_dashboard_view()
        self._create_processes_view()
        self._create_settings_view()
        
        # Show initial view
        self._show_view("dashboard")
    
    def _create_sidebar(self):
        """Create sidebar navigation"""
        sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", pady=(20, 30))
        logo_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="⚡ SPEED DEMON",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(expand=True)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", "dashboard", "📊"),
            ("Processes", "processes", "⚙️"),
            ("Performance", "performance", "📈"),
            ("Settings", "settings", "⚙️")
        ]
        
        self.nav_buttons = {}
        
        for text, view, icon in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=f"{icon}  {text}",
                font=("Segoe UI", 14),
                height=50,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#2a2a2a",
                anchor="w",
                command=lambda v=view: self._show_view(v)
            )
            btn.pack(fill="x", padx=20, pady=5)
            self.nav_buttons[view] = btn
        
        # System info at bottom
        info_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        info_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        
        # Admin status
        admin_status = "Admin Mode" if is_admin() else "Limited Mode"
        admin_label = ctk.CTkLabel(
            info_frame,
            text=f"🔒 {admin_status}",
            font=("Segoe UI", 11),
            text_color="#888888"
        )
        admin_label.pack(anchor="w")
        
        # Version
        version_label = ctk.CTkLabel(
            info_frame,
            text="Version 1.0.0",
            font=("Segoe UI", 10),
            text_color="#666666"
        )
        version_label.pack(anchor="w", pady=(5, 0))
    
    def _create_dashboard_view(self):
        """Create dashboard view"""
        self.dashboard_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="System Dashboard",
            font=("Segoe UI", 28, "bold")
        )
        welcome_label.pack(side="left")
        
        # Quick actions
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        boost_all_btn = ctk.CTkButton(
            action_frame,
            text="⚡ Boost All",
            width=120,
            height=40,
            font=("Segoe UI", 14),
            command=self._boost_all_processes
        )
        boost_all_btn.pack(side="left", padx=5)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=20)
        
        # Create stat cards
        self.stat_cards = {
            'total_boost': StatCard(
                stats_frame,
                title="Total Boost",
                value="0%",
                subtitle="System Performance",
                color="#00ff88"
            ),
            'processes': StatCard(
                stats_frame,
                title="Optimized",
                value="0",
                subtitle="Processes",
                color="#0084ff"
            ),
            'cpu_usage': StatCard(
                stats_frame,
                title="CPU Usage",
                value="0%",
                subtitle="Current",
                color="#ffaa00"
            ),
            'memory': StatCard(
                stats_frame,
                title="Memory",
                value="0%",
                subtitle="In Use",
                color="#ff4444"
            ),
            'network': StatCard(
                stats_frame,
                title="Network",
                value="0 MB/s",
                subtitle="Download",
                color="#9b59b6"
            )
        }

        for card in self.stat_cards.values():
            card.pack(side="left", fill="both", expand=True, padx=10)
        
        # Performance charts
        charts_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # CPU Chart
        self.cpu_chart = PerformanceChart(
            charts_frame,
            title="CPU Usage",
            color="#00ff88"
        )
        self.cpu_chart.pack(side="left", fill="both", expand=True, padx=10)
        
        # Memory Chart
        self.memory_chart = PerformanceChart(
            charts_frame,
            title="Memory Usage",
            color="#0084ff"
        )
        self.memory_chart.pack(side="left", fill="both", expand=True, padx=10)
        game_mode_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        game_mode_frame.pack(side="right", padx=20)
        self.game_mode_label = ctk.CTkLabel(
            game_mode_frame,
            text="🎮 Game Mode: OFF",
            font=("Segoe UI", 14, "bold"),
            text_color="#666666"
        )
        self.game_mode_label.pack(side="top")
    
        self.game_mode_switch = ctk.CTkSwitch(
            game_mode_frame,
            text="Auto-detect",
            font=("Segoe UI", 12),
            command=self._toggle_game_mode_auto
        )
        self.game_mode_switch.pack(side="top", pady=(5, 0))
        # Add to dashboard view
        quick_actions_frame = ctk.CTkFrame(self.dashboard_frame)
        quick_actions_frame.pack(fill="x", padx=30, pady=20)

        quick_actions_label = ctk.CTkLabel(
            quick_actions_frame,
            text="Quick Actions",
            font=("Segoe UI", 16, "bold")
        )
        quick_actions_label.pack(anchor="w", pady=(10, 15))

        actions_grid = ctk.CTkFrame(quick_actions_frame, fg_color="transparent")
        actions_grid.pack(fill="x")

        # Quick action buttons
        quick_actions = [
            ("🎮 Gaming Mode", lambda: self._quick_gaming_mode()),
            ("🌐 Optimize Network", lambda: self._quick_network_optimize()),
            ("📁 Save Profile", lambda: self._quick_save_profile()),
            ("⏰ Schedule", lambda: self._show_view('settings')),
            ("🧹 Clean Memory", lambda: self._quick_clean_memory()),
            ("⚡ Max Performance", lambda: self._quick_max_performance())
        ]

        for i, (text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(
                actions_grid,
                text=text,
                width=180,
                height=50,
                font=("Segoe UI", 12),
                command=command
            )
            btn.grid(row=i // 3, column=i % 3, padx=10, pady=10)
    
    def _quick_gaming_mode(self):
        """Quick toggle gaming mode"""
        self.game_mode_switch.toggle()
        self._toggle_game_mode_auto()

    def _quick_network_optimize(self):
        """Quick network optimization for current apps"""
        processes = self.monitor.get_processes()
        optimized = 0
    
        for process in processes[:5]:  # Top 5 processes
            if process['cpu_percent'] > 10:
                success, _ = self.network_optimizer.optimize_for_application(
                    process['pid'], 
                    'gaming' if self.game_detector.game_mode_active else 'general'
                )
                if success:
                    optimized += 1
    
        notification = NotificationBanner(
            self.content_area,
            message=f"Network optimized for {optimized} applications",
            type="success"
        )
        notification.show()

    def _quick_save_profile(self):
        """Quick save current settings as profile"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        profile_id = self.profile_manager.create_profile(
            name=f"Quick Save - {timestamp}",
            description="Automatically saved profile"
        )
    
        if profile_id:
            notification = NotificationBanner(
                self.content_area,
                message="Current settings saved as profile",
                type="success"
            )
            notification.show()

    def _quick_clean_memory(self):
        """Quick memory cleanup"""
        import gc
        gc.collect()
    
        # Clean process working sets
        cleaned = 0
        for pid in list(self.optimizer.optimized_processes.keys()):
            try:
                process = psutil.Process(pid)
                self.optimizer._optimize_memory(process)
                cleaned += 1
            except:
                pass
    
        notification = NotificationBanner(
            self.content_area,
            message=f"Memory cleaned for {cleaned} processes",
            type="success"
        )
        notification.show()

    def _quick_max_performance(self):
        """Enable maximum performance mode"""
        # Set power plan
        if hasattr(self, 'game_detector'):
            self.game_detector._set_power_plan('high_performance')
    
        # Optimize all high-usage processes
        processes = self.monitor.get_processes()
        optimized = 0
    
        for process in processes[:15]:  # Top 15 processes
            if process['cpu_percent'] > 3 or process['memory_percent'] > 3:
                success, _ = self.optimizer.optimize_process(process['pid'])
                if success:
                    optimized += 1
    
        notification = NotificationBanner(
            self.content_area,
            message=f"Maximum performance mode enabled! {optimized} processes optimized",
            type="success"
        )
        notification.show()
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = {
            '<Control-g>': lambda e: self._quick_gaming_mode(),
            '<Control-n>': lambda e: self._quick_network_optimize(),
            '<Control-s>': lambda e: self._quick_save_profile(),
            '<Control-m>': lambda e: self._quick_clean_memory(),
            '<Control-p>': lambda e: self._quick_max_performance(),
            '<F1>': lambda e: self._show_help(),
            '<F5>': lambda e: self._refresh_all()
        }

        for key, command in shortcuts.items():
            self.bind(key, command)

    def _show_help(self):
        """Show help dialog"""
        help_text = """
            Speed Demon Keyboard Shortcuts:

            trl+G - Toggle Gaming Mode
            Ctrl+N - Optimize Network
            Ctrl+S - Save Current Profile
            Ctrl+M - Clean Memory
            Ctrl+P - Maximum Performance
            F1 - Show This Help
            F5 - Refresh All

            For more information, visit the documentation.
        """
    
        dialog = ctk.CTkToplevel(self)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("400x400")
    
        text_widget = ctk.CTkTextbox(dialog, width=350, height=300)
        text_widget.pack(pady=20)
        text_widget.insert("1.0", help_text)
        text_widget.configure(state="disabled")

    def _refresh_all(self):
        """Refresh all displays"""
        processes = self.monitor.get_processes()
        self._update_process_list(processes)
        self._update_dashboard()

    def _create_processes_view(self):
        """Create processes view"""
        self.processes_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Header with search
        header_frame = ctk.CTkFrame(self.processes_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        processes_label = ctk.CTkLabel(
            header_frame,
            text="Process Manager",
            font=("Segoe UI", 28, "bold")
        )
        processes_label.pack(side="left")
        
        # Search bar
        search_bar = SearchBar(
            header_frame,
            on_search=self._on_search
        )
        search_bar.pack(side="right", fill="x", expand=True, padx=(50, 0))
        
        # Process list container
        self.process_list_frame = ctk.CTkScrollableFrame(
            self.processes_frame,
            fg_color="transparent"
        )
        self.process_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_network_optimization_ui(self, parent):
        """Create network optimization UI"""
        network_frame = ctk.CTkFrame(parent)
        network_frame.pack(fill="x", pady=10)
    
        # Title
        title_label = ctk.CTkLabel(
            network_frame,
            text="🌐 Network Optimization",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(anchor="w", padx=20, pady=(15, 10))
    
        # Network stats
        stats_frame = ctk.CTkFrame(network_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20)
    
        self.network_labels = {
            'speed': ctk.CTkLabel(stats_frame, text="Speed: 0 MB/s", font=("Segoe UI", 12)),
            'latency': ctk.CTkLabel(stats_frame, text="Latency: 0 ms", font=("Segoe UI", 12)),
            'connections': ctk.CTkLabel(stats_frame, text="Connections: 0", font=("Segoe UI", 12))
        }
    
        for label in self.network_labels.values():
            label.pack(side="left", padx=20)
    
        # Optimization buttons
        button_frame = ctk.CTkFrame(network_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
    
        gaming_btn = ctk.CTkButton(
            button_frame,
            text="🎮 Gaming Mode",
            width=120,
            command=lambda: self._apply_network_profile('gaming')
        )
        gaming_btn.pack(side="left", padx=5)
    
        streaming_btn = ctk.CTkButton(
            button_frame,
            text="📺 Streaming Mode",
            width=120,
            command=lambda: self._apply_network_profile('streaming')
        )
        streaming_btn.pack(side="left", padx=5)
    
        download_btn = ctk.CTkButton(
            button_frame,
            text="⬇️ Download Mode",
            width=120,
            command=lambda: self._apply_network_profile('download')
        )
        download_btn.pack(side="left", padx=5)

    def _enable_lightweight_mode(self):
        """Enable lightweight mode for better performance"""
        # Reduce update frequencies
        self.monitor.refresh_interval = 10.0  # 10 seconds
        
        # Disable animations
        ctk.set_widget_scaling(1.0)
        
        # Limit process display
        self.config.set('performance.max_processes_display', 10)
        
        # Disable auto features
        self.game_mode_auto = False
        
        # Show notification
        notification = NotificationBanner(
            self.content_area,
            message="Lightweight mode enabled for better performance",
            type="info"
        )
        notification.show()
    
    def _create_settings_view(self):
        """Create settings view"""
        self.settings_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        settings_label = ctk.CTkLabel(
            header_frame,
            text="Settings",
            font=("Segoe UI", 28, "bold")
        )
        settings_label.pack(side="left")
        
        # Settings sections
        settings_container = ctk.CTkScrollableFrame(
            self.settings_frame,
            fg_color="transparent"
        )
        settings_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # General Settings
        general_section = self._create_settings_section(
            settings_container,
            "General Settings"
        )
        
        # Theme selector
        theme_frame = ctk.CTkFrame(general_section, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=("Segoe UI", 12),
            width=150,
            anchor="w"
        )
        theme_label.pack(side="left")
        
        self.theme_var = ctk.StringVar(value=self.config.get('ui.theme', 'dark'))
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self._on_theme_change
        )
        theme_menu.pack(side="left")
        
        # Auto-start
        autostart_frame = ctk.CTkFrame(general_section, fg_color="transparent")
        autostart_frame.pack(fill="x", pady=10)
        
        autostart_label = ctk.CTkLabel(
            autostart_frame,
            text="Start with Windows:",
            font=("Segoe UI", 12),
            width=150,
            anchor="w"
        )
        autostart_label.pack(side="left")
        
        self.autostart_var = ctk.BooleanVar(value=self.config.get('general.autostart', False))
        autostart_switch = ctk.CTkSwitch(
            autostart_frame,
            variable=self.autostart_var,
            command=self._on_autostart_change
        )
        autostart_switch.pack(side="left")
        
        # Performance Settings
        perf_section = self._create_settings_section(
            settings_container,
            "⚡ Performance Settings"
        )

        # Lightweight mode toggle
        lightweight_var = ctk.BooleanVar(value=False)
        lightweight_check = ctk.CTkCheckBox(
            perf_section,
            text="Enable Lightweight Mode (Better performance, fewer features)",
            variable=lightweight_var,
            command=lambda: self._enable_lightweight_mode() if lightweight_var.get() else self._disable_lightweight_mode()
        )
        lightweight_check.pack(anchor="w", pady=5)

        # Process limit slider
        process_limit_label = ctk.CTkLabel(
            perf_section,
            text="Max Processes to Display:",
            font=("Segoe UI", 12)
        )
        process_limit_label.pack(anchor="w", pady=(10, 5))

        process_limit_slider = ctk.CTkSlider(
            perf_section,
            from_=10,
            to=50,
            command=lambda v: self.config.set('performance.max_processes_display', int(v))
        )
        process_limit_slider.set(self.config.get('performance.max_processes_display', 20))
        process_limit_slider.pack(fill="x", pady=5)
        
        # Refresh interval
        refresh_frame = ctk.CTkFrame(perf_section, fg_color="transparent")
        refresh_frame.pack(fill="x", pady=10)
        
        refresh_label = ctk.CTkLabel(
            refresh_frame,
            text="Refresh Interval:",
            font=("Segoe UI", 12),
            width=150,
            anchor="w"
        )
        refresh_label.pack(side="left")
        
        self.refresh_var = ctk.StringVar(value=str(self.config.get('performance.refresh_interval', 2000)))
        refresh_slider = ctk.CTkSlider(
            refresh_frame,
            from_=500,
            to=5000,
            command=self._on_refresh_change
        )
        refresh_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        refresh_value = ctk.CTkLabel(
            refresh_frame,
            textvariable=self.refresh_var,
            font=("Segoe UI", 12)
        )
        refresh_value.pack(side="left")
        
        # About section
        about_section = self._create_settings_section(
            settings_container,
            "About"
        )
        
        about_text = """Speed Demon v1.0.0
        Universal Software Accelerator
        Created with ❤️ for maximum performance
        © 2025 Speed Demon Software"""
        
        about_label = ctk.CTkLabel(
            about_section,
            text=about_text,
            font=("Segoe UI", 12),
            justify="left"
        )
        about_label.pack(pady=20)
        scheduler_section = self._create_settings_section(
            settings_container,
            "⏰ Scheduled Optimizations"
        )
        schedule_list_frame = ctk.CTkScrollableFrame(
            scheduler_section,
            height=200,
            fg_color="transparent"
        )
        schedule_list_frame.pack(fill="both", expand=True, pady=10)

        # Add schedule button
        add_schedule_btn = ctk.CTkButton(
            scheduler_section,
            text="+ Add Schedule",
            command=self._show_add_schedule_dialog
        )
        add_schedule_btn.pack(pady=10)
        # Add to _create_settings_view method
        profiles_section = self._create_settings_section(
            settings_container,
            "📁 Optimization Profiles"
        )

        # Initialize profile manager
        from src.core.profile_manager import ProfileManager
        self.profile_manager = ProfileManager(self.optimizer, self.config)

        # Profile list
        profile_list_frame = ctk.CTkScrollableFrame(
            profiles_section,
            height=200,
            fg_color="transparent"
        )
        profile_list_frame.pack(fill="both", expand=True, pady=10)

        # Profile buttons
        profile_buttons = ctk.CTkFrame(profiles_section, fg_color="transparent")
        profile_buttons.pack(fill="x", pady=10)

        create_profile_btn = ctk.CTkButton(
            profile_buttons,
            text="+ Create Profile",
            width=120,
            command=self._show_create_profile_dialog
        )
        create_profile_btn.pack(side="left", padx=5)

        import_profile_btn = ctk.CTkButton(
            profile_buttons,
            text="⬇️ Import",
            width=100,
            command=self._import_profile
        )
        import_profile_btn.pack(side="left", padx=5)

        # Refresh profile list
        self._refresh_profile_list(profile_list_frame)
        
    def _refresh_profile_list(self, container):
        """Refresh the profile list display"""
        # Clear existing
        for widget in container.winfo_children():
            widget.destroy()
    
        profiles = self.profile_manager.profiles
    
        if not profiles:
            empty_label = ctk.CTkLabel(
                container,
                text="No profiles saved yet",
                font=("Segoe UI", 12),
                text_color="#666666"
            )
            empty_label.pack(pady=50)
            return
    
        for profile_id, profile_data in profiles.items():
            profile_card = ctk.CTkFrame(container, corner_radius=10)
            profile_card.pack(fill="x", pady=5)
        
            # Profile info
            info_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
            name_label = ctk.CTkLabel(
                info_frame,
                text=profile_data['name'],
                font=("Segoe UI", 14, "bold")
            )
            name_label.pack(anchor="w")
        
            desc_text = profile_data.get('description', 'No description')
            created = profile_data.get('created', 'Unknown')
        
            desc_label = ctk.CTkLabel(
                info_frame,
                text=f"{desc_text[:50]}{'...' if len(desc_text) > 50 else ''}",
                font=("Segoe UI", 11),
                text_color="#888888"
            )
            desc_label.pack(anchor="w", pady=(2, 0))
        
            date_label = ctk.CTkLabel(
                info_frame,
                text=f"Created: {created[:10]}",
                font=("Segoe UI", 10),
                text_color="#666666"
            )
            date_label.pack(anchor="w")
        
            # Action buttons
            action_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
            action_frame.pack(side="right", padx=10)
        
            apply_btn = ctk.CTkButton(
                action_frame,
                text="Apply",
                width=70,
                height=28,
                command=lambda pid=profile_id: self._apply_profile(pid)
            )
            apply_btn.pack(side="left", padx=2)
        
            export_btn = ctk.CTkButton(
                action_frame,
                text="Export",
                width=70,
                height=28,
                fg_color="transparent",
                border_width=1,
                command=lambda pid=profile_id: self._export_profile(pid)
            )
            export_btn.pack(side="left", padx=2)
        
            share_btn = ctk.CTkButton(
                action_frame,
                text="Share",
                width=60,
                height=28,
                fg_color="transparent",
                border_width=1,
                command=lambda pid=profile_id: self._share_profile(pid)
            )
            share_btn.pack(side="left", padx=2)
        
            delete_btn = ctk.CTkButton(
                action_frame,
                text="🗑️",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color="#ff4444",
                command=lambda pid=profile_id: self._delete_profile(pid, container)
            )
            delete_btn.pack(side="left", padx=2)

    def _show_create_profile_dialog(self):
        """Show dialog to create new profile"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Optimization Profile")
        dialog.geometry("500x400")
        dialog.transient(self)
    
        # Profile name
        name_label = ctk.CTkLabel(
            dialog,
            text="Profile Name:",
            font=("Segoe UI", 12)
        )
        name_label.pack(pady=(30, 5))
    
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack()
    
        # Description
        desc_label = ctk.CTkLabel(
            dialog,
            text="Description:",
            font=("Segoe UI", 12)
        )
        desc_label.pack(pady=(20, 5))
    
        desc_text = ctk.CTkTextbox(dialog, width=300, height=100)
        desc_text.pack()
    
        # Options
        options_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        options_frame.pack(pady=20)
    
        include_system_var = ctk.BooleanVar(value=True)
        include_system_check = ctk.CTkCheckBox(
            options_frame,
            text="Include current system settings",
            variable=include_system_var
        )
        include_system_check.pack(anchor="w", pady=5)
    
        include_network_var = ctk.BooleanVar(value=True)
        include_network_check = ctk.CTkCheckBox(
            options_frame,
            text="Include network optimizations",
            variable=include_network_var
        )
        include_network_check.pack(anchor="w", pady=5)
    
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
    
        def create_profile():
            name = name_entry.get()
            if not name:
                return
        
            description = desc_text.get("1.0", "end-1c")
        
            profile_id = self.profile_manager.create_profile(
                name=name,
                description=description,
                include_system_settings=include_system_var.get()
            )
        
            if profile_id:
                # Refresh profile list
                profile_list_frame = self.settings_frame.winfo_children()[1].winfo_children()[5]
                self._refresh_profile_list(profile_list_frame)
            
                # Show success notification
                notification = NotificationBanner(
                    self.content_area,
                    message=f"Profile '{name}' created successfully!",
                    type="success"
                )
                notification.show()
        
            dialog.destroy()
    
        create_btn = ctk.CTkButton(
            button_frame,
            text="Create Profile",
            command=create_profile
        )
        create_btn.pack(side="left", padx=10)
    
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            command=dialog.destroy
        )
        cancel_btn.pack(side="left")

    def _apply_profile(self, profile_id: str):
        """Apply a profile"""
        if self.profile_manager.apply_profile(profile_id):
            profile_name = self.profile_manager.profiles[profile_id]['name']
            notification = NotificationBanner(
                self.content_area,
                message=f"Profile '{profile_name}' applied successfully!",
                type="success"
            )
            notification.show()
        else:
            notification = NotificationBanner(
                self.content_area,
                message="Failed to apply profile",
                type="error"
            )
            notification.show()

    def _export_profile(self, profile_id: str):
        """Export a profile"""
        from tkinter import filedialog
    
        profile_name = self.profile_manager.profiles[profile_id]['name']
        filename = filedialog.asksaveasfilename(
            defaultextension=".sdprofile",
            filetypes=[("Speed Demon Profile", "*.sdprofile"), ("All Files", "*.*")],
            initialfile=f"{profile_name}.sdprofile"
        )
    
        if filename:
            if self.profile_manager.export_profile(profile_id, filename):
                notification = NotificationBanner(
                    self.content_area,
                    message=f"Profile exported to {Path(filename).name}",
                    type="success"
                )
                notification.show()

    def _import_profile(self):
        """Import a profile"""
        from tkinter import filedialog
    
        filename = filedialog.askopenfilename(
            filetypes=[("Speed Demon Profile", "*.sdprofile"), ("All Files", "*.*")]
        )
    
        if filename:
            profile_id = self.profile_manager.import_profile(filename)
            if profile_id:
                # Refresh profile list
                profile_list_frame = self.settings_frame.winfo_children()[1].winfo_children()[5]
                self._refresh_profile_list(profile_list_frame)
            
                notification = NotificationBanner(
                    self.content_area,
                    message="Profile imported successfully!",
                    type="success"
                )
                notification.show()
            else:
                notification = NotificationBanner(
                    self.content_area,
                    message="Failed to import profile",
                    type="error"
                )
                notification.show()

    def _share_profile(self, profile_id: str):
        """Share a profile"""
        share_code = self.profile_manager.share_profile(profile_id)
    
        if share_code:
            # Show share dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Share Profile")
            dialog.geometry("500x300")
            dialog.transient(self)
        
            info_label = ctk.CTkLabel(
                dialog,
                text="Share this code with others to share your profile:",
                font=("Segoe UI", 12)
            )
            info_label.pack(pady=(30, 20))
        
            # Share code display
            code_text = ctk.CTkTextbox(dialog, width=400, height=100)
            code_text.pack(pady=10)
            code_text.insert("1.0", share_code)
            code_text.configure(state="disabled")
        
            # Copy button
            def copy_code():
                self.clipboard_clear()
                self.clipboard_append(share_code)
                copy_btn.configure(text="Copied! ✓")
                self.after(2000, lambda: copy_btn.configure(text="Copy to Clipboard"))
        
            copy_btn = ctk.CTkButton(
                dialog,
                text="Copy to Clipboard",
                command=copy_code
            )
            copy_btn.pack(pady=20)
        else:
            notification = NotificationBanner(
                self.content_area,
                message="Profile too large to share via code. Use Export instead.",
                type="warning"
            )
            notification.show()

    def _delete_profile(self, profile_id: str, container):
        """Delete a profile with confirmation"""
        profile_name = self.profile_manager.profiles[profile_id]['name']
    
        # Confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("400x200")
        dialog.transient(self)
    
        confirm_label = ctk.CTkLabel(
            dialog,
            text=f"Are you sure you want to delete the profile:\n'{profile_name}'?",
            font=("Segoe UI", 12)
        )
        confirm_label.pack(pady=40)
    
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack()
    
        def confirm_delete():
            if self.profile_manager.delete_profile(profile_id):
                self._refresh_profile_list(container)
                notification = NotificationBanner(
                    self.content_area,
                    message=f"Profile '{profile_name}' deleted",
                    type="info"
                )
                notification.show()
            dialog.destroy()
    
        yes_btn = ctk.CTkButton(
            button_frame,
            text="Delete",
            fg_color="#ff4444",
            hover_color="#cc3333",
            command=confirm_delete
        )
        yes_btn.pack(side="left", padx=10)
    
        no_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            command=dialog.destroy
        )
        no_btn.pack(side="left")

    def _create_settings_section(self, parent, title: str) -> ctk.CTkFrame:
        """Create a settings section"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=10)
        
        # Section title
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Section content frame
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        return content_frame
    
    def _show_view(self, view: str):
        """Show specific view"""
        # Hide all views
        self.dashboard_frame.pack_forget()
        self.processes_frame.pack_forget()
        self.settings_frame.pack_forget()
        
        # Update nav buttons
        for btn_view, btn in self.nav_buttons.items():
            if btn_view == view:
                btn.configure(fg_color="#2a2a2a")
            else:
                btn.configure(fg_color="transparent")
        
        # Show selected view
        if view == "dashboard":
            self.dashboard_frame.pack(fill="both", expand=True)
        elif view == "processes":
            self.processes_frame.pack(fill="both", expand=True)
        elif view == "settings":
            self.settings_frame.pack(fill="both", expand=True)
        
        self.current_view = view
    
    def _on_process_update(self, processes: List[Dict]):
        """Handle process list update from monitor"""
        # Put update in queue for main thread
        self.update_queue.put(('processes', processes))
    
    def _process_updates(self):
        """Process updates from queue (main thread)"""
        try:
            while not self.update_queue.empty():
                update_type, data = self.update_queue.get_nowait()
                
                if update_type == 'processes':
                    self._update_process_list(data)
                    self._update_dashboard()
        except queue.Empty:
            pass

        self.update_counter += 1
        if self.update_counter % 5 == 0:
            # Update performance charts
            self.profiler.update_metrics()
            metrics = self.profiler.get_current_metrics()
        
            # Update charts
            if hasattr(self, 'cpu_chart'):
                self.cpu_chart.update_data(metrics['cpu']['percent'])
        
            if hasattr(self, 'memory_chart'):
                self.memory_chart.update_data(metrics['memory']['percent'])
            if hasattr(self, 'game_mode_auto') and self.game_mode_auto:
                self._check_for_games()
    
            # Update network stats
            if hasattr(self, 'network_optimizer'):
                network_stats = self.network_optimizer.get_network_status()
                if hasattr(self, 'stat_cards') and 'network' in self.stat_cards:
                    self.stat_cards['network'].update_value(
                        f"{network_stats['download_speed']:.1f} MB/s",
                        subtitle=f"↑ {network_stats['upload_speed']:.1f} MB/s"
                    )
        
                # Update network labels if visible
                if hasattr(self, 'network_labels'):
                    self.network_labels['speed'].configure(
                        text=f"Speed: ↓{network_stats['download_speed']:.1f} ↑{network_stats['upload_speed']:.1f} MB/s"
                    )
                    self.network_labels['latency'].configure(
                        text=f"Latency: {network_stats['latency']:.0f} ms"
                    )
                    self.network_labels['connections'].configure(
                        text=f"Connections: {network_stats['active_connections']}"
                    )

        # Schedule next update
        self.after(100, self._process_updates)
    
    def _update_process_list(self, processes: List[Dict]):
        """Update process list display"""
        if self.current_view != "processes":
            return
        
        # Filter by search query
        if self.search_query:
            processes = [p for p in processes if self.search_query.lower() in p['name'].lower()]
        
        # Limit to top processes
        max_display = self.config.get('performance.max_processes_display', 20)
        processes = processes[:max_display]
        
        # Update or create process cards
        displayed_pids = set()
        
        for process in processes:
            pid = process['pid']
            displayed_pids.add(pid)
            
            # Add optimization info
            process['is_optimized'] = pid in self.optimizer.optimized_processes
            if process['is_optimized']:
                process['boost'] = self.optimizer.calculate_boost(pid)
            
            # Convert memory to MB
            process['memory_mb'] = process.get('memory_mb', 0)
            
            # Update or create card
            if pid in self.process_cards:
                # Update existing card
                self.process_cards[pid].update_data(process)
            else:
                # Create new card
                card = ProcessCard(
                    self.process_list_frame,
                    process,
                    on_optimize=self._optimize_process,
                    on_details=self._show_process_details
                )
                card.pack(fill="x", pady=5)
                self.process_cards[pid] = card
        
        # Remove cards for processes that are no longer displayed
        for pid in list(self.process_cards.keys()):
            if pid not in displayed_pids:
                self.process_cards[pid].destroy()
                del self.process_cards[pid]
    
    def _update_dashboard(self):
        """Update dashboard statistics"""
        if self.current_view != "dashboard":
            return
        
        # Get optimization stats
        stats = self.optimizer.get_optimization_stats()
        
        # Update stat cards
        self.stat_cards['total_boost'].update_value(f"{stats['total_boost']}%")
        self.stat_cards['processes'].update_value(str(stats['total_optimized']))
        
        # Update system stats
        metrics = self.profiler.get_current_metrics()
        self.stat_cards['cpu_usage'].update_value(f"{metrics['cpu']['percent']:.1f}%")
        self.stat_cards['memory'].update_value(f"{metrics['memory']['percent']:.1f}%")
    
    def _optimize_process(self, pid: int):
        """Optimize a single process"""
        def optimize_thread():
            success, message = self.optimizer.optimize_process(pid)
            self.update_queue.put(('optimization_complete', (success, message)))
        
            if success:
                # Show success notification
                notification = NotificationBanner(
                    self.content_area,
                    message=f"Process optimized successfully! {message}",
                    type="success"
                )
                notification.show()
            else:
                # Show error notification
                notification = NotificationBanner(
                    self.content_area,
                    message=f"Optimization failed: {message}",
                    type="error"
                )
                notification.show()
        thread = threading.Thread(target=optimize_thread, daemon=True)
        thread.start()
    
    def _boost_all_processes(self):
        """Optimize all running processes"""
        processes = self.monitor.get_processes()
        optimized_count = 0
        
        for process in processes[:10]:  # Limit to top 10 processes
            if process['cpu_percent'] > 5 or process['memory_percent'] > 5:
                success, _ = self.optimizer.optimize_process(process['pid'])
                if success:
                    optimized_count += 1
        
        # Show notification
        notification = NotificationBanner(
            self.content_area,
            message=f"Optimized {optimized_count} processes!",
            type="success"
        )
        notification.show()
    
    def _show_process_details(self, pid: int):
        """Show detailed process information"""
        details = self.monitor.get_process_details(pid)
        if not details:
            return
        
        # Create details dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Process Details - {details['name']}")
        dialog.geometry("600x500")
        dialog.transient(self)
        
        # Process info
        info_frame = ctk.CTkFrame(dialog)
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add details
        details_text = f"""
            Process: {details['name']}
            PID: {details['pid']}
            Status: {details['status']}
            CPU Usage: {details['cpu_percent']:.1f}%
            Memory: {format_bytes(details['memory_info']['rss'])}
            Threads: {details['num_threads']}
            Nice Value: {details['nice']}
            Created: {details['create_time']}
        """
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            font=("Consolas", 12),
            justify="left"
        )
        details_label.pack(pady=20)
    
    def _on_search(self, query: str):
        """Handle search query change"""
        self.search_query = query
        # Trigger immediate update
        processes = self.monitor.get_processes()
        self._update_process_list(processes)
    
    def _on_theme_change(self, theme: str):
        """Handle theme change"""
        self.config.set('ui.theme', theme)
        ctk.set_appearance_mode(theme)
    
    def _on_autostart_change(self):
        """Handle autostart toggle"""
        enabled = self.autostart_var.get()
        self.config.set('general.autostart', enabled)
        # TODO: Implement actual autostart functionality
    
    def _on_refresh_change(self, value: float):
        """Handle refresh interval change"""
        self.refresh_var.set(f"{int(value)} ms")
        self.config.set('performance.refresh_interval', int(value))
        self.monitor.refresh_interval = value / 1000  # Convert to seconds
    
    def _on_closing(self):
        """Handle window closing"""
        # Stop all services
        self.monitor.stop_monitoring()
        self.scheduler.stop()
    
        # Save current state
        self.config._save_user_config()
    
        # Save any pending profiles
        if hasattr(self, 'profile_manager'):
            for profile_id in self.profile_manager.profiles:
                # Auto-save any unsaved changes
                pass
    
        # Reset network if optimized
        if hasattr(self, 'network_optimizer') and self.network_optimizer.optimized_connections:
            self.network_optimizer.reset_network_optimizations()
    
        # Disable game mode if active
        if hasattr(self, 'game_detector') and self.game_detector.game_mode_active:
            self.game_detector.disable_game_mode(self.optimizer)
    
        # Destroy window
        self.destroy()
        
    def _toggle_game_mode_auto(self):
        """Toggle automatic game mode detection"""
        self.game_mode_auto = self.game_mode_switch.get()
    
        if self.game_mode_auto:
            self._check_for_games()
        else:
            if self.game_detector.game_mode_active:
                self.game_detector.disable_game_mode(self.optimizer)
                self._update_game_mode_ui(False)

    def _check_for_games(self):
        """Check for running games"""
        if not self.game_mode_auto:
            return
    
        processes = self.monitor.get_processes()
        self.detected_games = self.game_detector.detect_games(processes)
    
        if self.detected_games and not self.game_detector.game_mode_active:
            # Games detected, enable game mode
            self.game_detector.enable_game_mode(self.optimizer, self.detected_games)
            self._update_game_mode_ui(True)
            self._show_game_notification(True)
        elif not self.detected_games and self.game_detector.game_mode_active:
            # No games detected, disable game mode
            self.game_detector.disable_game_mode(self.optimizer)
            self._update_game_mode_ui(False)
            self._show_game_notification(False)

    def _update_game_mode_ui(self, active: bool):
        """Update game mode UI elements"""
        if active:
            self.game_mode_label.configure(
                text="🎮 Game Mode: ON",
                text_color="#00ff88"
            )
            # Add glow effect to window
            if hasattr(self, 'main_container'):
                self.main_container.configure(border_width=2, border_color="#00ff88")
        else:
            self.game_mode_label.configure(
                text="🎮 Game Mode: OFF",
                text_color="#666666"
            )
            if hasattr(self, 'main_container'):
                self.main_container.configure(border_width=0)

    def _show_game_notification(self, enabled: bool):
        """Show game mode notification"""
        if enabled:
            games_list = ", ".join([g['name'] for g in self.detected_games[:3]])
            if len(self.detected_games) > 3:
                games_list += f" and {len(self.detected_games) - 3} more"
        
            notification = NotificationBanner(
                self.content_area,
                message=f"Game Mode activated! Detected: {games_list}",
                type="success"
            )
        else:
            notification = NotificationBanner(
                self.content_area,
                message="Game Mode deactivated - No games running",
                type="info"
            )
        notification.show(duration=5000)
    def _show_add_schedule_dialog(self):
        """Show dialog to add new schedule"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Schedule")
        dialog.geometry("500x600")
        dialog.transient(self)
    
        # Schedule name
        name_label = ctk.CTkLabel(dialog, text="Schedule Name:", font=("Segoe UI", 12))
        name_label.pack(pady=(20, 5))
    
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack()
    
        # Schedule type
        type_label = ctk.CTkLabel(dialog, text="Schedule Type:", font=("Segoe UI", 12))
        type_label.pack(pady=(20, 5))
    
        type_var = ctk.StringVar(value="daily")
        type_menu = ctk.CTkOptionMenu(
            dialog,
            values=["daily", "weekly", "interval", "startup", "idle"],
            variable=type_var,
            command=lambda x: self._update_schedule_options(dialog, x)
        )
        type_menu.pack()
    
        # Time input (for daily/weekly)
        self.time_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        self.time_frame.pack(pady=20)
    
        time_label = ctk.CTkLabel(self.time_frame, text="Time (HH:MM):", font=("Segoe UI", 12))
        time_label.pack()
    
        time_entry = ctk.CTkEntry(self.time_frame, width=100, placeholder_text="14:30")
        time_entry.pack()
    
        # Actions
        actions_label = ctk.CTkLabel(dialog, text="Actions:", font=("Segoe UI", 12))
        actions_label.pack(pady=(20, 5))
    
        actions_frame = ctk.CTkFrame(dialog)
        actions_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
        # Action checkboxes
        action_vars = {
            'optimize_all': ctk.BooleanVar(value=True),
            'clean_memory': ctk.BooleanVar(value=False),
            'gaming_mode': ctk.BooleanVar(value=False)
        }
    
        ctk.CTkCheckBox(
            actions_frame,
            text="Optimize all high-usage processes",
            variable=action_vars['optimize_all']
        ).pack(anchor="w", pady=5)
    
        ctk.CTkCheckBox(
            actions_frame,
            text="Clean system memory",
            variable=action_vars['clean_memory']
        ).pack(anchor="w", pady=5)
    
        ctk.CTkCheckBox(
            actions_frame,
            text="Enable gaming mode if games detected",
            variable=action_vars['gaming_mode']
        ).pack(anchor="w", pady=5)
    
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
    
        def add_schedule():
            name = name_entry.get()
            if not name:
                return
            # Build actions list
            actions = []
            if action_vars['optimize_all'].get():
                actions.append({'type': 'optimize_all'})
            if action_vars['clean_memory'].get():
                actions.append({'type': 'clean_memory'})
            if action_vars['gaming_mode'].get():
                actions.append({'type': 'gaming_mode'})
        
            # Add schedule
            schedule_id = self.scheduler.add_schedule(
                name=name,
                schedule_type=type_var.get(),
                time_str=time_entry.get() if type_var.get() in ['daily', 'weekly'] else None,
                actions=actions
            )
        
            self._refresh_schedule_list()
            dialog.destroy()
    
        ctk.CTkButton(
            button_frame,
            text="Add Schedule",
            command=add_schedule
        ).pack(side="left", padx=10)
    
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            command=dialog.destroy
        ).pack(side="left")

    def _on_schedule_executed(self, schedule_id: str, schedule_info: Dict):
        """Callback when a schedule is executed"""
        # Show notification about schedule execution
        schedule_name = schedule_info.get('name', 'Unknown')
    
        notification = NotificationBanner(
            self.content_area,
            message=f"Schedule '{schedule_name}' executed successfully",
            type="info"
        )
        notification.show()
    
        # Refresh UI if needed
        if self.current_view == "settings":
            # Refresh schedule list if we're viewing settings
            try:
                # Find the schedule list frame and refresh it
                self._refresh_schedule_list()
            except:
                pass
    
        # Log the execution
        logger.info(f"Schedule executed: {schedule_name} (ID: {schedule_id})")

    def _refresh_schedule_list(self):
        """Refresh the schedule list display"""
        # Clear existing
        for widget in self.schedule_list_frame.winfo_children():
            widget.destroy()
    
        schedules = self.scheduler.get_schedules()
    
        for schedule_id, schedule_info in schedules.items():
            schedule_card = ctk.CTkFrame(self.schedule_list_frame)
            schedule_card.pack(fill="x", pady=5)
        
            # Schedule info
            info_frame = ctk.CTkFrame(schedule_card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
            ctk.CTkLabel(
                info_frame,
                text=schedule_info['name'],
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w")
        
            ctk.CTkLabel(
                info_frame,
                text=f"Type: {schedule_info['type']} | Next run: {schedule_info.get('next_run', 'N/A')}",
                font=("Segoe UI", 11),
                text_color="#888888"
            ).pack(anchor="w")
        
            # Controls
            control_frame = ctk.CTkFrame(schedule_card, fg_color="transparent")
            control_frame.pack(side="right", padx=10)
        
            # Enable/disable switch
            enabled_var = ctk.BooleanVar(value=schedule_info.get('enabled', True))
            ctk.CTkSwitch(
                control_frame,
                text="",
                variable=enabled_var,
                command=lambda sid=schedule_id, var=enabled_var: 
                    self.scheduler.enable_schedule(sid, var.get())
            ).pack(side="left", padx=5)
        
            # Delete button
            ctk.CTkButton(
                control_frame,
                text="🗑️",
                width=30,
                fg_color="transparent",
                hover_color="#ff4444",
                command=lambda sid=schedule_id: self._delete_schedule(sid)
            ).pack(side="left")
    def _delete_schedule(self, schedule_id: str):
        """Delete a schedule with confirmation"""
        schedule_name = self.scheduler.schedules[schedule_id]['name']
    
        # Simple confirmation dialog
        result = tk.messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the schedule '{schedule_name}'?"
        )
    
        if result:
            self.scheduler.remove_schedule(schedule_id)
            self._refresh_schedule_list()
        
            notification = NotificationBanner(
                self.content_area,
                message=f"Schedule '{schedule_name}' deleted",
                type="info"
            )
            notification.show()