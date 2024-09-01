# Open the file in read mode
with open('../data/word_list_4000.txt', 'r') as file:
    lines = file.readlines()

# Open a new file in write mode to save the filtered words
with open('../data/filtered_words.txt', 'w') as file:
    for line in lines:
        # Check if the line contains a colon
        if ':' in line:
            # Split the line at the colon and take the first part (the word)
            word = line.split(':')[0].strip()
            # Write the word to the new file
            file.write(word + '\n')
