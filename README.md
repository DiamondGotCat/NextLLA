# NextLLA
(Next Large Language Agent) A cutting-edge AI agent built for gpt-4o-mini

## NEW: NextLLAKit has Released!
[Here!](https://github.com/DiamondGotCat/NextLLAKit)

## Warning
Please read the following before use:
- NextLLA is based on the concept of "Agent", where LLM controls a computer by itself.
- This can also happen if LLM tries to execute a command that it doesn't expect.
- We recommend using a virtual environment when possible as it gives you more control over the computer.
- This technology is still under development and I take no responsibility for any damage that may occur. Use at your own risk.
- NextLLA can execute shell commands and in some environments can use root privileges (also known as superuser).

## Dependencies
- `requests` (PyPI)
- `rich` (PyPI)
- `openai` or `ollama` (PyPI)

## Safety
Given the structure in which LLM operates computers, we cannot guarantee its safety.
However, in a recent commit, a system has been added that asks for permission from the user when LLM attempts to perform an operation.
We believe this makes it even safer to use, but please continue to use it at your own risk.

## How
LLM alone cannot execute code.

In reality, it needs to communicate with the outside world, but LLM itself is just an Large Language Model.

However, if you think about it, LLM can communicate in text.

By including commands from LLM in that communication and having the script execute them, LLM will essentially execute the code.

In NextLLA, you instruct LLM how to execute the code and what type of code to use in a system prompt beforehand.

For this, we use the AgentCode system.

NextLLA has additional AgentCode functions and an easier-to-read screen.

## Search Engine
By default, SearXNG is supported as a search function.

If you want to disable AgentCode functions such as searching with SearXNG, change the content of the "availableCommands" variable at the end of the script.

## About OpenAI API Key
in the `openai.py` (OpenAI API Version), NextLLA uses the OpenAI API to call GPT

Please set your API key to the "OPENAI_API_KEY" item in your shell environment variables.

You can issue an API key after signing up on https://platform.openai.com/.

NextLLA will stop working if you exceed the free space available in your API key.

## Cledit
- GPT Model Access with OpenAI Official API (using [Official Python Library](https://github.com/openai/openai-python)), by [OpenAI](https://openai.com)
- Ollama Model Access with Ollama Official API (using [Official Python Library](https://github.com/ollama/ollama-python)), by [Ollama](https://ollama.com)
- The concept of "agent", by AI/ML Researcher
- [AgentCode](https://github.com/DiamondGotCat/AgentGPT) by [DiamondGotCat](https://github.com/DiamondGotCat)
- Support by Everyone
