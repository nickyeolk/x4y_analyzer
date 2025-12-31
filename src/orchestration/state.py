"""
Analysis state schema for Startup Analyzer.

Defines the complete state for "X for Y" business idea analysis workflow.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict


@dataclass
class BusinessIdea:
    """The 'X for Y' business idea structure."""
    x_brand: str  # e.g., "Uber"
    y_market: str  # e.g., "Dog Walkers"
    full_idea: str  # e.g., "Uber for Dog Walkers"
    description: Optional[str] = None


@dataclass
class BrandDNA:
    """Brand analysis from the Analyst agent."""
    brand_name: str
    core_strengths: List[str] = field(default_factory=list)
    business_model: str = ""
    key_differentiators: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)
    summary: str = ""
    confidence: float = 0.0


@dataclass
class MarketResearch:
    """Market research from the Researcher agent."""
    market_name: str
    market_size: Optional[str] = None
    competitor_count: int = 0
    competitors: List[str] = field(default_factory=list)
    saturation_level: str = "unknown"  # low, medium, high, oversaturated
    market_trends: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    barriers: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class RiskAnalysis:
    """Risk analysis from the Risk Analyst agent."""
    competitive_threats: List[str] = field(default_factory=list)
    market_risks: List[str] = field(default_factory=list)
    execution_challenges: List[str] = field(default_factory=list)
    financial_risks: List[str] = field(default_factory=list)
    fatal_flaws: List[str] = field(default_factory=list)
    overall_risk_level: str = "medium"  # low, medium, high
    summary: str = ""
    confidence: float = 0.0


@dataclass
class Critique:
    """Critique from the Skeptic agent (DEPRECATED - kept for backward compatibility)."""
    approved: bool = False
    concerns: List[str] = field(default_factory=list)
    fatal_flaws: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    loop_back_reason: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class GTMPlan:
    """Go-To-Market plan from the Strategist agent."""
    target_audience: str = ""
    value_proposition: str = ""
    pricing_strategy: str = ""
    distribution_channels: List[str] = field(default_factory=list)
    marketing_hooks: List[str] = field(default_factory=list)
    competitive_advantages: List[str] = field(default_factory=list)
    key_risks: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    timeline: str = ""
    viability_score: float = 0.0
    summary: str = ""


@dataclass
class AgentInteraction:
    """Record of an agent interaction."""
    agent_name: str
    timestamp: datetime
    action: str
    reasoning: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    result: Optional[str] = None
    iteration: int = 0  # Track which loop iteration


@dataclass
class AnalysisMetadata:
    """Processing metadata."""
    token_usage: Dict[str, Any] = field(default_factory=dict)
    latency_ms: Dict[str, int] = field(default_factory=dict)
    error_count: int = 0
    retry_count: int = 0
    loop_count: int = 0
    total_duration_seconds: float = 0.0
    cost_usd: float = 0.0


@dataclass
class AnalysisState:
    """
    Complete state for startup analysis workflow.

    Supports dynamic research coordination with the Strategist agent.
    """
    # Identity
    analysis_id: str
    correlation_id: str
    timestamp: datetime

    # Input
    business_idea: BusinessIdea

    # Agent Results
    analyst_insights: Optional[BrandDNA] = None
    researcher_findings: Optional[MarketResearch] = None
    risk_analysis: Optional[RiskAnalysis] = None
    strategist_plan: Optional[GTMPlan] = None

    # Coordination Control
    coordination_iteration: int = 0
    max_coordination_iterations: int = 3
    ready_for_synthesis: bool = False
    follow_up_research: List[Dict[str, Any]] = field(default_factory=list)

    # Legacy Fields (DEPRECATED - kept for backward compatibility)
    skeptic_critique: Optional[Critique] = None
    skeptic_approved: bool = False
    loop_count: int = 0
    max_loops: int = 3

    # Current State
    current_agent: str = ""

    # History & Observability
    agent_interactions: List[AgentInteraction] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)

    # Final Output
    status: str = "pending"  # pending, analyzing, completed, failed
    final_recommendation: str = ""
    requires_human_review: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for LangGraph compatibility."""
        return {
            "analysis_id": self.analysis_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "business_idea": asdict(self.business_idea),
            "analyst_insights": asdict(self.analyst_insights) if self.analyst_insights else None,
            "researcher_findings": asdict(self.researcher_findings) if self.researcher_findings else None,
            "risk_analysis": asdict(self.risk_analysis) if self.risk_analysis else None,
            "strategist_plan": asdict(self.strategist_plan) if self.strategist_plan else None,
            "coordination_iteration": self.coordination_iteration,
            "max_coordination_iterations": self.max_coordination_iterations,
            "ready_for_synthesis": self.ready_for_synthesis,
            "follow_up_research": self.follow_up_research,
            # Legacy fields
            "skeptic_critique": asdict(self.skeptic_critique) if self.skeptic_critique else None,
            "skeptic_approved": self.skeptic_approved,
            "loop_count": self.loop_count,
            "max_loops": self.max_loops,
            # Current state
            "current_agent": self.current_agent,
            "agent_interactions": [asdict(i) for i in self.agent_interactions],
            "metadata": asdict(self.metadata),
            "status": self.status,
            "final_recommendation": self.final_recommendation,
            "requires_human_review": self.requires_human_review,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisState":
        """Create state from dictionary."""
        timestamp = data["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            analysis_id=data["analysis_id"],
            correlation_id=data["correlation_id"],
            timestamp=timestamp,
            business_idea=BusinessIdea(**data["business_idea"]),
            analyst_insights=BrandDNA(**data["analyst_insights"]) if data.get("analyst_insights") else None,
            researcher_findings=MarketResearch(**data["researcher_findings"]) if data.get("researcher_findings") else None,
            risk_analysis=RiskAnalysis(**data["risk_analysis"]) if data.get("risk_analysis") else None,
            strategist_plan=GTMPlan(**data["strategist_plan"]) if data.get("strategist_plan") else None,
            coordination_iteration=data.get("coordination_iteration", 0),
            max_coordination_iterations=data.get("max_coordination_iterations", 3),
            ready_for_synthesis=data.get("ready_for_synthesis", False),
            follow_up_research=data.get("follow_up_research", []),
            # Legacy fields
            skeptic_critique=Critique(**data["skeptic_critique"]) if data.get("skeptic_critique") else None,
            skeptic_approved=data.get("skeptic_approved", False),
            loop_count=data.get("loop_count", 0),
            max_loops=data.get("max_loops", 3),
            # Current state
            current_agent=data.get("current_agent", ""),
            agent_interactions=[AgentInteraction(**i) for i in data.get("agent_interactions", [])],
            metadata=AnalysisMetadata(**data.get("metadata", {})),
            status=data.get("status", "pending"),
            final_recommendation=data.get("final_recommendation", ""),
            requires_human_review=data.get("requires_human_review", False),
        )


def create_initial_state(
    analysis_id: str,
    correlation_id: str,
    x_brand: str,
    y_market: str,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create initial state for a new analysis.

    Args:
        analysis_id: Unique analysis identifier
        correlation_id: Correlation ID for tracing
        x_brand: The "X" brand (e.g., "Uber")
        y_market: The "Y" market (e.g., "Dog Walkers")
        description: Optional additional description

    Returns:
        Initial state dictionary
    """
    full_idea = f"{x_brand} for {y_market}"

    state = AnalysisState(
        analysis_id=analysis_id,
        correlation_id=correlation_id,
        timestamp=datetime.utcnow(),
        business_idea=BusinessIdea(
            x_brand=x_brand,
            y_market=y_market,
            full_idea=full_idea,
            description=description,
        ),
        metadata=AnalysisMetadata(),
    )

    return state.to_dict()
