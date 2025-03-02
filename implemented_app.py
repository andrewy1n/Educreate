from nicegui import ui
from dataclasses import dataclass
from typing import Dict

@dataclass
class Planet:
    name: str
    size: str
    surface: str
    atmosphere: str
    distance: str
    life_support: str
    facts: str
    emoji: str

planets = {
    'Earth': Planet('Earth', '1x', '70% Water', 'Nitrogen-Oxygen', '1 AU', 'Yes', 'Only known life-bearing planet', '🌍'),
    'Mars': Planet('Mars', '0.107x', 'Rocky', 'Carbon Dioxide', '1.5 AU', 'Potential', 'Largest dust storms', '🪐'),
    'Venus': Planet('Venus', '0.857x', 'Volcanic', 'Carbon Dioxide', '0.7 AU', 'No', 'Hottest planet', '⭐'),
    'Mercury': Planet('Mercury', '0.383x', 'Rocky', 'Thin Exosphere', '0.39 AU', 'No', 'Closest to the Sun', '☿'),
    'Jupiter': Planet('Jupiter', '11.209x', 'Gas Giant', 'Hydrogen-Helium', '5.2 AU', 'No', 'Largest planet', '♃'),
    'Saturn': Planet('Saturn', '9.449x', 'Gas Giant', 'Hydrogen-Helium', '9.58 AU', 'No', 'Has prominent rings', '♄'),
    'Uranus': Planet('Uranus', '4.007x', 'Ice Giant', 'Hydrogen-Helium-Methane', '19.22 AU', 'No', 'Rotates on its side', '♅'),
    'Neptune': Planet('Neptune', '3.883x', 'Ice Giant', 'Hydrogen-Helium-Methane', '30.05 AU', 'No', 'Farthest planet from the Sun', '♆'),
    'Pluto': Planet('Pluto', '0.186x', 'Rocky-Ice', 'Nitrogen-Methane', '39.48 AU', 'No', 'Dwarf planet', '♇'),
}

selected_planets: Dict[str, Planet] = {}

def update_chart(planet_name: str):
    if planet_name in selected_planets:
        del selected_planets[planet_name]
    else:
        selected_planets[planet_name] = planets[planet_name]
    comparison_grid.clear()
    build_comparison_chart()

def build_comparison_chart():
    if not selected_planets:
        with comparison_grid:
            ui.label('Select planets to compare').classes('text-lg')
        return

    with comparison_grid:
        with ui.grid(columns=len(selected_planets)+1).classes('w-full gap-4'):
            ui.label('Characteristic').classes('font-bold')
            for planet in selected_planets.values():
                ui.label(planet.emoji + ' ' + planet.name).classes('text-xl')

        characteristics = [
            ('Size (vs Earth)', 'size'),
            ('Surface', 'surface'),
            ('Atmosphere', 'atmosphere'),
            ('Distance from Sun', 'distance'),
            ('Life Support', 'life_support'),
            ('Notable Facts', 'facts'),
        ]

        for label, key in characteristics:
            with ui.row().classes('w-full hover:bg-gray-100 p-2 rounded gap-4'):
                ui.label(label).classes('w-48 font-medium').tooltip(f'Definition of {label}')
                for planet in selected_planets.values():
                    ui.label(getattr(planet, key)).classes('flex-1')

        with ui.row().classes('mt-4'):
            ui.button('Learn More', on_click=show_educational_notes).classes('bg-blue-100 hover:bg-blue-200')

def show_educational_notes():
    notes = {
        'Size (vs Earth)': 'Relative diameter compared to Earth',
        'Atmosphere': 'Primary atmospheric composition',
        'Distance from Sun': 'Measured in Astronomical Units (AU)',
    }
    with ui.dialog() as dialog, ui.card():
        ui.label('Educational Notes').classes('text-xl mb-4')
        for term, definition in notes.items():
            ui.markdown(f'**{term}**: {definition}')
        ui.button('Close', on_click=dialog.close)
    dialog.open()

with ui.column().classes('w-full max-w-4xl mx-auto p-8'):
    ui.label('Comparing Planets in the Solar System').classes('text-3xl mb-4')
    ui.label('Select planets below to compare their characteristics').classes('text-lg mb-8')

    with ui.row().classes('w-full mb-8 gap-8'):
        select = ui.select(options=list(planets.keys()), label='Choose Planet', on_change=lambda e: update_chart(e.value)).classes('flex-1')

        with ui.column().classes('flex-1 gap-2'):
            for planet in planets:
                ui.button(planet, on_click=lambda _, p=planet: update_chart(p)).classes('w-full')

    comparison_grid = ui.column().classes('w-full')

ui.run()