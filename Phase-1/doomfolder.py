"""
DoomFolder Module

This module contains the DoomFolder class, which is the core of the application.

Why this class exists:
- Serves as the main orchestrator for file scanning and analysis
- Demonstrates composition pattern (contains FileInfo objects)
- Separates analysis logic from user interface (in main.py)
- Follows Single Responsibility: coordinate file analysis operations

"""

from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime, timedelta
import hashlib
from collections import defaultdict

from fileinfo import FileInfo
from utils import (
    validate_folder_path,
    is_screenshot,
    is_archive,
    format_size_for_display,
    print_separator,
    print_header,
)


class DoomFolder:
    def __init__(self, folder_path: Path) -> None:
        is_valid, error_msg, validated_path = validate_folder_path(str(folder_path))
        if not is_valid:
            raise ValueError(error_msg)
        
        self.folder_path: Path = validated_path
        self.files: List[FileInfo] = []
        self.scan_complete: bool = False
        self.errors: List[str] = []
    
    def scan(self) -> None:
        try:
            print("🔍 Scanning folder...")
            
            # Use pathlib's rglob for recursive scanning
            # rglob = recursive glob, finds all files in all subdirectories
            file_count = 0
            
            for file_path in self.folder_path.rglob('*'):
                # Skip directories, only process files
                if not file_path.is_file():
                    continue
                
                try:
                    # Create FileInfo object (composition in action)
                    file_info = FileInfo(file_path)
                    self.files.append(file_info)
                    file_count += 1
                    
                    # Progress indicator for long scans
                    if file_count % 100 == 0:
                        print(f"  📄 Found {file_count} files...", end='\r')
                
                except (PermissionError, OSError) as e:
                    # Log error but continue scanning
                    self.errors.append(f"Cannot read {file_path}: {str(e)}")
            
            self.scan_complete = True
            print(f"\n✅ Scan complete! Found {file_count} files.\n")
            
            if self.errors:
                print(f"⚠️  {len(self.errors)} files could not be read due to permissions.\n")
        
        except PermissionError as e:
            raise PermissionError(f"Permission denied accessing folder: {e}")
        except Exception as e:
            raise Exception(f"Error during scan: {str(e)}")
    
    def find_duplicates(self) -> Dict[str, List[FileInfo]]:
        
        if not self.scan_complete:
            raise RuntimeError("Must call scan() before find_duplicates()")
        
        hash_map: Dict[str, List[FileInfo]] = defaultdict(list)
        
        for file_info in self.files:
            try:
                # Calculate SHA-256 hash of file content
                file_hash = self._get_file_hash(file_info.path)
                hash_map[file_hash].append(file_info)
            except (PermissionError, OSError) as e:
                self.errors.append(f"Cannot hash {file_info.name}: {str(e)}")
        
        # Return only groups with 2 or more files (actual duplicates)
        duplicates = {
            hash_val: files 
            for hash_val, files in hash_map.items() 
            if len(files) > 1
        }
        
        return duplicates
    
    def _get_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:

       
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def find_large_files(self, size_threshold: int = 100 * 1024 * 1024) -> List[FileInfo]:
        if not self.scan_complete:
            raise RuntimeError("Must call scan() before find_large_files()")
        
        # Filter files larger than threshold
        large_files = [f for f in self.files if f.size > size_threshold]
        
        # Sort by size, largest first
        large_files.sort(key=lambda f: f.size, reverse=True)
        
        return large_files
    
    def find_old_files(self, days_old: int = 180) -> List[FileInfo]:
        if not self.scan_complete:
            raise RuntimeError("Must call scan() before find_old_files()")
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Filter files older than cutoff
        old_files = [f for f in self.files if f.modified_date < cutoff_date]
        
        # Sort by date, oldest first
        old_files.sort(key=lambda f: f.modified_date)
        
        return old_files
    
    def find_screenshots(self) -> List[FileInfo]:
        if not self.scan_complete:
            raise RuntimeError("Must call scan() before find_screenshots()")
        
        # Filter using is_screenshot utility function
        screenshots = [f for f in self.files if is_screenshot(f.name)]
        
        # Sort by size, largest first
        screenshots.sort(key=lambda f: f.size, reverse=True)
        
        return screenshots
    
    def find_archive_files(self) -> List[FileInfo]:
        if not self.scan_complete:
            raise RuntimeError("Must call scan() before find_archive_files()")
        
        # Filter using is_archive utility function
        archives = [f for f in self.files if is_archive(f.extension)]
        
        # Sort by size, largest first
        archives.sort(key=lambda f: f.size, reverse=True)
        
        return archives
    
    def get_total_size(self) -> int:
        return sum(f.size for f in self.files)
    
    def get_largest_file(self) -> FileInfo | None:
        return max(self.files, key=lambda f: f.size) if self.files else None
    
    def get_file_count_by_extension(self) -> Dict[str, int]:
        extension_counts: Dict[str, int] = defaultdict(int)
        
        for file_info in self.files:
            ext = file_info.extension if file_info.extension else 'no_extension'
            extension_counts[ext] += 1
        
        # Sort by count, most common first
        return dict(sorted(extension_counts.items(), key=lambda x: x[1], reverse=True))
    
    def get_size_by_extension(self) -> Dict[str, int]:
        extension_sizes: Dict[str, int] = defaultdict(int)
        
        for file_info in self.files:
            ext = file_info.extension if file_info.extension else 'no_extension'
            extension_sizes[ext] += file_info.size
        
        # Sort by size, largest first
        return dict(sorted(extension_sizes.items(), key=lambda x: x[1], reverse=True))
    
    def print_detailed_report(
        self,
        large_threshold: int = 100 * 1024 * 1024,
        old_threshold: int = 180
    ) -> None:
        if not self.scan_complete:
            print("❌ Must run scan first!")
            return
        
        print_header("DOOMFOLDER REPORT", 60)
        
        # Basic statistics
        print("\n📊 FOLDER STATISTICS:")
        print(f"  Location: {self.folder_path}")
        print(f"  Total Files: {len(self.files)}")
        print(f"  Total Size: {format_size_for_display(self.get_total_size())}")
        
        # Largest file
        largest = self.get_largest_file()
        if largest:
            print(f"  Largest File: {largest.name} ({largest.get_human_readable_size()})")
        
        # Find all categories
        print("\n🔍 FINDINGS:")
        
        # Duplicates
        duplicates = self.find_duplicates()
        if duplicates:
            total_duplicate_files = sum(len(files) for files in duplicates.values())
            duplicate_size = sum(
                sum(f.size for f in files) - files[0].size 
                for files in duplicates.values()
            )
            print(f"  🔁 Duplicate Groups: {len(duplicates)}")
            print(f"    Files: {total_duplicate_files}")
            print(f"    Wasted Space: {format_size_for_display(duplicate_size)}")
        else:
            print(f"  🔁 Duplicate Groups: 0")
        
        # Large files
        large_files = self.find_large_files(large_threshold)
        if large_files:
            large_size = sum(f.size for f in large_files)
            print(f"  📦 Large Files (>{format_size_for_display(large_threshold)}): {len(large_files)}")
            print(f"    Total Size: {format_size_for_display(large_size)}")
        else:
            print(f"  📦 Large Files: 0")
        
        # Old files
        old_files = self.find_old_files(old_threshold)
        if old_files:
            old_size = sum(f.size for f in old_files)
            print(f"  🕰️  Old Files (>{old_threshold} days): {len(old_files)}")
            print(f"    Total Size: {format_size_for_display(old_size)}")
        else:
            print(f"  🕰️  Old Files: 0")
        
        # Screenshots
        screenshots = self.find_screenshots()
        if screenshots:
            screenshot_size = sum(f.size for f in screenshots)
            print(f"  📸 Screenshots: {len(screenshots)}")
            print(f"    Total Size: {format_size_for_display(screenshot_size)}")
        else:
            print(f"  📸 Screenshots: 0")
        
        # Archives
        archives = self.find_archive_files()
        if archives:
            archive_size = sum(f.size for f in archives)
            print(f"  📦 Archive Files: {len(archives)}")
            print(f"    Total Size: {format_size_for_display(archive_size)}")
        else:
            print(f"  📦 Archive Files: 0")
        
        # File extensions
        print("\n📈 TOP FILE EXTENSIONS:")
        ext_sizes = self.get_size_by_extension()
        for i, (ext, size) in enumerate(list(ext_sizes.items())[:5], 1):
            ext_name = ext if ext else "no extension"
            count = self.get_file_count_by_extension().get(ext, 0)
            print(f"  {i}. {ext_name}: {count} files, {format_size_for_display(size)}")
        
        if self.errors:
            print(f"\n⚠️  {len(self.errors)} files could not be read.")
        
        print_separator(60)
        print()
    
    def print_summary(self) -> None:
        """
        Print quick summary statistics.
        
        Why this method exists:
        - Provides lightweight summary without full report
        - Shows key metrics at a glance
        """
        if not self.scan_complete:
            print("❌ Must run scan first!")
            return
        
        print(f"\n📁 {self.folder_path.name} Summary:")
        print(f"   Files: {len(self.files)}")
        print(f"   Total Size: {format_size_for_display(self.get_total_size())}")
        print()
