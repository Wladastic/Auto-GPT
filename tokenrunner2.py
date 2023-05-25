import ast
import collections
import os

# Define the directory containing your Python projects
directory = "."

# Initialize a counter to count the occurrences of each sequence
counter = collections.Counter()

# Iterate over each file in the directory
for filename in os.listdir(directory):
    # Only process .py files
    if filename.endswith(".py"):
        with open(os.path.join(directory, filename), "r") as file:
            # Read the file content
            content = file.read()

            # Parse the content into an AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue  # Skip files that cause a SyntaxError

            # Tokenize the AST into sequences of four nodes
            nodes = list(ast.walk(tree))
            tokens = [tuple(nodes[i : i + 4]) for i in range(len(nodes) - 3)]

            # Update the counter with the new tokens
            counter.update(tokens)

# Find the most common tokens
most_common_tokens = counter.most_common()

# Create a mapping from four-digit keys to the most common tokens
key_to_token = {
    str(i).zfill(4): token for i, (token, count) in enumerate(most_common_tokens)
}

# Write the mapping to a text file
with open("key_to_token.txt", "w") as f:
    for key, token in key_to_token.items():
        f.write(f"{key}: {str(token)}\n")
