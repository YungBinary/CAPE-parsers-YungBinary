"""
Description: Winos 4.0 "OnlineModule" config parser
Author: x.com/YungBinary
"""

from contextlib import suppress
import re


CONFIG_KEY_MAP = {
    "dd": "execution_delay_seconds",
    "cl": "communication_interval_seconds",
    "bb": "version",
    "bz": "comment",
    "jp": "keylogger",
    "bh": "end_bluescreen",
    "ll": "anti_traffic_monitoring",
    "dl": "entrypoint",
    "sh": "process_daemon",
    "kl": "process_hollowing"
}


def find_config(data):
    start = ":db|".encode("utf-16le")
    end = ":1p|".encode("utf-16le")
    pattern = re.compile(re.escape(start) + b".*?" + re.escape(end), re.DOTALL)
    match = pattern.search(data)
    if match:
        return match.group(0).decode("utf-16le")


def extract_config(data: bytes) -> dict:
    config_dict = {}
    final_config = {}

    with suppress(Exception):
        config = find_config(data)
        if not config:
            return config_dict

        # Reverse the config string, which is delimited by '|'
        config = config[::-1]
        # Remove leading/trailing pipes and split into key/value pairs
        elements = [element for element in config.strip('|').split('|') if ':' in element]
        # Split each element for key : value in a dictionary
        config_dict = dict(element.split(':', 1) for element in elements)
        if config_dict:
            # Handle extraction and formatting of CNCs
            for i in range(1, 4):
                p, o, t = config_dict.get(f"p{i}"), config_dict.get(f"o{i}"), config_dict.get(f"t{i}")
                if p and p != "127.0.0.1" and o:
                    protocol = {"0": "udp", "1": "tcp"}.get(t)
                    if protocol:
                        cnc = f"{protocol}://{p}:{o}"
                        final_config.setdefault("CNCs", []).append(cnc)

            if "CNCs" not in final_config:
                return {}

            final_config["CNCs"] = list(set(final_config["CNCs"]))
            # Extract campaign ID
            final_config["campaign_id"] = "default" if config_dict["fz"] == "\u9ed8\u8ba4" else config_dict["fz"]

            # Map keys, e.g. dd -> execution_delay_seconds
            final_config["raw"] = {v: config_dict[k] for k, v in CONFIG_KEY_MAP.items() if k in config_dict}

    return final_config


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], "rb") as f:
        print(extract_config(f.read()))
