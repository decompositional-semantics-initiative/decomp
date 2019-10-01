FROM python:3.6

WORKDIR /usr/src/decomp

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir . && \
    python -c "from decomp import UDSCorpus; UDSCorpus()"