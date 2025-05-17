# kp_antardasha_parser.py
import json

def parse_kp_antardasha(json_input, output_file):
    """
    Parse KP Antardasha details from JSON input and save formatted output
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
        output = ["=== KP Antardasha Analysis ==="]

        # Get antardasha lists
        antardashas = response.get('antardashas', [])
        dates = response.get('antardasha_order', [])

        # Process each mahadasha
        for i, (mahadasha_list, date_list) in enumerate(zip(antardashas, dates)):
            if len(mahadasha_list) != len(date_list):
                continue  # Skip mismatched entries

            # Get mahadasha name from first entry
            mahadasha = mahadasha_list[0].split('/')[0]
            output.append(f"\n✦ {mahadasha} Mahadasha:")

            # Add antardashas with dates
            for antardasha, date_str in zip(mahadasha_list, date_list):
                planet1, planet2 = antardasha.split('/')
                output.append(f"  - {planet2} Antardasha: {date_str}")

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

        return True

    except Exception as e:
        print(f"Error processing Antardasha data: {str(e)}")
        return False