# kp_parser.py
import json

# Helper functions
def get_house_significance(house_num):
    significations = {
        1: "Self, Personality, Physique",
        2: "Wealth, Family, Speech",
        3: "Courage, Siblings, Short Travel",
        4: "Home, Mother, Comforts",
        5: "Children, Intelligence, Past Karma",
        6: "Health, Debts, Enemies",
        7: "Marriage, Partnerships, Business",
        8: "Longevity, Occult, Sudden Gains",
        9: "Fortune, Father, Long Travel",
        10: "Career, Status, Authority",
        11: "Gains, Friends, Aspirations",
        12: "Losses, Isolation, Moksha"
    }
    return significations.get(house_num, "General Life Area")

def get_star_lord(nakshatra_no):
    star_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", 
                "Jupiter", "Saturn", "Mercury"] * 3
    return star_lords[nakshatra_no-1]

def get_star_lord_significance(planet):
    significations = {
        "Sun": "Soul, Vitality, Authority",
        "Moon": "Mind, Emotions, Public",
        "Mars": "Courage, Energy, Conflicts",
        "Mercury": "Intellect, Communication, Trade",
        "Jupiter": "Wisdom, Expansion, Fortune",
        "Venus": "Relationships, Luxury, Arts",
        "Saturn": "Discipline, Challenges, Longevity",
        "Rahu": "Unconventional, Obsessions, Modern Tech",
        "Ketu": "Spirituality, Detachment, Past Karma"
    }
    return significations.get(planet, "General Influence")

def calculate_planet_strength(planet, house):
    strengths = []
    if planet['retro']:
        strengths.append("Retrograde - Modified Influence")
    if house['start_nakshatra_lord'] == planet['full_name']:
        strengths.append("In Own Constellation - Strong")
    return " | ".join(strengths) if strengths else "Neutral Position"

def get_sub_lord_house(planet, houses):
    for h in houses:
        if any(p['name'] == planet for p in h['planets']):
            return f"House {h['house']}"
    return "Not found in chart"

def get_aspects(house_num, houses):
    aspect_map = {
        1: [1, 5, 9],
        2: [2, 6, 10],
        3: [3, 7, 11],
        4: [4, 8, 12],
        5: [5, 9, 1],
        6: [6, 10, 2],
        7: [7, 11, 3],
        8: [8, 12, 4],
        9: [9, 1, 5],
        10: [10, 2, 6],
        11: [11, 3, 7],
        12: [12, 4, 8]
    }
    return f"Aspects houses: {aspect_map.get(house_num, [])}"

def get_key_significators(houses):
    significators = set()
    for house in houses:
        significators.add(house['cusp_sub_lord'])
        significators.add(house['cusp_sub_sub_lord'])
        for planet in house['planets']:
            significators.add(planet['full_name'])
    return ", ".join(significators)

def get_planetary_configurations(houses):
    aspects = []
    for house in houses:
        if len(house['planets']) > 1:
            planets = [p['name'] for p in house['planets']]
            aspects.append(f"Conjunction in House {house['house']}: {', '.join(planets)}")
    return "\n".join(aspects) if aspects else "No major conjunctions"

# Main parser
def parse_kp_houses(json_data):
    """Parse KP houses JSON into readable text with KP astrology terminology"""
    output = []
    
    houses = json_data.get('response', [])
    
    for house in houses:
        house_info = [
            f"=== Bhava {house['house']} ({get_house_significance(house['house'])}) ===",
            f"Rasi Transition : {house['start_rasi']} ({house['start_nakshatra_lord']}) → {house['end_rasi']} ({house['end_nakshatra_lord']})",
            f"Cusp Details:",
            f"  - Sublord (Vargas)    : {house['cusp_sub_lord']} in {get_sub_lord_house(house['cusp_sub_lord'], houses)}",
            f"  - Sub-Sublord (Sub-Sub): {house['cusp_sub_sub_lord']}",
            f"Positional Data:",
            f"  - Bhavmadhya (Cusp Midpoint) : {house['bhavmadhya']:.2f}°",
            f"  - Span: {house['length']:.2f}° ({house['local_start_degree']:.2f}° to {house['local_end_degree']:.2f}° local)",
            f"  - Galactic Longitude: {house['global_start_degree']:.2f}° to {house['global_end_degree']:.2f}°"
        ]
        
        planets = house['planets']
        if planets:
            house_info.append("Planetary Influences:")
            for planet in planets:
                retro_status = "Rx" if planet['retro'] else "Direct"
                planet_info = [
                    f"  ✦ {planet['full_name']} ({planet['name']}) [{retro_status}]",
                    f"    Nakshatra: {planet['nakshatra']} (Padam {planet['nakshatra_pada']})",
                    f"    Starlord : {get_star_lord(planet['nakshatra_no'])} → {get_star_lord_significance(get_star_lord(planet['nakshatra_no']))}",
                    f"    Position : {calculate_planet_strength(planet, house)}"
                ]
                house_info.extend(planet_info)
        else:
            house_info.append("No planets in this celestial sector")
        
        house_info.extend([
            f"Significator Chain:",
            f"  {house['cusp_sub_lord']} → {house['cusp_sub_sub_lord']} → ...",
            f"Aspect Analysis: {get_aspects(house['house'], houses)}"
        ])
        
        output.append("\n".join(house_info))
    
    output.insert(0, "=== KP Astrological Chart Analysis ===")
    output.append("\n=== KP Chart Summary ===")
    output.append(f"Total Cuspal Points: {len(houses)}")
    output.append(f"Key Significators: {get_key_significators(houses)}")
    output.append(f"Planetary Configurations:\n{get_planetary_configurations(houses)}")
    
    return "\n\n".join(output)

# Public interface function
def get_kp_details(input_source, output_file=None):
    """
    Process KP astrology data from file path or Python dict
    :param input_source: str (file path) or dict (JSON data)
    :param output_file: Optional output file path
    :return: Analysis text
    """
    try:
        # Load data
        if isinstance(input_source, str):
            with open(input_source, 'r') as f:
                data = json.load(f)
        else:
            data = input_source

        # Validate data structure
        if data.get('status') != 200:
            raise ValueError("Invalid KP data: Status code not 200")
        if 'response' not in data:
            raise ValueError("Invalid KP data: Missing 'response' array")
        if len(data['response']) != 12:
            raise ValueError("Invalid KP data: Expected 12 houses")

        # Generate analysis
        analysis = parse_kp_houses(data)

        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analysis)

        return analysis

    except Exception as e:
        error_msg = f"KP Analysis Error: {str(e)}"
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        return error_msg