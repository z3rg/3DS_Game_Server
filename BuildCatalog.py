import os
import sys
from struct import unpack
import xml.etree.ElementTree as ET
import shutil
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import socket
import webbrowser

releasesXML = '3dsreleases.xml'  # Name of XML downloaded from http://www.3dsdb.com/
ciaFolder = 'Complete US 3DS ROM Set (CIA)'  # Root folder with CIAs

def buildReleaseLookup(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    return root

def getTitleID(input_file):
    with open(input_file, 'rb') as cia_file:
        cia_header = cia_file.read(0x20)

        # Find offset for tmd
        cert_offset = 0x2040
        cert_size = unpack('<I', cia_header[0x08:0x0C])[0]
        tik_size = unpack('<I', cia_header[0x0C:0x10])[0]
        tmd_size = unpack('<I', cia_header[0x10:0x14])[0]
        tmd_offset = cert_offset + cert_size + 0x30 + tik_size

        # Read titleid from tmd
        cia_file.seek(tmd_offset + 0x18C)
        titleid = format(unpack('>Q', cia_file.read(0x8))[0], '016x')
        return titleid

def addListing(release):
    global strTable
    name = release.find('name').text
    print(f'Found game "{name}"...')
    id_parts = release.find('serial').text.split('-')
    id = id_parts[-1]  # Get the last part of the serial
    
    coverURL = f'https://art.gametdb.com/3ds/box/US/{id}.png'
    dbURL = f'https://www.gametdb.com/3DS/{id}'
    strTable += f'''
    <tr>
        <td><a href="{dbURL}">{name}</a></td>
        <td><img src="{coverURL}"></td>
        <td><a href="{relpath}"><div id="qrcode{id}"></div>
            <script type="text/javascript">
            var loc = window.location.href;
            var dir = loc.substring(0, loc.lastIndexOf('/'));
            //console.log(document.getElementById("qrcode{id}"));
            //console.log("encodeURI:"+encodeURI(dir + "/{relpath.replace(os.sep, '/')}"))
            new QRCode(document.getElementById("qrcode{id}"),{{width : 125,height : 125,text: encodeURI(dir + "/{relpath.replace(os.sep, '/')}") }});
            </script></a></td>
    </tr>'''
    print('Done.')

releases = buildReleaseLookup(releasesXML)

strTable = '''<html>
    <script type="text/javascript" src="jquery.min.js"></script>
    <script type="text/javascript" src="qrcode.js"></script>
    <script src="sorttable.js"></script>
        <table class="sortable" border="1">
            <tr>
                <th>Title</th>
                <th>Cover</th>
                <th>Download</th>
            </tr>'''

# Process every CIA in ciaFolder and subfolders
for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), ciaFolder)):
    for file in files:
        if file.endswith('.cia'):
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, os.path.dirname(__file__))
            titleid = getTitleID(filepath)
            print(f'Processing "{file}"...')
            print(f'Title ID: {titleid}')
            for release in releases:
                if release.find('titleid').text.lower() == titleid.lower():
                    addListing(release)
                    break

strTable += "</table></html>"

htmlFile = 'index.html'
with open(htmlFile, 'w') as hs:
    hs.write(strTable)
