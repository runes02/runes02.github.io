import os
import xml.etree.ElementTree as ET
from urllib.parse import quote
from xml.dom import minidom

def create_xml_from_mp3s(base_directory, radio_name, radio_description):
    # Create the root element with the Radio tag
    radio = ET.Element("Radio", name=radio_name, description=radio_description)
    albums = ET.SubElement(radio, "Albums")

    for folder in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder)
        if os.path.isdir(folder_path):
            dir_path = quote(f"/tracks/{folder.replace('\\', '/')}")

            album = ET.SubElement(albums, "Album", name=folder, dir=dir_path)

            mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
            mp3_files.sort()

            for index, mp3_file in enumerate(mp3_files):
                encoded_file_name = quote(mp3_file)
                ET.SubElement(album, "Song", index=str(index)).text = encoded_file_name

    xml_str = ET.tostring(radio, encoding='utf-8', method='xml')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")

    xml_filename = os.path.join(base_directory, "Tracks.xml")
    with open(xml_filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)
    
    print(f"XML file created: {xml_filename}")

if __name__ == "__main__":
    # Prompt for Radio name and description
    radio_name = input("Enter the name for the Radio: ")
    radio_description = input("Enter the description for the Radio: ")

    # Get the current working directory
    current_directory = os.getcwd()
    
    # Create the XML with the provided inputs
    create_xml_from_mp3s(current_directory, radio_name, radio_description)
