---
title: "pg_durable: Microsoft open sources in-database durable execution"
source: https://github.com/microsoft/pg_durable
date: 2026-06-06
tags:
  - news
  - auto-learning
  - auto-injected
---

# pg_durable: Microsoft open sources in-database durable execution

Long-running, fault-tolerant SQL functions for teams that already keep their state in Postgres and want to stop stitching together cron jobs, workers, queues, and status tables to make background work reliable. Define the workflow in SQL, let pg_durable checkpoint each step, and resume after crashes, restarts, or failed steps.
Durable execution is now a standard industry pattern, and pg_durable brings it inside Postgres with no extra service infrastructure required. Part of our mission to bring compute close to data.
Try pg_durable now in Azure HorizonDB, Microsoft's new PostgreSQL cloud service engineered for performance and built with pg_durable inside
- Backend and data engineers who want workflows to live next to the data they touch.
- DBAs and SREs automating runbooks that must survive restarts and be auditable in SQL.
- Teams building data or AI pipelines that need durable execution per row, document, or batch.
A pg_durable function is a graph of SQL steps that PostgreSQL executes and checkpoints as it goes. If the database crashes, restarts, or a step fails, execution resumes from the last durable checkpoint instead of making you reconstruct state by hand.
- Vector embedding pipelines: chunk, call an embedding API, and upsert into
pgvector
. - Ingest pipelines: stage, deduplicate, transform, and publish large batches.
- Scheduled maintenance: detect bloat, notify, wait for approval, then run the next action.
- Fan-out aggregation: run independent queries in parallel, then join the results.
- External API workflows: enrichment, classification, and webhook-style calls from SQL.
pg_cron
plus a jobs table, status columns, retry counters, and a polling worker.- An external orchestrator such as Airflow, Temporal, Step Functions, or Argo calling back into Postgres.
- A queue plus workers plus a separate state table to coordinate retries and partial completion.
- A
plpgsql
procedure that works until a crash or long-running transaction forces you to start over.
- A restart in the middle of a long job means rerunning work that already succeeded.
- One failed row or one failed API call turns into manual cleanup and uncertain replay.
- Long transactions hold locks, grow WAL, and make batch jobs fragile at larger scale.
- Parallel work in the app tier creates more places for partial-failure bugs and drift.
- The workflow logic ends up spread across SQL, workers, queues, dashboards, and status tables.
- The workflow definition moves into SQL and starts with
df.start(...)
. - Retry state, progress tracking, and checkpointing move into Postgres instead of bespoke app code.
- Some app-tier workers, queue consumers, or scheduler glue can disappear entirely.
- Operational visibility comes from Postgres tables such as
df.instances
, using the same auth and backup model as your data.
- The job is already a single
INSERT ... SELECT
or one ordinary SQL statement. - You need sub-millisecond synchronous request handling rather than durable background execution.
- You cannot install extensions or run a background worker in your Postgres environment.
- The workflow mostly lives outside Postgres and spans many heterogeneous systems.
- You need arbitrary application logic that does not map cleanly to SQL steps, branching, loops, or HTTP calls.
- Define a workflow in SQL using composable operators such as
~>
and|=>
. - Start it with
df.start()
and get back an instance ID. - Let the runtime execute each step durably with checkpointing between steps.
- Query status and results from PostgreSQL while the workflow runs or after it completes.
The model is intentionally SQL-shaped. If a step needs arbitrary code, a non-HTTP SDK, or rich in-memory control flow, you may need to wrap that logic in a SQL function, expose it behind an HTTP endpoint for df.http()
, or use a general-purpose orchestrator for that part of the system.
- Durable — Function state persists to PostgreSQL. Survives crashes, restarts, and failovers.
- SQL-native — Define functions in SQL using composable operators.
- Database-aware — First-class primitives for scheduling, conditions, and parallel execution.
- Zero infrastructure — Runs as a PostgreSQL extension. No Redis, no Temporal, no external services.
-- A durable function that processes data in steps
SELECT df.start(
'SELECT id FROM documents WHERE processed = false LIMIT 100' |=> 'batch'
~> 'UPDATE documents SET processed = true WHERE id = ANY($batch)'
);
Tagged releases publish Debian packages for PostgreSQL 17 and 18 on amd64 from the GitHub release assets. Packages are named pg-durable-postgresql-<PG major>_<pg_durable version>-1_<arch>.deb
and install the extension library, control file, and SQL upgrade files into the matching PostgreSQL installation directories.
After installing a package, add pg_durable
to shared_preload_libraries
, restart PostgreSQL, and create the extension in the configured pg_durable database:
CREATE EXTENSION pg_durable;
The default pg_durable database is postgres
; see User Guide fo

---
*Synthesized by AutonomousLearner*
