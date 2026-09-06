# Software Architect Roadmap: all 53 topics

This index maps every label in the supplied ByteByteGo image to an explanation and a concrete implementation or worked exercise. Technical explanations use plain English for interview practice. Commands run from the module directory.

**Executable model** means a deliberately limited learning implementation. **Configuration** means real service configuration requiring the named external runtime. See [validation](VALIDATION.md) for what actually ran.

## 1. Programming languages

| # | Topic | Deliverable |
|---|---|---|
| 01 | [Java](topics/01-java.md) | Executable HTTP service |
| 02 | [Python](topics/02-python.md) | Executable HTTP service and core labs |
| 03 | [Go / Golang](topics/03-go.md) | Executable HTTP service |
| 04 | [JavaScript / Node.js](topics/04-javascript.md) | Executable HTTP service |

## 2. Tools

| # | Topic | Deliverable |
|---|---|---|
| 05 | [GitHub](topics/05-github.md) | Workflow and repository integration |
| 06 | [Jenkins](topics/06-jenkins.md) | Pipeline configuration |
| 07 | [Jira](topics/07-jira.md) | Concrete issue payload and workflow exercise |
| 08 | [ELK: Elasticsearch, Logstash, Kibana](topics/08-elk.md) | Real integration configuration |
| 09 | [Sonar / SonarQube](topics/09-sonar.md) | Scanner configuration |

## 3. Design principles

| # | Topic | Deliverable |
|---|---|---|
| 10 | [OOPS / Object-oriented programming](topics/10-oops.md) | Executable domain model |
| 11 | [Clean Code](topics/11-clean-code.md) | Executable functional core and adapters |
| 12 | [TDD](topics/12-tdd.md) | Behavior tests and red/green/refactor exercise |
| 13 | [Domain-Driven Design](topics/13-ddd.md) | Domain model and context boundary exercise |
| 14 | [CAP theorem](topics/14-cap.md) | Deterministic partition model |
| 15 | [ACID](topics/15-acid.md) | Real SQLite transaction and failure injection |
| 16 | [MVC pattern](topics/16-mvc.md) | HTTP controller and HTML view |
| 17 | [GoF design patterns](topics/17-gof.md) | All 23 executable patterns |

## 4. Architectural patterns

| # | Topic | Deliverable |
|---|---|---|
| 18 | [Microservices](topics/18-microservices.md) | Two real HTTP services |
| 19 | [Publish Subscribe](topics/19-pubsub.md) | Consumer-offset model and Kafka integration |
| 20 | [Event-Driven Architecture / EDA](topics/20-eda.md) | Transactional outbox and inbox |
| 21 | [Layered architecture](topics/21-layered.md) | Presentation, domain, and persistence separation |
| 22 | [Client-Server](topics/22-client-server.md) | HTTP client and server contract |
| 23 | [Hexagonal architecture](topics/23-hexagonal.md) | Ports and adapters |

## 5. Platform knowledge

| # | Topic | Deliverable |
|---|---|---|
| 24 | [Containers](topics/24-containers.md) | Dockerfile and Compose |
| 25 | [Orchestration / Kubernetes](topics/25-orchestration.md) | Deployment, Service, probes, resource limits |
| 26 | [Cloud](topics/26-cloud.md) | AWS CloudFormation template |
| 27 | [Serverless](topics/27-serverless.md) | Lambda handler and SAM template |
| 28 | [CDN](topics/28-cdn.md) | Local reverse-proxy cache simulation |
| 29 | [API Gateway](topics/29-gateway.md) | NGINX routing and rate-limit configuration |
| 30 | [Distributed Systems](topics/30-distributed-systems.md) | Hashing, partitions, retries, and delivery models |
| 31 | [CI/CD](topics/31-cicd.md) | Automated validation and release exercise |

## 6. Data and analytics

| # | Topic | Deliverable |
|---|---|---|
| 32 | [SQL](topics/32-sql.md) | SQLite schema, transaction, index, and query plan |
| 33 | [NoSQL](topics/33-nosql.md) | Document model plus real Redis profile |
| 34 | [Hadoop](topics/34-hadoop.md) | Hadoop Streaming mapper and reducer |
| 35 | [Kafka](topics/35-kafka.md) | Real broker and producer/consumer integration |
| 36 | [Data Streaming](topics/36-data-streaming.md) | Event-time windows and late-data policy |
| 37 | [OLAP](topics/37-olap.md) | Star-schema aggregation |
| 38 | [Object Storage](topics/38-object-storage.md) | Immutable local objects and S3 template |
| 39 | [Data Migration](topics/39-data-migration.md) | Idempotent expand/backfill example |

## 7. Networking and security

| # | Topic | Deliverable |
|---|---|---|
| 40 | [DNS](topics/40-dns.md) | Real loopback UDP packet exchange |
| 41 | [TCP](topics/41-tcp.md) | Real framed byte-stream exchange |
| 42 | [TLS](topics/42-tls.md) | Real certificate-verified TLS handshake |
| 43 | [HTTPS](topics/43-https.md) | Real HTTP over TLS |
| 44 | [Encryption](topics/44-encryption.md) | AES-GCM authenticated encryption |
| 45 | [JWT](topics/45-jwt.md) | Fixed-algorithm educational signer and verifier |
| 46 | [OAuth](topics/46-oauth.md) | Authorization Code with PKCE model |
| 47 | [Credentials](topics/47-credentials.md) | Salted password verification and secret handling |

## 8. Supporting skills

| # | Topic | Deliverable |
|---|---|---|
| 48 | [Technology evaluation](topics/48-technology.md) | Decision matrix and evaluation record |
| 49 | [Decision Making](topics/49-decision-making.md) | ADR with alternatives and revisit criteria |
| 50 | [Stakeholder Management](topics/50-stakeholders.md) | Concrete RACI and review plan |
| 51 | [Communication](topics/51-communication.md) | Architecture brief and incident update examples |
| 52 | [Estimation](topics/52-estimation.md) | PERT and critical-path calculator |
| 53 | [Leadership](topics/53-leadership.md) | Incident exercise and ownership practices |

## Attribution

The topic inventory follows [ByteByteGo: The Ultimate Software Architect Knowledge Map](https://bytebytego.com/guides/the-ultimate-software-architect-knowledge-map/). The code, explanation text, data, exercises, and Mermaid diagrams in this module are original. The supplied screenshot is not redistributed.
