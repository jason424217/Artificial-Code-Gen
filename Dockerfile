FROM tensorflow/tensorflow:2.0.0b1-gpu-py3-jupyter

ARG USERNAME=semeru
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ADD ./requirements.txt .

RUN apt install git wget -y
RUN pip install -r requirements.txt
#fastai sentencepiece pandas numpy image jupyterthemes
RUN jt -t chesterish
RUN apt-get install -y sudo && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && chmod 0440 /etc/sudoers.d/$USERNAME

EXPOSE 8888 6006
