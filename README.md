# GitHub Project Analyst Agent

A powerful AI-driven agent built on Llama Stack that provides deep insights into GitHub repositories and the broader software ecosystem. Leveraging advanced language models, comprehensive GitHub API integration, and general web search capabilities, this agent can analyze codebases, track project health, examine contributor patterns, and gather contextual information from across the web.

Whether you're evaluating open-source libraries, conducting competitive analysis, or monitoring project ecosystems, this agent transforms raw repository data and web intelligence into meaningful insights through natural language conversations.

## Features

- **Repository Analysis**: Get detailed information about any GitHub repository
- **Language Analysis**: Analyze programming languages used with usage percentages
- **Contributor Insights**: Examine contributor activity and statistics
- **Issue & PR Tracking**: Review open/closed issues and pull requests
- **Release Monitoring**: Track project releases and versions
- **Repository Search**: Find repositories based on various criteria
- **Web Search Integration**: General web search (like Google) for broader context and information

## Prerequisites

1. **Llama Stack Server**: Make sure you have Llama Stack running on `http://localhost:8321`
2. **Python 3.8+**: Required for running the agent
3. **GitHub Token** (Optional): For increased API rate limits

## Quick Start

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure environment (optional):**

```bash
cp example.env .env
# Edit .env to add your tokens (GITHUB_TOKEN, TAVILY_API_KEY)
```

3. **Start Llama Stack server** (in another terminal):

Pull and run the models:

```bash
ollama run llama3.2:3b --keepalive 90m
ollama run llama-guard3:1b --keepalive 90m

```

Installation and Setup:

[Detailed Tutorial](https://llama-stack.readthedocs.io/en/latest/getting_started/detailed_tutorial.html#detailed-tutorial)

```bash

# Just for reference:
# Container way to run server with local run.yaml file:

podman run -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ~/.llama:/root/.llama \
  -v ./run.yaml:/usr/local/lib/python3.12/site-packages/llama_stack/distributions/starter/run.yaml:z \
  llamastack/distribution-starter \
  --port $LLAMA_STACK_PORT \
  --env OLLAMA_URL=http://host.docker.internal:11434

# With venv
- llama stack build --distro starter --image-type venv --image-name distro
- llama stack run /Users/opavale/.llama/distributions/starter/starter-run.yaml --image-type venv --image-name distro --env OLLAMA_URL=http://127.0.0.1:11434
```

## Usage

### REST API Server

Start the FastAPI server for web integration:

```bash
python github_agent_api.py
```

### Interactive Mode

Run the agent in interactive mode for conversational analysis:

```bash
python github_agent.py
```

The API will be available at:

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Chat Endpoint**: POST http://localhost:8000/chat

### Example Queries

The agent can handle various types of queries:

- "Analyze the health and activity of the facebook/react repository"
- "What are the main contributors to the Kubernetes project?"
- "Show me recent issues in the TensorFlow repository"
- "Find the most popular Python machine learning libraries"
- "Search for recent news about TensorFlow updates"
- "What are developers saying about the latest facebook/react release?"
- "What is the latest IBM share price?"

### API Endpoints

**POST /chat** - Chat with the agent

```json
{
  "session_id": "optional-session-id",
  "message": "Analyze the repository facebook/react"
}
```

**POST /sessions** - Create a new session

```json
{
  "session_name": "my-analysis-session"
}
```

**GET /health** - Check API health status

## Available Tools

The agent has access to the following tools:

### GitHub API Tools

1. **get_repository_info**: Basic repository information (stars, forks, description, etc.)
2. **get_repository_languages**: Programming languages with usage percentages
3. **get_repository_contributors**: Contributor list with contribution counts
4. **get_repository_issues**: Issues with filtering options
5. **get_repository_pulls**: Pull requests with detailed information
6. **get_repository_releases**: Releases and version information
7. **search_repositories**: Search GitHub repositories with various criteria

Github public APIs: https://api.github.com/

### Web Search Tool

- **web_search**: General web search capabilities (like Google) using Tavily API for broader context and real-time information (requires `TAVILY_API_KEY`)

## Architecture

This agent demonstrates modern Llama Stack patterns:

- **Agent-based Architecture**: Uses Llama Stack's Agent class for seamless tool integration
- **Tool Integration**: GitHub API tools + optional web search capabilities
- **Session Management**: Persistent conversations across multiple queries

## API Rate Limits

- **Without GitHub Token**: 60 requests per hour
- **With GitHub Token**: 5,000 requests per hour

**To get a GitHub token:**

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Generate a new token with `public_repo` scope
3. Add it to your `.env` file

## Configuration

Configure through environment variables in `.env`:

```bash
# API Server
API_HOST=localhost
API_PORT=8000

# Llama Stack
LLAMA_STACK_URL=http://localhost:8321

# Optional: GitHub API (for higher rate limits)
GITHUB_TOKEN=your_github_token_here

# Optional: Web search (for enhanced analysis)
TAVILY_API_KEY=your_tavily_api_key_here
```

## License

This project is open source and available under the MIT License.

## Troubleshooting

**Common Issues:**

- **Connection refused**: Ensure Llama Stack is running on port 8321
- **Rate limits**: Add GitHub token for higher limits
- **Repository not found**: Check owner/repo name spelling
