FROM python:3.6.5

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY interfaces /app/interfaces
COPY models /app/models
COPY updaters /app/updaters
COPY update_journey_times.py /app/update_journey_times.py
COPY update_season_tickets.py /app/update_season_tickets.py

COPY update /app/update
RUN chmod +x /app/update

ENTRYPOINT ["bash", "-c"]
