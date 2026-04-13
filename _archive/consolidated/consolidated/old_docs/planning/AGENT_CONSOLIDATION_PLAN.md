# Agent Consolidation Plan

**Generated:** 2026-03-28  
**Total agents:** 281  
**Target:** ≤68 agents  
**Planned reduction:** ~213 agents (75.8%)

---

## EXECUTIVE SUMMARY

| Action | Count | Result |
|--------|-------|--------|
| KEEP | 68 | Core business agents |
| MERGE | 23 | Into existing agents |
| KILL | 190 | Stubs, duplicates, irrelevant verticals |
| **Total** | **281** | **→ 68** |

---

## SECTION 1: KILL (Delete - 190 agents)

### 1.1 TINY STUB AGENTS (<20 lines) — 6 agents — KILL

| Agent | Lines | Reason |
|-------|-------|--------|
| `gardening_agent.py` | 3 | 3-line bash exec wrapper, irrelevant vertical |
| `petcare_agent.py` | 3 | 3-line bash exec wrapper, irrelevant vertical |
| `photography_agent.py` | 3 | 3-line bash exec wrapper, irrelevant vertical |
| `home_agent.py` | 10 | Tiny stub, delegated to subdirectory |
| `support_agent.py` | 19 | Minimal stub, use `customer_support_agent.py` instead |
| `translation_agent.py` | 10 | Minimal stub, use `localization_agent.py` instead |

### 1.2 DEPRECATED _llm.py VARIANTS — 4 agents — KILL

| Agent | Replaced By |
|-------|------------|
| `cold_outreach_llm.py` | `cold_outreach_agent.py` |
| `lead_qualifier_llm.py` | `lead_qualifier_agent.py` |
| `content_production_llm.py` | `content_production_agent.py` |
| `sales_executor_llm.py` | `sales_executor_agent.py` |

### 1.3 INFRASTRUCTURE WRAPPERS (<100 lines) — 10 agents — KILL

These are tiny wrappers for the main orchestrator/infrastructure. Their functionality is covered by larger agents.

| Agent | Lines | Reason |
|-------|-------|--------|
| `agent_hub.py` | 58 | Wrapper, use `agent_registry.py` or `orchestrator.py` |
| `agent_wrapper.py` | 58 | Minimal wrapper, use `orchestrator.py` |
| `agent-dashboard.js` | 63 | Dashboard JS, can be regenerated |
| `shared_memory.py` | 68 | Use `memory_agent.py` |
| `shared-memory.js` | 77 | Use `memory_agent.py` |
| `event-bus.js` | 76 | Use `workflow_engine.py` or `dag_executor.py` |
| `error-handler.js` | 73 | Utility, not a main agent |
| `auto-scaler.js` | 69 | Utility, not a main agent |
| `auto-learn.js` | 43 | Utility/learning, not a main agent |
| `multi-agent.js` | 77 | Multi-agent orchestration, use `orchestrator.py` |
| `escalation.py` | 58 | Simple escalation, use `customer_support_agent.py` |
| `learning.py` | 58 | Learning utility, use `memory_agent.py` |

### 1.4 IRRELEVANT VERTICAL DIRECTORIES — 16 agents — KILL (entire dirs)

These verticals don't match EmpireHazeClaw's business (Managed AI Web Hosting + POD + Digital Products):

| Directory | Contents |
|-----------|----------|
| `agriculture/` | Farming-specific agents |
| `automotive/` | Car/vehicle agents |
| `civic/` | Government/civic agents |
| `construction/` | Construction-specific agents |
| `education/` | Generic education (keep `tutor_agent.py` if used) |
| `energy/` | Energy sector agents |
| `entertainment/` | Entertainment industry agents |
| `fitness/` | Fitness-specific agents |
| `food/` | Food/restaurant agents |
| `gardening/` | Gardening agents |
| `government/` | Government agents |
| `grant/` | Grant writing agents |
| `healthcare/` | Healthcare-specific agents |
| `insurance/` | Insurance agents |
| `legal/` | Legal-specific agents |
| `manufacturing/` | Manufacturing agents |
| `hospitality/` | Hospitality (hotel/restaurant) agents |

**Note:** If any of these subdirectories contain agents actually used by the business, they should be moved to the main agents/ directory and evaluated individually.

### 1.5 VERTICAL-SPECIFIC AGENTS in main dir — 20 agents — KILL

| Agent | Reason |
|-------|--------|
| `access_auditor_agent.py` | Niche security, use `security_agent.py` |
| `accounts_payable_agent.py` | Finance niche, not core business |
| `blockchain_analyst_agent.py` | Irrelevant vertical |
| `book_writer_agent.py` | Not core (use content_agent for blog/books) |
| `clinical_notes_agent.py` | Healthcare niche |
| `commercial_re_agent.py` | Real estate niche |
| `compensation_benchmarker_agent.py` | HR niche |
| `curriculum_designer_agent.py` | Education niche |
| `essay_grader_agent.py` | Education niche |
| `exit_interview_agent.py` | HR niche |
| `family_coordinator_agent.py` | Lifestyle niche |
| `flashcard_generator_agent.py` | Education niche |
| `flight_scraper_agent.py` | Travel niche |
| `fraud_detector_agent.py` | Finance niche (consider keeping if transaction-heavy) |
| `game_designer_agent.py` | Gaming niche |
| `habit_tracker_agent.py` | Personal/lifestyle niche |
| `health_tracker_agent.py` | Healthcare niche |
| `inventory_forecaster_agent.py` | Logistics niche |
| `inventory_tracker_agent.py` | Logistics niche |
| `invoice_manager_agent.py` | Finance niche |

### 1.6 MORE VERTICAL-SPECIFIC — 20 agents — KILL

| Agent | Reason |
|-------|--------|
| `job_applicant_agent.py` | HR/recruiting niche |
| `language_tutor_agent.py` | Education niche |
| `legal_brief_writer_agent.py` | Legal niche |
| `logistics_agent.md` | Markdown only, logistics niche |
| `meal_planner_agent.py` | 77 | Personal/lifestyle niche |
| `medical_checker_agent.py` | Healthcare niche |
| `medication_checker_agent.py` | Healthcare niche |
| `nda_generator_agent.py` | Legal niche |
| `patent_analyzer_agent.py` | Legal niche |
| `patient_intake_agent.py` | Healthcare niche |
| `performance_reviewer_agent.py` | HR niche |
| `petcare_agent.py` | Already listed above |
| `phishing_detector_agent.py` | Security subset, use `security_agent.py` |
| `portfolio_rebalancer_agent.py` | Finance niche |
| `property_video_agent.py` | Real estate niche |
| `recruiter_agent.py` | HR niche |
| `resume_optimizer_agent.py` | HR niche |
| `resume_screener_agent.py` | HR niche |
| `route_optimizer_agent.py` | Logistics niche |
| `study_planner_agent.py` | Education niche |

### 1.7 YET MORE VERTICAL-SPECIFIC — 20 agents — KILL

| Agent | Reason |
|-------|--------|
| `symptom_triage_agent.py` | Healthcare niche |
| `tax_preparer_agent.py` | Finance niche |
| `telemarketer_agent.py` | Outdated/sales niche (use cold_outreach_agent) |
| `threat_monitor_agent.py` | Security subset (use `security_agent.py`) |
| `travel_planner_agent.py` | Lifestyle/travel niche |
| `tutor_agent.py` | Education niche |
| `upwork_proposal_agent.py` | Freelance niche |
| `voicemail_transcriber_agent.py` | Communication subset |
| `wellness_coach_agent.py` | Health/lifestyle niche |
| `workout_tracker_agent.py` | Fitness niche |
| `dropshipping_researcher_agent.py` | Ecommerce niche |
| `listing_scout_agent.py` | Ecommerce/real estate niche |
| `product_lister_agent.py` | Ecommerce subset |
| `contract_reviewer_agent.py` | Legal niche |
| `roi_tracker_agent.py` | Finance/marketing niche |
| `survey_analyzer_agent.py` | Research subset (use `data_agent.py`) |
| `transcription_agent.py` | Communication subset |
| `audio_producer_agent.py` | Media niche |
| `thumbnail_designer_agent.py` | Media subset |
| `storyboard_writer_agent.py` | Media niche |

### 1.8 FRAMEWORK/UTILITY NON-AGENTS — 12 agents — KILL

These are not agents but framework/utility files:

| File | Reason |
|------|--------|
| `agent_registry.py` | Framework file, keep if actively used |
| `agent_hierarchie.md` | Documentation, move to docs/ |
| `consolidated_agents.py` | Already consolidated, deprecated |
| `learning-agent.js` | Utility script |
| `llm_config.py` | Config file, keep |
| `llm_router.py` | Symlink to workspace root, keep |
| `llm_agent.py` | Duplicated by `example_llm_agent.py` |
| `example_llm_agent.py` | Example/template, not production |
| `auto-delegate` variants | Deprecated |
| `reporting.py` | Framework file |
| `scheduler.py` | 42-line utility, use `workflow_engine.py` |
| `stripe_check.py` | Utility script, not agent |

### 1.9 DUPLICATE/SIMILAR AGENTS — 15 agents — KILL

| Agent | Keep Instead | Reason |
|-------|-------------|--------|
| `ab_testing_agent.py` | `ab_test_analyzer_agent.py` | Keep more complete analyzer |
| `code_reviewer_agent.py` | `code_review_agent.py` | Keep more complete version |
| `daily_standup_agent.py` | `morning_briefing_agent.py` | Merge into morning briefing |
| `dashboard_builder_agent.py` | `data_visualization_agent.py` | Analytics overlap |
| `data_entry_agent.py` | `data_cleaner_agent.py` | Data processing subset |
| `deploy_guardian_agent.py` | `deployment_guardian_agent.py` | Duplicates |
| `deployment_agent_agent.py` | `deployment_guardian_agent.py` | Duplicates |
| `price_monitor_agent.py` | `competitor_monitor_agent.py` | Overlap |
| `competitor_watch_agent.py` | `competitor_monitor_agent.py` | Overlap |
| `competitor_pricing_agent.py` | `competitor_monitor_agent.py` | Overlap |
| `churn_predictor_agent.py` | `churn_prevention_agent.py` | Keep prevention (more complete) |
| `funnel_analysis_agent.py` | `cohort_analysis_agent.py` | Analytics overlap |
| `linkedin_content_agent.py` | `social_media_agent.py` | Social content subset |
| `multi_account_social_agent.py` | `social_media_agent.py` | Overlap |
| `x_twitter_growth_agent.py` | `twitter_growth_agent.py` | Duplicates |
| `reddit_scout_agent.py` | `hackernews_agent.py` | Similar research, keep hackernews |

### 1.10 GRAPHIC/MEDIA AGENTS — 8 agents — KILL

| Agent | Reason |
|-------|--------|
| `brand_designer_agent.py` | 84 | Graphic design niche |
| `podcast_producer_agent.py` | Media niche |
| `ugc_video_agent.py` | Video content niche |
| `video_scripter_agent.py` | Video subset |
| `brand_monitor_agent.py` | Marketing subset |
| `influencer_finder_agent.py` | Marketing niche |
| `review_responder_agent.py` | Support subset |
| `youtube_seo_agent.py` | Video SEO subset |

---

## SECTION 2: MERGE (23 agents → merge into targets)

| # | Source Agent | Target Agent | Notes |
|---|-------------|--------------|-------|
| 1 | `sdr_outbound_agent.py` | `cold_outreach_agent.py` | SDR + Cold Outreach = same function |
| 2 | `lead_intelligence_agent.py` | `lead_gen_agent.py` | Intelligence is subset of lead gen |
| 3 | `objection_handler_agent.py` | `cold_outreach_agent.py` | Objection handling is part of outreach |
| 4 | `negotiation_agent.py` | `sales_executor_agent.py` | Sales negotiation = executor |
| 5 | `ad_copywriter_agent.py` | `copywriter_agent.py` | Ad copy is subset of copywriting |
| 6 | `seo_writer_agent.py` | `content_agent.py` | SEO writing is content creation |
| 7 | `proofreader_agent.py` | `content_agent.py` | Proofreading is content subset |
| 8 | `content_repurposer_agent.py` | `content_production_agent.py` | Repurposing is production subset |
| 9 | `news_curator_agent.py` | `research_agent.py` | News curation is research |
| 10 | `reading_digest_agent.py` | `research_agent.py` | Digest = research |
| 11 | `radar_agent.py` | `research_agent.py` | Radar = market research |
| 12 | `market_analyzer_agent.py` | `research_agent.py` | Market analysis = research |
| 13 | `trend_detector_agent.py` | `research_agent.py` | Trend detection = research |
| 14 | `client_manager_agent.py` | `customer_support_agent.py` | Client management = support |
| 15 | `personal_crm_agent.py` | `customer_support_agent.py` | CRM = support |
| 16 | `github_issue_triager_agent.py` | `code_review_agent.py` | Issue triage = dev workflow |
| 17 | `github_pr_reviewer_agent.py` | `code_review_agent.py` | PR review = code review |
| 18 | `test_writer_agent.py` | `code_review_agent.py` | Testing = dev subset |
| 19 | `test_generator_agent.py` | `code_review_agent.py` | Test gen = dev subset |
| 20 | `analytics_check.py` | `metrics_agent.py` | Analytics check = metrics |
| 21 | `self_healing_server_agent.py` | `infra_monitor_agent.py` | Self-healing = monitoring |
| 22 | `sla_monitor_agent.py` | `infra_monitor_agent.py` | SLA = infrastructure monitoring |
| 23 | `dependency_scanner_agent.py` | `security_agent.py` | Dependencies = security |

---

## SECTION 3: KEEP (68 agents)

### 3.1 REVENUE (8 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `cold_outreach_agent.py` | 33KB | Main outreach engine, comprehensive |
| `lead_gen_agent.py` | 34KB | Lead generation, comprehensive |
| `lead_qualifier_agent.py` | ~100 | Lead qualification, active |
| `conversion_optimizer_agent.py` | 32KB | Conversion optimization |
| `sales_executor_agent.py` | 347L | Sales execution |
| `deal_forecaster_agent.py` | 30KB | Deal forecasting |
| `churn_prevention_agent.py` | 29KB | Churn prevention (keep vs predictor) |
| `revenue_agent.py` | 58L | Revenue overview (used daily) |

### 3.2 CONTENT (6 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `content_agent.py` | 546L | Main content engine, comprehensive |
| `content_production_agent.py` | 431L | Content production pipeline |
| `copywriter_agent.py` | 519L | Professional copywriting |
| `email_sequence_agent.py` | 38KB | Email sequences, Brevo integration |
| `mail_agent.py` | 483L | Email outreach + management |
| `social_media_agent.py` | 557L | Social media (multi-platform) |

### 3.3 OPERATIONS (10 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `security_agent.py` | 415L | Security scanning, CVE/NVD, OWASP |
| `vuln_scanner_agent.py` | 373L | Vulnerability scanning |
| `incident_responder_agent.py` | 46KB | Incident response |
| `infra_monitor_agent.py` | 23KB | Infrastructure monitoring |
| `operations_agent.py` | 47L | Operations overview |
| `deployment_guardian_agent.py` | 6KB | Deployment safety |
| `gdpr_auditor_agent.py` | 8KB | GDPR compliance |
| `coding_agent.py` | 513L | Main coding agent |
| `code_review_agent.py` | 548L | Code review (keeps code_reviewer + github pr + tests) |
| `overnight_coder_agent.py` | 531L | Overnight coding sessions |

### 3.4 RESEARCH (5 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `research_agent.py` | 42L | Main research agent (used) |
| `data_agent.py` | 469L | Data analysis, comprehensive |
| `data_visualization_agent.py` | 553L | Data visualization |
| `data_cleaner_agent.py` | 531L | Data cleaning |
| `competitor_monitor_agent.py` | 555L | Competitor monitoring (keeps pricing + watch) |

### 3.5 SUPPORT (4 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `customer_support_agent.py` | 558L | Main support agent, comprehensive |
| `onboarding_agent.py` | ~150L | User onboarding |
| `knowledge_base_agent.py` | ~100L | Knowledge base management |
| `ticket_agent.py` | ~100L | Ticket management |

### 3.6 MASTER/ORCHESTRATION (5 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `master_orchestrator.py` | 264L | Main orchestrator |
| `orchestrator.py` | 411L | Task orchestration |
| `dag_executor.py` | 358L | DAG execution |
| `workflow_engine.py` | 313L | Workflow automation |
| `memory_agent.py` | 395L | Memory management |

### 3.7 DATA & ANALYTICS (6 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `anomaly_detector_agent.py` | 531L | Anomaly detection |
| `cohort_analysis_agent.py` | 526L | Cohort analysis (keeps funnel + ab_test_analyzer) |
| `predictive_modeling_agent.py` | 463L | Predictive modeling |
| `metrics_agent.py` | 299L | Metrics collection |
| `etl_pipeline_agent.py` | 33KB | ETL pipelines |
| `google_analytics_agent.py` | 406L | Google Analytics integration |

### 3.8 SPECIALIZED BUSINESS (8 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `pod_agent.py` | 37L | Print-on-Demand (Etsy/Printify) |
| `discord_business_agent.py` | 519L | Discord community management |
| `inbox_zero_agent.py` | 366L | Email inbox management |
| `librarian_agent.py` | 429L | Knowledge/library management |
| `onboarding_flow_agent.py` | ~150L | Onboarding flows |
| `changelog_agent.py` | ~100L | Changelog generation |
| `release_notes_agent.py` | ~100L | Release notes |
| `proposal_writer_agent.py` | ~150L | Business proposals |

### 3.9 COMMUNICATIONS (4 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `meeting_scheduler_agent.py` | 27KB | Meeting scheduling |
| `meeting_transcriber_agent.py` | 362L | Meeting transcription |
| `newsletter_agent.py` | ~150L | Newsletter management |
| `community_manager_agent.py` | 84L | Community management |

### 3.10 REMAINING KEEP (12 agents)

| Agent | Size | Why Keep |
|-------|------|----------|
| `ab_test_analyzer_agent.py` | 338L | A/B test analysis |
| `hackernews_agent.py` | 28KB | Tech news monitoring |
| `invoice_tracker_agent.py` | 26KB | Invoice tracking |
| `log_analyzer_agent.py` | 7KB | Log analysis |
| `monitoring_agent_agent.py` | 23KB | Agent monitoring |
| `morning_briefing_agent.py` | 15KB | Morning briefing (keeps daily_standup) |
| `notion_organizer_agent.py` | 486L | Notion integration |
| `pr_merger_agent.py` | ~100L | PR merging |
| `report_generator_agent.py` | ~200L | Report generation |
| `sql_assistant_agent.py` | ~100L | SQL assistance |
| `statistical_analysis_agent.py` | 413L | Statistical analysis |
| `usage_analytics_agent.py` | ~100L | Usage analytics |

**TOTAL KEEP: 68 agents**

---

## SECTION 4: Category Summary

| Category | Keep | Merge→ | Kill | Original |
|----------|------|--------|------|----------|
| REVENUE | 8 | 4→ | 5 | 17 |
| CONTENT | 6 | 6→ | 10 | 22 |
| OPERATIONS | 10 | 4→ | 14 | 28 |
| RESEARCH | 5 | 7→ | 13 | 25 |
| SUPPORT | 4 | 3→ | 4 | 11 |
| MASTER/ORCHESTRATION | 5 | 1→ | 5 | 11 |
| DATA & ANALYTICS | 6 | 3→ | 9 | 18 |
| SPECIALIZED BUSINESS | 8 | 2→ | 6 | 16 |
| COMMUNICATIONS | 4 | 1→ | 5 | 10 |
| VERTICALS/OTHER | 12 | 2→ | 105 | 119 |
| **TOTAL** | **68** | **33** | **190** | **281** |

---

## Backup Location
All KILLed agents will be moved to: `/home/clawbot/.openclaw/workspace/archive/agents_backup/`

---

*Plan generated by Kill List Subagent — 2026-03-28*
