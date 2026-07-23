"""
FileInfo Module
This module defines the FileInfo class which represents metadata about a single file.
"""

from pathlib import Path
from datetime import datetime
import os


class FileInfo:
    def __init__(self, file_path: Path) -> None:
        #Initialize FileInfo by reading file metadata from disk.
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.path: Path = file_path
        self.name: str = file_path.name
        self.extension: str = file_path.suffix.lower()
        
        # Use os.path.getsize() as fallback for compatibility
        # pathlib.stat() is preferred but os gives us redundancy
        try:
            self.size: int = file_path.stat().st_size
        except (OSError, PermissionError):
            self.size: int = 0
        
        # Get modification time as datetime object
        try:
            mod_timestamp = file_path.stat().st_mtime
            self.modified_date: datetime = datetime.fromtimestamp(mod_timestamp)
        except (OSError, PermissionError):
            self.modified_date: datetime = datetime.now()
    
    def get_size_mb(self) -> float:
        #Convert file size from bytes to megabytes.
        return round(self.size / (1024 * 1024), 2)
    
    def get_size_gb(self) -> float:
       # Convert file size from bytes to gigabytes.
        return round(self.size / (1024 * 1024 * 1024), 2)
    
    def get_human_readable_size(self) -> str:
        #Return size in most appropriate unit (B, KB, MB, GB).
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                if unit == 'B':
                    return f"{int(size)} {unit}"
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def get_age_days(self) -> int:
        #Calculate how many days since file was last modified.
        age = datetime.now() - self.modified_date
        return age.days
    
    def display(self) -> str:
        return (
            f"📄 {self.name}\n"
            f"   Path: {self.path}\n"
            f"   Size: {self.get_human_readable_size()}\n"
            f"   Modified: {self.modified_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"   Age: {self.get_age_days()} days"
        )
    
    def __repr__(self) -> str:
        return f"FileInfo(name={self.name}, size={self.get_human_readable_size()})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileInfo):
            return False
        return self.path == other.path
    
    def __lt__(self, other: 'FileInfo') -> bool:
        return self.size < other.size
