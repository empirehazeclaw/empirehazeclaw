#!/usr/bin/env python3
"""
Case Study Agent — Generate detailed business case studies
Version: 1.0
Usage: python3 case_study_agent.py --task <task> [options]
"""

import argparse
import json
import logging
import sys
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# Logging Setup
LOG_DIR = "/home/clawbot/.openclaw/workspace/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [CASE_STUDY] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "case_study.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class CaseStudyAgent:
    """Generate comprehensive business case studies."""

    CASE_STUDY_STRUCTURE = {
        "executive_summary": "Brief overview of the case",
        "company_background": "About the company/organization",
        "challenge": "The problem or opportunity",
        "solution": "Approach taken",
        "implementation": "How it was executed",
        "results": "Quantifiable outcomes",
        "lessons_learned": "Key takeaways",
        "conclusion": "Final thoughts"
    }

    def __init__(self):
        self.log = log

    def generate_case_study(self, company_name: str, industry: str, challenge: str,
                           solution: str, results: Dict[str, Any],
                           timeline: str = "3 months") -> Dict[str, Any]:
        """Generate a complete case study document."""

        case_study = {
            "title": f"{company_name} Case Study: {challenge[:50]}...",
            "company": company_name,
            "industry": industry,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sections": self._generate_sections(company_name, industry, challenge, solution, results, timeline),
            "results": results,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "template": "business_case_study",
                "word_count_estimate": 1500
            }
        }

        # Build full document
        case_study["full_document"] = self._build_markdown(case_study)

        return case_study

    def generate_customer_success_story(self, customer_name: str, product: str,
                                       pain_point: str, outcome: str,
                                       metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a customer success story (shorter format)."""

        story = f"""# {customer_name} Success Story

**Product:** {product}
**Challenge:** {pain_point}
**Outcome:** {outcome}

---

## The Beginning

{customer_name} was facing a significant challenge with {pain_point}. This was impacting their ability to scale and compete effectively in the market.

## The Solution

By implementing {product}, {customer_name} was able to address their core pain points and transform their operations.

## Results

"""

        for metric, value in metrics.items():
            story += f"- **{metric}:** {value}\n"

        story += f"""
---

## Customer Quote

> "This solution completely transformed how we operate. The results speak for themselves."
> — *{customer_name} Representative*

## Looking Forward

{customer_name} continues to grow and innovate, building on the foundation established through this partnership.

---

*Would you like to achieve similar results? Contact us to learn more.*
"""

        return {
            "customer": customer_name,
            "product": product,
            "story": story,
            "metrics": metrics,
            "type": "customer_success_story"
        }

    def generate_competitive_analysis(self, company: str, competitors: List[str],
                                     strengths: List[str],
                                     weaknesses: List[str] = None) -> Dict[str, Any]:
        """Generate a competitive analysis case study."""

        analysis = f"""# Competitive Analysis: {company}

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}
**Competitors Analyzed:** {", ".join(competitors)}

---

## Company Overview

{company} operates in a competitive landscape with key players including {", ".join(competitors)}.

## Competitive Strengths

"""

        for strength in strengths:
            analysis += f"- {strength}\n"

        if weaknesses:
            analysis += "\n## Areas for Improvement\n\n"
            for weakness in weaknesses:
                analysis += f"- {weakness}\n"

        analysis += """
## Market Position

Based on this analysis, several key insights emerge regarding competitive positioning and opportunities for differentiation.

## Recommendations

1. Leverage existing strengths
2. Address identified weaknesses
3. Monitor competitor movements
4. Focus on unique value proposition

---

*This analysis is for strategic planning purposes.*
"""

        return {
            "company": company,
            "competitors": competitors,
            "analysis": analysis,
            "strengths": strengths,
            "weaknesses": weaknesses or []
        }

    def generate_roi_calculator(self, investment: float, return_value: float,
                                 timeframe: str) -> Dict[str, Any]:
        """Calculate and generate ROI case study metrics."""

        roi = ((return_value - investment) / investment) * 100
        payback_months = (investment / (return_value / 12)) if return_value > 0 else 0

        return {
            "investment": f"${investment:,.2f}",
            "return_value": f"${return_value:,.2f}",
            "roi_percentage": f"{roi:.1f}%",
            "payback_period": f"{payback_months:.1f} months",
            "timeframe": timeframe,
            "summary": f"Within {timeframe}, this investment yielded a {roi:.1f}% return with payback achieved in approximately {payback_months:.1f} months."
        }

    def generate_metrics_summary(self, results: Dict[str, Any]) -> str:
        """Generate a formatted metrics summary."""

        summary = "## Key Results\n\n"
        summary += "| Metric | Value | Change |\n"
        summary += "|--------|-------|--------|\n"

        for metric, value in results.items():
            change = results.get(f"{metric}_change", "N/A")
            summary += f"| {metric} | {value} | {change} |\n"

        return summary

    def _generate_sections(self, company: str, industry: str, challenge: str,
                          solution: str, results: Dict, timeline: str) -> Dict[str, str]:
        """Generate all case study sections."""

        return {
            "executive_summary": f"This case study examines how {company} in the {industry} industry successfully addressed {challenge} through the implementation of {solution}, resulting in measurable improvements across key performance indicators within {timeline}.",
            "company_background": f"{company} is a company operating in the {industry} sector. With a focus on innovation and customer value, the company has established itself as a key player in its market.",
            "challenge": challenge,
            "solution": solution,
            "implementation": f"The solution was implemented over {timeline}, following a structured approach that prioritized minimal disruption and maximum impact. Key phases included planning, execution, and optimization.",
            "results": self._format_results(results),
            "lessons_learned": f"Key lessons from this case study include the importance of clear goals, stakeholder buy-in, and iterative optimization. Organizations undertaking similar initiatives should focus on measurable outcomes from the start.",
            "conclusion": f"{company}'s success demonstrates the value of strategic approach to problem-solving. The measurable results achieved validate the effectiveness of the chosen solution and provide a template for future initiatives."
        }

    def _format_results(self, results: Dict) -> str:
        """Format results section."""

        formatted = "The following measurable outcomes were achieved:\n\n"
        for key, value in results.items():
            formatted += f"- **{key}:** {value}\n"
        return formatted

    def _build_markdown(self, case_study: Dict) -> str:
        """Build full case study as markdown."""

        sections = case_study.get("sections", {})

        doc = f"""# {case_study.get('title', 'Case Study')}

**Company:** {case_study.get('company', '')}
**Industry:** {case_study.get('industry', '')}
**Date:** {case_study.get('date', '')}

---

## Executive Summary

{sections.get('executive_summary', '')}

---

## Company Background

{sections.get('company_background', '')}

---

## The Challenge

{sections.get('challenge', '')}

---

## The Solution

{sections.get('solution', '')}

---

## Implementation

{sections.get('implementation', '')}

---

## Results

{sections.get('results', '')}

---

## Lessons Learned

{sections.get('lessons_learned', '')}

---

## Conclusion

{sections.get('conclusion', '')}

---

*Case study generated on {datetime.now().strftime('%Y-%m-%d')}*
"""

        return doc


def main():
    parser = argparse.ArgumentParser(
        description="Case Study Agent — Generate business case studies",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--task", required=True,
                        choices=["case-study", "success-story", "competitive", "roi", "metrics"],
                        help="Task to perform")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--customer", help="Customer name (for success stories)")
    parser.add_argument("--industry", help="Industry")
    parser.add_argument("--challenge", help="The problem/challenge")
    parser.add_argument("--pain-point", help="Customer pain point")
    parser.add_argument("--solution", help="Solution implemented")
    parser.add_argument("--outcome", help="Outcome achieved")
    parser.add_argument("--product", help="Product name")
    parser.add_argument("--results", help="JSON string of results")
    parser.add_argument("--metrics", help='JSON string of metrics')
    parser.add_argument("--timeline", default="3 months", help="Implementation timeline")
    parser.add_argument("--competitors", help="Comma-separated competitor names")
    parser.add_argument("--strengths", help="Comma-separated strengths")
    parser.add_argument("--weaknesses", help="Comma-separated weaknesses")
    parser.add_argument("--investment", type=float, help="Investment amount")
    parser.add_argument("--return-value", dest="return_value", type=float, help="Return value")
    parser.add_argument("--timeframe", default="12 months", help="Timeframe")
    parser.add_argument("--input", help="Input JSON file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    agent = CaseStudyAgent()

    try:
        result = None

        if args.task == "case-study":
            if not args.company or not args.challenge:
                raise ValueError("--company and --challenge required")

            results = json.loads(args.results) if args.results else {}
            result = agent.generate_case_study(
                company_name=args.company,
                industry=args.industry or "General",
                challenge=args.challenge,
                solution=args.solution or "Strategic initiative",
                results=results,
                timeline=args.timeline
            )

        elif args.task == "success-story":
            if not args.customer or not args.product:
                raise ValueError("--customer and --product required")

            metrics = json.loads(args.metrics) if args.metrics else {"improvement": "significant"}
            result = agent.generate_customer_success_story(
                customer_name=args.customer,
                product=args.product,
                pain_point=args.pain_point or "operational challenges",
                outcome=args.outcome or "improved performance",
                metrics=metrics
            )

        elif args.task == "competitive":
            if not args.company or not args.competitors:
                raise ValueError("--company and --competitors required")

            competitors = args.competitors.split(",")
            strengths = args.strengths.split(",") if args.strengths else []
            weaknesses = args.weaknesses.split(",") if args.weaknesses else None

            result = agent.generate_competitive_analysis(
                company=args.company,
                competitors=competitors,
                strengths=strengths,
                weaknesses=weaknesses
            )

        elif args.task == "roi":
            if not args.investment or not args.return_value:
                raise ValueError("--investment and --return required")

            result = agent.generate_roi_calculator(
                investment=args.investment,
                return_value=args.return_value,
                timeframe=args.timeframe
            )

        elif args.task == "metrics":
            if not args.metrics:
                raise ValueError("--metrics required")

            metrics = json.loads(args.metrics)
            result = {"summary": agent.generate_metrics_summary(metrics)}

        if result:
            if args.output:
                with open(args.output, 'w') as f:
                    if args.format == "markdown":
                        if "full_document" in result:
                            f.write(result["full_document"])
                        elif "story" in result:
                            f.write(result["story"])
                        elif "analysis" in result:
                            f.write(result["analysis"])
                        else:
                            json.dump(result, f, indent=2)
                    else:
                        json.dump(result, f, indent=2)
                log.info(f"Output saved to {args.output}")
            else:
                if args.format == "markdown":
                    if "full_document" in result:
                        print(result["full_document"])
                    elif "story" in result:
                        print(result["story"])
                    elif "analysis" in result:
                        print(result["analysis"])
                    else:
                        print(json.dumps(result, indent=2))
                else:
                    print(json.dumps(result, indent=2))
            log.info("Task completed successfully")

    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Task failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
