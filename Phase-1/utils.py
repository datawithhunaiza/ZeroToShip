"""
Utils Module

This module contains utility functions for common operations used throughout
the DoomFolder application.

Why this module exists:
- Keeps utility functions separate from core logic (SRP)
- Promotes code reuse across modules
- Makes testing easier
- Demonstrates modularity in OOP design

Functions here handle:
- Path validation and normalization
- User input validation
- String formatting for CLI
- File extension detection
"""

from pathlib import Path
from typing import Tuple
import os


def validate_folder_path(folder_path: str) -> Tuple[bool, str, Path | None]:
    """
    Validate that a folder exists and is accessible.
    
    Why this function exists:
    - Centralizes input validation logic
    - Prevents repeated validation code in DoomFolder
    - Provides clear error messages to users
    - Demonstrates defensive programming
    
    Args:
        folder_path (str): User-provided folder path
        
    Returns:
        Tuple[bool, str, Path | None]: 
            - bool: whether path is valid
            - str: error message if invalid, empty string if valid
            - Path: pathlib.Path object if valid, None otherwise
    """
    try:
        # Convert string to pathlib.Path for cross-platform compatibility
        path_obj = Path(folder_path).expanduser()
        
        # Check if path exists
        if not path_obj.exists():
            return False, f"❌ Path does not exist: {folder_path}", None
        
        # Check if it's a directory, not a file
        if not path_obj.is_dir():
            return False, f"❌ Path is not a directory: {folder_path}", None
        
        # Check if we have read permissions
        if not os.access(path_obj, os.R_OK):
            return False, f"❌ No read permission for: {folder_path}", None
        
        return True, "", path_obj
    
    except Exception as e:
        return False, f"❌ Error validating path: {str(e)}", None


def get_file_extension_category(extension: str) -> str:
    """
    Categorize file by extension.
    
    Why this function exists:
    - Centralizes extension categorization logic
    - Makes it easy to add new categories
    - Promotes consistency across the application
    
    Args:
        extension (str): File extension (e.g., '.txt', '.jpg')
        
    Returns:
        str: Category name (e.g., 'Image', 'Document', 'Archive')
    """
    ext = extension.lower()
    
    categories = {
        'Image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
        'Document': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt'],
        'Archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
        'Video': ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm'],
        'Code': ['.py', '.js', '.java', '.cpp', '.c', '.php', '.html', '.css'],
        'Executable': ['.exe', '.bat', '.sh', '.app', '.dmg'],
    }
    
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    
    return 'Other'


def is_screenshot(filename: str) -> bool:
    """
    Detect if a file is a screenshot based on filename patterns.
    
    Why this function exists:
    - Encapsulates screenshot detection logic
    - Demonstrates pattern matching and case-insensitivity
    - Makes it easy to add/remove screenshot patterns
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if filename matches screenshot patterns
        
    Examples:
        "Screenshot.png" -> True
        "Screenshot (1).png" -> True
        "Screen Shot.png" -> True
        "screen_capture.png" -> True
        "document.pdf" -> False
    """
    filename_lower = filename.lower()
    
    # Patterns that indicate a screenshot
    screenshot_patterns = [
        'screenshot',
        'screen shot',
        'screen_shot',
        'screen capture',
        'screen_capture',
        'screencapture',
        'screen-shot',
        'screenclip',
        'snagit',
        'capture',
    ]
    
    return any(pattern in filename_lower for pattern in screenshot_patterns)


def is_archive(extension: str) -> bool:
    """
    Check if file extension indicates an archive.
    
    Why this function exists:
    - Centralizes archive detection
    - Demonstrates simplicity of focused functions
    
    Args:
        extension (str): File extension (e.g., '.zip')
        
    Returns:
        bool: True if extension is an archive format
    """
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
    return extension.lower() in archive_extensions


def format_size_for_display(size_bytes: int) -> str:
    """
    Format byte size into human-readable string.
    
    Why this function exists:
    - Centralizes formatting logic
    - Reusable across multiple display methods
    - Ensures consistent formatting throughout app
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
        
    Example:
        1024 -> "1.00 KB"
        1048576 -> "1.00 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            if unit == 'B':
                return f"{int(size_bytes)} {unit}"
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    
    return f"{size_bytes:.2f} TB"


def format_bytes(size_bytes: int, precision: int = 2) -> str:
    """
    Alternative format function with precision control.
    
    Args:
        size_bytes (int): Size in bytes
        precision (int): Decimal places to show
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024:
            if unit == 'B':
                return f"{int(size_bytes)} {unit}"
            return f"{size_bytes:.{precision}f} {unit}"
        size_bytes /= 1024
    
    return f"{size_bytes:.{precision}f} PB"


def print_separator(width: int = 50, char: str = "=") -> None:
    """
    Print a decorative separator line.
    
    Why this function exists:
    - Centralizes UI formatting
    - Improves consistency across CLI output
    - Demonstrates helper functions for UX
    
    Args:
        width (int): Length of separator line
        char (str): Character to use for separator
    """
    print(char * width)


def print_header(title: str, width: int = 50) -> None:
    """
    Print a formatted header with separators.
    
    Args:
        title (str): Header text
        width (int): Width of separator
    """
    print_separator(width)
    print(f"  {title}")
    print_separator(width)


def get_user_input_choice(prompt: str, valid_choices: list) -> str:
    """
    Get validated user input from a list of choices.
    
    Why this function exists:
    - Centralizes input validation
    - Handles error cases gracefully
    - Promotes consistent user experience
    
    Args:
        prompt (str): Question to ask user
        valid_choices (list): List of acceptable responses
        
    Returns:
        str: Valid user choice
        
    Example:
        choice = get_user_input_choice("Pick one:", ["1", "2", "3"])
    """
    while True:
        try:
            user_input = input(prompt).strip()
            if user_input in valid_choices:
                return user_input
            print(f"❌ Invalid choice. Please enter one of: {', '.join(valid_choices)}")
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
            raise


def get_folder_input() -> Path | None:
    """
    Get folder path from user with validation.
    
    Why this function exists:
    - Centralizes folder input logic
    - Handles validation and error messages
    - Improves code reuse in main.py
    
    Returns:
        Path: Valid folder path, or None if user cancels
        
    Example:
        folder = get_folder_input()
        if folder:
            print(f"Using folder: {folder}")
    """
    while True:
        try:
            folder_input = input(
                "📁 Enter folder path (or 'q' to cancel): "
            ).strip()
            
            if folder_input.lower() == 'q':
                return None
            
            is_valid, error_msg, path_obj = validate_folder_path(folder_input)
            
            if is_valid:
                return path_obj
            
            print(error_msg)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
            return None


def get_size_threshold() -> int:
    """
    Get file size threshold from user in MB.
    
    Why this function exists:
    - Centralizes user input for threshold
    - Handles validation and conversion
    - Returns size in bytes for internal use
    
    Returns:
        int: File size threshold in bytes
        
    Example:
        threshold = get_size_threshold()  # User enters "100"
        # Returns 104857600 (100 MB in bytes)
    """
    while True:
        try:
            size_input = input(
                "📊 Enter minimum file size in MB (default: 100): "
            ).strip()
            
            if not size_input:
                return 100 * 1024 * 1024  # 100 MB in bytes
            
            size_mb = int(size_input)
            
            if size_mb <= 0:
                print("❌ Size must be greater than 0.")
                continue
            
            return size_mb * 1024 * 1024  # Convert to bytes
        
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
            return None
