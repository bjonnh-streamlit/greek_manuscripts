#!/usr/bin/env bash

# check if there are two arguments and the first one is an existing file
if [ "$#" -ne 2 ] || [ ! -f "$1" ]; then
  echo "Usage: $0 <input.docx> <output.docx>"
  exit 1
fi

temp_file=$(mktemp)
python3 cleaner.py "$1" "$temp_file"

temp_dir=$(mktemp -d)
unzip "$temp_file" -d "$temp_dir"
cat << EOF > "$temp_dir"/word/footnotes.xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:footnotes xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/
officeDocument/2006/relationships" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="http://schemas.openxml
formats.org/wordprocessingml/2006/main" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:wp="http:/
/schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:wps="http://schemas.microsoft.com/
office/word/2010/wordprocessingShape" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocess
ingGroup" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:wp14="http://schema
s.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:w14="http://schemas.microsoft.com/office/wor
d/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" mc:Ignorable="w14 wp14 w15
"></w:footnotes>
EOF
pushd "$PWD" || exit
cd "$temp_dir" || exit
zip -9 -r "$temp_file" -- *
popd || exit
cp "$temp_file" "$2"

rm -rf "$temp_dir" "$temp_file"
