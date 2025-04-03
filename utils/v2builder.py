#!/usr/bin/env python3
# Author: Dot(anty2bot)
# Date: 2024-12-14
# Description: This is a Python script for ProjectV config builder

import json

GLOBAL_RULES_PATH = "~/.v2rules.json"


class BaseServerProtocol:
    def __init__(
        self,
        server_address: str,
        server_port: int,
        server_uuid: str,
        server_method: str,
    ):
        self.server_address = server_address
        self.server_port = server_port
        self.server_uuid = server_uuid
        self.server_method = server_method

    def settings(self):
        raise NotImplementedError("Subclasses must implement settings method.")


class ServerProtocolA(BaseServerProtocol):
    NAME = b"\x73\x68\x61\x64\x6f\x77\x73\x6f\x63\x6b\x73".decode()

    def settings(self):
        return {
            "servers": [
                {
                    "address": self.server_address,
                    "method": self.server_method,
                    "ota": False,
                    "password": self.server_uuid,
                    "port": self.server_port,
                    "level": 1,
                }
            ]
        }


class ServerProtocolB(BaseServerProtocol):
    NAME = b"\x76\x6d\x65\x73\x73".decode()

    def settings(
        self,
    ):
        return {
            "vnext": [
                {
                    "address": self.server_address,
                    "port": self.server_port,
                    "users": [
                        {
                            "id": self.server_uuid,
                            "alterId": 0,
                            "email": "t@t.tt",
                            "security": "auto",
                        }
                    ],
                }
            ]
        }


class ServerProtocolC(BaseServerProtocol):
    NAME = b"\x74\x72\x6f\x6a\x61\x6e".decode()

    def settings(
        self,
    ):
        return {
            "servers": [
                {
                    "address": self.server_address,
                    "method": self.server_method,
                    "password": self.server_uuid,
                    "port": self.server_port,
                    "level": 1,
                }
            ]
        }


class configProjectV:
    def inbounds(self, allow_lan=True, port=10809):
        inbound_allow_lan = allow_lan
        inbound_port = port

        assert isinstance(inbound_port, int), "inbound_port should be integer"

        data = [
            {
                "tag": "http",
                "port": inbound_port,
                "listen": "0.0.0.0" if inbound_allow_lan else "127.0.0.1",
                "protocol": "http",
                "settings": {
                    "udp": False,
                },
            }
        ]

        data += [
            {
                "tag": "socks",
                "port": inbound_port + 1,
                "listen": "0.0.0.0" if inbound_allow_lan else "127.0.0.1",
                "protocol": "socks",
                "settings": {
                    "udp": True,
                },
            }
        ]

        return data

    def outbounds(self, protocol):
        data = []

        data.append(
            {
                "tag": "proxy",
                "protocol": protocol.NAME,
                "settings": protocol.settings(),
            }
        )
        data.append(
            {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {},
            }
        )
        data.append(
            {
                "tag": "block",
                "protocol": "blackhole",
                "settings": {
                    "response": {
                        "type": "http",
                    },
                },
            },
        )

        return data

    def rules(self):
        rules_config = load_rules_config()

        direct_1st = rules_config["direct_1st"]
        proxy_1st = rules_config["proxy_1st"]
        direct_2nd = rules_config["direct_2nd"]
        proxy_2nd = rules_config["proxy_2nd"]
        proxy_3rd = rules_config["proxy_3rd"]

        data = []

        if len(direct_1st["domain"]) > 0:
            obj = dict(type="field", outboundTag="direct", domain=direct_1st["domain"])
            data.append(obj)

        if len(proxy_1st["domain"]) > 0:
            obj = dict(type="field", outboundTag="proxy", domain=proxy_1st["domain"])
            data.append(obj)

        if len(direct_2nd["domain"]) > 0 and len(direct_2nd["source"]) > 0:
            obj = dict(
                type="field",
                outboundTag="direct",
                domain=direct_2nd["domain"],
                source=direct_2nd["source"],
            )
            data.append(obj)

        if len(proxy_2nd["domain"]) > 0 and len(proxy_2nd["source"]) > 0:
            obj = dict(
                type="field",
                outboundTag="proxy",
                domain=proxy_2nd["domain"],
                source=proxy_2nd["source"],
            )
            data.append(obj)

        obj = dict(type="field", outboundTag="direct", domain=["geosite:cn"])
        data.append(obj)

        obj = dict(type="field", outboundTag="direct", ip=["geoip:private", "geoip:cn"])
        data.append(obj)

        obj = dict(
            type="field", outboundTag="block", domain=["geosite:category-ads-all"]
        )
        data.append(obj)

        if len(proxy_3rd["source"]) > 0:
            obj = dict(type="field", outboundTag="proxy", source=proxy_3rd["source"])
            data.append(obj)

        obj = dict(type="field", outboundTag="direct", port="0-65535")
        data.append(obj)

        return data

    def routing(self):
        rules = self.rules()

        return {"domainStrategy": "IPIfNonMatch", "rules": rules}


def args_parse():
    example_commands = (
        "Examples:\n\n"
        "  # way 1\n"
        "  \033[1;32m$ python3 v2builder.py -i ~/.cache/server01.json -o config.json --allow_lan\033[0m\n"
        "\n"
        "  # way 2\n"
        "  \033[1;32m$ python3 v2builder.py -i ~/.cache/server01.json -o config.json --allow_lan --http_port=30030\033[0m\n"
        "\n"
    )

    from argparse import ArgumentParser
    from argparse import RawTextHelpFormatter

    parser = ArgumentParser(
        description="Project V Config Builder Tool",
        epilog=example_commands,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input",
        metavar="server.conf",
        required=True,
        help="Path to input server config file",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="config.json",
        required=True,
        help="Path to output client config file",
    )

    client = parser.add_argument_group("client Options")
    client.add_argument(
        "--http_port",
        metavar="PORT",
        default=10809,
        type=int,
        help="Set the HTTP proxy port. Must be an integer in the range of 0 to 65535.\n"
        "By default, http port is 10809.",
    )
    client.add_argument(
        "--allow_lan",
        action="store_true",
        help="If set, allow connections from local area network (LAN).\n"
        "By default, connections are only allowed from localhost.",
    )

    return parser.parse_args()


def load_rules_config():
    import os

    default_rules = {
        "direct_1st": {
            "Note": "e.g. domain",
            "domain": ["domain:baidu.com", "domain:youdao.com"],
        },
        "proxy_1st": {
            "Note": "e.g. domain",
            "domain": [
                # OpenAI rules
                "domain:chat.openai.com",
                "domain:cdn.openai.com",
                "domain:beacons.gcp.gvt2.com",
                "domain:widget.intercom.io",
                "domain:tcr9i.chat.openai.com",
                "domain:api-iam.intercom.io",
                "domain:events.statsigapi.net",
                # Github rules
                "domain:github.com",
                # Spotify rules
                "domain:pscdn.co",
                "domain:scdn.co",
                "domain:spoti.fi",
                "domain:spotifycdn.com",
                "domain:spotifycdn.net",
                "domain:spotifycharts.com",
                "domain:spotifycodes.com",
                "domain:spotify.com",
                "domain:spotifyjobs.com",
                "domain:spotifynewsroom.jp",
                "domain:spotilocal.com",
                "domain:tospotify.com",
            ],
        },
        "direct_2nd": {
            "Note": "e.g. domain & source mix",
            "domain": [],
            "source": [],
        },
        "proxy_2nd": {
            "Note": "e.g. domain & source mix",
            "domain": [],
            "source": [],
        },
        "proxy_3rd": {
            "Note": "e.g. 192.168.2.2 (IP firstly)",
            "source": [],
        },
    }

    file_path = os.path.expanduser(GLOBAL_RULES_PATH)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default_rules, f, indent=4)

    with open(file_path, "r") as f:
        rules_config = json.load(f)
        print(f"Using \033[1;32m{f.name}\033[0m rules config")
        print(
            f"\n\nNote: If you want to add more rules, please modified \033[1;32m{f.name}\033[0m rules config"
        )

    return rules_config


def load_server_config(data):
    assert isinstance(data, dict), "data should be a dict"

    server_uuid = data.get("uuid")
    server_port = data.get("port")
    server_address = data.get("addr")
    server_protocol = data.get("protocol")
    server_method = data.get("method")
    server_note = data.get("note")

    assert isinstance(server_uuid, str)
    assert isinstance(server_port, str)
    assert isinstance(server_address, str)
    assert isinstance(server_protocol, str)

    for server in [ServerProtocolA, ServerProtocolB, ServerProtocolC]:
        if server.NAME == server_protocol:
            print(f"Loading \033[1;32m{server_note}\033[0m server config")
            return server(server_address, int(server_port), server_uuid, server_method)

    print(f"Unsupport server protocol: {server_protocol}")
    exit(1)


def main():
    args = args_parse()

    input_file = args.input
    output_file = args.output

    http_port = args.http_port
    allow_lan = args.allow_lan

    with open(input_file, "r", encoding="utf-8") as f:
        outbounds_protocol = load_server_config(json.load(f))

    with open(output_file, "w") as f:
        config = {
            "inbounds": configProjectV().inbounds(allow_lan, http_port),
            "outbounds": configProjectV().outbounds(outbounds_protocol),
            "routing": configProjectV().routing(),
        }

        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main()
