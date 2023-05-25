import os

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class AI:
    def __init__(self):
        self.requests = []
        self.messages = []

    def request_shell_command(self, command):
        self.requests.append(("shell_command", command))

    def request_write_file(self, filename, content):
        self.requests.append(("write_file", filename, content))

    def get_requests(self):
        return self.requests

    def send_prompt(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )
        self.messages.append(
            {
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }
        )
        return response["choices"][0]["message"]["content"]


class User:
    def __init__(self, ai):
        self.ai = ai

    def review_requests(self):
        for request in self.ai.get_requests():
            action, *args = request
            if action == "shell_command":
                command = args[0]
                print(f"The AI wants to execute the following shell command: {command}")
                if input("Do you approve? (yes/no, default: yes) ") in ["yes", ""]:
                    os.system(command)
            elif action == "write_file":
                filename, content = args
                print(
                    f"The AI wants to write the following content to {filename}: {content}"
                )
                if input("Do you approve? (yes/no, default: yes) ") in ["yes", ""]:
                    with open(filename, "w") as f:
                        f.write(content)


def main():
    ai = AI()
    user = User(ai)

    # The AI makes some requests
    task = "I want you to create a better version of yourself. Your filename is './mando-ai2.py'"

    while True:
        run(task, ai, user)


def run(task, ai, user):
    # The AI sends a prompt to GPT-3
    response = ai.send_prompt(
        "You are receiving this prompt from Jarvis Ai, a programm that reads your responses and executes them inside a windows cmd shell. Please help me with the task: "
        + task
        + ". Only respond with a shell command."
    )
    print("GPT-3's response: ", response)

    # The AI makes a request based on the response
    ai.request_shell_command(response)

    # The user reviews the new request
    user.review_requests()


if __name__ == "__main__":
    main()
