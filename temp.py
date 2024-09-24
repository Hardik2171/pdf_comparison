import fitz  # PyMuPDF
import Levenshtein

def extract_paragraphs_from_pdf(pdf_path):
    """Extracts paragraphs from a PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    paragraphs = []
    
    # Loop through each page
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")  # Get text blocks from the page
        
        for block in blocks:
            block_text = block[4].strip()  # Extract the text part
            # Split into paragraphs based on line breaks or multiple spaces
            block_paragraphs = block_text.split("\n\n")  # Assuming \n\n separates paragraphs
            paragraphs.extend([p.strip() for p in block_paragraphs if p.strip()])
    
    return paragraphs

def highlight_differences_in_pdf(master_pdf, edited_pdf, output_pdf):
    """Highlights differences in the edited PDF based on Levenshtein Distance on paragraphs"""
    
    # Step 1: Extract paragraphs from both PDFs
    master_paragraphs = extract_paragraphs_from_pdf(master_pdf)
    edited_paragraphs = extract_paragraphs_from_pdf(edited_pdf)

    # Step 2: Open the edited PDF for highlighting
    doc = fitz.open(edited_pdf)
    highlight_color = (1, 0, 0)  # Red color for highlighting differences

    # Loop through each page in the edited PDF
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        
        # Get all paragraphs from the current page's blocks
        page_paragraphs = [block[4].strip() for block in blocks if block[4].strip()]
        
        # Step 3: Compare each paragraph from the page with corresponding paragraph in master
        for block, edited_paragraph in zip(blocks, page_paragraphs):
            # Find the closest match in master_paragraphs using Levenshtein distance
            min_distance = float('inf')
            closest_master_paragraph = None
            for master_paragraph in master_paragraphs:
                distance = Levenshtein.distance(master_paragraph, edited_paragraph)
                if distance < min_distance:
                    min_distance = distance
                    closest_master_paragraph = master_paragraph
            
            # Step 4: If the distance is greater than a threshold, highlight it
            if min_distance > 0:  # Set a threshold if needed, like min_distance > 10
                # Highlight this block in the edited PDF
                rect = fitz.Rect(block[:4])  # Get the block's bounding box
                page.add_highlight_annot(rect)
                page.draw_rect(rect, color=highlight_color, width=1)
        
    # Save the highlighted PDF
    doc.save(output_pdf)
    doc.close()
    print(f"Saved highlighted PDF as {output_pdf}")

# Example usage
master_pdf_path = "master (1).pdf"
edited_pdf_path = "edited.pdf"
output_pdf_path = "highlighted_agreement_output.pdf"

highlight_differences_in_pdf(master_pdf_path, edited_pdf_path, output_pdf_path)