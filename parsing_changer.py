from AI_connector import AI_connector
import json
import os
from utils import write_list_to_file

conn = AI_connector()

for root, dirs, files in os.walk("./courses/quantum physics/"):
    for file in files:
            if file == 'content.json':
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = json.load(f)
                    
                    total_message = ""
                    for item in content:        
                        if item["type"] == "text":
                             total_message += item["content"]
                        else:
                             total_message += f"\[{item['content']}\]"

                    items = conn._extract_section_subsections(total_message)

                    write_list_to_file(file_path, items)
