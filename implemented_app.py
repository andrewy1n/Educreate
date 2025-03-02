from nicegui import ui

planet_data = [
    {"name": "Mercury", "size_relative_to_earth": "0.38", "surface_features": "Cratered", "atmospheric_composition": "Oxygen, Sodium, Hydrogen", "distance_from_sun": "57.9 million km", "habitability": "No"},
    {"name": "Venus", "size_relative_to_earth": "0.95", "surface_features": "Volcanic", "atmospheric_composition": "Carbon Dioxide, Nitrogen", "distance_from_sun": "108.2 million km", "habitability": "No"},
    {"name": "Earth", "size_relative_to_earth": "1", "surface_features": "Liquid Water, Landmasses", "atmospheric_composition": "Nitrogen, Oxygen", "distance_from_sun": "149.6 million km", "habitability": "Yes"},    
    {"name": "Mars", "size_relative_to_earth": "0.53", "surface_features": "Mountains, Valleys", "atmospheric_composition": "Carbon Dioxide, Nitrogen", "distance_from_sun": "227.9 million km", "habitability": "No"}, 
    {"name": "Jupiter", "size_relative_to_earth": "11.21", "surface_features": "Gas Giant", "atmospheric_composition": "Hydrogen, Helium", "distance_from_sun": "778.5 million km", "habitability": "No"},
    {"name": "Saturn", "size_relative_to_earth": "9.45", "surface_features": "Gas Giant with Rings", "atmospheric_composition": "Hydrogen, Helium", "distance_from_sun": "1.434 billion km", "habitability": "No"},     
    {"name": "Uranus", "size_relative_to_earth": "4.01", "surface_features": "Ice Giant", "atmospheric_composition": "Hydrogen, Helium, Methane", "distance_from_sun": "2.871 billion km", "habitability": "No"},       
    {"name": "Neptune", "size_relative_to_earth": "3.88", "surface_features": "Ice Giant", "atmospheric_composition": "Hydrogen, Helium, Methane", "distance_from_sun": "4.495 billion km", "habitability": "No"},      
]

quiz_questions = [
    {"question": "Which planet is known as the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Saturn"], "answer": "Mars"},
    {"question": "Which is the largest planet in our solar system?", "options": ["Earth", "Saturn", "Jupiter", "Neptune"], "answer": "Jupiter"},
    {"question": "Which planet is closest to the Sun?", "options": ["Mercury", "Venus", "Earth", "Mars"], "answer": "Mercury"},
]

notes = ""

def landing_page():
    ui.label("Welcome to the Solar System Planet Comparator").classes("text-h4")
    ui.markdown("Explore and compare different planets in our solar system. Learn about their characteristics, engage with interactive modules, take quizzes, and keep your notes all in one place.")
    ui.button("Start", on_click=show_comparison).classes("mt-4").props("color=primary size=large")

def show_comparison():
    ui.clear()
    with ui.header():
        ui.label("Solar System Planet Comparator").classes("text-2xl")
        with ui.menu():
            ui.menu_item("Learning Modules", on_click=show_learning_modules)
            ui.menu_item("Quizzes", on_click=show_quizzes)
            ui.menu_item("Notes", on_click=show_notes)
            ui.menu_item("Settings", on_click=show_settings)
    with ui.main().classes("p-4"):
        ui.label("Planet Comparison Chart").classes("text-xl")
        table = ui.table(columns=["Name", "Size Relative to Earth", "Surface Features", "Atmospheric Composition", "Distance from Sun", "Habitability"], rows=planet_data)
        table.on_edit(edit_cell)
        table.on_click_cell(show_planet_info)

def edit_cell(row, column, value):
    planet_data[row][column] = value

def show_planet_info(row, column):
    planet = planet_data[row]
    with ui.dialog().props("max-width=600"):
        with ui.card():
            ui.label(planet["name"]).classes("text-2xl")
            ui.markdown(f"**Size Relative to Earth:** {planet['size_relative_to_earth']}  \n**Surface Features:** {planet['surface_features']}  \n**Atmospheric Composition:** {planet['atmospheric_composition']}  \n**Distance from Sun:** {planet['distance_from_sun']}  \n**Habitability:** {planet['habitability']}")
            ui.button("Close", on_click=lambda: ui.close())

def show_learning_modules():
    ui.clear()
    with ui.header():
        ui.label("Learning Modules").classes("text-2xl")
        ui.menu_item("Back to Chart", on_click=back_to_chart)
    with ui.main().classes("p-4"):
        ui.label("Gravity").classes("text-xl")
        ui.markdown("Gravity is the force that attracts two bodies towards each other. It governs the motion of planets around the Sun.")
        ui.label("Interactive Example").classes("text-lg")
        ui.button("Animate Gravity", on_click=animate_gravity)

def animate_gravity():
    with ui.dialog().props("max-width=400"):
        with ui.card():
            ui.label("Gravity Animation").classes("text-xl")
            ui.markdown("*Animation would be here*")
            ui.button("Close", on_click=lambda: ui.close())

def back_to_chart():
    ui.clear()
    show_comparison()

def show_quizzes():
    ui.clear()
    with ui.header():
        ui.label("Quizzes").classes("text-2xl")
        ui.menu_item("Back to Chart", on_click=back_to_chart)
    with ui.main().classes("p-4"):
        for q in quiz_questions:
            with ui.card().classes("mb-4"):
                ui.label(q["question"]).classes("text-lg")
                selected = ui.radio(q["options"], label="", value="", on_change=lambda e, q=q: check_answer(q, e.value))

def check_answer(question, answer):
    feedback = ui.label("")
    if answer == question["answer"]:
        feedback.set_text("Correct!").style("color: green")
    else:
        feedback.set_text(f"Incorrect. The correct answer is {question['answer']}.").style("color: red")

def show_notes():
    ui.clear()
    with ui.header():
        ui.label("Notes").classes("text-2xl")
        ui.menu_item("Back to Chart", on_click=back_to_chart)
    with ui.main().classes("p-4"):
        ui.textarea("Your Notes", value=notes, on_change=lambda e: save_notes(e.value)).classes("w-full h-64")
        ui.button("Save", on_click=lambda: ui.notify("Notes saved")).classes("mt-2")

def save_notes(value):
    global notes
    notes = value

def show_settings():
    ui.clear()
    with ui.header():
        ui.label("Settings").classes("text-2xl")
        ui.menu_item("Back to Chart", on_click=back_to_chart)
    with ui.main().classes("p-4"):
        ui.label("Accessibility Features").classes("text-xl")
        ui.button("Increase Text Size", on_click=lambda: ui.run_js("document.body.style.fontSize='larger'")).classes("mr-2")
        ui.button("Decrease Text Size", on_click=lambda: ui.run_js("document.body.style.fontSize='smaller'")).classes("mr-2")
        ui.button("High Contrast Mode", on_click=lambda: ui.run_js("document.body.style.backgroundColor='black'; document.body.style.color='white'"))
        ui.button("Normal Mode", on_click=lambda: ui.run_js("document.body.style.backgroundColor='white'; document.body.style.color='black'")).classes("mt-2")
        ui.label("Printable Summary").classes("text-xl mt-4")
        ui.button("Print Chart and Notes", on_click=print_summary)

def print_summary():
    with ui.dialog().props("max-width=800"):
        with ui.card():
            ui.label("Printable Summary").classes("text-xl")
            ui.markdown("## Planet Comparison Chart")
            table_html = "<table border='1'><tr><th>Name</th><th>Size Relative to Earth</th><th>Surface Features</th><th>Atmospheric Composition</th><th>Distance from Sun</th><th>Habitability</th></tr>"
            for planet in planet_data:
                table_html += f"<tr><td>{planet['name']}</td><td>{planet['size_relative_to_earth']}</td><td>{planet['surface_features']}</td><td>{planet['atmospheric_composition']}</td><td>{planet['distance_from_sun']}</td><td>{planet['habitability']}</td></tr>"
            table_html += "</table>"
            ui.markdown(table_html)
            ui.markdown(f"## Notes\n{notes}")
            ui.button("Print", on_click=lambda: ui.run_js("window.print()"))
            ui.button("Close", on_click=lambda: ui.close())

ui.run()