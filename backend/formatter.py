from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import io
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def add_bottom_border(paragraph):
    """Add a bottom border to a paragraph"""
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'auto')
    pBdr.append(bottom)
    
    pPr.append(pBdr)


def get_template_path():
    """Get the template file path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(current_dir, '../templates/sample_formatted.docx'),
        os.path.join(current_dir, 'templates/sample_formatted.docx'),
        'templates/sample_formatted.docx',
        os.path.join(os.path.dirname(current_dir), 'templates/sample_formatted.docx')
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Template file not found.")


def get_claude_client():
    """Initialize and return Claude client"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return Anthropic(api_key=api_key)


def split_text_into_chunks(text: str, max_chunk_size: int = 15000) -> list[str]:
    """
    Split transcript into smaller chunks to avoid token limits.
    Tries to split at natural boundaries (speaker changes, sentences).
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        # Try to find a good splitting point
        chunk_end = min(current_pos + max_chunk_size, len(text))
        
        if chunk_end >= len(text):
            # Last chunk
            chunks.append(text[current_pos:])
            break
        
        # Try to find a speaker boundary
        next_speaker = text.find(':', chunk_end - 500, chunk_end)
        if next_speaker > current_pos:
            chunk_end = next_speaker + 50  # Include the speaker name
        
        chunks.append(text[current_pos:chunk_end])
        current_pos = chunk_end
    
    return chunks

def format_transcript_with_claude(text: str) -> bytes:
    """
    Use Claude AI to format the transcript according to professional standards.
    """
    client = get_claude_client()
    
    # Open the template
    template_path = get_template_path()
    doc = Document(template_path)
    
    # Prepare the comprehensive formatting instructions
    system_prompt = """You are a professional transcript formatting assistant specializing in converting raw TV show transcripts into polished, publication-ready documents with excellent readability and logical flow.

Your task is to transform unformatted transcript text into well-structured, readable content that will be formatted into a professional Word document.

Return the formatted content as JSON with this structure:
{
  "title": "Episode Title",
  "segments": [
    {
      "type": "speaker|music|scripture|narration",
      "speaker": "Speaker name or null",
      "content": "Concise, readable content (2-3 sentences max per segment to avoid truncation)",
      "emphasis": [{"text": "example", "style": "bold|italic"}]
    }
  ]
}

IMPORTANT: Keep content concise (max 200 characters per segment) to avoid token limits. Split long speeches into multiple segments if needed.

CRITICAL READABILITY REQUIREMENTS:
1. SENTENCE STRUCTURE: Break long, complex sentences into shorter, more readable sentences
2. PARAGRAPH LENGTH: Keep paragraphs to 3-5 sentences for better readability
3. LOGICAL FLOW: Ensure each paragraph has a clear topic and flows naturally to the next
4. TRANSITIONS: Add natural transitions between topics and speakers
5. CLARITY: Remove run-on sentences and fix awkward phrasing
6. PUNCTUATION: Add proper punctuation where missing
7. CAPITALIZATION: Correct improper capitalization for professional appearance
8. GRAMMAR: Fix obvious grammatical errors while PRESERVING each speaker's authentic voice and natural speaking style
   - Maintain conversational tone and informal expressions when appropriate
   - Don't over-formalize spoken language
   - Keep regional dialects, idioms, and personal speaking patterns intact
   - Only fix errors that would confuse meaning or look unprofessional

FORMATTING RULES:
- Speaker names: Bold with colon (Dr. Billy Wilson:)
- Show names: Italic (World Impact)
- Websites: Bold (worldimpact.tv)
- Organizations: Bold (ORU, Oral Roberts University)
- Scripture references: Bold (1 John 2:18, 2 Timothy 3:1-5)
- Song titles: Italic with quotes ("Give Me Jesus")
- Music/lyrics: Preserve ♪ symbols, italic text
- Quoted scripture: Italic with quotes ("But mark this...")

Transform the raw transcript to be PROFESSIONALLY READABLE with clear logical flow, proper sentence structure, polished language, and correct grammar. Maintain the original meaning, tone, and EACH SPEAKER'S AUTHENTIC VOICE - preserve their natural speaking style, conversational patterns, and personal expressions. Only fix errors that would hinder readability or professionalism.

IMPORTANT: DO NOT include standalone musical symbol segments (like "♪♪♪ ♪♪♪ ♪♪♪" by itself) that appear right after the title. Skip these noise segments to keep the transcript clean. Only include musical segments if they contain actual lyrics or meaningful musical content."""
    
    # Split transcript into chunks if needed
    chunks = split_text_into_chunks(text)
    print(f"Processing transcript in {len(chunks)} chunk(s)")
    
    all_segments = []
    title = None
    
    for i, chunk in enumerate(chunks):
        user_message = f"""Format this raw transcript according to professional standards:\n\n{chunk}"""
        
        # Call Claude with optimized parameters for readability
        # Use non-streaming to avoid connection issues
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",  # Using Claude Sonnet 4
                max_tokens=8192,  # Maximum allowed for Claude Sonnet
                temperature=0.2,  # Lower temperature for more consistent, polished output
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                stream=False  # Non-streaming for reliability
            )
            
            # Get the response text
            full_response = response.content[0].text if response.content else ""
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            # If Claude fails, return basic formatted document
            return format_basic_transcript(text)
        
        # Parse the JSON response
        # Extract JSON from markdown fences if present
        if '```json' in full_response:
            full_response = full_response.split('```json')[1].split('```')[0]
        elif '```' in full_response:
            full_response = full_response.split('```')[1]
        
        import json
        try:
            chunk_data = json.loads(full_response)
            print(f"Successfully parsed chunk {i+1} with {len(chunk_data.get('segments', []))} segments")
            
            # Store title from first chunk only
            if i == 0 and chunk_data.get("title"):
                title = chunk_data["title"]
            
            # Collect segments from this chunk
            all_segments.extend(chunk_data.get("segments", []))
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in chunk {i+1}: {e}")
            
            # Try to repair truncated JSON
            try:
                last_brace = full_response.rfind('}')
                second_last_brace = full_response.rfind('}', 0, last_brace) if last_brace > 0 else -1
                
                if last_brace > 0 and second_last_brace > 0:
                    repaired = full_response[:second_last_brace+1] + ']}'
                    try:
                        chunk_data = json.loads(repaired)
                        print(f"Successfully repaired chunk {i+1} JSON with {len(chunk_data.get('segments', []))} segments")
                        if i == 0 and chunk_data.get("title"):
                            title = chunk_data["title"]
                        all_segments.extend(chunk_data.get("segments", []))
                    except json.JSONDecodeError:
                        repaired = full_response[:last_brace+1] + ']}'
                        chunk_data = json.loads(repaired)
                        print(f"Successfully repaired chunk {i+1} JSON with {len(chunk_data.get('segments', []))} segments")
                        if i == 0 and chunk_data.get("title"):
                            title = chunk_data["title"]
                        all_segments.extend(chunk_data.get("segments", []))
            except Exception as repair_err:
                print(f"JSON repair failed for chunk {i+1}: {repair_err}")
    
    # Combine all segments into one structure
    data = {
        "title": title or "World Impact Transcript",
        "segments": all_segments
    }
    
    print(f"Total segments after combining: {len(all_segments)}")
    
    # Apply formatting to document
    if data.get("title"):
        title_para = doc.add_paragraph(data["title"])
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in title_para.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(18)
            run.bold = True
        title_para.paragraph_format.space_before = Pt(12)
        title_para.paragraph_format.space_after = Pt(18)
        add_bottom_border(title_para)
    
    # Process segments
    prev_seg_type = None
    
    for i, segment in enumerate(data.get("segments", [])):
        seg_type = segment.get("type", "narration")
        content = segment.get("content", "")
        speaker = segment.get("speaker")
        emphasis = segment.get("emphasis", [])
        
        # Filter out pure musical symbol noise (after title)
        if i <= 2 and content.strip() in ['♪♪♪', '♪♪', '♪♪♪ ♪♪♪', '♪♪♪ ♪♪♪ ♪♪♪', '♪ ♪ ♪']:
            continue  # Skip pure musical symbol segments right after title
        
        # Add extra break when transitioning between different content types
        if prev_seg_type and prev_seg_type != seg_type:
            # Add extra spacing for major transitions
            blank_para = doc.add_paragraph()
            blank_para.paragraph_format.space_after = Pt(3)
        
        # Track previous values for transitions
        prev_seg_type = seg_type
        
        if seg_type == "speaker":
            # Add speaker line
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            para.paragraph_format.line_spacing = 1.2  # Increased for better readability
            para.paragraph_format.space_before = Pt(3)  # Add space before speaker for clarity
            
            # Add speaker name in bold
            if speaker:
                speaker_run = para.add_run(f"{speaker}: ")
                speaker_run.font.name = 'Calibri'
                speaker_run.font.size = Pt(12)
                speaker_run.bold = True
                speaker_run.italic = False
                content = content[len(speaker)+1:].strip() if content.startswith(speaker) else content
            
            # Add content with emphasis
            add_formatted_text(content, emphasis, para)
            
            para.paragraph_format.space_after = Pt(9)  # Increased for better readability
        
        elif seg_type == "music":
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            para.paragraph_format.line_spacing = 1.2  # Increased for better readability
            
            music_run = para.add_run(content)
            music_run.font.name = 'Calibri'
            music_run.font.size = Pt(12)
            music_run.italic = True
            music_run.bold = False
            
            para.paragraph_format.space_after = Pt(3)
        
        elif seg_type == "scripture":
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            para.paragraph_format.line_spacing = 1.2  # Increased for better readability
            para.paragraph_format.left_indent = Inches(0.5)
            
            scripture_run = para.add_run(content)
            scripture_run.font.name = 'Calibri'
            scripture_run.font.size = Pt(12)
            scripture_run.bold = True
            scripture_run.italic = False
            
            para.paragraph_format.space_after = Pt(9)  # Increased for better readability
        
        else:  # narration
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            para.paragraph_format.line_spacing = 1.2  # Increased for better readability
            para.paragraph_format.first_line_indent = Inches(0.25)
            
            add_formatted_text(content, emphasis, para)
            
            para.paragraph_format.space_after = Pt(9)  # Increased for better readability
    
    # Save to bytes
    doc_bytes = io.BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)
    return doc_bytes.read()


def add_formatted_text(text: str, emphasis_list: list, para):
    """Add text to paragraph with emphasis formatting using regex for reliability"""
    import re
    
    if not emphasis_list:
        # Simple text without emphasis
        run = para.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.bold = False
        run.italic = False
        return
    
    # Sort emphasis by occurrence in text, avoiding duplicates
    emph_positions = []
    seen_positions = set()
    for emph in emphasis_list:
        emph_text = emph.get("text", "")
        style = emph.get("style", "")
        # Find all occurrences
        for match in re.finditer(re.escape(emph_text), text):
            pos_key = (match.start(), match.end())
            if pos_key not in seen_positions:
                emph_positions.append((match.start(), match.end(), emph_text, style))
                seen_positions.add(pos_key)
    
    if not emph_positions:
        # No matches found, just add the text
        run = para.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.bold = False
        run.italic = False
        return
    
    # Sort by position
    emph_positions.sort()
    
    # Apply emphasis (handle overlapping spans by taking the maximum)
    last_pos = 0
    for i, (start, end, emph_text, style) in enumerate(emph_positions):
        # Skip if this span is already covered
        if start < last_pos:
            continue
            
        # Add text before this emphasis
        if start > last_pos:
            before = text[last_pos:start]
            if before:
                run = para.add_run(before)
                run.font.name = 'Calibri'
                run.font.size = Pt(12)
                run.bold = False
                run.italic = False
        
        # Add emphasized text
        emph_run = para.add_run(emph_text)
        emph_run.font.name = 'Calibri'
        emph_run.font.size = Pt(12)
        
        if style == "bold":
            emph_run.bold = True
            emph_run.italic = False
        elif style in ["italic", "italic_quote"]:
            emph_run.italic = True
            emph_run.bold = False
        else:
            emph_run.bold = False
            emph_run.italic = False
        
        last_pos = end
    
    # Add remaining text
    if last_pos < len(text):
        remaining = text[last_pos:]
        if remaining:
            run = para.add_run(remaining)
            run.font.name = 'Calibri'
            run.font.size = Pt(12)
            run.bold = False
            run.italic = False


def format_basic_transcript(text: str) -> bytes:
    """
    Fallback formatting function when AI fails.
    Returns a basic formatted document.
    """
    try:
        template_path = get_template_path()
        doc = Document(template_path)
        
        # Add a title paragraph
        title_para = doc.add_paragraph("Transcript")
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in title_para.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(18)
            run.bold = True
        title_para.paragraph_format.space_after = Pt(18)
        add_bottom_border(title_para)
        
        # Add content
        content_para = doc.add_paragraph(text)
        content_para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        content_para.paragraph_format.line_spacing = 1.2
        content_para.paragraph_format.first_line_indent = Inches(0.25)
        content_para.paragraph_format.space_after = Pt(9)
        
        # Save to bytes
        doc_bytes = io.BytesIO()
        doc.save(doc_bytes)
        doc_bytes.seek(0)
        return doc_bytes.read()
    except Exception as e:
        print(f"Error in format_basic_transcript: {e}")
        raise


def format_transcript(text: str, title: str = None) -> bytes:
    """Main entry point for formatting"""
    try:
        return format_transcript_with_claude(text)
    except Exception as e:
        print(f"Error in format_transcript: {e}")
        # Fallback to basic formatting
        return format_basic_transcript(text)
