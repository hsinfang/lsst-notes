```mermaid
graph TD
  Summit[Summit Observations] --> Producer[Realtime Prompt Processing]
  Summit --> Catchup[Catchup and daytime processing]
  Producer -->|Alert Kafka stream| Alert[Alert Brokers]
  Producer -->|DIA catalogs| APDB[(Cassandra APDB)] -->|Replication| PPDB[(BigQuery PPDB)]
  PPDB -->|Bridge| TAP[(PP TAP)]
  Felis[sdm_schemas] --> PPDB
  Felis --> APDB
  Felis --> TAP_SCHEMA[TAP_SCHEMA, VO Registration?]

 subgraph RepoEmbargo["/repo/prompt"]
    EmbargoStorage[Embargo Object Storage]
    EmbargoRegistry[Embargo Postgres]
  end
 subgraph RepoPrompt["/repo/prompt"]
    PromptStorage["/sdf/data"]
    RepoPromptRegistry[Postgres]
  end
 subgraph RepoMain["/repo/main"]
    MainStorage["/sdf/data"]
    RepoMainRegistry[Postgres]
  end

  Producer -->|Files| EmbargoStorage
  Producer --> EmbargoRegistry
  PromptStorage --- MainStorage
  EmbargoStorage -->|Unembargo after 80hr| PromptStorage
