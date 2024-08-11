# Distributed Tracing Demo

This is PoC project demonstrating how to achieve distributed tracing using invasive (OTel) and non invasive (ebpf) tools. 
The workload is very simple (depicted below). You can use it to deep dive into how context propagation and distributed tracing can be achieved.

![workload.png](images%2Fworkload.png)

## Docker Compose Deployment

The docker compose deployment use OTel Collector to collect and send telemetry data to Jaeger for assembling and visualization. 
Metrics are not covered here, but you can easily integrate it through Prometheus. Metrics will be logged though: 

[otel-collector-config.yaml](otel-collector%2Fotel-collector-config.yaml):

```yaml
...
exporters:
    logging:
    loglevel: debug
    otlp:
      endpoint: jaeger-all-in-one:4317
```

### 1.1 Build
To build and deploy the system components, run the following command:

```bash
docker-compose up -d --build
```

you should see all containers running:

![containers.png](images%2Fcontainers.png)

#### 1.2. Testing

To publish records, use the following curl command:

```bash
curl -X POST http://0.0.0.0:10000/publish -H "Content-Type: application/json" -d '{"content": "message content"}'
```

To retrieve messages, use the following curl command:

```bash
curl http://0.0.0.0:10000/messages
```

![curl.png](images%2Fcurl.png)

The Jaeger UI is accessible at: http://localhost:16686/search

![jaeger.png](images%2Fjaeger.png)


![jaeger error.png](images%2Fjaeger%20error.png)


## Kubernetes Deployment

- Deploy kafka: `cd kakfa && helm install my-kafka bitnami/kafka -f values.yaml`
- Deploy postgres: `helm install postgres bitnami/postgresql`
- Deploy jaeger: `cd jaeger/kubernetes && kubectl apply -f deployment.yaml`
- Deploy otel collector: `cd otel-collector/kubernetes && kubectl apply -f deployment.yaml`
- Deploy [java-springwebflux](java-springwebflux): `cd java-springwebflux/kubernetes && kubectl apply -f deployment.yaml`
- Deploy [quarkus-rest](quarkus-rest): `cd quarkus-rest/kubernetes  && kubectl apply -f deployment.yaml`
- Deploy [python-fastapi](python-fastapi): `cd python-fastapi/kubernetes && kubectl apply -f deployment.yaml`
- Deploy envoy[envoy-proxy](envoy-proxy): `cd envoy-proxy/kubernetes && kubectl apply -f deployment.yaml`

You should see all pods running: 

![alll-pods.png](images%2Falll-pods.png)

To access Jaeger UI: 
- `kubectl port-forward deployment/jaeger-all-in-one 16686:16686`
-  http://localhost:16686/search
- You should see k8s attributes !

![k8s-attributes.png](images%2Fk8s-attributes.png)

To publish records: 

First port-forward: 

```bash
kubectl port-forward svc/envoy-proxy 10000:10000
```

Then, send records. 

```bash
curl -X POST http://localhost:10000/publish -H "Content-Type: application/json" -d '{"content": "message content"}'
```

Similar to docker compose deployment, you can retrieve messages, use the following curl command:

```bash
curl http://localhost:10000/messages
```
