FROM jupyter/minimal-notebook:latest


#COPY ./app ./app

# Install Python Packages & Requirements (Done near end to avoid invalidating cache)
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt



# Expose Jupyter port & cmd
#EXPOSE 8888
#RUN mkdir -p /opt/app/data
CMD jupyter lab --ip=* --port=8888 --no-browser --notebook-dir=./app --allow-root