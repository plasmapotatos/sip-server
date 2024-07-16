import re

def get_titles_from_input(input_text):
    # Extract titles from the input text
    titles = []
    for line in input_text.strip().split('\n'):
        title = re.split(' - Authors:', line)[0].strip()
        titles.append(title)
    return titles

def get_titles_from_bib(file_path):
    # Extract titles from the .bib file
    with open(file_path, 'r') as file:
        bib_data = file.read()
    return re.findall(r'title = {([^}]+)}', bib_data)

def main():
    input_text = input("Enter the input titles and authors:\n")
    bib_file_path = input("Enter the path to the .bib file:\n")

    input_titles = get_titles_from_input(input_text)
    bib_titles = get_titles_from_bib(bib_file_path)

    # Check for titles not found in the .bib file
    not_found_titles = [title for title in input_titles if title not in bib_titles]

    # Print the titles that are not found
    if not_found_titles:
        print("Titles not found in the .bib file:")
        for title in not_found_titles:
            print(title)
    else:
        print("All titles were found in the .bib file.")

if __name__ == "__main__":
    main()
