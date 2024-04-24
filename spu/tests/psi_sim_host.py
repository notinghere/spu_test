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

from __future__ import annotations

# from typing import List
from absl import app, flags

import libpsi
import libspu

def prepare_data():
    start = 991
    total = 1990

    id_list = [n for n in range(start, start + total)]
    id_list_str = []
    for num in id_list:
        id_list_str.append(str(num))
    return id_list_str

def prepare_hosts():
    return [f"127.0.0.1:61530",f"127.0.0.1:61531"]

def simple_in_memory_psi(_):

    hosts = prepare_hosts()
    lctx_desc = libspu.link.Desc()
    
    lctx_desc.add_party(f"id_0", hosts[0])
    lctx_desc.add_party(f"id_1", hosts[1])

    lctx_desc.recv_timeout_ms= 2*60*1000

    lctx = libspu.link.create_brpc(lctx_desc, 1)
    intersection = libpsi.libs.ecdh_psi(lctx,prepare_data())
    print(intersection)
    lctx.stop_link()

if __name__ == '__main__':
    app.run(simple_in_memory_psi)