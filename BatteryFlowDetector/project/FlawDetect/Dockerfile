FROM python:2.7.14-alpine3.7 as builder
MAINTAINER hongpu
EXPOSE 7912
COPY ./ /leqi_dianchi/
WORKDIR /leqi_dianchi/
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
CMD sh
