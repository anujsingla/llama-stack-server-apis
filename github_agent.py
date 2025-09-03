import os
import uuid
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from llama_stack_client import LlamaStackClient, Agent
from github_tools import (
    get_repository_info,
    get_repository_languages, 
    get_repository_contributors,
    get_repository_issues,
    get_repository_pulls,
    get_repository_releases,
    search_repositories
)
from web_search_tools import (
    web_search,
    is_tavily_configured
)
from promptUtils import GITHUB_AGENT_INSTRUCTIONS

load_dotenv()
console = Console()


class GitHubProjectAnalyst:
    """GitHub Project Analyst Agent"""
    
    def __init__(self, llama_stack_url: str = "http://localhost:8321"):
        """
        Initialize the GitHub Project Analyst Agent
        
        Args:
            llama_stack_url: URL of the Llama Stack server
        """
        self.client = LlamaStackClient(base_url=llama_stack_url)
        
        # Get available models
        models = self.client.models.list()
        self.llm = next(m for m in models if m.model_type == "llm" and m.provider_id == "ollama")
        self.model_id = self.llm.identifier

        available_shields = [shield.identifier for shield in self.client.shields.list()]
        if not available_shields:
            print("No available shields. Disabling safety.")
        else:
            print(f"Available shields found: {available_shields}")
        
        # Initialize agent with GitHub analysis instructions and tools
        tools_list = [
            get_repository_info,
            get_repository_languages,
            get_repository_contributors,
            get_repository_issues,
            get_repository_pulls,
            get_repository_releases,
            search_repositories
        ]
        
        # Add web search tool if Tavily is configured
        if is_tavily_configured():
            tools_list.append(web_search)
        
        self.agent = Agent(
            client=self.client,
            model=self.model_id,
            instructions=GITHUB_AGENT_INSTRUCTIONS,
            tools=tools_list,
            sampling_params={
                "strategy": {"type": "top_p", "temperature": 1.0, "top_p": 0.9},
            },
            
        )
        
        github_token_status = "Authenticated" if os.getenv("GITHUB_TOKEN") else "Public (Rate Limited)"
        
        web_search_status = "Enabled" if is_tavily_configured() else "Disabled (TAVILY_API_KEY not set)"
        total_tools = len(tools_list)
        
        print("GitHub Project Analyst Agent Initialized")
        print(f"Model: {self.model_id}")
        print(f"GitHub API: {github_token_status}")
        print(f"Web Search: {web_search_status}")
        print(f"Available Tools: {total_tools} tools")

    def create_session(self, session_name: str = None) -> str:
        """Create a new analysis session"""
        if not session_name:
            session_name = f"github_analysis_{uuid.uuid4().hex[:8]}"
        
        session_id = self.agent.create_session(session_name=session_name)
        print(f"Created new session: {session_name} - {session_id}")
        return session_id
    
    def _chat(self, message: str, session_id: str) -> str:
        """Send a message to the agent and get response"""
        print("************************************************")
        print(f"Query: {message}")
        print("************************************************")
        
        # Create the turn - the agent will automatically handle tool calls
        response = self.agent.create_turn(
            messages=[{"role": "user", "content": message}],
            session_id=session_id,
            stream=False
        )
        
        result = response.output_message.content
        print("************************************************")
        print(f"Analysis Result: {result}")
        print("************************************************")
        return result
    
    def interactive_mode(self):
        """Start interactive mode for continuous analysis"""
        session_id = self.create_session("interactive_session")
        
        while True:
            try:
                user_input = console.input("\n[bold blue]You:[/bold blue] ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[bold yellow]Goodbye![/bold yellow]")
                    break
                
                if user_input.strip():
                    self._chat(user_input, session_id)
                    
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Goodbye![/bold yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")


def main():
    """Main function to run the GitHub Project Analyst Agent"""
    
    try:
        # Initialize the agent
        analyst = GitHubProjectAnalyst()
        
        # Start interactive mode
        analyst.interactive_mode()
        
    except Exception as e:
        print(f"Error initializing agent: {str(e)}")

if __name__ == "__main__":
    main()
