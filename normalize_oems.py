import csv
import re

def normalize_name(name):
    """
    Normalizes an OEM/Product string to the likely OEM name.
    """
    original = name
    name = name.strip()
    
    # Remove markdown bolding asterisks and strike-through artifacts
    name = name.replace("*", "")
    name = re.sub(r"~~.*~~", "", name) # Remove strict strikethrough blocks if any
    name = re.sub(r"[~\|]+", "", name) # Remove leftover ~ and | characters from table artifacts
    
    # Remove "L-<number>" prefixes (e.g., L-13, L-4-4)
    name = re.sub(r"^L-[\d-]+", "", name).strip()
    
    # Common mappings
    mappings = {
        "checkpoint": "Check Point",
        "check point": "Check Point",
        "che k point": "Check Point", # Handle the broken artifact "Che  k Point"
        "crowdstrike": "CrowdStrike",
        "cyberark": "CyberArk",
        "cyber ark": "CyberArk",
        "palo alto": "Palo Alto Networks",
        "paloalto": "Palo Alto Networks",
        "prisma": "Palo Alto Networks",
        "zscaler": "Zscaler",
        "tenable": "Tenable",
        "trellix": "Trellix",
        "vmray": "VMRay",
        "sophos": "Sophos",
        "sentinelone": "SentinelOne",
        "sentinel one": "SentinelOne",
        "singularity": "SentinelOne",
        "proofpoint": "Proofpoint",
        "pfpt": "Proofpoint",
        "psat": "Proofpoint",
        "tessian": "Proofpoint",
        "infoblox": "Infoblox",
        "nios": "Infoblox",
        "fortinet": "Fortinet",
        "forti": "Fortinet", # Catch FortiEDR, FortiGate, etc.
        "forescout": "Forescout",
        "elastic": "Elastic",
        "couchbase": "Couchbase",
        "cisco": "Cisco",
        "viptela": "Cisco",
        "duo": "Cisco",
        "broadcom": "Broadcom",
        "akamai": "Akamai",
        "armis": "Armis",
        "axonius": "Axonius",
        "axonious": "Axonius",
        "barracuda": "Barracuda",
        "bluevoyant": "BlueVoyant",
        "cloudflare": "Cloudflare",
        "cohesity": "Cohesity",
        "commvault": "Commvault",
        "darktrace": "Darktrace",
        "dell": "Dell",
        "forcepoint": "Forcepoint",
        "google": "Google",
        "ibm": "IBM",
        "ivanti": "Ivanti",
        "ivant": "Ivanti",
        "microsoft": "Microsoft",
        "intune": "Microsoft",
        "entra": "Microsoft",
        "defender": "Microsoft",
        "okta": "Okta",
        "omnissa": "Omnissa",
        "rapid7": "Rapid7",
        "servicenow": "ServiceNow",
        "splunk": "Splunk",
        "tanium": "Tanium",
        "trend micro": "Trend Micro",
        "trend vision": "Trend Micro", 
        "vision one": "Trend Micro",
        "taegis": "Secureworks", 
        "nessus": "Tenable",
        "mandiant": "Google", 
        "mcafee": "Trellix", 
        "fireeye": "Trellix", 
        "carbon black": "Broadcom", 
        "symantec": "Broadcom", 
        "metallic": "Commvault", 
        "fiddler": "Fiddler AI",
        "wiz": "Wiz",
        "snowflake": "Snowflake",
        "rubrik": "Rubrik",
        "sailpoint": "SailPoint",
        "secureworks": "Secureworks",
        "shodan": "Shodan",
        "solarwinds": "SolarWinds",
        "varonis": "Varonis",
        "versa": "Versa Networks",
        "zimperium": "Zimperium",
        "archer": "Archer",
        "arctic wolf": "Arctic Wolf",
        "mix mode": "MixMode",
        "mixmode": "MixMode",
        "black kite": "Black Kite",
        "apptega": "Apptega",
        "wazuh": "Wazuh",
        "torq": "Torq",
        "qualys": "Qualys",
        "onspring": "OnSpring",
        "netscout": "NETSCOUT",
        "netskope": "Netskope",
        "mimecast": "Mimecast",
        "lookout": "Lookout",
        "lumen": "Lumen",
        "logrhythm": "LogRhythm",
        "knowbe4": "KnowBe4",
        "halcyon": "Halcyon",
        "heimdal": "Heimdal",
        "island": "Island",
        "invicti": "Invicti",
        "ironradar": "IronRadar",
        "iris": "IRIS Tech",
        "kaseya": "Kaseya",
        "manageengine": "ManageEngine",
        "blueally": "BlueAlly",
        "abnormal security": "Abnormal Security",
        "adlumin": "Adlumin",
        "anomali": "Anomali",
        "centripetal": "Centripetal",
        "cribl": "Cribl",
        "critical start": "Critical Start",
        "cylance": "Cylance",
        "deepseas": "DeepSeas",
        "diligent": "Diligent",
        "drata": "Drata",
        "egnyte": "Egnyte",
        "extrahop": "ExtraHop",
        "freshworks": "Freshworks",
        "greymatter": "GreyMatter",
        "hyperproof": "Hyperproof",
        "legato": "Legato Security",
        "paramify": "Paramify",
        "pulse": "Pulse",
        "sepio": "SEPIO",
        "sepio": "SEPIO",
        "secpod": "SecPod",
        "semperis": "Semperis",
        "threatspike": "ThreatSpike",
        "vanta": "Vanta",
        "recorded future": "Recorded Future",
        "highwire": "HighWire Networks",
        "n-able": "N-Able",
        "one identity": "One Identity",
        "skyhigh": "Skyhigh Security",
        "threatboard": "ThreatBoard",
        "divergent": "Divergent",
        "rsm": "RSM",
        "shi": "SHI",
        "nvisionx": "NVISIONx",
        "netwatch": "NetWatch.ai",
        "di suite": "DI Suite", 
        "disp": "DISP", 
        "socure": "Socure",
        "che   ility m": "Check Point", # specific garbage mapping
        "directory services protector": "Semperis",
        "hosted fortisiem": "Fortinet",
        "soc co-managed fortiedr": "Fortinet",
        "secure email relay": "Proofpoint",
    }
    
    # 1. Lowercase for matching
    lower_name = name.lower()
    
    # 2. Check for known keys in the start of the string
    for key, value in mappings.items():
        if lower_name.startswith(key):
            return value
        # Also check if key appears as a distinct word
        if re.search(r'\b' + re.escape(key) + r'\b', lower_name):
            return value

    # 3. Strip "Inc", "LLC", etc.
    name = re.sub(r",?\s*(Inc|LLC|Corp|Ltd|Corporation)\.?$", "", name, flags=re.IGNORECASE)
    
    # 4. Remove anything after specialized separators like " - ", ":", "(", " w/"
    name = re.split(r"[:\(\)]| - | w/| with ", name)[0]
   
    # 5. Filter out generic terms
    generic_terms = [
        "Identity Access Management",
        "Implementation and Training",
        "Service Category",
        "Labor, Services and Technology",
        "Managed External Attack Surface Management",
        "Managed, Detection and Response",
        "Mobile Threat Defense",
        "Observability & Security Platform",
        "SASE Security",
        "Secure Access Service Edge",
        "Security Operations Platform",
        "Vulnerability assessment",
        "Vulnerability Management",
        "Email Security",
        "Content Delivery Network",
        "Antivirus for Amazon S3",
        "SecOps",
        "Tech Risk and Compliance",
        "Security Software Design",
        "Value Add",
        "Singularity",
        "Hosted",
        "Managed",
    ]
    
    clean_name = name.strip()
    for term in generic_terms:
        if term.lower() in clean_name.lower():
            # If it's JUST the generic term (or close to it), return None to filter it out
            if len(clean_name) < len(term) + 5: 
                return None
            
    if not clean_name or len(clean_name) < 3:
        return None
        
    return clean_name

def main():
    input_file = "unique_oems.csv"
    output_file = "final_unique_oems.csv"
    
    raw_entries = set()
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row:
                    raw_entries.add(row[0])
    except FileNotFoundError:
        print("Input file not found.")
        return

    normalized_oems = set()
    for entry in raw_entries:
        norm = normalize_name(entry)
        if norm:
            normalized_oems.add(norm)
            
    # Sorted list
    sorted_oems = sorted(list(normalized_oems), key=lambda x: x.lower())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Unique OEMs"])
        for oem in sorted_oems:
            writer.writerow([oem])
            
    print(f"Processed {len(raw_entries)} raw entries into {len(sorted_oems)} unique OEMs.")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
