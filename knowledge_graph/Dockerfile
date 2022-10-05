FROM python:3.8

COPY requirements.txt ./

RUN pip install -r requirements.txt

#COPY ./app ./app

RUN mkdir ./app

CMD ["python", "./app/main.py","--dbName","ESAEMs","--defineSchema", "True", "--schemaFile","./app/TypeDB/schema/TypeDBSchemaECSS_relunique", "--insertData", "True","--em_dir_path", "./app/datasets","--defineRules","True","--rulesFile","./app/TypeDB/rules","--insertMetadata", "True","--meta_dir", "./app/Metadata" ]
