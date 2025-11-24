#!/usr/bin/env python3
# Author: Dot
# Date: 2024-09-17
# Description: This is a Python script used to convert subscription to json
#
# Usage:
# 1). subscribe URL
# $ python3 sub2json.py -s https://abc?token=xyz -o ./
#
# 2). subscribe FILE
# $ python3 sub2json.py -r subscribe.data -o ./

import re
import os
import urllib
import json
import base64
import requests
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def base64_decode(data):
    return base64.urlsafe_b64decode(data + "=" * (4 - len(data) % 4)).decode("utf-8")


def good_content(s):
    try:
        base64.b64decode(s).decode("utf8") if s else None
        return True
    except:
        return False


def subscribe(url) -> bytes:
    # Pretend to access the subscription using a browser
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url=url, headers=headers, timeout=(10, 10))

    except Exception:
        raise ValueError("requests.get() Exception")

    if response.content == b"" or not good_content(response.content):
        print("\033[1;31mPlease check if your subscription link is valid\033[0m")
        exit(1)

    return response.content


class Protocol(object):
    def __init__(self, name, link) -> None:
        self._name = name
        self._link = link
        pass

    def decode(self):
        raise NotImplementedError("decode() method must be implemented")


class ProtocolA:
    NAME = b"\x73\x73\x3a\x2f\x2f".decode()
    PROTOCOL = b"\x73\x68\x61\x64\x6f\x77\x73\x6f\x63\x6b\x73".decode()

    def _remove_code(self, text):
        return re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+",
            flags=re.UNICODE,
        ).sub(r"", text)

    def decode(self, link):
        body = link.replace(self.NAME, "").replace("\r", "")
        header, footer = body.split("#")

        try:
            base64_decode(header)
            """
            ProtocolA pattern1

              [base64]
                 |
               (dec)
                 |
                 V
              [method]:[uuid]@[addr]:[port]

            """
            method, uuid, addr, port = re.split(r"[:@]", base64_decode(header))
            note = footer
        except:
            """
            ProtocolA pattern2

              [base64]@[addr]:[port]
                 |
               (dec)
                 |
                 V
              [method]:[uuid]

            """
            method_uuid, addr, port = re.split(r"[:@]", header)
            method, uuid = base64_decode(method_uuid).split(":", 1)
            note = self._remove_code(urllib.parse.unquote(footer))

        return {
            "uuid": uuid,
            "port": port,
            "addr": addr,
            "protocol": self.PROTOCOL,
            "method": method,
            "note": note,
        }


class ProtocolB:
    NAME = b"\x76\x6d\x65\x73\x73\x3a\x2f\x2f".decode()
    PROTOCOL = b"\x76\x6d\x65\x73\x73".decode()

    def _remove_code(self, text):
        filter_text = re.sub(r"\\ud[0-9a-fA-F]{4}", "", text)

        try:
            return filter_text.encode("utf-8", "ignore").decode("utf-8", "ignore")
        except UnicodeDecodeError:
            return ""

    def decode(self, link):
        body = link.replace(self.NAME, "")
        decoded_body = base64_decode(body)
        decoded_body = eval(decoded_body)

        return {
            "uuid": decoded_body["id"],
            "port": decoded_body["port"],
            "addr": decoded_body["add"],
            "protocol": self.PROTOCOL,
            "note": self._remove_code(decoded_body["ps"]),
        }


class ProtocolC:
    NAME = b"\x74\x72\x6f\x6a\x61\x6e\x3a\x2f\x2f".decode()
    PROTOCOL = b"\x74\x72\x6f\x6a\x61\x6e".decode()

    def _remove_code(self, text):
        return re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+",
            flags=re.UNICODE,
        ).sub(r"", text)

    def decode(self, link):
        body = link.replace(self.NAME, "").replace("\r", "")

        """
        [uuid]@[addr]:[port]?[config]#[note]
                              /  \
                           item1 & item2 & ...
        """

        uuid, addr, port, config, note = re.split(r"[@:?#]", body)

        params = urllib.parse.parse_qs(config)

        allowInsecure = bool(int(params.get("allowInsecure", ["0"])[0]))
        peer = params.get("peer", [""])[0]
        sni = params.get("sni", [""])[0]

        return {
            "uuid": uuid,
            "port": port,
            "addr": addr,
            "protocol": self.PROTOCOL,
            "note": self._remove_code(urllib.parse.unquote(note)),
            "allowInsecure": allowInsecure,
            "peer": peer,
            "sni": sni,
        }


class ProtocolD:
    NAME = b"\x68\x79\x73\x74\x65\x72\x69\x61\x32\x3a\x2f\x2f".decode()
    PROTOCOL = b"\x68\x79\x73\x74\x65\x72\x69\x61\x32".decode()

    def _remove_code(self, text):
        return re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+",
            flags=re.UNICODE,
        ).sub(r"", text)

    def decode(self, link):
        body = link.replace(self.NAME, "").replace("\r", "")

        """
        [uuid]@[addr]:[port]?[config]#[note]
                              /  \
                           item1 & item2 & ...
        """

        uuid, addr, port, config, note = re.split(r"[@:?#]", body)

        params = urllib.parse.parse_qs(config)

        insecure = bool(int(params.get("insecure", ["0"])[0]))
        security = params.get("security", [""])[0]
        sni = params.get("sni", [""])[0]

        return {
            "uuid": uuid,
            "port": port,
            "addr": addr,
            "protocol": self.PROTOCOL,
            "note": self._remove_code(urllib.parse.unquote(note)),
            "insecure": insecure,
            "security": security,
            "sni": sni,
        }


class ProtocolE:
    NAME = b"\x76\x6c\x65\x73\x73\x3a\x2f\x2f".decode()
    PROTOCOL = b"\x76\x6c\x65\x73\x73".decode()

    def _remove_code(self, text):
        return re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+",
            flags=re.UNICODE,
        ).sub(r"", text)

    def decode(self, link):
        body = link.replace(self.NAME, "").replace("\r", "")

        """
        [uuid]@[addr]:[port]?[config]#[note]
                              /  \
                           item1 & item2 & ...
        """

        uuid, addr, port, config, note = re.split(r"[@:?#]", body)

        params = urllib.parse.parse_qs(config)

        main = {
            "uuid": uuid,
            "port": port,
            "addr": addr,
            "protocol": self.PROTOCOL,
            "note": self._remove_code(urllib.parse.unquote(note)),
        }

        main.update(params)

        return main


class Sub2Json:
    def __init__(self, data: bytes) -> None:
        self.__data = data
        pass

    def _predecode(self):
        """
        First decode the base64 string into multiple protocol strings
        """
        try:
            result = base64.b64decode(self.__data).decode("utf-8")

        except Exception:
            exit(1)

        return result.strip().split("\n")

    def decode(self):
        protocols = {
            ProtocolA.NAME: ProtocolA(),
            ProtocolB.NAME: ProtocolB(),
            ProtocolC.NAME: ProtocolC(),
            ProtocolD.NAME: ProtocolD(),
            ProtocolE.NAME: ProtocolE(),
        }

        data = []
        for link in self._predecode():
            found = False
            for name, obj in protocols.items():
                if link.startswith(name):
                    found = True
                    data.append(obj.decode(link))
            if not found:
                protocol, _ = re.split(r"://", link)
                print(f"{protocol} is not implemented")
                hex_str = "".join(f"\\x{byte:02x}" for byte in protocol.encode("utf-8"))
                print(f'NAME = b"{hex_str}\\x3a\\x2f\\x2f".decode()')
                print(f'PROTOCOL = b"{hex_str}".decode()')

        return data


def args_parse():

    example_commands = (
        "Examples:\n\n"
        "  # Download subscription data from (\033[1;34mURL\033[0m) and save to (\033[1;34mDIR\033[0m)\n"
        "  \033[1;32m$ python3 sub2json.py -s https://xxxxxx?token=[REDACTED] -o ~/.cache\033[0m\n"
        "\n"
        "  # Use local subscription data from (\033[1;34mFILE\033[0m) and save to (\033[1;34mDIR\033[0m)\n"
        "  \033[1;32m$ python3 sub2json.py -r ~/.cache/subscribe.data -o ~/.cache\033[0m\n"
        "\n"
    )

    parser = ArgumentParser(
        description="subscription to json",
        epilog=example_commands,
        formatter_class=RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--subscribe",
        metavar="URL",
        required=False,
        help="URL to subscribe",
    )

    parser.add_argument(
        "-r",
        "--rawcontent",
        metavar="FILE",
        required=False,
        help="Path to subscribe (raw content)",
    )

    parser.add_argument(
        "-o", "--outdir", metavar="DIR", required=True, help="Path to outdir"
    )

    args = parser.parse_args()

    if (args.subscribe and args.rawcontent) or (
        not args.subscribe and not args.rawcontent
    ):
        parser.error("You must specify exactly one of --subscribe or --rawcontent.")

    return args


def main():
    args = args_parse()

    if args.rawcontent:
        data = open(args.rawcontent, "rb").read()
    else:
        if not args.subscribe:
            print("must specified --subscribe or --rawcontent")
            exit(1)

        data = subscribe(url=args.subscribe)
        cached_subscribe = os.path.join(args.outdir, "subscribe.data")
        print(f"Writing subscribe data (rawcontent) at {cached_subscribe}")
        with open(cached_subscribe, "wb") as f:
            f.write(data)

    count = 0
    for server in Sub2Json(data).decode():
        count += 1
        filename = os.path.join(args.outdir, f"server{count:02d}.json")
        with open(filename, "w", encoding="utf-8") as f:
            server["index"] = count
            json.dump(server, f, indent=4, ensure_ascii=False)
            print(
                f"Output file saved at \033[1;32m{os.path.realpath(f.name)}\033[0m ({count:02d}: {server['note']})"
            )

    print("Subscribe conversion: \033[1;32mCompleted\033[0m")


if __name__ == "__main__":
    main()
