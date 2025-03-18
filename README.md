# NextLLA
(Next Large Language Agent) A cutting-edge AI agent built for gpt-4o-mini

## Warning
Please read the following before use:
- NextLLA is based on the concept of "Agent", where GPT controls a computer by itself.
- This can also happen if GPT tries to execute a command that it doesn't expect.
- We recommend using a virtual environment when possible as it gives you more control over the computer.
- This technology is still under development and I take no responsibility for any damage that may occur. Use at your own risk.
- NextLLA can execute shell commands and in some environments can use root privileges (also known as superuser).

## How
GPT alone cannot execute code.

In reality, it needs to communicate with the outside world, but GPT itself is just an LLM.

However, if you think about it, GPT can communicate in text.

By including commands from GPT in that communication and having the script execute them, GPT will essentially execute the code.

In NextLLA, you instruct GPT how to execute the code and what type of code to use in a system prompt beforehand.

For this, we use the AgentCode system.

NextLLA has additional AgentCode functions and an easier-to-read screen.

## Search Engine
By default, SearXNG is supported as a search function.

If you want to disable AgentCode functions such as searching with SearXNG, change the content of the "availableCommands" variable at the end of the script.

## About API Key
NextLLA uses the OpenAI API to call GPT.

Please set your API key to the "OPENAI_API_KEY" item in your shell environment variables.

You can issue an API key after signing up on https://platform.openai.com/.

NextLLA will stop working if you exceed the free space available in your API key.

## Cledit
- GPT Model Access with OpenAI Official API (using [Official Python Library](https://github.com/openai/openai-python)), by [OpenAI](https://openai.com/ja-JP/)
- The concept of "agent", by AI/ML Researcher
- [AgentCode](https://github.com/DiamondGotCat/AgentGPT) by [DiamondGotCat](https://github.com/DiamondGotCat)
- Support by Everyone
