# OpenManus Technical Architecture

OpenManus is a comprehensive, open-source framework for building general-purpose AI agents. This document provides a detailed technical overview of the system architecture, components, and their interactions.

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Agent Architecture](#agent-architecture)
4. [Tool Framework](#tool-framework)
5. [Flow Management](#flow-management)
6. [LLM Integration](#llm-integration)
7. [MCP Protocol Support](#mcp-protocol-support)
8. [Configuration System](#configuration-system)
9. [Execution Patterns](#execution-patterns)
10. [Data Flow](#data-flow)

## System Overview

OpenManus is built on a modular architecture that separates concerns into distinct layers:

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[User Input]
        CLI[Command Line Interface]
    end
    
    subgraph "Application Layer"
        MAIN[main.py]
        FLOW[run_flow.py]
        MCP[run_mcp.py]
    end
    
    subgraph "Agent Layer"
        MANUS[Manus Agent]
        SWE[SWE Agent]
        BROWSER[Browser Agent]
        DATA[Data Analysis Agent]
    end
    
    subgraph "Tool Layer"
        PYTHON[Python Execute]
        BROWSER_TOOL[Browser Use Tool]
        FILE[File Operations]
        SEARCH[Web Search]
        MCP_TOOLS[MCP Tools]
    end
    
    subgraph "Infrastructure Layer"
        LLM[LLM Providers]
        CONFIG[Configuration]
        MEMORY[Memory System]
        SANDBOX[Sandbox Environment]
    end
    
    UI --> CLI
    CLI --> MAIN
    CLI --> FLOW
    CLI --> MCP
    
    MAIN --> MANUS
    FLOW --> MANUS
    FLOW --> SWE
    FLOW --> BROWSER
    FLOW --> DATA
    MCP --> MANUS
    
    MANUS --> PYTHON
    MANUS --> BROWSER_TOOL
    MANUS --> FILE
    MANUS --> SEARCH
    MANUS --> MCP_TOOLS
    
    SWE --> FILE
    SWE --> PYTHON
    BROWSER --> BROWSER_TOOL
    DATA --> PYTHON
    DATA --> FILE
    
    PYTHON --> SANDBOX
    BROWSER_TOOL --> LLM
    FILE --> CONFIG
    SEARCH --> CONFIG
    MCP_TOOLS --> CONFIG
    
    MANUS --> LLM
    SWE --> LLM
    BROWSER --> LLM
    DATA --> LLM
    
    MANUS --> MEMORY
    SWE --> MEMORY
    BROWSER --> MEMORY
    DATA --> MEMORY
```

## Core Components

### 1. Agent System

The agent system is the central orchestrator of OpenManus, built on a hierarchical class structure:

```mermaid
classDiagram
    class BaseAgent {
        +string name
        +string description
        +LLM llm
        +Memory memory
        +AgentState state
        +int max_steps
        +run(prompt) Promise
        +step() Promise
        +cleanup() Promise
    }
    
    class ToolCallAgent {
        +ToolCollection available_tools
        +list special_tool_names
        +execute_tool(tool_call) Promise
        +get_tool_output() string
    }
    
    class Manus {
        +MCPClients mcp_clients
        +BrowserContextHelper browser_context
        +Dict connected_servers
        +connect_mcp_server(url) Promise
        +disconnect_mcp_server(id) Promise
    }
    
    class SWEAgent {
        +string workspace_root
        +list allowed_tools
        +validate_file_operation() bool
    }
    
    class BrowserAgent {
        +BrowserController controller
        +handle_browser_action() Promise
    }
    
    class DataAnalysisAgent {
        +ChartVisualization chart_tool
        +analyze_data() Promise
        +create_visualization() Promise
    }
    
    BaseAgent <|-- ToolCallAgent
    ToolCallAgent <|-- Manus
    ToolCallAgent <|-- SWEAgent
    ToolCallAgent <|-- BrowserAgent
    ToolCallAgent <|-- DataAnalysisAgent
```

### 2. Tool Framework

Tools provide specific capabilities to agents through a standardized interface:

```mermaid
classDiagram
    class BaseTool {
        +string name
        +string description
        +dict parameters
        +execute(**kwargs) Promise
        +to_param() Dict
    }
    
    class PythonExecute {
        +execute_code(code) Promise
        +validate_syntax(code) bool
    }
    
    class BrowserUseTool {
        +navigate(url) Promise
        +click(selector) Promise
        +type(text) Promise
        +take_screenshot() Promise
    }
    
    class StrReplaceEditor {
        +create_file(path, content) Promise
        +view_file(path) Promise
        +str_replace(old, new) Promise
    }
    
    class WebSearch {
        +search(query) Promise
        +get_results() List
    }
    
    class MCPClientTool {
        +string server_id
        +connect_server() Promise
        +call_tool(name, args) Promise
    }
    
    BaseTool <|-- PythonExecute
    BaseTool <|-- BrowserUseTool
    BaseTool <|-- StrReplaceEditor
    BaseTool <|-- WebSearch
    BaseTool <|-- MCPClientTool
```

## Agent Architecture

### Agent Lifecycle and State Management

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> THINKING: run(prompt)
    THINKING --> ACTING: determine_action()
    ACTING --> OBSERVING: execute_tool()
    OBSERVING --> THINKING: process_result()
    OBSERVING --> COMPLETED: is_task_complete()
    THINKING --> COMPLETED: no_more_actions()
    ACTING --> FAILED: tool_error()
    COMPLETED --> [*]
    FAILED --> [*]
    
    note right of THINKING
        Agent analyzes situation
        and decides next action
    end note
    
    note right of ACTING
        Agent executes selected
        tool with parameters
    end note
    
    note right of OBSERVING
        Agent processes tool
        output and updates memory
    end note
```

### Memory System

```mermaid
graph TB
    subgraph "Memory Components"
        SHORT[Short-term Memory]
        LONG[Long-term Memory]
        CONTEXT[Context Buffer]
    end
    
    subgraph "Message Types"
        SYSTEM[System Messages]
        USER[User Messages]
        ASSISTANT[Assistant Messages]
        TOOL[Tool Messages]
    end
    
    INPUT[User Input] --> SHORT
    SHORT --> CONTEXT
    CONTEXT --> LLM[LLM Processing]
    LLM --> ASSISTANT
    ASSISTANT --> SHORT
    
    TOOL --> SHORT
    SHORT --> LONG
    LONG --> CONTEXT
    
    SYSTEM --> CONTEXT
    USER --> CONTEXT
```

## Tool Framework

### Tool Categories and Relationships

```mermaid
graph TB
    subgraph "Execution Tools"
        PYTHON[Python Execute]
        BASH[Bash Commands]
        DOCKER[Docker Container]
    end
    
    subgraph "File Operations"
        FILE_READ[File Reader]
        FILE_WRITE[File Writer]
        STR_REPLACE[String Replace Editor]
    end
    
    subgraph "Web & Browser"
        BROWSER[Browser Use Tool]
        WEB_SEARCH[Web Search]
        CRAWL[Web Crawler]
    end
    
    subgraph "Data & Analysis"
        CHART[Chart Visualization]
        DATA_PROC[Data Processing]
    end
    
    subgraph "Communication"
        ASK_HUMAN[Ask Human]
        TERMINATE[Terminate]
    end
    
    subgraph "External Integration"
        MCP_CLIENT[MCP Client Tool]
        API_TOOLS[API Tools]
    end
    
    subgraph "Planning & Coordination"
        PLANNING[Planning Tool]
    end
    
    AGENT[Agent] --> PYTHON
    AGENT --> FILE_READ
    AGENT --> BROWSER
    AGENT --> CHART
    AGENT --> ASK_HUMAN
    AGENT --> MCP_CLIENT
    AGENT --> PLANNING
```

### Tool Execution Pattern

```mermaid
sequenceDiagram
    participant A as Agent
    participant TC as ToolCollection
    participant T as Tool
    participant ENV as Environment
    
    A->>TC: get_tool(name)
    TC->>A: return tool instance
    A->>T: validate_parameters(params)
    T->>A: validation result
    A->>T: execute(**params)
    T->>ENV: perform operation
    ENV->>T: operation result
    T->>A: ToolResult(output, error)
    A->>A: update_memory(result)
```

## Flow Management

### Planning Flow Architecture

```mermaid
graph TB
    subgraph "Planning Flow"
        PLANNER[Planning Agent]
        EXECUTOR[Executor Agents]
        MONITOR[Progress Monitor]
    end
    
    subgraph "Plan Structure"
        STEPS[Plan Steps]
        STATUS[Step Status]
        DEPS[Dependencies]
    end
    
    USER_INPUT[User Input] --> PLANNER
    PLANNER --> STEPS
    STEPS --> STATUS
    STATUS --> DEPS
    
    PLANNER --> EXECUTOR
    EXECUTOR --> MONITOR
    MONITOR --> PLANNER
    
    EXECUTOR --> TOOLS[Available Tools]
    TOOLS --> RESULTS[Execution Results]
    RESULTS --> MONITOR
```

### Multi-Agent Coordination

```mermaid
sequenceDiagram
    participant U as User
    participant PF as PlanningFlow
    participant PA as Planning Agent
    participant EA as Executor Agent
    participant T as Tools
    
    U->>PF: submit task
    PF->>PA: create plan
    PA->>PA: analyze task
    PA->>PF: return plan steps
    
    loop For each step
        PF->>EA: assign step
        EA->>T: execute actions
        T->>EA: return results
        EA->>PF: report completion
        PF->>PA: update plan status
    end
    
    PF->>U: final results
```

## LLM Integration

### LLM Provider Architecture

```mermaid
graph TB
    subgraph "LLM Abstraction Layer"
        LLM_BASE[LLM Base Class]
        CONFIG[LLM Configuration]
    end
    
    subgraph "Provider Implementations"
        OPENAI[OpenAI Provider]
        ANTHROPIC[Anthropic Provider]
        AZURE[Azure Provider]
        OLLAMA[Ollama Provider]
        BEDROCK[AWS Bedrock Provider]
    end
    
    subgraph "Specialized Models"
        VISION[Vision Models]
        CODING[Code Models]
        GENERAL[General Models]
    end
    
    LLM_BASE --> OPENAI
    LLM_BASE --> ANTHROPIC
    LLM_BASE --> AZURE
    LLM_BASE --> OLLAMA
    LLM_BASE --> BEDROCK
    
    CONFIG --> LLM_BASE
    
    OPENAI --> VISION
    ANTHROPIC --> VISION
    AZURE --> CODING
    OLLAMA --> GENERAL
    BEDROCK --> GENERAL
```

### Message Processing Flow

```mermaid
sequenceDiagram
    participant A as Agent
    participant LLM as LLM Provider
    participant API as External API
    
    A->>A: prepare_messages()
    A->>LLM: create_completion(messages)
    LLM->>LLM: format_request()
    LLM->>API: send_request()
    API->>LLM: response
    LLM->>LLM: parse_response()
    LLM->>A: completion_result
    A->>A: process_response()
```

## MCP Protocol Support

### MCP Integration Architecture

```mermaid
graph TB
    subgraph "MCP Client Layer"
        MCP_CLIENT[MCP Client]
        SERVER_MGR[Server Manager]
        TRANSPORT[Transport Layer]
    end
    
    subgraph "MCP Servers"
        GITHUB[GitHub MCP]
        FILESYSTEM[Filesystem MCP]
        DATABASE[Database MCP]
        CUSTOM[Custom MCP Servers]
    end
    
    subgraph "Agent Integration"
        MANUS_AGENT[Manus Agent]
        TOOL_COLLECTION[Tool Collection]
        MCP_TOOL[MCP Client Tool]
    end
    
    MANUS_AGENT --> TOOL_COLLECTION
    TOOL_COLLECTION --> MCP_TOOL
    MCP_TOOL --> MCP_CLIENT
    MCP_CLIENT --> SERVER_MGR
    SERVER_MGR --> TRANSPORT
    
    TRANSPORT --> GITHUB
    TRANSPORT --> FILESYSTEM
    TRANSPORT --> DATABASE
    TRANSPORT --> CUSTOM
```

### MCP Communication Flow

```mermaid
sequenceDiagram
    participant A as Agent
    participant MCT as MCP Tool
    participant MC as MCP Client
    participant MS as MCP Server
    
    A->>MCT: connect_server(url)
    MCT->>MC: initialize_connection()
    MC->>MS: handshake
    MS->>MC: capabilities
    MC->>MCT: connection_ready
    MCT->>A: server_connected
    
    A->>MCT: call_tool(name, params)
    MCT->>MC: send_request()
    MC->>MS: tool_call
    MS->>MC: tool_result
    MC->>MCT: result
    MCT->>A: tool_output
```

## Configuration System

### Configuration Hierarchy

```mermaid
graph TB
    subgraph "Configuration Sources"
        DEFAULT[Default Values]
        CONFIG_FILE[config.toml]
        ENV_VARS[Environment Variables]
        CLI_ARGS[CLI Arguments]
    end
    
    subgraph "Configuration Categories"
        LLM_CONFIG[LLM Configuration]
        BROWSER_CONFIG[Browser Configuration]
        SEARCH_CONFIG[Search Configuration]
        SANDBOX_CONFIG[Sandbox Configuration]
        MCP_CONFIG[MCP Configuration]
        RUNFLOW_CONFIG[RunFlow Configuration]
    end
    
    DEFAULT --> LLM_CONFIG
    CONFIG_FILE --> LLM_CONFIG
    ENV_VARS --> LLM_CONFIG
    CLI_ARGS --> LLM_CONFIG
    
    CONFIG_FILE --> BROWSER_CONFIG
    CONFIG_FILE --> SEARCH_CONFIG
    CONFIG_FILE --> SANDBOX_CONFIG
    CONFIG_FILE --> MCP_CONFIG
    CONFIG_FILE --> RUNFLOW_CONFIG
```

## Execution Patterns

### Single Agent Execution (main.py)

```mermaid
flowchart TD
    START([Start]) --> PARSE[Parse CLI Arguments]
    PARSE --> CREATE[Create Manus Agent]
    CREATE --> INPUT[Get User Input]
    INPUT --> VALIDATE{Validate Input}
    VALIDATE -->|Invalid| INPUT
    VALIDATE -->|Valid| RUN[Agent.run(prompt)]
    RUN --> RESULT[Process Results]
    RESULT --> CLEANUP[Agent Cleanup]
    CLEANUP --> END([End])
    
    subgraph "Agent.run() Internal Flow"
        RUN --> INIT[Initialize State]
        INIT --> LOOP{Step < Max Steps}
        LOOP -->|Yes| STEP[Execute Step]
        STEP --> UPDATE[Update Memory]
        UPDATE --> CHECK{Task Complete?}
        CHECK -->|No| LOOP
        CHECK -->|Yes| DONE[Mark Complete]
        LOOP -->|No| TIMEOUT[Max Steps Reached]
        TIMEOUT --> DONE
        DONE --> RESULT
    end
```

### Multi-Agent Flow Execution (run_flow.py)

```mermaid
flowchart TD
    START([Start]) --> CONFIG[Load Configuration]
    CONFIG --> AGENTS[Initialize Agents]
    AGENTS --> FLOW[Create Planning Flow]
    FLOW --> INPUT[Get User Input]
    INPUT --> PLAN[Generate Plan]
    
    PLAN --> EXECUTE[Execute Plan]
    
    subgraph "Plan Execution Loop"
        EXECUTE --> NEXT{Next Step Available?}
        NEXT -->|Yes| ASSIGN[Assign to Agent]
        ASSIGN --> EXEC[Execute Step]
        EXEC --> MONITOR[Monitor Progress]
        MONITOR --> UPDATE[Update Plan Status]
        UPDATE --> NEXT
        NEXT -->|No| COMPLETE[Plan Complete]
    end
    
    COMPLETE --> RESULTS[Collect Results]
    RESULTS --> CLEANUP[Cleanup Resources]
    CLEANUP --> END([End])
```

### MCP Server Execution (run_mcp.py)

```mermaid
flowchart TD
    START([Start]) --> SERVER[Start MCP Server]
    SERVER --> LISTEN[Listen for Connections]
    LISTEN --> CONNECT{Client Connected?}
    CONNECT -->|Yes| HANDSHAKE[Perform Handshake]
    CONNECT -->|No| LISTEN
    HANDSHAKE --> READY[Server Ready]
    
    READY --> WAIT[Wait for Requests]
    WAIT --> REQUEST{Request Received?}
    REQUEST -->|Yes| PROCESS[Process Request]
    REQUEST -->|No| WAIT
    
    PROCESS --> ROUTE[Route to Handler]
    ROUTE --> EXECUTE[Execute Action]
    EXECUTE --> RESPOND[Send Response]
    RESPOND --> WAIT
    
    WAIT --> SHUTDOWN{Shutdown Signal?}
    SHUTDOWN -->|No| WAIT
    SHUTDOWN -->|Yes| CLEANUP[Cleanup]
    CLEANUP --> END([End])
```

## Data Flow

### Information Flow Through the System

```mermaid
graph LR
    subgraph "Input Processing"
        USER_INPUT[User Input]
        PARSER[Input Parser]
        VALIDATOR[Input Validator]
    end
    
    subgraph "Agent Processing"
        MEMORY[Agent Memory]
        LLM_CALL[LLM Processing]
        DECISION[Decision Making]
    end
    
    subgraph "Tool Execution"
        TOOL_SELECT[Tool Selection]
        TOOL_EXEC[Tool Execution]
        RESULT_PROC[Result Processing]
    end
    
    subgraph "Output Generation"
        RESPONSE[Response Generation]
        FORMATTER[Output Formatter]
        USER_OUTPUT[User Output]
    end
    
    USER_INPUT --> PARSER
    PARSER --> VALIDATOR
    VALIDATOR --> MEMORY
    MEMORY --> LLM_CALL
    LLM_CALL --> DECISION
    DECISION --> TOOL_SELECT
    TOOL_SELECT --> TOOL_EXEC
    TOOL_EXEC --> RESULT_PROC
    RESULT_PROC --> MEMORY
    MEMORY --> RESPONSE
    RESPONSE --> FORMATTER
    FORMATTER --> USER_OUTPUT
```

### Memory and Context Management

```mermaid
graph TB
    subgraph "Memory Layers"
        WORKING[Working Memory]
        SHORT[Short-term Memory]
        LONG[Long-term Memory]
    end
    
    subgraph "Context Processing"
        CONTEXT[Context Buffer]
        COMPRESS[Context Compression]
        RELEVANCE[Relevance Filtering]
    end
    
    INPUT[New Information] --> WORKING
    WORKING --> SHORT
    SHORT --> LONG
    
    WORKING --> CONTEXT
    SHORT --> CONTEXT
    LONG --> RELEVANCE
    RELEVANCE --> CONTEXT
    
    CONTEXT --> COMPRESS
    COMPRESS --> LLM[LLM Context Window]
    LLM --> OUTPUT[Agent Response]
```

## Security and Sandboxing

### Sandbox Architecture

```mermaid
graph TB
    subgraph "Host Environment"
        AGENT[Agent Process]
        CONFIG[Configuration]
        HOST_FS[Host Filesystem]
    end
    
    subgraph "Sandbox Container"
        SANDBOX[Sandbox Environment]
        WORK_DIR[Working Directory]
        PYTHON[Python Runtime]
        TOOLS[Sandboxed Tools]
    end
    
    subgraph "Security Boundaries"
        NETWORK[Network Controls]
        RESOURCE[Resource Limits]
        FILE_ACCESS[File Access Controls]
    end
    
    AGENT --> SANDBOX
    CONFIG --> RESOURCE
    CONFIG --> NETWORK
    CONFIG --> FILE_ACCESS
    
    SANDBOX --> WORK_DIR
    SANDBOX --> PYTHON
    SANDBOX --> TOOLS
    
    WORK_DIR -.-> HOST_FS
    PYTHON --> NETWORK
    TOOLS --> RESOURCE
```

---

This architecture documentation provides a comprehensive overview of OpenManus's technical design. Each component is designed to be modular, extensible, and maintainable, allowing for easy integration of new agents, tools, and capabilities.

For specific implementation details, refer to the source code in the respective modules:
- Agents: `app/agent/`
- Tools: `app/tool/`
- Flows: `app/flow/`
- Configuration: `app/config.py`
- LLM Integration: `app/llm.py`
- MCP Support: `app/mcp/`