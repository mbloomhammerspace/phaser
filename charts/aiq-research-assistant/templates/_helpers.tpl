{{- define "aiq-research-assistant.name" -}}
aiq-research-assistant
{{- end -}}

{{- define "aiq-research-assistant.backendName" -}}
{{ .Release.Name }}-aiq-backend
{{- end -}}

{{- define "aiq-research-assistant.proxyName" -}}
{{ .Release.Name }}-aiq-proxy
{{- end -}}
