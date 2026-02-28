"""
NyayVandan - Ethical Review Module
=====================================
Pipeline Stage 6: Ethical & Bias Checks

Evaluates the retrieved precedent set for potential biases:
  1. Precedent Diversity Score (court diversity, temporal spread)
  2. Demographic / Legal Skew Detection
  3. Constitutional Alignment Notes

⚠️ These are FLAGS for judicial awareness — not directives.
"""

from backend.config import (
    DIVERSITY_THRESHOLD,
    MIN_COURT_DIVERSITY,
    MIN_YEAR_RANGE,
)


def compute_diversity_score(results: list) -> dict:
    """
    Compute a diversity score for the retrieved precedent set.
    
    Measures:
      - Court diversity: How many distinct courts are represented
      - Temporal diversity: Year range of retrieved cases
      - Outcome diversity: Variety in judgment outcomes
    
    Args:
        results: List of retrieved case dicts
    
    Returns:
        Dict with diversity metrics and overall score
    """
    if not results:
        return {
            "overall_score": 0.0,
            "court_diversity": 0.0,
            "temporal_diversity": 0.0,
            "outcome_diversity": 0.0,
            "details": {}
        }
    
    n = len(results)
    
    # --- Court Diversity ---
    courts = [r.get("court", "Unknown") for r in results]
    unique_courts = set(courts)
    court_diversity = len(unique_courts) / n if n > 0 else 0
    
    # --- Temporal Diversity ---
    years = [r.get("year", 0) for r in results if r.get("year", 0) > 0]
    if len(years) >= 2:
        year_range = max(years) - min(years)
        temporal_diversity = min(year_range / 10.0, 1.0)  # Normalize: 10+ year range = 1.0
    else:
        temporal_diversity = 0.0
    
    # --- Outcome Diversity ---
    outcomes = [r.get("judgment_outcome", "Unknown") for r in results]
    unique_outcomes = set(outcomes)
    outcome_diversity = len(unique_outcomes) / n if n > 0 else 0
    
    # --- Overall Score (weighted average) ---
    overall = (
        0.40 * court_diversity +
        0.30 * temporal_diversity +
        0.30 * outcome_diversity
    )
    
    return {
        "overall_score": round(overall, 4),
        "court_diversity": round(court_diversity, 4),
        "temporal_diversity": round(temporal_diversity, 4),
        "outcome_diversity": round(outcome_diversity, 4),
        "details": {
            "courts_represented": sorted(unique_courts),
            "year_range": f"{min(years)}-{max(years)}" if years else "N/A",
            "outcomes_found": sorted(unique_outcomes),
            "total_cases": n
        }
    }


def check_bias_indicators(results: list) -> list:
    """
    Scan retrieved precedents for potential bias indicators.
    
    Flags:
      - Single-court dominance
      - All same outcome (confirmation bias risk)
      - Narrow temporal window
      - Single jurisdiction / state focus
    
    Args:
        results: List of retrieved case dicts
    
    Returns:
        List of warning dicts
    """
    warnings = []
    
    if not results:
        return warnings
    
    n = len(results)
    
    # --- Check: Single Court Dominance ---
    courts = [r.get("court", "Unknown") for r in results]
    unique_courts = set(courts)
    
    if len(unique_courts) < MIN_COURT_DIVERSITY and n >= 3:
        dominant = max(set(courts), key=courts.count)
        warnings.append({
            "type": "COURT_DOMINANCE",
            "severity": "MEDIUM",
            "message": f"All/most precedents are from {dominant}. "
                       f"Consider reviewing judgments from other High Courts or the Supreme Court "
                       f"for a more balanced perspective.",
            "recommendation": "Cross-reference with other jurisdictions"
        })
    
    # --- Check: Outcome Homogeneity (Confirmation Bias Risk) ---
    outcomes = [r.get("judgment_outcome", "") for r in results]
    unique_outcomes = set(outcomes)
    
    if len(unique_outcomes) == 1 and n >= 3:
        warnings.append({
            "type": "OUTCOME_HOMOGENEITY",
            "severity": "HIGH",
            "message": f"All {n} retrieved precedents resulted in '{outcomes[0]}'. "
                       f"This may indicate confirmation bias in retrieval. "
                       f"Judicial discretion should account for contrary precedents.",
            "recommendation": "Actively seek contrary / distinguishing precedents"
        })
    
    # --- Check: Narrow Temporal Window ---
    years = [r.get("year", 0) for r in results if r.get("year", 0) > 0]
    if len(years) >= 2:
        year_range = max(years) - min(years)
        if year_range < MIN_YEAR_RANGE:
            warnings.append({
                "type": "TEMPORAL_NARROWNESS",
                "severity": "LOW",
                "message": f"Retrieved cases span only {year_range} year(s) ({min(years)}-{max(years)}). "
                           f"Older landmark precedents may provide additional legal grounding.",
                "recommendation": "Consider expanding search to include landmark older cases"
            })
    
    # --- Check: Legal Section Concentration ---
    all_ipc = []
    for r in results:
        ipc = str(r.get("ipc_sections", ""))
        if ipc:
            all_ipc.extend([s.strip() for s in ipc.split(",") if s.strip()])
    
    if all_ipc:
        from collections import Counter
        ipc_counts = Counter(all_ipc)
        most_common = ipc_counts.most_common(1)[0]
        if most_common[1] == n and n >= 3:
            warnings.append({
                "type": "SECTION_CONCENTRATION",
                "severity": "LOW",
                "message": f"IPC Section {most_common[0]} appears in all retrieved cases. "
                           f"Consider whether related provisions or alternative charges are relevant.",
                "recommendation": "Review if allied provisions apply"
            })
    
    return warnings


def generate_constitutional_notes(results: list, query_entities: dict) -> list:
    """
    Generate constitutional alignment notes for judicial consideration.
    
    Maps constitutional articles in the query/results to their fundamental
    rights/principles for judge-readable context.
    
    Args:
        results: Retrieved case results
        query_entities: Extracted entities from query
    
    Returns:
        List of constitutional alignment notes
    """
    # Mapping of constitutional articles to their rights/principles
    ARTICLE_MAP = {
        "14": "Equality before law / Equal protection of laws",
        "15": "Prohibition of discrimination on grounds of religion, race, caste, sex, place of birth",
        "19": "Protection of fundamental freedoms (speech, assembly, movement, profession)",
        "20": "Protection in respect of conviction for offences (double jeopardy, self-incrimination)",
        "21": "Right to life and personal liberty",
        "21A": "Right to education",
        "22": "Protection against arrest and detention",
        "25": "Freedom of conscience and free profession, practice, and propagation of religion",
        "32": "Right to constitutional remedies",
        "39": "Certain principles of policy to be followed by the State",
        "43": "Living wage, conditions of work, and decent standard of life",
        "48A": "Protection and improvement of environment and safeguarding forests",
        "51A": "Fundamental duties of citizens",
        "244": "Administration of Scheduled Areas and Tribal Areas",
        "300A": "Right to property — no person shall be deprived without authority of law",
        "311": "Dismissal, removal, or reduction in rank of civil servants",
    }
    
    notes = []
    
    # Collect all referenced articles
    all_articles = set()
    
    # From query
    for art in query_entities.get("Constitutional_Articles", []):
        # Extract number from "Article 14" → "14"
        num = art.replace("Article", "").strip()
        all_articles.add(num)
    
    # From results
    for r in results:
        articles_str = str(r.get("constitutional_articles", ""))
        if articles_str:
            for a in articles_str.split(","):
                a = a.strip()
                if a:
                    all_articles.add(a)
    
    for art_num in sorted(all_articles):
        if art_num in ARTICLE_MAP:
            notes.append({
                "article": f"Article {art_num}",
                "principle": ARTICLE_MAP[art_num],
                "note": f"Article {art_num} of the Constitution of India guarantees: "
                        f"{ARTICLE_MAP[art_num]}. This principle is relevant to the "
                        f"current case analysis."
            })
    
    return notes


def run_ethical_review(results: list, query_entities: dict) -> dict:
    """
    Full ethical review pipeline for retrieved precedents.
    
    Combines diversity scoring, bias detection, and constitutional alignment.
    
    Args:
        results: List of retrieved case dicts
        query_entities: Extracted entities from query
    
    Returns:
        Complete ethical review dict
    """
    diversity = compute_diversity_score(results)
    warnings = check_bias_indicators(results)
    constitutional_notes = generate_constitutional_notes(results, query_entities)
    
    # Overall ethical flag
    has_concerns = (
        diversity["overall_score"] < DIVERSITY_THRESHOLD or
        any(w["severity"] == "HIGH" for w in warnings)
    )
    
    return {
        "diversity_score": diversity,
        "bias_warnings": warnings,
        "constitutional_alignment": constitutional_notes,
        "has_ethical_concerns": has_concerns,
        "review_summary": (
            "⚠️ Ethical concerns detected in the retrieved precedent set. "
            "Please review bias warnings and consider expanding the search scope."
            if has_concerns else
            "✅ Retrieved precedents appear reasonably diverse. "
            "Standard judicial discretion applies."
        ),
        "disclaimer": (
            "This ethical review is advisory only. It surfaces potential biases "
            "for judicial awareness and does not constitute a recommendation or directive."
        )
    }
