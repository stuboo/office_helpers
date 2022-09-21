from flask import app, Flask
import json
from fpdf import FPDF
from PyPDF2 import PdfFileReader
import PyPDF2

with open('input/9b0040bc.json', 'r') as f:
    data = json.load(f)

def merge_pdfs(_pdfs, file_name):
    mergeFile = PyPDF2.PdfFileMerger()
    for _pdf in _pdfs:
        mergeFile.append(PyPDF2.PdfFileReader(_pdf, 'rb'))
    mergeFile.write(f"{file_name}.pdf")

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/intake', methods=['POST', 'GET'])
def create_report():
    # print(data)
    # get the json and make it usable, save it as a file in the appropriate folder (202209)??
    
    # uncomment these eight lines and comment out the with statement on line 7ish when live
    # also remove GET method on this route
    # content = request.json
    # content = json.dumps(content)
    # data = json.loads(content)
    filename = data['results']['ukey']
    # jsonFile = open(f"intpu/{filename}.json", "w+")
    # jsonFile.write(content)
    # jsonFile.close()

    # define variables for TOC (list), bladder diary (bool), and education (list)
    diary = data['results']['diary']
    education = data['results']['edu']
    # print(f"{toc}\n{diary}\n{edu}")
    # generate pdf and save

    # WRITE THE PATIENT LETTER
    letter_text = """Dear Patient,\n\nThank you for coming in today for this initial visit. The time you spent today answering these valuable questions and completing these tests will help Dr. Stewart and the rest of the team greatly in the coming weeks and months. \n\nWith your permission, we will likely perform a short physical exam at the next visit. However, because you spent this time today, the majority of the next visit will be spent determining your goals and working with you to develop a treatment plan.\n\nI encourage you to read through the attached pages as they include specific information surrounding the possible diagnoses and some of the options for treatment. As you read, please write down any questions you may have as they will help to guide our conversation.\n\nI look forward to meeting you at your appointment on _______________ at _______________.\n\nSincerely,\n\n\n\nRyan Stewart, DO, FACOG\nUrogynecology and Female Pelvic Surgery\n\n\n\nP.S. If you haven't already done so, please sign up for MyChart so that we may communicate with one another more easily and efficiently. You can do this using the QR code below and the medical record number on the attached sticker."""
    pdf = FPDF(orientation="P", unit="mm", format="Letter")
    pdf.add_page()
    pdf.set_margins(25.4, 50.8, 25.4)
    pdf.set_font("times", "", 12)
    pdf.write(6, letter_text)
    pdf.image("assets/ryan_signature.png", x=22, y=155, w=0, h=15)
    pdf.image("assets/mychart_qr.png", x=150, y=230, w=30)
    ## sticker box
    pdf.set_draw_color(150)
    pdf.set_xy(45, 235)
    pdf.set_font("helvetica", "B", 8)
    pdf.set_text_color(150)
    pdf.cell(60, 20, txt="PLACE PATIENT STICKER HERE", border=1, align="C")

    # ADD THE TABLE OF CONTENTS
    pdf.set_text_color(0)
    pdf.add_page()
    pdf.set_margins(25.4, 50.8, 25.4)
    pdf.set_font("times", "B", 18)
    pdf.write(22, "Table of Contents\n")
    pdf.set_font("courier", "", 11)
    # monospaced at this size accommodates 70 chars
    if diary:
        lastpage = "4"
    else:
        lastpage = "2"
    for e in education:
        page = str(int(lastpage) + 1)
        page_len = len(page)
        title_len = len(e['title'])
        dot_len = 70 - title_len - page_len
        dots = "."*dot_len
        pdf_path = f"assets/education/iuga/{e['filename']}"
        currentpdf = PdfFileReader(str(pdf_path))
        
        lastpage = str(int(page) + currentpdf.getNumPages() - 1)
        pdf.write(6, f"{e['title']}{dots}{page}\n")

    pdf.set_font("times", "", 12)
    txt = f"\n\nThis document contains {lastpage} pages in total. The included documents were selected for you based on your responses to the questions at your recent visit. They include specific information related to your *possible* diagnoses and some possible options for treatment.\n\nYou can read more about these & other pelvic floor disorders at https://yourpelvicfloor.org and https://voicesforpfd.org"
    pdf.write(6, txt)
    pdf.output(f"output/{filename}_cover.pdf")

    # COMBINE PDF PAGES
    edu_list = [f"output/{filename}_cover.pdf"]
    for e in education:
        edu_list.append(f"assets/education/iuga/{e['filename']}")
    print(edu_list)
    merge_pdfs(edu_list, f"output/{filename}_packet")

    # BUILD THE RESPONSE OBJECT

    education_provided = ""
    for e in education:
        education_provided += "- {title}\n".format(title = e['title']) 

    return {
        "code" : 200,
        "status": "success",
        "data": {
            "resource_id" : filename,
            "education_provided" : education_provided,
            "voiding_diary" : True,
            "packet_url" : f"https://tools-stuboo.pythonanywhere.com/packet/{filename}"
        },
        "messages": [
            f"JSON created with {filename}",
        ] 
    }

@app.route('/packet/<id>', methods=['POST', 'GET'])
def packet(id):
    return {
        "packet_id": f"{id}",
        "message": f"This will eventually return the PDF"
    }

if __name__ == '__main__':
    app.run(debug=True)