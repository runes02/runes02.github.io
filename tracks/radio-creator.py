import os
import xml.etree.ElementTree as ET
from urllib.parse import quote
from xml.dom import minidom
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3

def get_mp3_metadata(mp3_path):
    try:
        audio = EasyID3(mp3_path)
        title = audio.get('title', ['Unknown Title'])[0]
        author = audio.get('artist', ['Unknown Artist'])[0]
    except ID3NoHeaderError:
        title = 'Unknown Title'
        author = 'Unknown Artist'
    except Exception as e:
        print(f"Error reading metadata for {mp3_path}: {e}")
        title = 'Unknown Title'
        author = 'Unknown Artist'
    return title, author

def get_mp3_length(mp3_path):
    try:
        audio = MP3(mp3_path)
        length_seconds = audio.info.length
        return length_seconds  # Return as float for conversion
    except Exception as e:
        print(f"Error reading length for {mp3_path}: {e}")
        return 0.0

def format_seconds_to_mmss(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def get_existing_radio_info(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        name = root.get('name', 'Unknown Radio Name')
        description = root.get('description', 'No Description')
        return name, description
    except Exception as e:
        print(f"Error reading existing XML file: {e}")
        return None, None

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
                mp3_path = os.path.join(folder_path, mp3_file)
                encoded_file_name = quote(mp3_file)
                title, author = get_mp3_metadata(mp3_path)
                length_seconds = get_mp3_length(mp3_path)
                length_mmss = format_seconds_to_mmss(length_seconds)

                song = ET.SubElement(album, "Song", index=str(index), length=length_mmss)
                song.text = encoded_file_name
                ET.SubElement(song, "Title").text = title
                ET.SubElement(song, "Author").text = author

    xml_str = ET.tostring(radio, encoding='utf-8', method='xml')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")

    xml_filename = os.path.join(base_directory, "Tracks.xml")
    with open(xml_filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)
    
    print(f"XML file created: {xml_filename}")

if __name__ == "__main__":
    # Check if Tracks.xml exists
    xml_path = os.path.join(os.getcwd(), "Tracks.xml")
    if os.path.exists(xml_path):
        # Prompt user to use existing radio title and description
        existing_name, existing_description = get_existing_radio_info(xml_path)
        if existing_name and existing_description:
            use_existing = input(f"Do you want to use the details from the radio '{existing_name}'? (y/n): ").strip().lower()
            if use_existing == 'y':
                radio_name = existing_name
                radio_description = existing_description
            else:
                radio_name = input("Enter a name for your radio: ")
                radio_description = input("Enter a description for your radio: ")
        else:
            print("Error retrieving existing radio information. Please enter new details.")
            radio_name = input("Enter a name for your radio: ")
            radio_description = input("Enter a description for your radio: ")
    else:
        radio_name = input("Enter a name for your radio: ")
        radio_description = input("Enter a description for your radio: ")

    # Create the XML with the provided inputs
    create_xml_from_mp3s(os.getcwd(), radio_name, radio_description)
