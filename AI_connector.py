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
    
    def _extract_exercises_types_and_counts(self, ai_response):
        print(ai_response)
        # Split the text into lines
        lines = ai_response.strip().split('\n')

        # Initialize an empty dictionary
        result = {}

        # Iterate through each line
        for line in lines:
            # Split the line by the colon
            key, value = line.split(':')
            # Trim whitespace and convert value to an integer
            result[key.strip()] = int(value.strip())

        return result
    
    def _extract_math_exercise(self, ai_response):
        print(ai_response)
        # Extract variables section
        variables_section = re.search(r'=== Variables(.*?)=== Problem', ai_response, re.DOTALL).group(1).strip()

        # Extract values in the variables section
        variables = re.findall(r'(\w|θ)\d?\s*=\s*(\S+)', variables_section)
        variables_dict = {key: value for key, value in variables}

        # Extract problem section
        problem_section = re.search(r'=== Problem(.*?)=== Solution', ai_response, re.DOTALL).group(1).strip()

        # Extract solution section
        solution_section = re.search(r'=== Solution(.*)', ai_response, re.DOTALL).group(1).strip()

        # Extract values in the solution section
        solution = re.findall(r'(\w|θ)\d?\s*=\s*(\S+)', solution_section)
        solution_dict = {key: value for key, value in solution}

        # Combine dictionaries
        result = {"variables": variables_dict, "problem": problem_section, "solution": solution_dict}

        return result
    
    def generate_course_chapters(self, subject):
        chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an online teacher.  
                                      You need to build complete courses plans that would allow anyone to learn anything, 
                                      including all prior knowledge needed.  For example, a chapter or two on classical physics is needed for quantum physics.  
                                      Assume every student only knows how to read and do basic arithmetic.  
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
        subsections, unformatted_subsections = self._generate_section_subsections(section["title"], section["description"])

        return subsections, unformatted_subsections

    def get_exercises_types_and_couts(self, content):
        chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an online teacher.  You need to build exercises to let the students practice the material.  
                                      They can be one of four types:
                                      - Math problem
                                      - Coding problem
                                      - Words association
                                      - Single-choice questions

                                      Tell me what type of questions is appropriate for the content, 
                                      and tell me how many of each type should be created.

                                      ### Output example
                                      Math problem: 3
                                      Coding problem: 0
                                      Words association: 2
                                      Single-choice questions: 5
                                      """,
                    },
                    {
                        "role": "user",
                        "content": f"{content}"
                    }
                ],
                model="gpt-4o-mini",
        )
        
        return self._extract_exercises_types_and_counts(chat_completion.choices[0].message.content)
    
    def generate_math_exercises(self, content, count):
        problems = []

        for i in range(count):
            chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": """You are an online teacher.  
                                        You need to build exercises to let the students practice the material.  
                                        We will be building math exercises based on the content I will provide you.  
                                        You need to give me a very specific output.  
                                        I need the useful variables (only the name of the variable, its value and units) 
                                        for the problem identified so I can parse them automatically.  
                                        Then I need the written problem.  
                                        Then I need the solution (only the answer) to the problem. 
                                        ### Output example
                                        === Variables
                                        c = ...
                                        x = ...
                                        \theta = ...
                                        === Problem
                                        ...
                                        === Solution
                                        y = ...
                                        x = ...
                                        """,
                        },
                        {
                            "role": "user",
                            "content": f"{content}"
                        }
                    ],
                    model="gpt-4o-mini",
            )
            problems.append(self._extract_math_exercise(chat_completion.choices[0].message.content))

        return problems
    
    def _generate_chapter_sections(self, chapter_title, chapter_description):
        chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an online teacher.  You need to build a learning chapter plan based on its title and description.  
                                      Assume every student only knows how to read and do basic arithmetic.  
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
                                      Assume every student only knows how to read and do basic arithmetic.  
                                      The material needs to be easy to understand for everyone, but attain undergraduate level.  
                                      Go in-depth and use examples.  Any line of LaTeX needs to be written in [] for easy parsing.  
                                      Only build the content.  We will deal with exercises later.  
                                      Format the content with markdown, starting at header 1 (#).
                                      """,
                    },
                    {
                        "role": "user",
                        "content": f"{section_title},{section_description}"
                    }
                ],
                model="gpt-4o-mini",
        )
        
        return self._extract_section_subsections(chat_completion.choices[0].message.content), chat_completion.choices[0].message.content