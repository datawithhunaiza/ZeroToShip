"""
DoomFolder - CLI Storage Analyzer

Main entry point for the DoomFolder application.

This module:
- Provides interactive CLI menu
- Handles user input/output
- Orchestrates DoomFolder and FileInfo objects
- Demonstrates application flow

Why main.py is separate:
- Separates UI logic from core analysis logic
- Makes testing analysis functions easier
- Allows reusing DoomFolder in other UIs (GUI, API)
- Follows layered architecture pattern
"""

from pathlib import Path
from typing import Optional
import sys
import time

from doomfolder import DoomFolder
from utils import (
    get_folder_input,
    get_size_threshold,
    print_header,
    print_separator,
    format_size_for_display,
)


class DoomFolderApp:
    def __init__(self) -> None:
        """Initialize the application."""
        self.current_folder: Optional[DoomFolder] = None
        self.running: bool = True
    
    def show_welcome(self) -> None:
        """Display welcome screen."""
        print("\n")
        print_separator(60, "=")
        print("  🔥 DOOMFOLDER - CLI STORAGE ANALYZER 🔥")
        print("  Analyze folders without deleting files")
        print_separator(60, "=")
        print()
    
    def show_menu(self) -> str:
        """
        Display main menu and get user choice.
        
        Returns:
            str: User's menu selection
        """
        print("\n" + "=" * 60)
        print("MAIN MENU")
        print("=" * 60)
        
        if self.current_folder:
            print(f"📁 Current Folder: {self.current_folder.folder_path.name}")
            print()
        
        print("1. 📂 Scan Folder")
        print("2. 📊 View Summary")
        print("3. 📦 View Large Files")
        print("4. 🔁 View Duplicate Files")
        print("5. 🕰️  View Old Files")
        print("6. 📸 View Screenshots")
        print("7. 📦 View Archive Files")
        print("8. 📈 Full Report")
        print("9. 🔄 Change Folder")
        print("0. ❌ Exit")
        print("=" * 60)
        
        choice = input("\n🎯 Enter your choice (0-9): ").strip()
        return choice
    
    def scan_folder_menu(self) -> None:
        """Handle scan folder option."""
        print()
        folder_path = get_folder_input()
        
        if not folder_path:
            print("⚠️  Cancelled.")
            return
        
        try:
            self.current_folder = DoomFolder(folder_path)
            self.current_folder.scan()
            print(f"✅ Folder analysis ready!")
            print(f"   Files found: {len(self.current_folder.files)}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def view_summary(self) -> None:
        """Display folder summary."""
        if not self._check_folder_scanned():
            return
        
        print()
        self.current_folder.print_summary()
    
    def view_large_files(self) -> None:
        """Display large files with user-defined threshold."""
        if not self._check_folder_scanned():
            return
        
        print()
        threshold = get_size_threshold()
        
        if threshold is None:
            return
        
        large_files = self.current_folder.find_large_files(threshold)
        
        if not large_files:
            print(f"✅ No files larger than {format_size_for_display(threshold)}\n")
            return
        
        print_header(
            f"LARGE FILES (>{format_size_for_display(threshold)})",
            60
        )
        print(f"\nFound {len(large_files)} files:\n")
        
        total_size = 0
        for i, file_info in enumerate(large_files[:20], 1):  # Show top 20
            print(f"{i}. {file_info.name}")
            print(f"   Size: {file_info.get_human_readable_size()}")
            print(f"   Path: {file_info.path}")
            print()
            total_size += file_info.size
        
        if len(large_files) > 20:
            print(f"... and {len(large_files) - 20} more files")
        
        print(f"\nTotal Space Used: {format_size_for_display(total_size)}")
        print_separator(60)
        print()
    
    def view_duplicates(self) -> None:
        """Display duplicate files and wasted space."""
        if not self._check_folder_scanned():
            return
        
        print()
        print("🔍 Finding duplicates (this may take a moment)...")
        duplicates = self.current_folder.find_duplicates()
        
        if not duplicates:
            print("✅ No duplicate files found!\n")
            return
        
        print_header(f"DUPLICATE FILES ({len(duplicates)} groups)", 60)
        print(f"\nFound {len(duplicates)} groups of duplicate files:\n")
        
        total_wasted = 0
        
        for i, (file_hash, files) in enumerate(
            sorted(duplicates.items(), 
                   key=lambda x: sum(f.size for f in x[1]), 
                   reverse=True)[:10], 1
        ):
            size_per_file = files[0].size
            wasted_space = size_per_file * (len(files) - 1)
            total_wasted += wasted_space
            
            print(f"{i}. {len(files)} copies of {format_size_for_display(size_per_file)}")
            print(f"   Wasted Space: {format_size_for_display(wasted_space)}")
            print(f"   Files:")
            
            for file_info in files[:3]:
                print(f"     • {file_info.path}")
            
            if len(files) > 3:
                print(f"     ... and {len(files) - 3} more")
            print()
        
        if len(duplicates) > 10:
            print(f"... and {len(duplicates) - 10} more duplicate groups")
        
        print(f"Total Wasted Space: {format_size_for_display(total_wasted)}")
        print("💡 Tip: These files have identical content (same SHA-256 hash)")
        print_separator(60)
        print()
    
    def view_old_files(self) -> None:
        """Display old files not modified recently."""
        if not self._check_folder_scanned():
            return
        
        print()
        days = input("🕰️  Files not modified for how many days? (default: 180): ").strip()
        
        try:
            days_threshold = int(days) if days else 180
        except ValueError:
            print("❌ Please enter a valid number.")
            return
        
        old_files = self.current_folder.find_old_files(days_threshold)
        
        if not old_files:
            print(f"✅ No files older than {days_threshold} days\n")
            return
        
        print_header(f"OLD FILES (not modified for {days_threshold}+ days)", 60)
        print(f"\nFound {len(old_files)} files:\n")
        
        total_size = 0
        for i, file_info in enumerate(old_files[:20], 1):
            age_days = file_info.get_age_days()
            print(f"{i}. {file_info.name}")
            print(f"   Last Modified: {file_info.modified_date.strftime('%Y-%m-%d')}")
            print(f"   Age: {age_days} days")
            print(f"   Size: {file_info.get_human_readable_size()}")
            print()
            total_size += file_info.size
        
        if len(old_files) > 20:
            print(f"... and {len(old_files) - 20} more files")
        
        print(f"\nTotal Space Used: {format_size_for_display(total_size)}")
        print_separator(60)
        print()
    
    def view_screenshots(self) -> None:
        """Display screenshot files found."""
        if not self._check_folder_scanned():
            return
        
        print()
        screenshots = self.current_folder.find_screenshots()
        
        if not screenshots:
            print("✅ No screenshot files found\n")
            return
        
        print_header(f"SCREENSHOT FILES ({len(screenshots)} found)", 60)
        print(f"\nFound {len(screenshots)} screenshot files:\n")
        
        total_size = 0
        for i, file_info in enumerate(screenshots[:20], 1):
            print(f"{i}. {file_info.name}")
            print(f"   Size: {file_info.get_human_readable_size()}")
            print(f"   Path: {file_info.path}")
            print()
            total_size += file_info.size
        
        if len(screenshots) > 20:
            print(f"... and {len(screenshots) - 20} more files")
        
        print(f"Total Space Used: {format_size_for_display(total_size)}")
        print_separator(60)
        print()
    
    def view_archives(self) -> None:
        """Display archive files found."""
        if not self._check_folder_scanned():
            return
        
        print()
        archives = self.current_folder.find_archive_files()
        
        if not archives:
            print("✅ No archive files found\n")
            return
        
        print_header(f"ARCHIVE FILES ({len(archives)} found)", 60)
        print(f"\nFound {len(archives)} archive files:\n")
        
        total_size = 0
        for i, file_info in enumerate(archives[:20], 1):
            print(f"{i}. {file_info.name}")
            print(f"   Size: {file_info.get_human_readable_size()}")
            print(f"   Path: {file_info.path}")
            print()
            total_size += file_info.size
        
        if len(archives) > 20:
            print(f"... and {len(archives) - 20} more files")
        
        print(f"Total Space Used: {format_size_for_display(total_size)}")
        print("Supported Formats: .zip, .rar, .7z, .tar, .gz, .bz2, .xz, .iso")
        print_separator(60)
        print()
    
    def view_full_report(self) -> None:
        """Display comprehensive report."""
        if not self._check_folder_scanned():
            return
        
        print()
        self.current_folder.print_detailed_report()
    
    def _check_folder_scanned(self) -> bool:
        """
        Verify that a folder has been scanned.
        """
        if self.current_folder is None:
            print("❌ No folder scanned yet. Please scan a folder first.")
            return False
        
        if not self.current_folder.scan_complete:
            print("❌ Folder scan not complete.")
            return False
        
        return True
    
    def handle_menu_choice(self, choice: str) -> None:
        """
        Route menu choice to appropriate handler.
        
        """
        handlers = {
            '1': self.scan_folder_menu,
            '2': self.view_summary,
            '3': self.view_large_files,
            '4': self.view_duplicates,
            '5': self.view_old_files,
            '6': self.view_screenshots,
            '7': self.view_archives,
            '8': self.view_full_report,
            '9': self.scan_folder_menu,  # Re-scan with new folder
            '0': self.exit_app,
        }
        
        handler = handlers.get(choice)
        
        if handler:
            try:
                handler()
            except KeyboardInterrupt:
                print("\n\n⚠️  Operation cancelled by user.")
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
        else:
            print("❌ Invalid choice. Please try again.")
    
    def exit_app(self) -> None:
        """Handle exit gracefully."""
        print("\n")
        print_separator(60)
        print("  Thank you for using DoomFolder!")
        print("  Remember: Never delete files without reviewing them first!")
        print_separator(60)
        print()
        self.running = False
    
    def run(self) -> None:
        self.show_welcome()
        
        try:
            while self.running:
                choice = self.show_menu()
                self.handle_menu_choice(choice)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Application interrupted.")
            self.running = False
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.running = False


def main() -> None:
    app = DoomFolderApp()
    app.run()


if __name__ == "__main__":
    main()
