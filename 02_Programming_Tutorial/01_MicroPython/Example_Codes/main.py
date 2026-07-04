"""
This is a Python script executor that will:
    1. Scan all files in the current directory
    2. Skip the boot.py and main.py files
    3. Only execute files with .py extensions
    4. Ensure only files are executed (not directories)
"""
#!/opt/bin/lv_micropython
# Import MicroPython specific modules
import uos as os           # MicroPython's os module 
import uerrno as errno     # MicroPython's errno module

# Get directory iterator for listing files in current directory
# os.ilistdir() returns an iterator of directory entries
iter = os.ilistdir()

# File type constants for directory entries
# These constants come from stat
# module but MicroPython uses different approach
IS_DIR = 0x4000      # Flag indicating the entry is a directory
IS_REGULAR = 0x8000  # Flag indicating the entry is a regular file

# Main loop: Process each entry in the directory
while True:
    try:
        # Get next directory entry using iterator
        # Each entry is a tuple: (name, type, inode[, size])
        entry = next(iter)
        
        # Extract filename (first element of tuple)
        filename = entry[0]
        
        # Extract file type (second element of tuple)
        # This indicates if it's a file, directory, etc.
        file_type = entry[1]
        
        # Skip system files that should not be executed
        # boot.py: Runs on boot, should not be executed manually
        # main.py: Main application file, should be run separately
        if filename == 'boot.py' or filename == 'main.py':
            continue  # Skip to next file
            
        else:
            # Print separator for visual clarity in output
            print("===============================")
            
            # Print filename without newline (end="")
            print(filename, end="")
            
            # Check if current entry is a directory
            if file_type == IS_DIR:
                print(", File is a directory")
                print("===============================")
                # Note: Directories are only identified, not processed further
                
            else:
                # For regular files, just close the filename line
                print("\n===============================")
                
                # Originally commented code that would print file contents:
                # print("Contents:")
                # with open(filename) as f:
                #    for line in enumerate(f):
                #        print("{}".format(line[1]),end="")
                # print("")
                
                # Actually execute the Python file
                # exec() runs the code in the file with global context
                # open(filename).read() reads the entire file content
                # globals() provides the current global
                # namespace to the executed code
                exec(open(filename).read(), globals())
                
    # StopIteration exception is raised when iterator has no more items
    except StopIteration:
        break  # Exit the infinite while loop
    