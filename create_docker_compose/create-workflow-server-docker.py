#!/usr/bin/env python
""" Script to create the docker-compose file for running the ocrd-webapi-implementation and the
processing server
"""

import requests
from pathlib import Path
import yaml
import re

DEST = "../docker-compose.yaml"
DEST_ENV = "../env"
REPLACE_IMAGE_NAME = ""
#REPLACE_IMAGE_NAME = "ocrd_all_workflow"


DC_BASE_TEMPLATE = "docker-compose.template.yaml"
SERVICE_TEMPLATE = "docker-compose.processor.template.yaml"


SERVICE_TEMPLATE = Path(__file__).parents[0] / SERVICE_TEMPLATE
DC_BASE_TEMPLATE = Path(__file__).parents[0] / DC_BASE_TEMPLATE
DEST_ENV = Path(__file__).parents[0] / DEST_ENV
DEST = Path(__file__).parents[0] / DEST

# processors from ocrd-all-tool-json to be included
YES_LIST = [
    "ocrd-olena-binarize",
    "ocrd-anybaseocr-crop",
    "ocrd-cis-ocropy-denoise",
    "ocrd-tesserocr-segment-region",
    "ocrd-segment-repair",
    "ocrd-cis-ocropy-clip",
    "ocrd-cis-ocropy-dewarp",
    "ocrd-tesserocr-recognize",
]


def get_processors():
    r = requests.get("https://ocr-d.de/js/ocrd-all-tool.json")
    return [x for x in r.json().keys() if x in YES_LIST]


def read_dc_base() -> str:
    with open(DC_BASE_TEMPLATE, "r") as fin:
        return fin.read()


def create_dc_workers() -> str:
    res = ""
    processors = get_processors()
    with open(SERVICE_TEMPLATE, "r") as fin:
        template = fin.read()
        # TODO: remove the line when needed core changes (pr 1046 etc.) are available in ocrd-all
        if REPLACE_IMAGE_NAME:
            template = template.replace("ocrd/all:maximum", REPLACE_IMAGE_NAME)

    for p in processors:
        res += re.sub(r"{{[\s*]processor_name[\s*]}}", p, template)
    return res


def main():
    if not Path(DEST_ENV).exists():
        lines = [
            "OCRD_PS_PORT=8000",
            "OCRD_PS_MTU=1300",
            "MONGODB_USER=admin",
            "MONGODB_PASS=admin",
            "MONGODB_URL=mongodb://${MONGODB_USER}:${MONGODB_PASS}@ocrd-mongodb:27017",
            "RABBITMQ_USER=admin",
            "RABBITMQ_PASS=admin",
            "RABBITMQ_URL=amqp://${RABBITMQ_USER}:${RABBITMQ_PASS}@ocrd-rabbitmq:5672",

            "OCRD_WEBAPI_SERVER_PATH=http://141.5.102.11",
            "OCRD_WEBAPI_BASE_DIR=/tmp/ocrd-webapi-data",
            "OCRD_WEBAPI_DB_URL=${MONGODB_URL}",
            "OCRD_WEBAPI_DB_NAME=ocrd",
            "OCRD_WEBAPI_USERNAME=test",
            "OCRD_WEBAPI_PASSWORD=testtest",
        ]
        with open(DEST_ENV, "w+") as fout:
            fout.write("\n".join(lines))
    else:
        print("Skipping writing to .env")

    with open(DEST, "w") as fout:
        # TODO: remove the line when needed core changes (pr 1046 etc.) are available in ocrd-all
        dc_base = read_dc_base()
        if REPLACE_IMAGE_NAME:
            dc_base = dc_base.replace("ocrd/all:maximum", REPLACE_IMAGE_NAME)
        fout.write(dc_base)
        fout.write(create_dc_workers())


if __name__ == "__main__":
    main()
