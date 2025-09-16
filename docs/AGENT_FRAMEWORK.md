# Agent Framework Documentation

This document provides detailed information about the OpenManus agent framework, including agent types, lifecycle management, and extensibility patterns.

## Agent Hierarchy

### Base Agent Class

The `BaseAgent` class provides the foundation for all agents in OpenManus:

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +string name
        +string description
        +string system_prompt
        +string next_step_prompt
        +LLM llm
        +Memory memory
        +AgentState state
        +int max_steps
        +int current_step
        +int duplicate_threshold
        
        +create()* Promise~BaseAgent~
        +run(prompt: string)* Promise
        +step()* Promise
        +cleanup() Promise
        +reset() void
        +add_message(message: Message) void
        +get_last_message() Message
        +is_duplicate_action() bool
        +transition_state(new_state: AgentState) void
    }
    
    note for BaseAgent "Provides core agent functionality\nand state management"
```

### ToolCall Agent

The `ToolCallAgent` extends `BaseAgent` with tool execution capabilities:

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
    }
    
    class ToolCallAgent {
        +ToolCollection available_tools
        +list~string~ special_tool_names
        +int max_observe
        
        +execute_tool(tool_call: ToolCall) Promise~ToolResult~
        +get_tool_output(messages: list) string
        +format_tool_result(result: ToolResult) string
        +handle_tool_error(error: Exception) ToolResult
    }
    
    BaseAgent <|-- ToolCallAgent
    
    note for ToolCallAgent "Adds tool execution capabilities\nto the base agent"
```

### Specialized Agents

```mermaid
classDiagram
    class ToolCallAgent {
        <<abstract>>
    }
    
    class Manus {
        +MCPClients mcp_clients
        +Dict~string, string~ connected_servers
        +BrowserContextHelper browser_context_helper
        
        +connect_mcp_server(url: string) Promise
        +disconnect_mcp_server(server_id: string) Promise
        +list_mcp_servers() List~string~
        +get_mcp_tools() List~Tool~
    }
    
    class SWEAgent {
        +string workspace_root
        +List~string~ allowed_file_extensions
        +bool restrict_to_workspace
        
        +validate_file_path(path: string) bool
        +get_workspace_files() List~string~
        +create_file_safely(path: string, content: string) Promise
    }
    
    class BrowserAgent {
        +BrowserController controller
        +bool headless_mode
        +Dict browser_config
        
        +navigate_to(url: string) Promise
        +take_screenshot() Promise~bytes~
        +interact_with_page(action: string) Promise
    }
    
    class DataAnalysisAgent {
        +ChartVisualization chart_tool
        +PandasDataProcessor data_processor
        
        +load_data(source: string) Promise~DataFrame~
        +analyze_data(data: DataFrame) Promise~Dict~
        +create_visualization(data: DataFrame, chart_type: string) Promise~str~
    }
    
    ToolCallAgent <|-- Manus
    ToolCallAgent <|-- SWEAgent
    ToolCallAgent <|-- BrowserAgent
    ToolCallAgent <|-- DataAnalysisAgent
    
    note for Manus "General-purpose agent with\nMCP and browser support"
    note for SWEAgent "Software engineering focused\nwith file system restrictions"
    note for BrowserAgent "Web automation and\nbrowser interaction specialist"
    note for DataAnalysisAgent "Data analysis and\nvisualization specialist"
```

## Agent Lifecycle

### State Management

```mermaid
stateDiagram-v2
    [*] --> IDLE: create()
    IDLE --> THINKING: run(prompt)
    THINKING --> ACTING: choose_action()
    ACTING --> OBSERVING: execute_tool()
    OBSERVING --> THINKING: process_result()
    THINKING --> COMPLETED: task_finished()
    ACTING --> FAILED: tool_error()
    OBSERVING --> FAILED: critical_error()
    COMPLETED --> IDLE: reset()
    FAILED --> IDLE: reset()
    IDLE --> [*]: cleanup()
    
    state THINKING {
        [*] --> AnalyzingContext
        AnalyzingContext --> PlanningAction
        PlanningAction --> SelectingTool
        SelectingTool --> [*]
    }
    
    state ACTING {
        [*] --> ValidatingParameters
        ValidatingParameters --> ExecutingTool
        ExecutingTool --> [*]
    }
    
    state OBSERVING {
        [*] --> ProcessingOutput
        ProcessingOutput --> UpdatingMemory
        UpdatingMemory --> EvaluatingProgress
        EvaluatingProgress --> [*]
    }
```

### Step Execution Flow

```mermaid
flowchart TD
    START([Step Start]) --> CHECK_STATE{Check Agent State}
    CHECK_STATE -->|IDLE| ERROR[Error: Invalid State]
    CHECK_STATE -->|THINKING| PREPARE[Prepare Context]
    
    PREPARE --> LLM_CALL[Call LLM]
    LLM_CALL --> PARSE[Parse Response]
    PARSE --> VALIDATE{Valid Tool Call?}
    
    VALIDATE -->|No| HANDLE_ERROR[Handle Parse Error]
    VALIDATE -->|Yes| EXECUTE[Execute Tool]
    
    EXECUTE --> TOOL_RESULT[Get Tool Result]
    TOOL_RESULT --> UPDATE_MEMORY[Update Memory]
    UPDATE_MEMORY --> CHECK_COMPLETE{Task Complete?}
    
    CHECK_COMPLETE -->|Yes| SET_COMPLETE[Set State: COMPLETED]
    CHECK_COMPLETE -->|No| CHECK_STEPS{Max Steps Reached?}
    
    CHECK_STEPS -->|Yes| SET_FAILED[Set State: FAILED]
    CHECK_STEPS -->|No| SET_THINKING[Set State: THINKING]
    
    HANDLE_ERROR --> SET_FAILED
    ERROR --> SET_FAILED
    
    SET_COMPLETE --> END([Step End])
    SET_FAILED --> END
    SET_THINKING --> END
```

## Memory Management

### Memory Structure

```mermaid
graph TB
    subgraph "Memory Components"
        MESSAGES[Message History]
        CONTEXT[Context Buffer]
        METADATA[Metadata Store]
    end
    
    subgraph "Message Types"
        SYSTEM[System Messages]
        USER[User Messages]
        ASSISTANT[Assistant Messages]
        TOOL[Tool Messages]
        FUNCTION[Function Messages]
    end
    
    subgraph "Memory Operations"
        ADD[Add Message]
        RETRIEVE[Retrieve Messages]
        COMPRESS[Compress History]
        FILTER[Filter Relevant]
    end
    
    MESSAGES --> SYSTEM
    MESSAGES --> USER
    MESSAGES --> ASSISTANT
    MESSAGES --> TOOL
    MESSAGES --> FUNCTION
    
    ADD --> MESSAGES
    RETRIEVE --> CONTEXT
    COMPRESS --> CONTEXT
    FILTER --> CONTEXT
    
    CONTEXT --> LLM[LLM Context]
    METADATA --> FILTER
```

### Context Management

```mermaid
sequenceDiagram
    participant A as Agent
    participant M as Memory
    participant C as Context Manager
    participant LLM as LLM Provider
    
    A->>M: get_context()
    M->>M: retrieve_messages()
    M->>C: compress_if_needed()
    C->>C: calculate_token_count()
    C->>C: filter_relevant_messages()
    C->>M: return compressed_context
    M->>A: context_messages
    A->>LLM: create_completion(messages)
    LLM->>A: response
    A->>M: add_message(response)
```

## Tool Integration

### Tool Registration

```mermaid
flowchart TD
    START([Agent Creation]) --> INIT_TOOLS[Initialize Tool Collection]
    INIT_TOOLS --> REG_CORE[Register Core Tools]
    REG_CORE --> REG_SPECIAL[Register Specialized Tools]
    REG_SPECIAL --> REG_MCP[Register MCP Tools]
    REG_MCP --> VALIDATE[Validate Tool Collection]
    VALIDATE --> READY[Agent Ready]
    
    subgraph "Core Tools"
        PYTHON[Python Execute]
        FILE[File Operations]
        SEARCH[Web Search]
    end
    
    subgraph "Specialized Tools"
        BROWSER[Browser Use]
        CHART[Chart Visualization]
        ASK[Ask Human]
    end
    
    subgraph "MCP Tools"
        GITHUB[GitHub MCP]
        FS[Filesystem MCP]
        CUSTOM[Custom MCP]
    end
    
    REG_CORE --> PYTHON
    REG_CORE --> FILE
    REG_CORE --> SEARCH
    
    REG_SPECIAL --> BROWSER
    REG_SPECIAL --> CHART
    REG_SPECIAL --> ASK
    
    REG_MCP --> GITHUB
    REG_MCP --> FS
    REG_MCP --> CUSTOM
```

### Tool Execution Pattern

```mermaid
sequenceDiagram
    participant A as Agent
    participant TC as ToolCollection
    participant T as Tool
    participant V as Validator
    participant E as Executor
    
    A->>TC: get_tool(name)
    TC->>T: return tool instance
    A->>V: validate_parameters(tool, params)
    V->>A: validation_result
    
    alt Valid Parameters
        A->>T: execute(**params)
        T->>E: perform_operation()
        E->>T: operation_result
        T->>A: ToolResult(output, error)
    else Invalid Parameters
        A->>A: create_error_result()
    end
    
    A->>A: update_memory(result)
    A->>A: log_tool_usage()
```

## Agent Configuration

### Configuration Schema

```mermaid
classDiagram
    class AgentConfig {
        +string name
        +string description
        +string system_prompt
        +string next_step_prompt
        +int max_steps
        +int max_observe
        +LLMConfig llm_config
        +ToolConfig tool_config
        +BrowserConfig browser_config
    }
    
    class LLMConfig {
        +string model
        +string api_key
        +string base_url
        +int max_tokens
        +float temperature
        +Dict~string, any~ extra_params
    }
    
    class ToolConfig {
        +List~string~ enabled_tools
        +Dict~string, Dict~ tool_settings
        +bool allow_dangerous_tools
        +string workspace_root
    }
    
    class BrowserConfig {
        +bool headless
        +bool disable_security
        +List~string~ extra_args
        +string chrome_path
        +ProxyConfig proxy
    }
    
    AgentConfig --> LLMConfig
    AgentConfig --> ToolConfig
    AgentConfig --> BrowserConfig
```

## Extensibility Patterns

### Creating Custom Agents

```python
from app.agent.toolcall import ToolCallAgent
from app.tool import ToolCollection, PythonExecute

class CustomAgent(ToolCallAgent):
    """Custom agent for specific domain tasks."""
    
    name: str = "CustomAgent"
    description: str = "Specialized agent for domain-specific tasks"
    
    # Define custom tools
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            # Add custom tools here
        )
    )
    
    async def custom_method(self):
        """Custom agent-specific functionality."""
        pass
    
    async def step(self):
        """Override step method for custom behavior."""
        # Custom step logic
        result = await super().step()
        # Post-processing
        return result
```

### Adding Custom Tools

```python
from app.tool.base import BaseTool, ToolResult

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Description of what this tool does"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"},
            "param2": {"type": "integer", "description": "Another parameter"}
        },
        "required": ["param1"]
    }
    
    async def execute(self, param1: str, param2: int = 0) -> ToolResult:
        try:
            # Tool implementation
            result = self.perform_operation(param1, param2)
            return ToolResult(output=result)
        except Exception as e:
            return ToolResult(error=str(e))
    
    def perform_operation(self, param1: str, param2: int) -> str:
        """Implement tool-specific logic."""
        return f"Operation result for {param1} with {param2}"
```

## Error Handling

### Error Recovery Patterns

```mermaid
flowchart TD
    ERROR[Error Occurs] --> CLASSIFY{Classify Error}
    
    CLASSIFY -->|Tool Error| TOOL_RECOVERY[Tool Recovery]
    CLASSIFY -->|LLM Error| LLM_RECOVERY[LLM Recovery]
    CLASSIFY -->|Memory Error| MEMORY_RECOVERY[Memory Recovery]
    CLASSIFY -->|System Error| SYSTEM_RECOVERY[System Recovery]
    
    TOOL_RECOVERY --> RETRY_TOOL{Retry Tool?}
    RETRY_TOOL -->|Yes| EXECUTE_TOOL[Execute Tool Again]
    RETRY_TOOL -->|No| ALT_TOOL[Try Alternative Tool]
    
    LLM_RECOVERY --> RETRY_LLM{Retry LLM?}
    RETRY_LLM -->|Yes| CALL_LLM[Call LLM Again]
    RETRY_LLM -->|No| FALLBACK[Use Fallback Response]
    
    MEMORY_RECOVERY --> RESET_CONTEXT[Reset Context]
    RESET_CONTEXT --> CONTINUE[Continue Execution]
    
    SYSTEM_RECOVERY --> CLEANUP[Cleanup Resources]
    CLEANUP --> FAIL[Mark as Failed]
    
    EXECUTE_TOOL --> SUCCESS[Success]
    ALT_TOOL --> SUCCESS
    CALL_LLM --> SUCCESS
    FALLBACK --> SUCCESS
    CONTINUE --> SUCCESS
    
    SUCCESS --> RESUME[Resume Normal Flow]
    FAIL --> TERMINATE[Terminate Agent]
```

## Performance Optimization

### Memory Optimization

```mermaid
graph TB
    subgraph "Memory Optimization Strategies"
        COMPRESS[Context Compression]
        FILTER[Relevance Filtering]
        CHUNK[Message Chunking]
        CACHE[Response Caching]
    end
    
    subgraph "Performance Metrics"
        TOKEN_COUNT[Token Count]
        RESPONSE_TIME[Response Time]
        MEMORY_USAGE[Memory Usage]
        THROUGHPUT[Throughput]
    end
    
    COMPRESS --> TOKEN_COUNT
    FILTER --> TOKEN_COUNT
    CHUNK --> MEMORY_USAGE
    CACHE --> RESPONSE_TIME
    
    TOKEN_COUNT --> OPTIMIZATION[Optimization Decisions]
    RESPONSE_TIME --> OPTIMIZATION
    MEMORY_USAGE --> OPTIMIZATION
    THROUGHPUT --> OPTIMIZATION
```

### Execution Optimization

```mermaid
flowchart TD
    START([Execution Start]) --> PROFILE[Profile Performance]
    PROFILE --> ANALYZE[Analyze Bottlenecks]
    ANALYZE --> OPTIMIZE{Optimization Needed?}
    
    OPTIMIZE -->|Yes| STRATEGY[Choose Strategy]
    OPTIMIZE -->|No| MONITOR[Continue Monitoring]
    
    STRATEGY --> PARALLEL[Parallel Tool Execution]
    STRATEGY --> CACHE[Cache Frequent Results]
    STRATEGY --> BATCH[Batch Similar Operations]
    STRATEGY --> COMPRESS[Compress Context]
    
    PARALLEL --> MEASURE[Measure Improvement]
    CACHE --> MEASURE
    BATCH --> MEASURE
    COMPRESS --> MEASURE
    
    MEASURE --> VALIDATE{Performance Improved?}
    VALIDATE -->|Yes| MONITOR
    VALIDATE -->|No| REVERT[Revert Changes]
    
    REVERT --> ANALYZE
    MONITOR --> END([Execution End])
```

This agent framework documentation provides the foundation for understanding how to work with and extend the OpenManus agent system. Each agent type is designed for specific use cases while maintaining consistency through the common base classes and interfaces.