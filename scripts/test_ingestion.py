
import os
import requests
import io

try:
    from reportlab.pdfgen import canvas
except ImportError:
    print("Please run: pip install reportlab")
    # Just creating a dummy file if reportlab is missing is risky without content
    # But reportlab is not a project dependency, only for test generation.
    # We will try to write a simple text file renamed to pdf? No, PyPDFLoader will fail.
    # Let's rely on reportlab being installed or install it.

def create_test_pdf(filename):
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        import os
        os.system("pip install reportlab")
        from reportlab.pdfgen import canvas

    print(f"Creating test PDF: {filename}")
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Resume -- Test Candidate")
    c.drawString(100, 730, "Name: Alice Wonder")
    c.drawString(100, 710, "Title: Senior Graph Engineer")
    c.drawString(100, 690, "Skills: Neo4j, Python, LangChain, Artificial Intelligence")
    c.drawString(100, 670, "Experience: Worked at Google DeepMind on AlphaGo.")
    c.save()

def main():
    print("🚀 Testing PDF Ingestion...")
    
    # Check for reportlab
    try:
        import reportlab
    except ImportError:
        print("Installing reportlab for test generation...")
        os.system("pip install reportlab")
        
    pdf_path = "test_resume.pdf"
    create_test_pdf(pdf_path)
    
    try:
        url = "http://localhost:8000/api/v1/admin/ingest"
        print(f"POST {url}")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 200:
            print("✅ Ingestion successful!")
        else:
            print("❌ Ingestion failed.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    main()
