from IdeaAgent import IdeaAgent
from CodeAgent import CodeAgent
import sys

# if len(sys.argv) != 2:
#     print("Please include pdf path argument")
#     sys.exit(1)

# pdf_path = sys.argv[1]
idea_agent = IdeaAgent()
code_agent = CodeAgent()

# spec_doc = idea_agent.generate_web_app_description(pdf_path)
# print(spec_doc)

spec_doc = """
### Key Functionalities
1. **Planet Comparison Chart**:
   - A table or grid that allows users to compare planets based on key characteristics:
     - Size relative to Earth
     - Surface features
     - Atmospheric features
     - Relative distance from the Sun
     - Ability to support life
     - Other notable facts

2. **Interactive Planet Selection**:
   - Users can select a planet from a dropdown menu or clickable list to display its details in the comparison chart.

3. **Dynamic Data Display**:
   - When a planet is selected, its specific characteristics are dynamically populated in the chart for easy comparison with other planets.

4. **Visual Aids**:
   - Simple visual representations (e.g., icons or images) for each planet to help users quickly identify and differentiate them.

5. **Educational Notes**:
   - A section that provides brief explanations or definitions of key terms (e.g., "relative distance," "atmospheric features") to aid understanding.

---

### User Interaction Flow
1. **Landing Page**:
   - The app opens to a clean, single-page layout with a title ("Comparing Planets in the Solar System") and a brief description of its purpose.

2. **Planet Selection**:
   - The user selects a planet from a dropdown menu or a list of planet names.

3. **Data Population**:
   - Upon selection, the planet's details are automatically filled into the comparison chart.

4. **Comparison**:
   - The user can select multiple planets one after another to compare their characteristics side by side.

5. **Learning Support**:
   - The user can click on a "Learn More" button or hover over terms to see definitions or additional notes about the characteristics being compared.

---

### Special Features Needed
1. **Responsive Design**:
   - The app should be usable on both desktop and mobile devices, with a layout that adjusts to different screen sizes.

2. **Dynamic Updates**:
   - The comparison chart should update in real-time as the user selects different planets, without requiring a page reload.

3. **Visual Feedback**:
   - Highlighting or color-coding rows in the chart to make it easier to compare specific characteristics across planets.

4. **Minimalist Aesthetic**:
   - A clean, uncluttered design with a focus on usability and readability, avoiding unnecessary distractions.

---
"""
ui_components = code_agent.generate_ui_description(spec_doc)
code = code_agent.generate_code(ui_components, spec_doc)
print(code)