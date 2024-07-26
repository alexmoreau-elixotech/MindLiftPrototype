from openai import OpenAI
import os
import re

class AI_connector:
    def __init__(self):
        self.client = OpenAI(
                    # This is the default and can be omitted
                    api_key=os.environ.get("OPENAI_API_KEY"),
                )

    def _extract_course_chapters(self, ai_response):
        chapter_pattern = re.compile(r'\* (Chapter \d+\s*)\n(.*?)\n(.*?)\n', re.DOTALL)
    
        chapters = {}
        
        for match in chapter_pattern.finditer(ai_response):
            chapter_number = match.group(1).strip()
            title = match.group(2).strip()
            description = match.group(3).strip().replace('\n', ' ')
            
            chapters[chapter_number] = {
                "title": title,
                "description": description
            }
        
        return chapters
    
    def _extract_chapter_sections(self, ai_response):
        section_pattern = re.compile(r'\* (Section \d+\s*)\n(.*?)\n(.*?)\n', re.DOTALL)
    
        sections = {}
        
        for match in section_pattern.finditer(ai_response):
            section_number = match.group(1).strip()
            title = match.group(2).strip()
            description = match.group(3).strip().replace('\n', ' ')
            
            sections[section_number] = {
                "title": title,
                "description": description
            }
        
        return sections
    
    def _extract_section_subsections(self, ai_response):
        # Regular expression pattern to match LaTeX parts in square brackets
        pattern = re.compile(r'\\\[([^\]]+)\\\]')
        
        # Find all matches and store their positions
        matches = list(pattern.finditer(ai_response))
        
        # Initialize the result list
        parsed_text = []
        
        # Initialize the start position
        last_pos = 0
        
        # Iterate over all matches
        for match in matches:
            start, end = match.span()
            
            # Add the non-LaTeX part preceding this match
            if last_pos < start:
                parsed_text.append({"type": "text", "content": ai_response[last_pos:start]})
            
            # Add the LaTeX part
            parsed_text.append({"type": "latex", "content": match.group(1)})
            
            # Update the last position
            last_pos = end
        
        # Add the remaining non-LaTeX part after the last match
        if last_pos < len(ai_response):
            parsed_text.append({"type": "text", "content": ai_response[last_pos:]})
        
        return parsed_text
        
    def generate_course_chapters(self, subject):
        chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an online teacher.  
                                      You need to build complete courses plans that would allow anyone to learn anything, 
                                      including all prior knowledge needed.  For example, a chapter or two on classical physics is needed for quantum physics.  
                                      Assume every student only knows how to read and do basic arithmetics.  
                                      The course needs to be easy to understand for everyone, but attain undergraduate level.
                                      Only give the chapter titles and description.  No course title, no course description.
                                      ### Output example ###
                                      * Chapter 1
                                      Title
                                      Small description of chapter 1
                                      * Chapter 2
                                      Title
                                      Small description of chapter 2
                                      ...
                                      """,
                    },
                    {
                        "role": "user",
                        "content": f"{subject}"
                    }
                ],
                model="gpt-4o-mini",
        )
        
        return self._extract_course_chapters(chat_completion.choices[0].message.content)
    
    def generate_sections(self, chapters):
        chapter_sections = {}
        for keys in chapters:
            sections = self._generate_chapter_sections(chapters[keys]["title"], chapters[keys]["description"])
            chapter_sections[keys] = sections

        return chapter_sections
            
    def generate_subsections(self, section):
        subsections = self._generate_section_subsections(section["title"], section["description"])

        return subsections

    def _generate_chapter_sections(self, chapter_title, chapter_description):
        chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an online teacher.  You need to build a learning chapter plan based on its title and description.  
                                      Assume every student only knows how to read and do basic arithmetics.  
                                      The material needs to be easy to understand for everyone, but attain undergraduate level.  
                                      Only give the section titles and description.  No course title, no course description.
                                      ### Output example ###
                                      * Section 1
                                      Section title
                                      Small description of section 1
                                      * section 2
                                      Section title
                                      Small description of section 2
                                      ...
                                      """,
                    },
                    {
                        "role": "user",
                        "content": f"{chapter_title}:{chapter_description}"
                    }
                ],
                model="gpt-4o-mini",
        )
        
        return self._extract_chapter_sections(chat_completion.choices[0].message.content)
    
    def _generate_section_subsections(self, section_title, section_description):
        chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an online teacher.  
                                      You need to build the subsection learning content based on its title and description.  
                                      Assume every student only knows how to read and do basic arithmetics.  
                                      The material needs to be easy to understand for everyone, but attain undergraduate level.  
                                      Go in-depth and use examples.  Any line of LaTeX needs to be written in [] for easy parsing.  
                                      Only build the content.  We will deal with exercices later.  
                                      """,
                    },
                    {
                        "role": "user",
                        "content": f"{section_title},{section_description}"
                    }
                ],
                model="gpt-4o-mini",
        )
        
        return self._extract_section_subsections(chat_completion.choices[0].message.content)