# Copyright 2016 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import random
import string
import uuid


def rand_uuid_hex():
    """Generate a random UUID hex string

    :return: a random UUID (e.g. '0b98cf96d90447bda4b46f31aeb1508c')
    :rtype: string
    """
    return uuid.uuid4().hex


def rand_name(name='', prefix='deckhand'):
    """Generate a random name that includes a random number

    :param str name: The name that you want to include
    :param str prefix: The prefix that you want to include
    :return: a random name. The format is
             '<prefix>-<name>-<random number>'.
             (e.g. 'prefixfoo-namebar-154876201')
    :rtype: string
    """
    randbits = str(random.randint(1, 0x7fffffff))
    rand_name = randbits
    if name:
        rand_name = name + '-' + rand_name
    if prefix:
        rand_name = prefix + '-' + rand_name
    return rand_name


def rand_bool():
    """Generate a random boolean value.

    :return: a random boolean value.
    :rtype: boolean
    """
    return random.choice([True, False])


def rand_int(min, max):
    """Generate a random integer value between range (`min`, `max`).

    :return: a random integer between the range(`min`, `max`).
    :rtype: integer
    """
    return random.randint(min, max)


def rand_password(length=15):
    """Generate a random password
    :param int length: The length of password that you expect to set
                       (If it's smaller than 3, it's same as 3.)
    :return: a random password. The format is
             '<random upper letter>-<random number>-<random special character>
              -<random ascii letters or digit characters or special symbols>'
             (e.g. 'G2*ac8&lKFFgh%2')
    :rtype: string
    """
    upper = random.choice(string.ascii_uppercase)
    ascii_char = string.ascii_letters
    digits = string.digits
    digit = random.choice(string.digits)
    puncs = '~!@#%^&*_=+'
    punc = random.choice(puncs)
    seed = ascii_char + digits + puncs
    pre = upper + digit + punc
    password = pre + ''.join(random.choice(seed) for x in range(length - 3))
    return password
