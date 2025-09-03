FROM python:3.11-slim

WORKDIR /app
RUN useradd -m agent
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fileagent ./fileagent

USER agent
ENV PORT=8787 AGENT_TOKEN=dev-token AGENT_ROOT=/workspace
VOLUME ["/workspace"]
EXPOSE 8787
CMD ["uvicorn", "fileagent.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "$PORT"]
