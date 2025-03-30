import uuid
import argparse
import json
import subprocess
import requests
import logging
import rich
from rich import print
from rich.prompt import Prompt
from rich.markup import escape
from rich.logging import RichHandler
from openai import OpenAI

# ---------- Init ---------- #

client = OpenAI()

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

logging.basicConfig(
    level=(logging.DEBUG if args.debug else logging.INFO),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)]
)

logger = logging.getLogger("rich")

# ---------- Simple Variables ---------- #

localVars = {}
taskList = {}
chatHistory = []
current_session_id = uuid.uuid4()

# ---------- Simple Functions ---------- #

def convertCommandsToText(available_commands):
    serializable_commands = []
    for cmd in available_commands:
        serializable_commands.append({
            "id": cmd["id"],
            "args": cmd["args"],
            "desc": cmd["desc"].strip()
        })
    return json.dumps(serializable_commands, indent=2, ensure_ascii=False)

# ---------- OpenAI API Functions ---------- #

def getOneResponse(chat_history, model_id):
    response = client.chat.completions.create(model=model_id,
    messages=chat_history)
    return response.choices[0].message.content

# ---------- Basic Commands ---------- #

def runPython(script, resultVar):
    exec(script, globals(), localVars)
    result = localVars.get(resultVar)
    globals().update(localVars)
    return result

def runShellCommand(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"stdout: \n{result.stdout}\n\nstderr: \n{result.stderr}"

def searchSearXNG(keyword):
    response = requests.get(f"http://localhost:8080/search?q={keyword}&format=json")
    return response.content

def visitWeb(url):
    response = requests.get(url)
    return response.content

def endChat():
    print("[green]Chat session ended. Goodbye![/green]")
    raise SystemExit()

# ---------- TaskList Commands ---------- #

def convertTaskListToText():
    formatted_text = "\n".join(
        f"# {task['name']}\n- id: {task_id}\n- name: {task['name']}\n- desc: {task['desc']}\n- isCompleted: {task['isCompleted']}\n"
        for task_id, task in taskList.items()
    )
    return formatted_text

def showTaskList():
    print()
    print()
    for task_id, task in taskList.items():
        print("[blue]Task Status[/bold]")
        print()
        if task['isCompleted'] == "False":
            print(f"[red]# --- {task['name']} --- #[/red]")
        else:
            print(f"[green]# --- {task['name']} --- #[/green]")
        print(f"{task['desc']}")
        print()

def addTask(id, name, desc):
    taskList[id] = {"name": name, "desc": desc, "isCompleted": "False"}
    showTaskList()
    return "Done!"

def listTasks():
    return convertTaskListToText()

def completeTask(id):
    if id in taskList:
        taskList[id]["isCompleted"] = "True"
        showTaskList()
        return f"Done!"
    else:
        return f"Error: Task '{id}' not found."

def clearTasks():
    taskList.clear()
    return "Done!"

# ---------- Parser ---------- #

def parse_agent_code(response):
    lines = response.splitlines()
    in_block = False
    commands = []
    current_command = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "!AgentCode start":
            in_block = True
            i += 1
            continue
        if line == "!AgentCode end":
            in_block = False
            i += 1
            continue
        if in_block:
            if line.startswith("!") and not line.startswith("!!"):
                if current_command:
                    commands.append(current_command)
                command_id = line[1:].strip()
                current_command = {"id": command_id, "args": {}}
                i += 1
                continue
            elif line.startswith("!!"):
                if current_command is None:
                    i += 1
                    continue
                header = line[2:]
                if ":" not in header:
                    i += 1
                    continue
                header_parts = header.split(":", 1)
                cmd_id = header_parts[0].strip()
                arg_name = header_parts[1].strip()
                arg_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() != "!!":
                    arg_lines.append(lines[i])
                    i += 1
                i += 1
                arg_value = "\n".join(arg_lines).strip()
                current_command["args"][arg_name] = arg_value
                continue
            else:
                i += 1
                continue
        else:
            i += 1
    if current_command:
        commands.append(current_command)
    return commands

# ---------- Main Functions ---------- #

def getResponseWithAgentCode(chat_history, model_id, available_commands):
    global current_session_id

    chat_history_local = [
        {
            "role": "system",
            "content": f"""
You are an excellent assistant.
Your name is "NextLLA".
You can use AgentCode to access various functionalities.

# About AgentCode

Using AgentCode is simple.  
All you have to do is say something like the following in your response:

```
!AgentCode start
!runPython  
!!runPython:content  
result1 = len("Hello, World!")  
!!  
!!runPython:resultVar  
result1  
!!  
!AgentCode end  
```

```
!AgentCode start
!runShellCommand  
!!runShellCommand:command  
echo 1 + 1
!!
!AgentCode end  
```

- `!AgentCode start`: Start AgentCode
- `!<commandName>`: Set AgentCode Command for Execute
- `!!<commandName>:<argID>`: Set argID for following Content
- `!!`: End of that Arg.
- `!AgentCode end`: End AgentCode

After saying this, you should end your response.  
Once your response ends, the system (role) will report the result back to you.  

Below is a list of available AgentCode commands:

```
{convertCommandsToText(available_commands)}
```

Current Session ID: {current_session_id}
"""
        }
    ] + chat_history

    responseFromGPT = getOneResponse(chat_history_local, model_id)
    chatHistory.append({"role": "assistant", "content": responseFromGPT})

    return responseFromGPT

def sub(chat_history, model_id, available_commands):
    global current_session_id

    responseFromGPT = getResponseWithAgentCode(chat_history, model_id, available_commands)

    commands = parse_agent_code(responseFromGPT)
    available_commands_by_id = {cmd["id"]: cmd for cmd in available_commands}

    if 0 < len(commands):

        for command in commands:
            cmd_id = command["id"]
            if cmd_id in available_commands_by_id:
                action_func = available_commands_by_id[cmd_id]["action"]
                try:

                    print("\n[bold yellow]🛠️ AgentCode Execution Request[/bold yellow]")
                    print(f"Session ID: [cyan]{current_session_id}[/cyan]")
                    print(f"Command ID: [blue bold]{cmd_id}[/blue bold]")
                    print("\n[bold]📘 Description:[/bold]")
                    print(f"[dim]{available_commands_by_id[cmd_id]['desc'].strip()}[/dim]")
                    print("\n[bold]📦 Arguments:[/bold]")
                    print(f"[white]{escape(json.dumps(command['args'], indent=2, ensure_ascii=False))}[/white]")


                    userConfirm = Prompt.ask("Are you OK", default="y", choices=["y", "n"])
                    if userConfirm == "y":
                        result = action_func(**command["args"])
                        chatHistory.append({"role": "system", "content": f"AgentCode Session ID {current_session_id} EXECUTED '{cmd_id}'. \nResult: '''{repr(result)}'''"})
                        logger.info(f"[bold blue]AgentCode Session ID {current_session_id} has EXECUTED[/bold blue] {cmd_id}\nArgs: {command['args']}\nResult: '''{repr(result)}'''")
                    else:
                        raise RuntimeError("Sorry, the user refused to run.")

                except Exception as e:
                    chatHistory.append({"role": "system", "content": f"AgentCode Session ID {current_session_id} EXECUTED '{cmd_id}'\nError: '''{e}'''"})
                    escaped_args = escape(str(command['args']))
                    escaped_error = escape(str(e))
                    logger.info(f"[bold red]AgentCode Session ID {current_session_id} has EXECUTED[/bold red] {cmd_id}\nArgs: {escaped_args}\nError: '''{escaped_error}'''")
            else:
                chatHistory.append({"role": "system", "content": f"UNKNOWN COMMAND: '{cmd_id}'"})
        
        sub(chatHistory, model_id, available_commands)
    
    else:
        print(responseFromGPT)

    current_session_id = uuid.uuid4()

# ---------- Main Variables ---------- #

availableCommands = [

    # runPython
    {
        "id": "runPython",
        "args": [
            "content",
            "resultVar"
        ],
        "desc": """
Execute Python Script.
You should save the result in a variable of your choice within your script.

Arguments:
- content: Python Script
- resultVar: Variable Name of Saved Result Data

Output:
- Content of resultVar
""",
        "action": runPython
    },

    # runShellCommand
    {
        "id": "runShellCommand",
        "args": [
            "command"
        ],
        "desc": """
Execute a shell command.
This command will run the provided shell command and return its standard output.

Arguments:
- command: The shell command to execute as a string.

Output:
- Standard output of the shell command execution.
""",
        "action": runShellCommand
    },

    # addTask
    {
        "id": "addTask",
        "args": [
            "id",
            "name",
            "desc"
        ],
        "desc": """
Add Task to Task List.

Arguments:
- id: Task ID.
- name: Task Name
- desc: Task Description

Output: None
""",
        "action": addTask
    },

    # listTasks
    {
        "id": "listTasks",
        "args": [],
        "desc": """
Show Task List.

Output:
- Task List
""",
        "action": listTasks
    },

    # completeTask
    {
        "id": "completeTask",
        "args": [
            "id"
        ],
        "desc": """
Complete a Task.

Arguments:
- id: Task ID.
""",
        "action": completeTask
    },

    # clearTasks
    {
        "id": "clearTasks",
        "args": [],
        "desc": """
Clear the Task List.
""",
        "action": clearTasks
    },

    {
        "id": "searchWeb",
        "args": [
            "keyword"
        ],
        "desc": """
Search Web

Arguments:
- keyword: Keyword

Output:
- result: Search Result (JSON)
""",
        "action": searchSearXNG
    },

    {
        "id": "visitWeb",
        "args": [
            "url"
        ],
        "desc": """
Visit Website

Arguments:
- url: URL

Output:
- result: HTML Response
""",
        "action": visitWeb
    },

    # endChat
    {
        "id": "endChat",
        "args": [],
        "desc": """
End this Chat.
""",
        "action": endChat
    }
]

# ---------- Main ---------- #

if __name__ == "__main__":
    model_id = Prompt.ask("OpenAI Model ID", default="gpt-4o-mini")
    while True:
        prompt = input(">>> ")
        chatHistory.append({"role": "user", "content": prompt})
        sub(chatHistory, model_id, availableCommands)
