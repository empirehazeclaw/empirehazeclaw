#!/usr/bin/env python3
"""
Market Validator Agent
Validates startup ideas by analyzing market demand, competition, and viability.
"""

import argparse
import logging
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/home/clawbot/.openclaw/workspace/logs/market_validator.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of market validation."""
    score: int
    signals: List[str]
    risks: List[str]
    recommendations: List[str]
    summary: str


class MarketValidatorAgent:
    """Agent for validating startup market opportunities."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        logger.info("MarketValidatorAgent initialized")

    def validate_idea(self, idea_data: Dict[str, Any]) -> ValidationResult:
        """Validate a startup idea across multiple dimensions."""
        required = ["name", "problem", "solution"]
        missing = [f for f in required if f not in idea_data or not idea_data[f]]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        name = idea_data.get("name", "Unknown")
        problem = idea_data.get("problem", "")
        solution = idea_data.get("solution", "")

        signals = []
        risks = []
        recommendations = []
        score = 0

        # Problem validation (30 points max)
        problem_score = self._validate_problem(problem, idea_data.get("target_audience"))
        score += problem_score
        if problem_score < 10:
            risks.append("Problem may not be painful enough for customers to pay")

        # Solution validation (20 points max)
        solution_score = self._validate_solution(solution, problem, idea_data.get("unique_advantage"))
        score += solution_score
        if solution_score < 10:
            risks.append("Solution may not be differentiated enough")

        # Market validation (25 points max)
        market_score = self._validate_market(idea_data.get("market_size"), idea_data.get("target_audience"))
        score += market_score
        if market_score < 15:
            risks.append("Market may be too small or undefined")

        # Competition validation (15 points max)
        competition_score = self._validate_competition(idea_data.get("competitors"))
        score += competition_score
        if competition_score < 5:
            risks.append("Competitive landscape is crowded with no clear differentiator")

        # Business model validation (10 points max)
        business_score = self._validate_business_model(idea_data.get("revenue_model"), idea_data.get("pricing"))
        score += business_score

        # Generate signals
        if problem_score > 20:
            signals.append("Strong problem statement with clear pain point")
        if solution_score > 15:
            signals.append("Solution has clear differentiation")
        if market_score > 20:
            signals.append("Large addressable market with clear target")
        if competition_score > 10:
            signals.append("Can identify competitive advantages")
        if business_score > 7:
            signals.append("Clear revenue model identified")

        # Generate recommendations
        if problem_score < 15:
            recommendations.append("Strengthen problem statement with specific data and customer quotes")
        if market_score < 15:
            recommendations.append("Research market size more thoroughly - define TAM/SAM/SOM")
        if not idea_data.get("competitors"):
            recommendations.append("Conduct competitive analysis")
        if not idea_data.get("revenue_model"):
            recommendations.append("Define clear revenue model early")
        if competition_score < 10:
            recommendations.append("Identify and document unique competitive advantages")

        # Summary
        if score >= 80:
            summary = f"'{name}' shows STRONG market potential."
        elif score >= 60:
            summary = f"'{name}' shows MODERATE market potential. Address identified risks."
        elif score >= 40:
            summary = f"'{name}' needs IMPROVEMENT. Research more before building."
        else:
            summary = f"'{name}' shows WEAK market potential. Consider pivoting."

        result = ValidationResult(
            score=min(100, score),
            signals=signals,
            risks=risks,
            recommendations=recommendations,
            summary=summary
        )

        logger.info(f"Validated idea '{name}': score={score}")
        return result

    def _validate_problem(self, problem: str, audience: Optional[str]) -> int:
        """Validate problem statement quality."""
        score = 0
        if not problem:
            return 0
        if len(problem) > 50:
            score += 5
        if len(problem) > 100:
            score += 5
        if any(word in problem.lower() for word in ["waste", "lose", "fail", "struggle", "frustrat", "cost", "time-consuming"]):
            score += 5
        if any(char.isdigit() for char in problem):
            score += 5
        if audience and len(audience) > 10:
            score += 5
        emotional_words = ["hate", "despise", "painful", "nightmare", "annoying", "broken"]
        if any(word in problem.lower() for word in emotional_words):
            score += 5
        return min(30, score)

    def _validate_solution(self, solution: str, problem: str, advantage: Optional[str]) -> int:
        """Validate solution quality."""
        score = 0
        if not solution:
            return 0
        if len(solution) > 50:
            score += 5
        if len(solution) > 150:
            score += 5
        if problem and any(word in solution.lower() for word in problem.lower().split()[:5]):
            score += 5
        if advantage and len(advantage) > 20:
            score += 5
        return min(20, score)

    def _validate_market(self, market_size: Optional[str], audience: Optional[str]) -> int:
        """Validate market opportunity."""
        score = 0
        if not market_size and not audience:
            return 5
        if market_size:
            size_lower = market_size.lower()
            if any(unit in size_lower for unit in ["$", "billion", "million"]):
                score += 10
            if size_lower.count("/") >= 2 or "tam" in size_lower:
                score += 5
        if audience:
            if len(audience) > 20:
                score += 5
            if any(char.isdigit() for char in audience):
                score += 5
        return min(25, score)

    def _validate_competition(self, competitors: Optional[List[str]]) -> int:
        """Validate competitive awareness."""
        if not competitors:
            return 5
        return min(15, 5 + len(competitors) * 2)

    def _validate_business_model(self, revenue_model: Optional[str], pricing: Optional[str]) -> int:
        """Validate business model."""
        score = 0
        if revenue_model:
            score += 5
        if pricing:
            score += 5
        return min(10, score)

    def analyze_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keywords for market research signals."""
        if not keywords:
            raise ValueError("Keywords list cannot be empty")

        analysis = {
            "keywords": keywords,
            "count": len(keywords),
            "recommendations": []
        }

        long_tail = [k for k in keywords if len(k.split()) >= 3]
        commercial = [k for k in keywords if any(w in k.lower() for w in ["best", "top", "review", "vs", "alternative"])]

        analysis["long_tail_count"] = len(long_tail)
        analysis["commercial_intent_count"] = len(commercial)
        analysis["long_tail_keywords"] = long_tail[:10]
        analysis["commercial_keywords"] = commercial[:10]

        if len(long_tail) < len(keywords) * 0.3:
            analysis["recommendations"].append("Add more long-tail keywords for specific search intent")
        if len(commercial) < len(keywords) * 0.2:
            analysis["recommendations"].append("Add comparison keywords to gauge purchase intent")
        if len(keywords) < 10:
            analysis["recommendations"].append("Expand keyword list for comprehensive coverage")

        logger.info(f"Analyzed {len(keywords)} keywords")
        return analysis

    def generate_survey_questions(self, idea_data: Dict[str, Any]) -> List[str]:
        """Generate customer survey questions to validate the idea."""
        problem = idea_data.get("problem", "")
        solution = idea_data.get("solution", "")

        questions = [
            f"1. How would you describe the problem of '{problem[:50]}...' to someone who hasn't experienced it?",
            "2. On a scale of 1-10, how frustrated are you with the current solutions?",
            "3. What have you tried to solve this problem?",
            "4. What would your ideal solution look like?",
            f"5. How much would you pay for a solution that completely solves this? ($0 / $10 / $50 / $100+ monthly)",
            "6. What is the #1 thing missing from existing solutions?",
            "7. How does this problem affect your work/life daily?",
            "8. Would you use a product that solves this if it existed? (Yes/No/Maybe)",
            "9. What would convince you to switch from your current solution?",
            "10. Who else experiences this problem? Who should we talk to?"
        ]

        if solution:
            questions.insert(3, f"11. [Show {solution[:30]}...] How likely would you be to use this? (1-10)")

        logger.info(f"Generated {len(questions)} survey questions")
        return questions


def main():
    parser = argparse.ArgumentParser(
        description="Market Validator - Validate startup market opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --validate --name "MyStartup" --problem "Enterprises waste time on..." --solution "We automate..."
  %(prog)s --keywords "best project management tool" "vs asana" "alternative to jira"
  %(prog)s --survey --problem "Customer support is slow" --solution "AI chatbot"
  %(prog)s --validate --json --name "X" --problem "Pain point" --solution "Our fix"
        """
    )

    parser.add_argument("--validate", action="store_true", help="Validate a startup idea")
    parser.add_argument("--name", type=str, help="Startup/company name")
    parser.add_argument("--problem", type=str, help="Problem statement")
    parser.add_argument("--solution", type=str, help="Solution description")
    parser.add_argument("--market", type=str, help="Market size (TAM/SAM/SOM)")
    parser.add_argument("--audience", type=str, help="Target audience")
    parser.add_argument("--revenue", type=str, help="Revenue model")
    parser.add_argument("--pricing", type=str, help="Pricing strategy")
    parser.add_argument("--competitors", type=str, help="Competitors (comma-separated)")
    parser.add_argument("--keywords", nargs="+", help="Keywords to analyze")
    parser.add_argument("--survey", action="store_true", help="Generate survey questions")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()
    agent = MarketValidatorAgent(verbose=args.verbose)

    try:
        if args.validate:
            idea_data = {}
            if not args.name or not args.problem or not args.solution:
                print("Error: --name, --problem, and --solution are required for --validate")
                sys.exit(1)

            idea_data = {
                "name": args.name,
                "problem": args.problem,
                "solution": args.solution
            }
            if args.market:
                parts = args.market.split("/")
                if len(parts) >= 3:
                    idea_data["market_size"] = args.market
            if args.audience:
                idea_data["target_audience"] = args.audience
            if args.revenue:
                idea_data["revenue_model"] = args.revenue
            if args.pricing:
                idea_data["pricing"] = args.pricing
            if args.competitors:
                idea_data["competitors"] = [c.strip() for c in args.competitors.split(",")]

            result = agent.validate_idea(idea_data)

            if args.json:
                print(json.dumps(asdict(result), indent=2))
            else:
                print(f"\n📊 VALIDATION RESULT\n" + "-" * 50)
                print(f"  Score: {result.score}/100")
                print(f"\n  {result.summary}")
                if result.signals:
                    print(f"\n  Signals:")
                    for s in result.signals:
                        print(f"    ✅ {s}")
                if result.risks:
                    print(f"\n  Risks:")
                    for r in result.risks:
                        print(f"    ⚠️ {r}")
                if result.recommendations:
                    print(f"\n  Recommendations:")
                    for rec in result.recommendations:
                        print(f"    → {rec}")

        elif args.keywords:
            analysis = agent.analyze_keywords(args.keywords)
            if args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print(f"\n🔍 KEYWORD ANALYSIS\n" + "-" * 50)
                print(f"  Total Keywords: {analysis['count']}")
                print(f"  Long-tail: {analysis['long_tail_count']}")
                print(f"  Commercial Intent: {analysis['commercial_intent_count']}")
                if analysis['recommendations']:
                    print(f"\n  Recommendations:")
                    for rec in analysis['recommendations']:
                        print(f"    → {rec}")

        elif args.survey:
            if not args.problem:
                print("Error: --problem is required for --survey")
                sys.exit(1)

            idea_data = {"problem": args.problem}
            if args.solution:
                idea_data["solution"] = args.solution

            questions = agent.generate_survey_questions(idea_data)
            if args.json:
                print(json.dumps(questions, indent=2))
            else:
                print(f"\n📝 CUSTOMER VALIDATION SURVEY\n" + "-" * 50)
                for q in questions:
                    print(f"  {q}")
                print(f"\n  Note: Target 50-100 respondents for meaningful validation")

        else:
            parser.print_help()

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
