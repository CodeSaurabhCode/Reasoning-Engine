import docx
import json
 
class DocxTableExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.document = docx.Document(file_path)
 
    def extract_tables(self):
        """Extracts tables while preserving their structure, including empty cells."""
        tables_data = []
        for table in self.document.tables:
            table_content = []
            for row in table.rows:
                row_content = [cell.text.strip() if cell.text.strip() else "" for cell in row.cells]
                table_content.append(row_content)
            tables_data.append(table_content)
        return tables_data
 
    def save_to_json(self, output_path="tables.json"):
        """Extracts tables and saves them as a JSON file."""
        tables = self.extract_tables()
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump({"tables": tables}, json_file, indent=4, ensure_ascii=False)
        print(f"✅ Extracted tables saved to {output_path}")
 