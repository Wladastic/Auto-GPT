import os
import openai
import json
from typing import List

# Replace this with your OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")

# Initialize the OpenAI API client
openai.api_key = api_key



def split_code_into_chunks(code: str, max_tokens_per_chunk: int) -> List[str]:
    indentation_levels = [0]
    lines = code.split("\n")
    chunks = []
    current_chunk = ""
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if len(current_chunk) + len(line) > max_tokens_per_chunk:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"
        if stripped_line and (len(line) - len(stripped_line)) <= indentation_levels[-1] if indentation_levels else 0:
            indentation_levels.pop()
        indentation_levels.append(len(line) - len(stripped_line))
    chunks.append(current_chunk)

    # Remove any empty chunks
    chunks = [chunk for chunk in chunks if chunk.strip()]

    # Merge consecutive chunks if they are shorter than the maximum token length
    merged_chunks = []
    current_chunk = chunks[0]
    for chunk in chunks[1:]:
        if len(current_chunk) + len(chunk) <= max_tokens_per_chunk:
            current_chunk += chunk
        else:
            merged_chunks.append(current_chunk.strip())
            current_chunk = chunk
    merged_chunks.append(current_chunk.strip())

    return merged_chunks


def generate_code_summary(code: str) -> str:
    # Split the code into smaller chunks to avoid exceeding the token limit
    if len(code) > 4000:
        chunks = split_code_into_chunks(code, max_tokens_per_chunk=4000)
    else:
        chunks = [code]

    # Generate a summary for each chunk
    summaries = []
    for chunk in chunks:
        prompt = f"Please provide a summary of the following Python code:\n\n{chunk}\n\nSummary: "
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.5,
        )
        summary = response.choices[0].text.strip()
        summaries.append(summary)

    # Join the summaries into a single string
    return "\n\n".join(summaries)


def ask_model_which_files_to_summarize(files: list) -> list:
    important_files = []
    file_chunks = [files[i : i + 50] for i in range(0, len(files), 50)]

    for chunk in file_chunks:
        print(f"Summarzing the following files: {chunk}")
        print(f"Progress: {len(important_files)}/{len(files)}")
        file_list = "\n".join(chunk)
        prompt = f"I am currently working on Auto-GPT, which is a python project and want to summarize it's core functionality. Given the following list of files, which ones are important to summarize first?\n\n{file_list}\n\nImportant files: "

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.5,
        )

        important_files_text = response.choices[0].text.strip()
        important_files.extend(important_files_text.split("\n"))

    return important_files

def initialize_progress():
    progress = {
        "important_files": [],
        "processed_files": [],
        "summaries": {},
    }
    return progress

def load_or_initialize_progress(progress_file: str):
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            content = f.read()
            if content:
                progress = json.loads(content)
                return progress
    progress = initialize_progress()
    save_progress(progress, progress_file)
    return progress


def save_progress(progress, progress_file):
    with open(progress_file, "w") as file:
        json.dump(progress, file)


def load_summary_output(summary_output_file):
    if os.path.exists(summary_output_file):
        with open(summary_output_file, "r") as file:
            summary_output = json.load(file)
    else:
        summary_output = {}
    return summary_output


def save_summary_output(summary_output, summary_output_file):
    with open(summary_output_file, "w") as file:
        json.dump(summary_output, file)


def summarize_directory_files(directory: str):
    progress_file = "progress.json"
    summary_output_file = "summary_output.json"
    progress = load_or_initialize_progress(progress_file)
    summary_output = load_summary_output(summary_output_file)

    all_files = []

    if not progress["important_files"]:
        print("Getting all files in directory")
        for root, _, files in os.walk(directory):
            for file in files:
                if file != os.path.basename(__file__):
                    file_path = os.path.join(root, file)
                    # check if file is a python file or inside .git
                    if file_path.endswith(".py") and ".git" not in file_path:
                        all_files.append(file_path)
    else:
        print("Found important files in progress")
        all_files = progress["important_files"]

    if not progress["important_files"]:
        print("Asking model which files to summarize")
        important_files = ask_model_which_files_to_summarize(all_files)
        progress["important_files"] = important_files
        save_progress(progress, progress_file)
        print(f"Important files: {important_files}")
    else:
        print("Using important files from progress")
        important_files = [
            file for file in all_files if file not in progress["processed_files"]
        ]
        print(f"Important files: {important_files}")

    for file_path in important_files:
        file_path = file_path.strip()
        if file_path in progress["processed_files"]:
            print(f"Skipping {file_path} because it was already processed")
            continue
        print(f"Processing {file_path}")
        with open(file_path, "r") as f:
            code = f.read()
        summary = generate_code_summary(code)
        summary_output[file_path] = summary
        progress["processed_files"].append(file_path)
        save_progress(progress, progress_file)
        save_summary_output(summary_output, summary_output_file)
    with open("summary_output.txt", "w") as summary_output_txt:
        for file_path, summary in summary_output.items():
            summary_output_txt.write(f"Summary for {file_path}:\n")
            summary_output_txt.write(summary + "\n\n")


if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    summarize_directory_files(current_directory)
