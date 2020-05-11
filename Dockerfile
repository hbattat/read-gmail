FROM python:2.7
RUN mkdir app
COPY . app/
RUN pip install bottle
ENV PORT 80
EXPOSE 80
CMD python2 /app/server.py
