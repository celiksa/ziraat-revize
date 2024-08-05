FROM python:3.11.8-bullseye
COPY . /src
WORKDIR /src
COPY requirements.txt .
RUN pip3 install -r requirements.txt 
COPY . .
# Set the ownership and permissions
RUN chown -R 1000:3000 /app \
    && chmod -R 755 /app \
    && chmod -R 775 /app/uploaded_pdfs

# Switch to a non-root user
USER 1000:3000

EXPOSE 8510
CMD python flaskApp.py
