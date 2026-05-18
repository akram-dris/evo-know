# 📈 Observability & Monitoring (`monitoring/`)

This directory contains the configuration manifests and scraping rules for the observability stack powering the **Cloud-Native Knowledge Management Update System**. By integrating automated metrics collection, administrators can monitor real-time microservice health, API latency, and resource consumption.

```
monitoring/
├── prometheus.yml              # Prometheus Scraping Manifest & Target Configurations
└── README.md                   # Observability Overview & Access Guide
```

---

## 🔍 Prometheus Configuration & Targets

Prometheus is configured as a core infrastructure service within `docker-compose.yml` to scrape runtime metrics across the cluster.

### 🌐 Accessing the Prometheus Web UI
Prometheus is exposed on a remapped host port to avoid conflicts with existing local services. To access the live web dashboard and execute PromQL queries, navigate to:

```text
http://localhost:9095
```

### 🎯 Active Scraping Targets
- **`api-gateway` (Port 8000):** Scrapes HTTP request rates, endpoint latencies (`/ingest`, `/query`), and active database connection pool statuses.
- **`slack-bot` (Port 3000):** Scrapes Uvicorn runtime metrics and conversational event processing delays.
- **Kafka & Zookeeper:** Tracks message throughput, consumer group lags, and broker cluster health.

---

## 📊 Future Grafana Integration

To visualize Prometheus metrics via rich, dynamic operational dashboards, administrators can easily spin up a Grafana container connected to the Prometheus data source:

```yaml
# Example addition for docker-compose.yml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=km_secure_grafana_2026
  depends_on:
    - prometheus
```
Once deployed, configure `http://prometheus:9090` as the internal Grafana data source.
