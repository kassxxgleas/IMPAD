import json
import os
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from dotenv import load_dotenv

import json
import os
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")

def generate_pdf(data, filename="certificate.pdf"):
    """Generates a PDF certificate based on session data."""
    # Ensure filename is in data/certificates/
    if not os.path.isabs(filename):
        filename = os.path.join("data", "certificates", os.path.basename(filename))
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 100, "CERTIFICATE")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 140, f"Session ID: {data['session_id']}")
    
    c.setFont("Helvetica", 22)
    c.drawCentredString(width / 2, height - 200, f"Awarded to Candidate: {data['candidate_id']}")

    summary = data['summary']
    c.setFont("Helvetica", 18)
    c.drawString(100, height - 350, f"Hard Score: {summary['hard_score']}")
    c.drawString(100, height - 380, f"Soft Score: {summary['soft_score']}")
    c.drawString(100, height - 410, f"Verdict: {summary['verdict']}")
    
    c.save()
    print(f"[INFO] PDF certificate generated successfully: {filename}")
    return filename



def upload_to_pinata(filename):
    """Uploads file to Pinata IPFS and returns the Hash."""
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_KEY
    }
    
    print("[INFO] Initiating upload to Pinata IPFS...")
    
    with open(filename, "rb") as file:
        files = {"file": file}
        response = requests.post(url, files=files, headers=headers)
        
        if response.status_code != 200:
            print(f"[ERROR] Pinata API upload failed. Status Code: {response.status_code}")
            print(f"[DEBUG] Server response: {response.text}")
            raise ConnectionError("Pinata upload failed")
            
        json_response = response.json()
        ipfs_hash = json_response['IpfsHash']
        print(f"[INFO] Upload successful. IPFS Hash: {ipfs_hash}")
        return ipfs_hash

def sign_voucher(ipfs_hash, session_id):
    """Signs the payload (Hash + SessionID) using the Admin Private Key."""
    session_id_str = str(session_id)
    
    encoded_data = Web3.solidity_keccak(
        ['string', 'string'],
        [ipfs_hash, session_id_str]
    )
    
    message = encode_defunct(hexstr=encoded_data.hex())
    signed_message = Account.sign_message(message, ADMIN_PRIVATE_KEY)
    
    print("[INFO] Data signed securely by Admin wallet.")
    return "0x" + signed_message.signature.hex()

def main():
    try:
        with open("session_log.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] File 'session_log.json' not found in the current directory.")
        return

    pdf_filename = generate_pdf(data)

    try:
        ipfs_hash = upload_to_pinata(pdf_filename)
    except Exception as e:
        print("[CRITICAL] Process terminated due to upload failure.")
        return

    try:
        signature = sign_voucher(ipfs_hash, data['session_id'])
    except Exception as e:
        return

    output = {
        "session_id": str(data['session_id']),
        "ipfs_hash": ipfs_hash,
        "signature": signature,
        "pdf_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    }

    output_path = os.path.join("data", "certificates", "mint_data.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)
    
    print("\n[SUCCESS] Operation completed.")
    print(f"[INFO] Minting data saved to '{output_path}'.")
    print("[INFO] Ready to execute frontend minting transaction.")

if __name__ == "__main__":
    main()