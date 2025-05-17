# kp_paryantardasha_parser.py
import json

def parse_kp_paryantardasha(json_input, output_file):
    """
    Parse KP Paryantardasha details from JSON input and save formatted output
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
        output = ["=== KP Paryantardasha Analysis ==="]

        # Get paryantardasha lists
        paryantardashas = response.get('paryantardasha', [])
        dates = response.get('paryantardasha_order', [])

        # Process each mahadasha
        for md_idx, (md_periods, md_dates) in enumerate(zip(paryantardashas, dates)):
            # Flatten nested structure
            try:
                periods = [p for sublist in md_periods for p in sublist]
                dates_flat = [d for sublist in md_dates for d in sublist]
            except Exception as e:
                print(f"Error flattening structure for Mahadasha {md_idx}: {str(e)}")
                continue

            if len(periods) != len(dates_flat):
                print(f"Skipping Mahadasha {md_idx} due to length mismatch")
                continue

            # Get mahadasha name from first entry
            mahadasha_name = periods[0].split('/')[0] if periods else f"Mahadasha-{md_idx+1}"
            output.append(f"\n✦ {mahadasha_name} Mahadasha:")

            # Add all paryantardashas with dates
            for period, date_str in zip(periods, dates_flat):
                output.append(f"  - {period}: {date_str}")

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

        return True

    except Exception as e:
        print(f"Error processing Paryantardasha data: {str(e)}")
        return False