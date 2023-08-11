import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import filedialog
import time

def extract_method_name(text):
    parts = text.split('.')
    if len(parts) > 1:
        return parts[-1]
    return text
    
# Function to initialize the Chrome browser
def initialize_browser():
    return webdriver.Chrome()

# Function to get the span element corresponding to a variable
def get_span_element(driver, variable, version):
    prefix = variable[:2]  # Get the prefix (e.g., 'f_', 'm_', 'c_')
    allow_classes = "false"
    allow_methods = "false"
    allow_fields = "false"
    
    if prefix == 'f_':
        allow_fields = "true"
    elif prefix == 'm_':
        allow_methods = "true"
    elif prefix == 'c_':
        allow_classes = "true"
    
    url = f"https://linkie.shedaniel.dev/mappings?namespace=mojang_srg&version={version}&search={variable}" \
          f"&allowClasses={allow_classes}&allowMethods={allow_methods}&allowFields={allow_fields}"
    print(url)
    driver.get(url)
    driver.implicitly_wait(100)
    time.sleep(5)
    try:
        span_element = driver.find_element(By.CSS_SELECTOR, "span[data-v-1345ea4a]")
        return extract_method_name(span_element.text)
    except:
        return None

# Function to process .java files in a directory
def process_files(root_directory, driver, version):
    span_elements = {}
    total_files = sum(1 for root, dirs, files in os.walk(root_directory) for file in files if file.endswith(".java"))
    for idx, (root, dirs, files) in enumerate(os.walk(root_directory)):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as java_file:
                    lines = []
                    for line in java_file:
                        new_line = replace_variables(line, driver, span_elements, version)
                        lines.append(new_line)
                        print(new_line)  # Print for debugging
                        
                # Write the modified lines to the file
                with open(file_path, "w", encoding="utf-8") as modified_file:
                    modified_file.writelines(lines)
                    print(f"File {file} updated. ({idx + 1}/{total_files})")
                    
                    # Display progress percentage in the window title
                    progress_percentage = int((idx + 1) / total_files * 100)
                    os.system(f"title BON3 Progress : {progress_percentage}%")


# Function to replace variables with corresponding span elements
def replace_variables(line, driver, span_elements, version):
    variables = re.findall(r'\b([mf]_\w+_)', line)
    for variable in variables:
        if variable not in span_elements:
            span_text = get_span_element(driver, variable, version)
            if span_text is not None:
                span_elements[variable] = span_text
                print(f"Obf variable {variable} - Mapped variable : {span_text}")
    
    for variable, span_text in span_elements.items():
        line = line.replace(variable, span_text)
    return line

# Main function
def main():
    os.system("title BON3")
    root = tk.Tk()
    root.withdraw()

    root_directory = filedialog.askdirectory(title="Select the root directory")

    if not root_directory:
        print("No directory selected. The program is exiting.")
        return

    driver = initialize_browser()
    version = input("Enter the game version (in x.y.z format): ")

    # Check if the version is in correct format (digits and dots)
    if not re.match(r'^\d+(\.\d+)+$', version):
        print("Version format is not valid. Please enter a version in x.y.z format.")
        return
        
    process_files(root_directory, driver, version)
    driver.quit()

if __name__ == "__main__":
    main()
