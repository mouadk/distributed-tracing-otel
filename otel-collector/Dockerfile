#https://github.com/open-telemetry/opentelemetry-collector/blob/ef07ea073562c4eb4d63a9032e84a802d8424fe2/examples/k8s/otel-config.yaml
FROM alpine:3.20@sha256:0a4eaa0eecf5f8c050e5bba433f58c052be7587ee8af3e8b3910ef9ab5fbe9f5 AS otelc_curl
RUN apk --update add curl bash

FROM otel/opentelemetry-collector-contrib:latest

COPY --from=otelc_curl / /

COPY ./otel-collector-config.yaml /etc/otel-collector-config.yaml
USER 0
RUN chmod o+r /etc/otel-collector-config.yaml
USER nobody
