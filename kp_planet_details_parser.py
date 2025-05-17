# kp_planet_parser.py
import json

def parse_kp_planet_details(json_input, output_file):
    """
    Parse KP planet details from JSON (file path or dict) and save to output file
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

        planets = data.get('response', {})
        output = ["=== KP Planetary Details Analysis ==="]

        # Parse planets (entries 0-9)
        for pid in [str(i) for i in range(10)]:
            pdata = planets.get(pid, {})
            if not pdata:
                continue

            planet_info = [
                f"\n✦ {pdata['full_name']} ({pdata['name']})",
                f"  - Zodiac: {pdata['zodiac']} (House {pdata['house']})",
                f"  - Nakshatra: {pdata['nakshatra']} (Pada {pdata['nakshatra_pada']})",
                f"  - Lords: Nakshatra - {pdata['nakshatra_lord']}, Zodiac - {pdata['zodiac_lord']}",
                f"  - Degrees: Local {pdata['local_degree']:.2f}°, Global {pdata['global_degree']:.2f}°",
                f"  - Retrograde: {'Yes' if pdata.get('retro', False) else 'No'}",
                f"  - Combust: {'Yes' if pdata.get('is_combust', False) else 'No'}"
            ]
            output.extend(planet_info)

        # Add Dasa information
        output.extend([
            "\n=== Dasa Periods ===",
            f"Birth Dasa: {planets.get('birth_dasa', 'N/A')}",
            f"Current Dasa: {planets.get('current_dasa', 'N/A')}",
            f"Start Date: {planets.get('birth_dasa_time', 'N/A')}",
            f"Current Date: {planets.get('current_dasa_time', 'N/A')}"
        ])

        # Save to specified output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

        return True

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return False