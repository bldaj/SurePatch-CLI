FROM ubuntu
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
COPY . /surepatch
WORKDIR /surepatch
RUN pip3 install -r requirements.txt
WORKDIR /surepatch/scripts
RUN bash build_docker_ubuntu.sh
WORKDIR /surepatch/dist
# SUREPATCH COMMANDS
RUN ./surepatch --team=dima --user=ws.bespalov@gmail.com --password=Test123! --action=create_platform --platform=fff --description=test
#
CMD ["/bin/bash"]
