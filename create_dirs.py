import os
import yaml

def create_tree(base_path, structure):
    """
    Recursively creates directories based on a dictionary structure.
    """
    for folder_name, subfolders in structure.items():
        # Join the current path with the new folder name
        path = os.path.join(base_path, folder_name)
        
        # Create the directory
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")
        
        # If there are subfolders (a nested dictionary), recurse
        if isinstance(subfolders, dict):
            create_tree(path, subfolders)

def main():
    # Load the YAML configuration
    try:
        with open("dirs.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Start creating from the current directory
        create_tree(".", config)
        print("\nTree creation successful!")
        
    except FileNotFoundError:
        print("Error: dirs.yaml not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
