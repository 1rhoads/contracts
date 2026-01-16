import os
import urllib.request
import time

PDF_DIR = "pdfs"

# List extracted by browser subagent
PDF_LINKS = [
  {"text": "Agency Organization", "href": "https://www.dms.myflorida.com/content/download/97128/file/1-0%20Dept%20of%20Management%20Services%20Overview%20with%20Names%2024-25%20FY%20COLORED.pdf"},
  {"text": "AccessIT Group Inc.", "href": "https://www.dms.myflorida.com/content/download/404577/8227812/Exhibit%20B%20-%20AccessIT.pdf"},
  {"text": "Barracuda Networks, Inc.", "href": "https://www.dms.myflorida.com/content/download/404579/8227826/Exhibit%20B%20-%20Barracuda.pdf"},
  {"text": "Blackwood Associates, Inc.", "href": "https://www.dms.myflorida.com/content/download/404580/8227833/Exhibit%20B%20-%20Blackwood.pdf"},
  {"text": "BlueAlly Technology Solutions, LLC", "href": "https://www.dms.myflorida.com/content/download/404919/8231179/Exhibit_B_-_BlueAlly.pdf"},
  {"text": "Carahsoft Technology Corp.", "href": "https://www.dms.myflorida.com/content/download/423770/8789845/Exhibit_B_-_Carahsoft.pdf"},
  {"text": "CDW Government LLC", "href": "https://www.dms.myflorida.com/content/download/404769/8229361/Exhibit_B_-_CDWG.pdf"},
  {"text": "CenturyLink Communications, LLC", "href": "https://www.dms.myflorida.com/content/download/404833/8229932/Exhibit%20B%20-%20CenturyLink.pdf"},
  {"text": "Check Point Software Technologies LTD", "href": "https://www.dms.myflorida.com/content/download/404770/8229368/Exhibit%20B%20-%20Check%20Point.pdf"},
  {"text": "ConvergeOne, Inc.", "href": "https://www.dms.myflorida.com/content/download/405109/8233082/Exhibit%20B%20-%20Converge.pdf"},
  {"text": "Deloitte & Touche LLP", "href": "https://www.dms.myflorida.com/content/download/404950/8231466/Exhibit%20B%20-%20Deloitte.pdf"},
  {"text": "DG Technology Consulting LLC", "href": "https://www.dms.myflorida.com/content/download/404581/8227840/Exhibit%20B%20-%20DG.pdf"},
  {"text": "DigitalEra Group, L.L.C.", "href": "https://www.dms.myflorida.com/content/download/404921/8231205/Exhibit%20B%20-%20DigitalEra.pdf"},
  {"text": "Divergent Solutions, LLC", "href": "https://www.dms.myflorida.com/content/download/404834/8229939/Exhibit%20B%20-%20Divergent.pdf"},
  {"text": "EC America, Inc.", "href": "https://www.dms.myflorida.com/content/download/404582/8227847/Exhibit%20B%20-%20EC.pdf"},
  {"text": "FortifyData Inc", "href": "https://www.dms.myflorida.com/content/download/404583/8227854/Exhibit%20B%20-%20FortifyData.pdf"},
  {"text": "Gamma Defense", "href": "https://www.dms.myflorida.com/content/download/404584/8227861/Exhibit%20B%20-%20Gamma.pdf"},
  {"text": "Hayes E-Government Resources, Inc.", "href": "https://www.dms.myflorida.com/content/download/404585/8227868/Exhibit%20B%20-%20Hayes.pdf"},
  {"text": "Insight Public Sector, Inc.", "href": "https://www.dms.myflorida.com/content/download/404586/8227875/Exhibit_B_-_Insight.pdf"},
  {"text": "IRIS Tech Inc.", "href": "https://www.dms.myflorida.com/content/download/404587/8227882/Exhibit%20B%20-%20IRIS.pdf"},
  {"text": "Kapoor IT Consulting, LLC DBA K.I.T.C. LLC", "href": "https://www.dms.myflorida.com/content/download/404588/8227889/Exhibit%20B%20-%20Kapoor.pdf"},
  {"text": "KPMG LLP", "href": "https://www.dms.myflorida.com/content/download/404589/8227896/Exhibit%20B%20-%20KPMG.pdf"},
  {"text": "KR2 Technology, LLC", "href": "https://www.dms.myflorida.com/content/download/404590/8227903/Exhibit%20B%20-%20KR2.pdf"},
  {"text": "Mainline Information Systems, LLC", "href": "https://www.dms.myflorida.com/content/download/404835/8229946/Exhibit_B_-_Mainline.pdf"},
  {"text": "MAVERC LLC", "href": "https://www.dms.myflorida.com/content/download/404591/8227910/Exhibit%20B%20-%20Maverc.pdf"},
  {"text": "Nethive LLC", "href": "https://www.dms.myflorida.com/content/download/404592/8227917/Exhibit%20B%20-%20Nethive.pdf"},
  {"text": "Network Digital Security, Inc", "href": "https://www.dms.myflorida.com/content/download/404593/8227924/Exhibit%20B%20-%20Network.pdf"},
  {"text": "NWN Corporation", "href": "https://www.dms.myflorida.com/content/download/435786/9120551/Exhibit%20B%20-%20NWN.pdf"},
  {"text": "Optiv Security Inc.", "href": "https://www.dms.myflorida.com/content/download/404771/8229375/Exhibit%20B%20-%20Optiv.pdf"},
  {"text": "PC Solutions & Integration, Inc.", "href": "https://www.dms.myflorida.com/content/download/404594/8227931/Exhibit_B_-_PCS.pdf"},
  {"text": "Peraton State & Local Inc.", "href": "https://www.dms.myflorida.com/content/download/404772/8229382/Exhibit%20B%20-%20Peraton.pdf"},
  {"text": "ProCom Consulting, Inc.", "href": "https://www.dms.myflorida.com/content/download/424055/8792816/Exhibit%20B%20-%20ProCom.pdf"},
  {"text": "PruTech Solutions, Inc.", "href": "https://www.dms.myflorida.com/content/download/404722/8228967/Exhibit%20B%20-%20PruTech.pdf"},
  {"text": "R2 Unified Technologies, LLC", "href": "https://www.dms.myflorida.com/content/download/404774/8229396/Exhibit%20B%20-%20R2.pdf"},
  {"text": "RSM US LLP", "href": "https://www.dms.myflorida.com/content/download/423939/8791699/Exhibit%20B%20-%20RSM.pdf"},
  {"text": "Scyre LLC", "href": "https://www.dms.myflorida.com/content/download/404599/8227966/Exhibit%20B%20-%20Scyre.pdf"},
  {"text": "SGS Technologie LLC", "href": "https://www.dms.myflorida.com/content/download/404773/8229389/Exhibit%20B%20-%20SGS.pdf"},
  {"text": "SHI International Corp.", "href": "https://www.dms.myflorida.com/content/download/404836/8229953/Exhibit_B_-_SHI.pdf"},
  {"text": "Skyline Technology Solutions, LLC", "href": "https://www.dms.myflorida.com/content/download/404600/8227973/Exhibit%20B%20-%20Skyline.pdf"},
  {"text": "Squadra Solutions, LLC", "href": "https://www.dms.myflorida.com/content/download/404922/8231212/Exhibit_B_-_Squadra.pdf"},
  {"text": "St. Louis Based World Wide Technology, LLC", "href": "https://www.dms.myflorida.com/content/download/404601/8227980/Exhibit%20B%20-%20WWT.pdf"},
  {"text": "Stellar IT Solutions, Inc.", "href": "https://www.dms.myflorida.com/content/download/404924/8231222/Exhibit%20B%20-%20Stellar.pdf"},
  {"text": "Telaforce LLC dba Titan Technologies LLC", "href": "https://www.dms.myflorida.com/content/download/433657/9058497/Exhibit%20B%20-%20Titan.pdf"},
  {"text": "Thrive Operations, LLC", "href": "https://www.dms.myflorida.com/content/download/404602/8227987/Exhibit.pdf"},
  {"text": "Trend Micro Inc.", "href": "https://www.dms.myflorida.com/content/download/404838/8229968/Exhibit%20B%20-%20Trend.pdf"},
  {"text": "United Data Technologies, Inc.", "href": "https://www.dms.myflorida.com/content/download/404775/8229403/Exhibit_B_-_UDT.pdf"}
]

def download_file(url, filepath):
    try:
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
        
    print(f"Downloading {len(PDF_LINKS)} PDFs...")
    
    for item in PDF_LINKS:
        text = item['text']
        url = item['href']
        
        # Clean filename
        safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        if not safe_text:
            safe_text = "document"
            
        filename = f"{safe_text}.pdf"
        filepath = os.path.join(PDF_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"Skipping {filename} (already exists)")
            continue
            
        print(f"Downloading {text}...")
        if download_file(url, filepath):
            print(f"Success: {filename}")
        else:
            print(f"Failed: {filename}")
            
        time.sleep(0.5)

if __name__ == "__main__":
    main()
