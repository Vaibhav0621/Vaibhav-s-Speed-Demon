"""
UI Styles and Theme Configuration
"""

import customtkinter as ctk

class SpeedDemonTheme:
    """Speed Demon UI Theme"""
    
    # Color Palette
    COLORS = {
        # Dark theme colors
        'dark': {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'bg_tertiary': '#2a2a2a',
            'surface': '#1e1e1e',
            'surface_variant': '#2d2d2d',
            'accent': '#00ff88',
            'accent_hover': '#00cc66',
            'danger': '#ff4444',
            'warning': '#ffaa00',
            'success': '#00ff88',
            'text_primary': '#ffffff',
            'text_secondary': '#aaaaaa',
            'text_disabled': '#666666',
            'border': '#333333'
        },
        # Light theme colors (if needed)
        'light': {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f5f5f5',
            'bg_tertiary': '#eeeeee',
            'surface': '#ffffff',
            'surface_variant': '#f9f9f9',
            'accent': '#00cc66',
            'accent_hover': '#00aa55',
            'danger': '#ff4444',
            'warning': '#ffaa00',
            'success': '#00cc66',
            'text_primary': '#000000',
            'text_secondary': '#666666',
            'text_disabled': '#999999',
            'border': '#dddddd'
        }
    }
    
    # Font configuration
    FONTS = {
        'heading': ('Segoe UI', 24, 'bold'),
        'subheading': ('Segoe UI', 18, 'bold'),
        'body': ('Segoe UI', 14),
        'small': ('Segoe UI', 12),
        'mono': ('Consolas', 12)
    }
    
    # Component styles
    BUTTON_STYLES = {
        'primary': {
            'fg_color': COLORS['dark']['accent'],
            'hover_color': COLORS['dark']['accent_hover'],
            'text_color': '#000000',
            'corner_radius': 8,
            'height': 40
        },
        'secondary': {
            'fg_color': COLORS['dark']['surface_variant'],
                        'hover_color': COLORS['dark']['bg_tertiary'],
            'text_color': COLORS['dark']['text_primary'],
            'corner_radius': 8,
            'height': 40
        },
        'danger': {
            'fg_color': COLORS['dark']['danger'],
            'hover_color': '#cc3333',
            'text_color': '#ffffff',
            'corner_radius': 8,
            'height': 40
        }
    }
    
    @classmethod
    def apply_theme(cls, theme: str = 'dark'):
        """Apply theme to customtkinter"""
        ctk.set_appearance_mode(theme)
        
        # Create custom theme
        custom_theme = {
            "CTk": {
                "fg_color": [cls.COLORS['light']['bg_primary'], cls.COLORS['dark']['bg_primary']]
            },
            "CTkFrame": {
                "fg_color": [cls.COLORS['light']['surface'], cls.COLORS['dark']['surface']],
                "border_color": [cls.COLORS['light']['border'], cls.COLORS['dark']['border']],
                "corner_radius": 10
            },
            "CTkButton": {
                "fg_color": [cls.COLORS['light']['accent'], cls.COLORS['dark']['accent']],
                "hover_color": [cls.COLORS['light']['accent_hover'], cls.COLORS['dark']['accent_hover']],
                "corner_radius": 8
            }
        }
        
        return custom_theme