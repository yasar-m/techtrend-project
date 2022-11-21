#Base Image with version 3.8 
FROM python:3.8

#Maintainer
LABEL maintainer="Mohamed Yasar"

#Copy source files
COPY /techtrends /app

#Set working dir
WORKDIR /app

#Deploy prerequites
RUN pip install -r requirements.txt

#Expost port
EXPOSE 3111

#Deploy Database
CMD [ "python", "init_db.py" ]

#Run App
CMD [ "python", "app.py" ]
