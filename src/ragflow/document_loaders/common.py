from enum import Enum

class DocumentType(Enum):
    csv = ["csv"]
    excel = ["xlsx", "xls"]
    markdown = ["md"]
    pdf = ["pdf"]
    text = ["txt"]
    word = ["docx", "doc"]
    ppt = ['pptx']