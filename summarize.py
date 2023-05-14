import os

import openai

# Replace this with your OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")

# Initialize the OpenAI API client
openai.api_key = api_key


def generate_code_summary(code: str) -> str:
    prompt = (
        f"Please provide a summary of the following Python code:\n\n{code}\n\nSummary: "
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    )

    summary = response.choices[0].text.strip()
    return summary


def ask_model_which_files_to_summarize(files: list) -> list:
    file_list = "\n".join(files)
    prompt = f"Given the following list of Python files, which ones are important to summarize?\n\n{file_list}\n\nImportant files: "

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    )

    important_files_text = response.choices[0].text.strip()
    important_files = important_files_text.split("\n")
    return important_files


def summarize_directory_files(directory: str):
    print("Gathering Python files...")
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != os.path.basename(__file__):
                file_path = os.path.join(root, file)
                python_files.append(file_path)

    print("Asking the model which files to summarize...")
    important_files = ask_model_which_files_to_summarize(python_files)

    print("Generating summaries for important files...")
    for file_path in important_files:
        with open(file_path.strip(), "r") as f:
            code = f.read()
        summary = generate_code_summary(code)
        print(f"Summary for {file_path}:")
        print(summary)
        print()


if __name__ == "__main__":
    print("Script started.")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    summarize_directory_files(current_directory)
    print("Script finished.")
