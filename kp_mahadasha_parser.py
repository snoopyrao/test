# kp_mahadasha_parser.py
import json

def parse_kp_mahadasha(json_input, output_file):
    """
    Parse KP Mahadasha details from JSON input and save to output file
    :param json_input: str (file path) or dict (JSON data)
    :param output_file: str (output file path)
    :return: True if successful, False otherwise
    """
    try:
        # Load JSON data if input is a file path
        if isinstance(json_input, str):
            with open(json_input, 'r') as f:
                data = json.load(f)
        else:
            data = json_input

        if data.get('status') != 200:
            raise ValueError("Invalid response status")

        response = data.get('response', {})
        output = ["=== KP Mahadasha Analysis ==="]

        # Dasa period mapping
        planet_map = {
            "Me": "Mercury",
            "Ke": "Ketu",
            "Ve": "Venus",
            "Su": "Sun",
            "Mo": "Moon",
            "Ma": "Mars",
            "Ra": "Rahu",
            "Ju": "Jupiter",
            "Sa": "Saturn"
        }

        # Parse birth dasa
        birth_dasa = response.get('birth_dasa', '').split('>')
        birth_dasa_time = response.get('birth_dasa_time', 'N/A')
        output.extend([
            "\nBirth Dasa Period:",
            f"  - Mahadasha: {planet_map.get(birth_dasa[0], birth_dasa[0]) if len(birth_dasa) > 0 else 'N/A'}",
            f"  - Antardasha: {planet_map.get(birth_dasa[1], birth_dasa[1]) if len(birth_dasa) > 1 else 'N/A'}",
            f"  - Pratyantaradasha: {planet_map.get(birth_dasa[2], birth_dasa[2]) if len(birth_dasa) > 2 else 'N/A'}",
            f"  - Start Date: {birth_dasa_time.strip()}"
        ])

        # Parse current dasa
        current_dasa = response.get('current_dasa', '').split('>')
        current_dasa_time = response.get('current_dasa_time', 'N/A')
        output.extend([
            "\nCurrent Dasa Period:",
            f"  - Mahadasha: {planet_map.get(current_dasa[0], current_dasa[0]) if len(current_dasa) > 0 else 'N/A'}",
            f"  - Antardasha: {planet_map.get(current_dasa[1], current_dasa[1]) if len(current_dasa) > 1 else 'N/A'}",
            f"  - Pratyantaradasha: {planet_map.get(current_dasa[2], current_dasa[2]) if len(current_dasa) > 2 else 'N/A'}",
            f"  - Current Date: {current_dasa_time.strip()}"
        ])

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

        return True

    except Exception as e:
        print(f"Error processing Mahadasha data: {str(e)}")
        return False