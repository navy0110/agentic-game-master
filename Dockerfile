FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 AGENT_PORT=8001
WORKDIR /app
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt \
    && useradd --create-home --uid 10001 agent \
    && chown agent:agent /app
COPY --chown=agent:agent agm ./agm
COPY --chown=agent:agent agent.py ./
USER agent
EXPOSE 8001
CMD ["python", "agent.py"]
