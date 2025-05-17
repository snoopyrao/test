# kp_yoga_parser.py
import json

def parse_kp_yogas(json_input, output_file):
    """
    Parse KP Yoga details from JSON input and save formatted output
    :param json_input: str (file path) or dict (JSON data)
    :param output_file: str (output file path)
    :return: True if successful, False otherwise
    """
    try:
        # Load JSON data
        if isinstance(json_input, str):
            with open(json_input, 'r') as f:
                data = json.load(f)
        else:
            data = json_input

        if data.get('status') != 200:
            raise ValueError("Invalid response status")

        response = data.get('response', {})
        output = ["=== KP Yoga Analysis ==="]

        # Process each yoga
        for yoga in response.get('yogas_list', []):
            output.append(f"\n✦ {yoga['yoga']}")
            output.append(f"   Strength: {yoga['strength_in_percentage']:.2f}%")
            output.append(f"   Planets: {', '.join(yoga['planets_involved'])}")
            output.append(f"   Houses: {', '.join(map(str, yoga['houses_involved']))}")
            output.append(f"   Meaning: {yoga['meaning']}")

        # Add summary statistics
        output.append("\n=== Yoga Summary ===")
        output.append(f"Total Yogas: {response.get('yogas_count', 0)}")
        output.append(f"Raja Yogas: {response.get('raja_yoga_count', 0)}")
        output.append(f"Dhana Yogas: {response.get('dhana_yoga_count', 0)}")
        output.append(f"Daridra Yogas: {response.get('daridra_yoga_count', 0)}")

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

        return True

    except Exception as e:
        print(f"Error processing Yoga data: {str(e)}")
        return False