import collections
import os
import re

# Define the directory containing your Python projects
directory = "."

# Initialize a counter to count the occurrences of each sequence
counter = collections.Counter()

# Iterate over each file in the directory and its subdirectories
for root, dirs, files in os.walk(directory):
    for filename in files:
        # Only process .py files
        if filename.endswith(".py"):
            try:
                with open(os.path.join(root, filename), "r", errors="ignore") as file:
                    # Read the file content
                    content = file.read()

                    # Tokenize the content at each whitespace character
                    tokens = re.split(r"\s+", content)

                    # Filter out empty tokens
                    tokens = [token for token in tokens if token]

                    # Generate sequences of four tokens
                    sequences = [
                        tuple(tokens[i : i + 4]) for i in range(len(tokens) - 3)
                    ]

                    # Update the counter with the new sequences
                    counter.update(sequences)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

# Find the most common sequences
most_common_sequences = counter.most_common()

# Filter out sequences that don't appear very often
most_common_sequences = [
    (sequence, count) for sequence, count in most_common_sequences if count > 10
]

# Create a mapping from four-digit keys to the most common sequences
key_to_sequence = {
    str(i).zfill(4): sequence
    for i, (sequence, count) in enumerate(most_common_sequences)
}

# Write the mapping to a text file
with open("key_to_sequence.txt", "w") as f:
    for key, sequence in key_to_sequence.items():
        f.write(f"{key}: {str(sequence)}\n")
