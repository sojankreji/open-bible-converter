
import xml.etree.ElementTree as ET

def get_book_details_map(reference_path):
    """
    Parses the reference XML to create a map from book index to a
    dictionary of book details (name, testament).
    """
    details_map = {}
    try:
        tree = ET.parse(reference_path)
        root = tree.getroot()
        # The book tags are direct children of the root 'bible' tag
        for book_elem in root.findall('BIBLEBOOK'):
            index = book_elem.get('bnumber')
            name = book_elem.get('bname')
            bsname = book_elem.get('bsname')
            # The malyalam.xml uses 0-based 'id', reference.xml uses 1-based 'index'
            # We'll store using the 0-based index for easier lookup.
            zero_based_index = str(int(index) - 1)
            details_map[zero_based_index] = {'name': name, 'bsname': bsname}
    except (ET.ParseError, ValueError, AttributeError) as e:
        print(f"Error parsing reference.xml or its structure: {e}")
    return details_map

def convert_bible_xml(source_path, reference_path, output_path):
    """
    Converts the Malayalam Bible XML to the reference format, including an
    <information> tag and using <biblebook> for book elements.
    """
    book_details_map = get_book_details_map(reference_path)
    if not book_details_map:
        print("Could not create book details map from reference.xml. Aborting.")
        return

    try:
        source_tree = ET.parse(source_path)
        source_root = source_tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing malyalam.xml: {e}")
        return

    # Create the root for the new XML
    new_root = ET.Element('bible')

    # Add the <information> tag
    info = ET.SubElement(new_root, 'information')
    ET.SubElement(info, 'name').text = "Malayalam Bible"
    ET.SubElement(info, 'publisher').text = "Public Domain"
    ET.SubElement(info, 'date').text = "Unknown"
    ET.SubElement(info, 'version').text = "1.0"


    # The root of malyalam.xml is <Bible>, its children are <Book>
    for book in source_root.findall('Book'):
        book_id = book.get('id') # This is 0-based index
        book_details = book_details_map.get(book_id, {})
        book_name = book_details.get('name', f"Unknown Book (ID: {book_id})")
        book_bsname = book_details.get('bsname', 'O') # Default to Old

        # Create a new book element as <biblebook>
        new_book = ET.SubElement(new_root, 'biblebook')
        # Add attributes matching reference.xml's <book> tag
        new_book.set('bnumber', str(int(book_id) + 1)) # Convert back to 1-based index
        new_book.set('bname', book_name)
        new_book.set('bsname', book_bsname)

        for chapter in book.findall('Chapter'):
            chapter_id = chapter.get('id')
            new_chapter = ET.SubElement(new_book, 'CHAPTER')
            new_chapter.set('cnumber', chapter_id) # Match attribute name from reference

            for verse in chapter.findall('Verse'):
                verse_id = verse.get('id')
                new_verse = ET.SubElement(new_chapter, 'VERS')
                new_verse.set('vnumber', verse_id) # Match attribute name from reference
                new_verse.text = verse.text.strip() if verse.text else ''

    # Create a new ElementTree and write it to the output file
    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space="    ")
    new_tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Conversion complete. Output saved to {output_path}")

if __name__ == '__main__':
    convert_bible_xml('malyalam.xml', 'reference.xml', 'mal-malsvp.zefania.xml')
