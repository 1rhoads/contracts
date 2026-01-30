
SERVICE_CATEGORIES = {
    "1": "Endpoint-Based Asset Discovery",
    "2": "Network-Based Asset Discovery",
    "3": "Endpoint Detection and Response",
    "4": "External-Facing Asset Discovery",
    "5": "Email Security",
    "6": "Content Delivery Network",
    "7": "Security Operations Platform",
    "8": "Identity and Access Management (IAM)",
    "9": "Mobile Security and Threat Detection",
    "10": "Secure Access Service Edge (SASE)",
    "11": "Governance, Risk, and Compliance (GRC)",
    "12": "IT Service Management (ITSM)",
    "13": "Vulnerability Assessment and Management",
    "14": "Cybersecurity Threat Intelligence (CTI)",
    "15": "Data Security",
    "16": "Enterprise Security Log Management, Analytics, and Response"
}

def extract_categories(content):
    found_categories = []
    # Normalize content for search (optional, but good for messy spacing)
    # content_norm = " ".join(content.split()) 
    
    for num, name in SERVICE_CATEGORIES.items():
        # Search for "Service Category X:"
        # We look for the number specifically to be precise, or the name?
        # The user text has "Service Category 1: Endpoint..."
        # Let's search for "Service Category {num}"
        pattern = f"Service Category {num}"
        if pattern in content:
            found_categories.append(f"{num}. {name}")
            
    return found_categories
