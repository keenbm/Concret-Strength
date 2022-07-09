#Python Version
FROM python:3.7
# Add all the code/resources files/floders
COPY . /app
# Add all the code/resources files/floders
WORKDIR /app
# Add requirement file installation command
RUN pip install -r requirements.txt
# Expose port so that we can add parameter while running docker container
EXPOSE $PORT
# add command to RUN
CMD gunicorn --workers=4 --bind 0.0.0.0:$PORT app:app