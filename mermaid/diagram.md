```mermaid
---
config:
  layout: dagre
---
flowchart TD
 subgraph RepoEmbargo["/repo/embargo"]
        EmbargoStorage["Embargo Object Storage"]
        EmbargoRegistry["embargo Postgres"]
  end
 subgraph RepoUSDF["/repo/prompt, /repo/main"]
        WekaStorage["/sdf/data"]
        RepoPromptRegistry["prompt Postgres"]
        RepoMainRegistry["main Postgres"]
  end
 subgraph RepoCloud["repo at RSP"]
        CloudStorage["Hybrid from SLAC; Partially Cached at Cloud"]
        CloudRegistry["AlloyDB"]
  end
    Summit["Summit Observations"] --> Producer["Realtime Prompt Processing"] & Catchup["Catchup and daytime processing"]
    Producer -- Alert Kafka stream --> Alert["Alert Brokers"]
    Producer -- DIA catalogs --> APDB[("Cassandra APDB")]
    Catchup --> APDB & RepoEmbargo
    APDB -- Replication --> PPDB[("BigQuery PPDB")]
    PPDB -- Bridge --> TAP[("PP TAP")]
    Felis["sdm_schemas"] --> PPDB & APDB & TAP_SCHEMA["TAP_SCHEMA, VO Registration?"]
    Producer -- Butler Files --> RepoEmbargo
    RepoEmbargo -- Unembargo after 80hr --> RepoUSDF
    RepoUSDF -- "Expire data after 30d/1y?" ? --> Regeneration["Regeneration Servivce"]
    WekaStorage -- when? --> CloudStorage
    RepoPromptRegistry -- when? --> CloudRegistry
    RepoCloud --> SODA["SIA/SODA/etc"]
    RepoCloud -- ? --> ObsTAP["ObsTAP"]
    Regeneration -- for data older than 30d/1yr? --> SODA
    TAP & ObsTAP & SODA --> RSP["RSP"]
    RepoCloud -- Notebook access --> RSP
