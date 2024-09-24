import fitz  # PyMuPDF
from Levenshtein import distance as levenshtein_distance
from diff_match_patch import diff_match_patch
import concurrent.futures

# Function to extract text from a PDF by page
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pdf_text = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")  # Extracts plain text
        pdf_text.append(text)
    return pdf_text

# Function to compare texts using Levenshtein distance or diff-match-patch
def compare_texts(master_text, edited_text):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(master_text, edited_text)
    dmp.diff_cleanupSemantic(diffs)
    return diffs

# Function to highlight differences in the PDF
def highlight_differences_in_pdf(edited_pdf_path, diffs, output_pdf_path):
    doc = fitz.open(edited_pdf_path)
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        # Loop through diffs and highlight changes
        for op, data in diffs:
            if op == 1:  # Insertion
                highlight_text_in_page(page, data, color=(0, 1, 0))  # Green for insertion
            elif op == -1:  # Deletion
                highlight_text_in_page(page, data, color=(1, 0, 0))  # Red for deletion

    doc.save(output_pdf_path)

# Function to highlight text in a page
def highlight_text_in_page(page, text_to_highlight, color=(1, 0, 0)):
    text_instances = page.search_for(text_to_highlight)
    # Check if text_instances is not None and has found any instances
    if text_instances is not None and len(text_instances) > 0:
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.set_colors({"stroke": color})
            highlight.update()  # Update the annotation
    else:
        print(f"No instances found for: '{text_to_highlight}' on this page.")
# Function to process and compare each page separately for better performance
def process_pdf_pages(master_pdf, edited_pdf, output_pdf, num_workers=4):
    master_text = extract_text_from_pdf(master_pdf)
    edited_text = extract_text_from_pdf(edited_pdf)
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for master_page, edited_page in zip(master_text, edited_text):
            futures.append(executor.submit(compare_texts, master_page, edited_page))
        
        # Retrieve and apply diffs
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            diffs = future.result()
            highlight_differences_in_pdf(edited_pdf, diffs, output_pdf)

if __name__ == "__main__":
    master_pdf_path = "master (1).pdf"
    edited_pdf_path = "edited.pdf"
    output_pdf_path = "highlighted_agreement.pdf"
    
    process_pdf_pages(master_pdf_path, edited_pdf_path, output_pdf_path, num_workers=8)
