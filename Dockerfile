FROM ocrd/all:maximum

RUN git clone https://github.com/ocr-d/core.git && \
	cd core && \
	make install
WORKDIR /data
