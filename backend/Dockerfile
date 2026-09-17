# PyLucene preinstalled. Check the Lucene version once with:
#   docker compose run --rm backend python -c "import lucene; print(lucene.VERSION)"
# and then pin the tag here instead of :latest.
FROM coady/pylucene:latest

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# CPU-only torch (avoids multi-GB CUDA wheels)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/app ./app
COPY scripts ./scripts

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
