# Copyright 2021 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3

from __future__ import annotations

import json

import subprocess
import time
from numpy.random import randint
from tempfile import TemporaryDirectory

import multiprocess
from google.protobuf import json_format


# from typing import List
from absl import app, flags

import libpsi
import libspu
import psi

def wc_count(file_name):
    out = subprocess.getoutput("wc -l %s" % file_name)
    return int(out.split()[0])

def prepare_hosts():
    return [f"127.0.0.1:61530",f"127.0.0.1:61531"]

def run_psi(_):

    tempdir_ = TemporaryDirectory()

    hosts = prepare_hosts()
    lctx_desc = libspu.link.Desc()
    lctx_desc.id = "abc"

    lctx_desc.add_party(f"alice", hosts[0])
    lctx_desc.add_party(f"bob", hosts[1])

    receiver_config_json = f'''
    {{
        "protocol_config": {{
            "protocol": "PROTOCOL_ECDH",
            "ecdh_config": {{
                "curve": "CURVE_25519"
            }},
            "role": "ROLE_RECEIVER",
            "broadcast_result": true
        }},
        "input_config": {{
            "type": "IO_TYPE_FILE_CSV",
            "path": "{tempdir_.name}/data/alice.csv"
        }},
        "output_config": {{
            "type": "IO_TYPE_FILE_CSV",
            "path": "{tempdir_.name}/spu_test_psi_alice_psi_ouput.csv"
        }},
        "keys": [
            "id"
        ],
        "skip_duplicates_check": true,
        "disable_alignment": true
    }}
    '''

    sender_config_json = f'''
    {{
        "protocol_config": {{
            "protocol": "PROTOCOL_ECDH",
            "ecdh_config": {{
                "curve": "CURVE_25519"
            }},
            "role": "ROLE_SENDER",
            "broadcast_result": true
        }},
        "input_config": {{
            "type": "IO_TYPE_FILE_CSV",
            "path": "{tempdir_.name}/data/bob.csv"
        }},
        "output_config": {{
            "type": "IO_TYPE_FILE_CSV",
            "path": "{tempdir_.name}/spu_test_psi_bob_psi_ouput.csv"
        }},
        "keys": [
            "id"
        ],
        "skip_duplicates_check": true,
        "disable_alignment": true
    }}
    '''

    configs = [
        json_format.ParseDict(json.loads(receiver_config_json), psi.PsiConfig()),
        json_format.ParseDict(json.loads(sender_config_json), psi.PsiConfig()),
    ]

    def wrap(rank, link_desc, configs):
        link_ctx = libspu.link.create_brpc(link_desc, rank)
        psi.psi(configs[rank], link_ctx)

    jobs = [
        multiprocess.Process(
            target=wrap,
            args=(rank, lctx_desc, configs),
        )
        for rank in range(2)
    ]
    [job.start() for job in jobs]
    for job in jobs:
        job.join()


if __name__ == '__main__':
    app.run(run_psi)