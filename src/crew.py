from typing import List, Optional
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from numpy import concatenate
from pydantic import BaseModel, Field
from dotenv import load_dotenv

_ = load_dotenv(override=True)

# LLM Configuration
# NOTE: gemma3:1b is a small model (1B parameters) suitable for basic tasks
# For better performance, consider using larger models:
#   - ollama/llama3:8b (8B params) - good balance
#   - ollama/llama3:70b (70B params) - best quality
#   - openai/gpt-4 - commercial option
# Features disabled for small models:
#   - reasoning=True (requires 8B+ params)
#   - planning=True (requires 8B+ params)
#   - output_json=Content (structured JSON output unreliable with small models)
default_llm = LLM(
    model="ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)


def create_llm(provider: str, model: str, api_key: Optional[str] = None) -> LLM:
    """Create LLM instance based on provider and model"""
    if provider == "ollama":
        return LLM(
            model=f"ollama/{model}",
            base_url="http://localhost:11434"
        )
    elif provider == "openai":
        return LLM(
            model=f"openai/{model}",
            api_key=api_key
        )
    elif provider == "anthropic":
        return LLM(
            model=f"anthropic/{model}",
            api_key=api_key
        )
    elif provider == "groq":
        return LLM(
            model=f"groq/{model}",
            api_key=api_key
        )
    else:
        return default_llm


# Pydantic Schema for Inputs
class Content(BaseModel):
    content_type: str = Field(...,
                              description="The type of content to be created (e.g., financial report, analysis, summary)")
    topic: str = Field(..., description="The topic of the content")
    target_audience: str = Field(..., description="The target audience for the content")
    tags: List[str] = Field(..., description="Tags to be used for the content")
    content: str = Field(..., description="The content itself")


@CrewBase
class ResearchCrew():
    """Crew for financial research tasks"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, llm_instance: Optional[LLM] = None):
        """Initialize ResearchCrew with optional LLM instance"""
        self.llm_instance = llm_instance or default_llm

    @agent
    def head_of_research(self) -> Agent:
        """Head of Research"""
        return Agent(
            config=self.agents_config["head_of_research"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
            ],
            # reasoning=True,  # Disabled - requires more capable model (8B+ params)
            inject_date=True,
            llm=self.llm_instance,
            allow_delegation=False,
        )

    
    @agent
    def financial_analyst(self) -> Agent:
        """Financial Analyst"""
        return Agent(
            config=self.agents_config["financial_analyst"],
            tools=[],
            inject_date=True,
            llm=self.llm_instance,
            allow_delegation=False,
            max_iterations=30
        )


    @agent
    def data_analyst(self) -> Agent:
        """Data Analyst"""
        return Agent(
            config=self.agents_config["data_analyst"],
            tools=[],
            inject_date=True,
            llm=self.llm_instance,
            allow_delegation=False,
            max_iterations=10
        )

    
    @agent
    def report_writer(self) -> Agent:
        """Report Writer"""
        return Agent(
            config=self.agents_config["report_writer"],
            tools=[],
            inject_date=True,
            llm=self.llm_instance,
            allow_delegation=False,
            max_iterations=30
        )


    @task
    def financial_research(self) -> Task:
        """Financial Research"""
        return Task(
            config=self.tasks_config["financial_research"],
            agent=self.head_of_research(),
            output_file="output/financial_research.md",
        )


    @task
    def prepare_research_strategy(self) -> Task:
        """Prepare Research Strategy"""
        return Task(
            config=self.tasks_config["prepare_research_strategy"],
            agent=self.head_of_research(),
            output_file="output/research_strategy.md",
            context=[self.financial_research()],
        )

    
    @task
    def company_analysis(self) -> Task:
        """Company Analysis"""
        return Task(
            config=self.tasks_config["company_analysis"],
            agent=self.financial_analyst(),
            output_file="output/company_analysis.md",
            context=[self.prepare_research_strategy()],
        )

    
    @task
    def financial_data_analysis(self) -> Task:
        """Financial Data Analysis"""
        return Task(
            config=self.tasks_config["financial_data_analysis"],
            agent=self.financial_analyst(),
            output_file="output/financial_data_analysis.md",
            context=[self.company_analysis()],
            # output_json=Content  # Disabled - small model can't reliably produce structured JSON
        )

    
    @task
    def risk_assessment(self) -> Task:
        """Risk Assessment"""
        return Task(
            config=self.tasks_config["risk_assessment"],
            agent=self.financial_analyst(),
            output_file="output/risk_assessment.md",
            context=[self.financial_data_analysis()],
            # output_json=Content  # Disabled - small model can't reliably produce structured JSON
        )

    
    @task
    def market_analysis(self) -> Task:
        """Market Analysis"""
        return Task(
            config=self.tasks_config["market_analysis"],
            agent=self.data_analyst(),
            output_file="output/market_analysis.md",
            context=[self.risk_assessment()],
        )
    

    @task
    def draft_report(self) -> Task:
        """Draft Report"""
        return Task(
            config=self.tasks_config["draft_report"],
            agent=self.data_analyst(),
            output_file="output/draft_report.md",
            context=[self.market_analysis()],
            # output_json=Content  # Disabled - small model can't reliably produce structured JSON
        )


    @task
    def finalize_report(self) -> Task:
        """Finalize Report"""
        return Task(
            config=self.tasks_config["finalize_report"],
            agent=self.report_writer(),
            output_file="output/report.md",
            context=[self.draft_report()],
            # output_json=Content  # Disabled - small model can't reliably produce structured JSON
        )


    @crew
    def crew(self) -> Crew:
        """Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            # Planning disabled - gemma3:1b (1B params) is too small for reliable planning
            # To enable: use a larger model like llama3:8b or gpt-4 for planning_llm
            planning=False,
            # planning_llm=llm,
        )


    
if __name__ == "__main__":
    from datetime import datetime

    inputs = {
        "company": "Apple",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    research_crew = ResearchCrew(llm_instance=default_llm)
    research_crew.crew().kickoff(inputs=inputs)

    print("Research Crew has completed the task.")
