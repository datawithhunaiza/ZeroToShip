# DoomFolder - CLI Storage Analyzer

A Python command-line tool to analyze and understand disk storage usage without deleting files. Written to demonstrate Object-Oriented Programming (OOP) principles using only Python standard library.

## Project Overview

DoomFolder scans your folders (Downloads, Desktop, Documents, etc.) and provides detailed analysis:
- **Large Files** - Find files consuming the most space
- **Duplicate Files** - Identify wasted space from copies
- **Old Files** - Locate files not accessed in months
- **Screenshots** - Find cluttering screenshot files
- **Archive Files** - Locate compressed archives
- **Detailed Reports** - Get comprehensive statistics

**Safety First:** DoomFolder never deletes files. It only analyzes and reports.

## Features

### 1. Folder Scanning
- Recursively scans all subfolders
- Validates folder existence and permissions
- Shows progress during scanning
- Handles permission errors gracefully

### 2. Large File Detection
- Find files larger than configurable threshold
- Default threshold: 100 MB
- Shows total space used by large files
- Lists files sorted by size

### 3. Duplicate File Detection
- Uses SHA-256 hashing to find identical files
- Efficient chunked reading for large files
- Shows wasted space from duplicates
- Groups identical files together
- Example: 3 copies of 50MB file = 100MB wasted

### 4. Old File Detection
- Finds files not modified in N days
- Default threshold: 180 days
- Shows file age and last modified date
- Useful for archival or cleanup

### 5. Screenshot Detection
- Identifies screenshots by filename patterns
- Case-insensitive pattern matching
- Recognizes: "Screenshot", "Screen Shot", "screen_capture", etc.
- Shows total screenshot storage

### 6. Archive Detection
- Identifies: .zip, .rar, .7z, .tar, .gz, .bz2, .xz, .iso
- Lists all compressed archives
- Shows total archive storage

### 7. Reporting
- Summary statistics
- File extension analysis
- Top extensions by count and size
- Wasted space calculations
- Error reporting

**NOTE:** DoomFolder never deletes files. Always review recommendations before taking action.