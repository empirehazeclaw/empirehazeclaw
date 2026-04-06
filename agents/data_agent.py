#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          DATA ANALYSIS AGENT                                 ║
║          CSV/JSON · Stats · Charts · BI Reports             ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - CSV, JSON, Tabellen-Daten analysieren
  - Deskriptive Statistik (Mean, Median, StdDev, Quantile)
  - Korrelations- & Trend-Analyse
  - Chart-Beschreibungen
  - Business Intelligence Reports
  - Anomalie-Erkennung
  - SQL-Query Generierung
  - Natural Language → Insights

Hinweis: LLM-Routing wird NICHT verwendet
"""

from __future__ import annotations

import json
import logging
import math
import re
import statistics
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv
import io

log = logging.getLogger("openclaw.data")


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BOXPLOT = "boxplot"


@dataclass
class ColumnStats:
    """Statistiken für eine Datenspalte"""
    name: str
    dtype: str  # "numeric", "categorical", "datetime", "text"
    count: int
    null_count: int
    unique_count: int
    # Numeric
    mean: float = None
    median: float = None
    std_dev: float = None
    min_val: Any = None
    max_val: Any = None
    q25: float = None
    q75: float = None
    # Categorical
    top_values: List[tuple] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Ergebnis einer Datenanalyse"""
    row_count: int
    column_count: int
    columns: List[ColumnStats]
    correlations: Dict = field(default_factory=dict)
    anomalies: List[Dict] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    chart_suggestions: List[Dict] = field(default_factory=list)


class DataAgent:
    """
    Data Analysis Agent mit:
    - CSV/JSON Analysis
    - Statistics
    - Charts
    - Anomaly Detection
    - SQL Generation
    """
    
    def __init__(self):
        self.workspace = Path("/home/clawbot/.openclaw/workspace")
        
    def load_csv(self, content: str) -> List[Dict]:
        """Lade CSV Daten"""
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
    
    def load_json(self, content: str) -> List[Dict]:
        """Lade JSON Daten"""
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        return []
    
    def analyze_data(self, data: List[Dict]) -> AnalysisResult:
        """
        Analysiere Daten und generiere Insights
        """
        log.info(f"📊 Analysiere {len(data)} Zeilen...")
        
        if not data:
            return AnalysisResult(0, 0, [], {}, [], [])
        
        # Get columns
        columns = list(data[0].keys())
        row_count = len(data)
        column_count = len(columns)
        
        # Analyze each column
        column_stats = []
        for col in columns:
            stats = self.analyze_column(data, col)
            column_stats.append(stats)
        
        # Correlations
        correlations = self.calculate_correlations(data, column_stats)
        
        # Anomalies
        anomalies = self.detect_anomalies(column_stats)
        
        # Insights
        insights = self.generate_insights(column_stats, correlations)
        
        # Chart suggestions
        chart_suggestions = self.suggest_charts(column_stats)
        
        return AnalysisResult(
            row_count=row_count,
            column_count=column_count,
            columns=column_stats,
            correlations=correlations,
            anomalies=anomalies,
            insights=insights,
            chart_suggestions=chart_suggestions
        )
    
    def analyze_column(self, data: List[Dict], column: str) -> ColumnStats:
        """Analysiere eine einzelne Spalte"""
        values = [row.get(column) for row in data if row.get(column) is not None]
        
        # Determine type
        dtype = self.detect_dtype(values)
        
        # Basic stats
        stats = ColumnStats(
            name=column,
            dtype=dtype,
            count=len(values),
            null_count=len(data) - len(values),
            unique_count=len(set(values))
        )
        
        if dtype == "numeric":
            numeric_values = [float(v) for v in values if self.is_numeric(v)]
            if numeric_values:
                stats.mean = statistics.mean(numeric_values)
                stats.median = statistics.median(numeric_values)
                if len(numeric_values) > 1:
                    stats.std_dev = statistics.stdev(numeric_values)
                stats.min_val = min(numeric_values)
                stats.max_val = max(numeric_values)
                # Quantiles
                sorted_vals = sorted(numeric_values)
                n = len(sorted_vals)
                stats.q25 = sorted_vals[int(n * 0.25)]
                stats.q75 = sorted_vals[int(n * 0.75)]
        
        elif dtype == "categorical":
            # Top values
            value_counts = {}
            for v in values:
                value_counts[v] = value_counts.get(v, 0) + 1
            stats.top_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return stats
    
    def detect_dtype(self, values: List[Any]) -> str:
        """Erkenne Datentyp"""
        if not values:
            return "text"
        
        # Check if numeric
        numeric_count = sum(1 for v in values if self.is_numeric(v))
        if numeric_count > len(values) * 0.8:
            return "numeric"
        
        # Check if datetime
        datetime_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}.\d{2}.\d{4}'
        datetime_count = sum(1 for v in values if re.match(datetime_pattern, str(v)))
        if datetime_count > len(values) * 0.8:
            return "datetime"
        
        # Check unique ratio (categorical vs text)
        unique_ratio = len(set(values)) / len(values)
        if unique_ratio < 0.5:
            return "categorical"
        
        return "text"
    
    def is_numeric(self, value: Any) -> bool:
        """Prüfe ob Wert numerisch ist"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def calculate_correlations(self, data: List[Dict], column_stats: List[ColumnStats]) -> Dict:
        """Berechne Korrelationen zwischen numerischen Spalten"""
        correlations = {}
        
        numeric_cols = [c for c in column_stats if c.dtype == "numeric"]
        
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                # Get values
                vals1 = []
                vals2 = []
                for row in data:
                    v1 = row.get(col1.name)
                    v2 = row.get(col2.name)
                    if self.is_numeric(v1) and self.is_numeric(v2):
                        vals1.append(float(v1))
                        vals2.append(float(v2))
                
                if len(vals1) > 2:
                    corr = self.pearson_correlation(vals1, vals2)
                    if abs(corr) > 0.5:  # Only significant correlations
                        correlations[f"{col1.name}_vs_{col2.name}"] = corr
        
        return correlations
    
    def pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Berechne Pearson Korrelation"""
        n = len(x)
        if n == 0:
            return 0
        
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
        
        if denom_x == 0 or denom_y == 0:
            return 0
        
        return numerator / (denom_x * denom_y)
    
    def detect_anomalies(self, column_stats: List[ColumnStats]) -> List[Dict]:
        """Erkenne Anomalien in den Daten"""
        anomalies = []
        
        for col in column_stats:
            if col.dtype == "numeric" and col.std_dev:
                # Z-Score based anomalies
                values = []  # Would need original data
                
                # Simple outlier detection via IQR
                if col.q25 and col.q75:
                    iqr = col.q75 - col.q25
                    lower = col.q25 - 1.5 * iqr
                    upper = col.q75 + 1.5 * iqr
                    
                    if col.min_val < lower or col.max_val > upper:
                        anomalies.append({
                            "column": col.name,
                            "type": "outlier",
                            "description": f"Outliers detected (IQR method)"
                        })
        
        return anomalies
    
    def generate_insights(self, column_stats: List[ColumnStats], correlations: Dict) -> List[str]:
        """Generiere Insights aus den Daten"""
        insights = []
        
        # Column-based insights
        for col in column_stats:
            if col.dtype == "numeric" and col.mean is not None:
                insights.append(f"{col.name}: Durchschnitt = {col.mean:.2f}")
                
                if col.std_dev and col.std_dev > col.mean * 0.5:
                    insights.append(f"{col.name}: Hohe Variabilität (StdDev > 50% des Mittelwerts)")
            
            elif col.dtype == "categorical" and col.top_values:
                top = col.top_values[0]
                insights.append(f"{col.name}: Meistens '{top[0]}' ({top[1]}x)")
        
        # Correlation insights
        for corr_key, corr_value in correlations.items():
            direction = "positiv" if corr_value > 0 else "negativ"
            strength = "stark" if abs(corr_value) > 0.7 else "moderat"
            insights.append(f"{corr_key}: {strength}e {direction}e Korrelation ({corr_value:.2f})")
        
        return insights
    
    def suggest_charts(self, column_stats: List[ColumnStats]) -> List[Dict]:
        """Schlage passende Charts vor"""
        suggestions = []
        
        numeric_cols = [c for c in column_stats if c.dtype == "numeric"]
        categorical_cols = [c for c in column_stats if c.dtype == "categorical"]
        
        # Numeric + Numeric = Scatter
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "scatter",
                "x": numeric_cols[0].name,
                "y": numeric_cols[1].name,
                "description": "Zeigt Beziehung zwischen zwei numerischen Werten"
            })
        
        # Categorical = Pie/Bar
        for col in categorical_cols[:2]:
            if col.unique_count <= 10:
                suggestions.append({
                    "type": "pie",
                    "column": col.name,
                    "description": f"Verteilung von {col.name}"
                })
            else:
                suggestions.append({
                    "type": "bar",
                    "column": col.name,
                    "description": f"Top Werte von {col.name}"
                })
        
        # Numeric = Histogram/Boxplot
        for col in numeric_cols[:2]:
            suggestions.append({
                "type": "histogram",
                "column": col.name,
                "description": f"Verteilung von {col.name}"
            })
        
        return suggestions
    
    def generate_sql(self, question: str, schema: Dict) -> str:
        """Generiere SQL Query basierend auf Frage"""
        # Simple pattern matching
        question_lower = question.lower()
        
        # Detect operation
        if "sum" in question_lower or "total" in question_lower:
            agg = "SUM"
        elif "average" in question_lower or "mean" in question_lower:
            agg = "AVG"
        elif "count" in question_lower:
            agg = "COUNT"
        elif "max" in question_lower:
            agg = "MAX"
        elif "min" in question_lower:
            agg = "MIN"
        else:
            agg = "SELECT * FROM"
        
        # Detect table
        table = schema.get("table", "data")
        
        # Detect column
        column = schema.get("column", "*")
        
        # Detect filter
        filters = []
        if "where" in question_lower:
            for col in schema.get("columns", []):
                if col in question_lower:
                    filters.append(f"{col} = 'value'")
        
        sql = f"SELECT {agg}({column}) FROM {table}"
        
        if filters:
            sql += " WHERE " + " AND ".join(filters)
        
        return sql
    
    def generate_report(self, result: AnalysisResult) -> str:
        """Generiere BI Report"""
        report = f"""
📊 DATA ANALYSIS REPORT
{'='*40}

DATASET:
  Rows: {result.row_count:,}
  Columns: {result.column_count}

COLUMNS:
"""
        for col in result.columns:
            report += f"\n  {col.name} ({col.dtype}):\n"
            report += f"    - Count: {col.count:,}\n"
            report += f"    - Null: {col.null_count:,}\n"
            report += f"    - Unique: {col.unique_count:,}\n"
            
            if col.dtype == "numeric" and col.mean is not None:
                report += f"    - Mean: {col.mean:.2f}\n"
                report += f"    - Median: {col.median:.2f}\n"
                report += f"    - StdDev: {col.std_dev:.2f}\n"
                report += f"    - Range: {col.min_val} - {col.max_val}\n"
            
            elif col.dtype == "categorical" and col.top_values:
                report += f"    - Top: {', '.join([f'{v[0]}({v[1]})' for v in col.top_values[:3]])}\n"
        
        if result.correlations:
            report += f"\nCORRELATIONS:\n"
            for key, val in result.correlations.items():
                report += f"  {key}: {val:.3f}\n"
        
        if result.insights:
            report += f"\nKEY INSIGHTS:\n"
            for insight in result.insights[:5]:
                report += f"  • {insight}\n"
        
        if result.chart_suggestions:
            report += f"\nCHART SUGGESTIONS:\n"
            for chart in result.chart_suggestions[:3]:
                report += f"  - {chart['type']}: {chart['description']}\n"
        
        return report


async def main():
    """CLI Test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Agent")
    parser.add_argument("--file", help="CSV/JSON file to analyze")
    parser.add_argument("--sample", action="store_true", help="Use sample data")
    
    args = parser.parse_args()
    
    agent = DataAgent()
    
    if args.sample:
        # Sample data
        data = [
            {"name": "Product A", "sales": 100, "category": "Electronics"},
            {"name": "Product B", "sales": 150, "category": "Electronics"},
            {"name": "Product C", "sales": 80, "category": "Clothing"},
            {"name": "Product D", "sales": 200, "category": "Electronics"},
            {"name": "Product E", "sales": 50, "category": "Clothing"},
        ]
    else:
        data = []
    
    if data:
        result = agent.analyze_data(data)
        print(agent.generate_report(result))
    
    print("\n✅ Data Agent ready")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
