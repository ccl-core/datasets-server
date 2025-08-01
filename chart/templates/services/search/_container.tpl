# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The HuggingFace Authors.

{{- define "containerSearch" -}}
- name: "{{ include "name" . }}-search"
  image: {{ include "services.search.image" . }}
  imagePullPolicy: {{ .Values.images.pullPolicy }}
  env:
  {{ include "envAssets" . | nindent 2 }}
  {{ include "envCachedAssets" . | nindent 2 }}
  {{ include "envS3" . | nindent 2 }}
  {{ include "envCloudfront" . | nindent 2 }}
  {{ include "envCache" . | nindent 2 }}
  {{ include "envParquetMetadata" . | nindent 2 }}
  {{ include "envQueue" . | nindent 2 }}
  {{ include "envCommon" . | nindent 2 }}
  {{ include "envHf" . | nindent 2 }}
  {{ include "envLog" . | nindent 2 }}
  - name: HF_HOME
    value: "/tmp/hf"
    # ^ensure the temporary files are created in /tmp, which is writable
  # service
  - name: API_MAX_AGE_LONG
    value: {{ .Values.search.maxAgeLong | quote }}
  - name: API_MAX_AGE_SHORT
    value: {{ .Values.search.maxAgeShort | quote }}
  # prometheus
  - name: PROMETHEUS_MULTIPROC_DIR
    value:  {{ .Values.search.prometheusMultiprocDirectory | quote }}
  # uvicorn
  - name: API_UVICORN_HOSTNAME
    value: {{ .Values.search.uvicornHostname | quote }}
  - name: API_UVICORN_NUM_WORKERS
    value: {{ .Values.search.uvicornNumWorkers | quote }}
  - name: API_UVICORN_PORT
    value: {{ .Values.search.uvicornPort | quote }}
  # duckdb
  - name: DUCKDB_INDEX_TARGET_REVISION
    value: {{ .Values.duckDBIndex.targetRevision | quote }}
  - name: DUCKDB_INDEX_CACHE_DIRECTORY
    value: {{ .Values.duckDBIndex.cacheDirectory | quote }}
  - name: DUCKDB_INDEX_CACHE_CLEAN_CACHE_PROBA
    value: {{ .Values.search.cleanCacheProba | quote }}
  - name: DUCKDB_INDEX_CACHE_EXPIRED_TIME_INTERVAL_SECONDS
    value: {{ .Values.search.expiredTimeIntervalSeconds | quote }}
  - name: DUCKDB_INDEX_EXTENSIONS_DIRECTORY
    value: "/tmp/duckdb-extensions"
  - name: HF_HUB_ENABLE_HF_TRANSFER
    value: "1"
  volumeMounts:
  {{ include "volumeMountParquetMetadataRW" . | nindent 2 }}
  securityContext:
    allowPrivilegeEscalation: false
  readinessProbe:
    failureThreshold: 30
    periodSeconds: 5
    httpGet:
      path: /healthcheck
      port: {{ .Values.search.uvicornPort }}
  livenessProbe:
    failureThreshold: 30
    periodSeconds: 5
    httpGet:
      path: /healthcheck
      port: {{ .Values.search.uvicornPort }}
  ports:
  - containerPort: {{ .Values.search.uvicornPort }}
    name: http
    protocol: TCP
  resources:
    {{ toYaml .Values.search.resources | nindent 4 }}
{{- end -}}
