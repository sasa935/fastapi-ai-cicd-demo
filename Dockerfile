###############################
# Stage 1 — build the frontend
###############################
FROM node:22-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

###############################
# Stage 2 — backend runtime
###############################
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir \
      "fastapi>=0.115" \
      "uvicorn[standard]>=0.32" \
      "sqlalchemy>=2.0" \
      "pydantic>=2.9" \
      "pydantic-settings>=2.6"

COPY backend/app ./app
COPY --from=frontend-build /app/dist ./static

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
