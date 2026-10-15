# README.md
This document contains a brief project review and summary. A more detailed project specification is provided in the sibling document `PROJECT.md`. 

## Project Review

The project specification comprises a principled, engineering-first approach to Polyscope summary file logs analysis and reporting by treating the logs themselves as the authoritative source of the domain model, with `Drain3` acting as the core analytical engine rather than relying on brittle, hard-coded regex taxonomies.

## Project Summary: Goals and Objectives

The primary goals and objectives outlined in the specification include:

- Template-First Log Mining:

    Integrate Drain3 to perform online log-template mining, clustering, masking, and parameter extraction on Universal Robots Polyscope support logs.

    Discover and preserve natural message structures while retaining meaningful variable parameters (such as error codes, states, and measurements) without fragmenting templates.

- Evidence-Based Diagnostic Architecture:

    Maintain full traceability from high-level findings and workbook summaries back to original raw log records, timestamps, logger classes, and threads.

    Discard rigid, predetermined event taxonomies in favor of discovering actual operational behaviors, anomalies, and temporal sequences.

- Domain-Specific Interpretation:

    Accurately handle complex log framing, including multiline stack traces, controller commands, and embedded payloads.

    Provide dedicated interpretation for structured safety-related records (e.g., RobotMode states, safety stops, and operational modes) while keeping template analysis primary.

    Model temporal correlations (e.g., sequences preceding faults) and component hierarchies based on logger classes.

- Actionable Excel Reporting:

    Deliver a multi-sheet diagnostic Excel workbook designed for maintenance engineers.

    Include essential views such as an Executive Summary, Template Catalog, Event Timeline, Component Analysis, Parameter Analysis, Errors/Warnings, Temporal Correlations, and a traceable Evidence Index.

    Ensure spreadsheet safety (protection against formula injection) and incorporate privacy safeguards for sensitive parameters.

- Robust Engineering & Reproducibility:

    Support both isolated bundle analysis (default, fresh miner per session) and longitudinal opt-in analysis (versioned state).

    Implement a modular Python architecture accompanied by a comprehensive automated test suite.

    Follow the recommended vertical-slice implementation strategy: establish the record schema and Drain3 lifecycle first, proving the complete pipeline from raw log to mined template and Excel row before expanding features or designing isolated UI layouts.

## References
*logpai/drain3*
[github | logpai/drain3](https://github.com/logpai/Drain3)

*uv/docs*
[astral docs | uv](https://docs.astral.sh/uv/)
