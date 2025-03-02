from nicegui import ui

planets = {
    'Mercury': {
        'size': '0.38 Earths', 'surface': 'Rocky, cratered', 'atmosphere': 'Thin exosphere',
        'distance': '0.4 AU', 'life': 'No', 'facts': 'Smallest planet, extreme temperature swings',
        'image': '🪐'
    },
    'Venus': {
        'size': '0.95 Earths', 'surface': 'Volcanic, thick clouds', 'atmosphere': 'CO₂-rich',
        'distance': '0.7 AU', 'life': 'No', 'facts': 'Hottest planet, retrograde rotation',
        'image': '🌌'
    },
    'Earth': {
        'size': '1 Earth', 'surface': 'Oceans, continents', 'atmosphere': 'Nitrogen-oxygen',
        'distance': '1 AU', 'life': 'Yes', 'facts': 'Only known life-bearing planet',
        'image': '🌍'
    },
    'Mars': {
        'size': '0.53 Earths', 'surface': 'Red soil, canyons', 'atmosphere': 'Thin CO₂',
        'distance': '1.5 AU', 'life': 'Potential', 'facts': 'Largest volcano in solar system',
        'image': '🔴'
    }
}

characteristics = [
    ('Size', 'size', 'Diameter relative to Earth'),
    ('Surface', 'surface', 'Primary surface composition and features'),
    ('Atmosphere', 'atmosphere', 'Main atmospheric components'),
    ('Distance', 'distance', 'Average distance from Sun in Astronomical Units (AU)'),
    ('Life Potential', 'life', 'Current scientific consensus on life support'),
    ('Notable Facts', 'facts', 'Unique or distinguishing characteristics')
]

with ui.column().classes('w-full p-4 gap-4'):
    ui.label('Comparing Planets in the Solar System').classes('text-2xl font-bold')
    ui.label('Select planets to compare their characteristics').classes('text-lg')
    
    selected_planet = ui.select(options=list(planets.keys()), label='Choose Planet').classes('w-64')
    
    with ui.grid().classes('grid-cols-1 md:grid-cols-2 gap-4 w-full'):
        chart_container = ui.column().classes('col-span-2 gap-2')
        
        def update_planet():
            chart_container.clear()
            if selected_planet.value:
                planet = planets[selected_planet.value]
                with chart_container:
                    with ui.row().classes('items-center gap-2'):
                        ui.label(planet['image']).classes('text-2xl')
                        ui.label(selected_planet.value).classes('text-xl font-bold')
                    
                    for title, key, desc in characteristics:
                        with ui.row().classes('p-2 bg-blue-50 rounded justify-between'):
                            with ui.tooltip(text=desc):
                                ui.label(title).classes('font-medium')
                            ui.label(planet[key]).classes('text-right')
        
        selected_planet.on('change', update_planet)
        
    with ui.expansion('Key Terms', icon='info').classes('w-full'):
        ui.markdown('''
            - **Relative Distance**: Measured in Astronomical Units (1 AU = Earth-Sun distance)
            - **Atmospheric Features**: Primary gases and atmospheric pressure
            - **Life Support**: Current scientific understanding of habitability
        ''')

ui.run()