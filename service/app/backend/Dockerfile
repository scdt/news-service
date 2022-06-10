FROM python:3.8
WORKDIR /code
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . .
ADD init.sh .
RUN chmod +x ./init.sh

CMD ["./init.sh"]
EXPOSE 8000