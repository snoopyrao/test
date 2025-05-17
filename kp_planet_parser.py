# kp_planet_parser.py
import json

def parse_kp_planets(json_data):
    """Parse KP planet data into human-readable format for LLMs"""
    try:
        if json_data.get('status') != 200:
            return "Error: Invalid response status"
            
        planets = json_data.get('response', {})
        output = ["=== KP Planetary Positions Analysis ==="]
        
        # Parse planets (exclude midheaven/ascendant)
        for pid, pdata in [(k,v) for k,v in planets.items() if k not in ('midheaven', 'ascendant')]:
            planet_info = [
                f"\n✦ {pdata['name']} ({pdata['zodiac']})",
                f"  - House Position: {pdata['house']}",
                f"  - Retrograde: {'Yes' if pdata['retro'] else 'No'}",
                f"  - Degrees: {pdata['global_degree']:.2f}° (Global) / {pdata['local_degree']:.2f}° (Local)",
                f"  - Nakshatra: {pdata['pseudo_nakshatra']} (Pada {pdata['pseudo_nakshatra_pada']})",
                f"  - Nakshatra Lord: {pdata['pseudo_nakshatra_lord']}",
                f"  - Sublord Chain: {pdata['sub_lord']} → {pdata['sub_sub_lord']}",
                f"  - Sign Lord: {pdata['pseudo_rasi_lord']}",
                f"  - Pseudo Sign: {pdata['pseudo_rasi']} (Based on Nakshatra)"
            ]
            output.extend(planet_info)
        
        # Add special points
        output.extend([
            "\n=== Special Points ===",
            f"Midheaven (MC): {planets.get('midheaven', 0):.2f}°",
            f"Ascendant (ASC): {planets.get('ascendant', 0):.2f}°"
        ])
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Planet Parsing Error: {str(e)}"

def get_kp_planets(input_source, output_file="output_kp_planet_analysis.txt"):
    """
    Get KP planet analysis and save to file
    :param input_source: str (file path) or dict (JSON data)
    :param output_file: Output file path (default: output_kp_planet_analysis.txt)
    :return: Status message
    """
    try:
        # Load data
        if isinstance(input_source, str):
            with open(input_source, 'r') as f:
                data = json.load(f)
        else:
            data = input_source
        
        # Generate analysis
        analysis = parse_kp_planets(data)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(analysis)
        
        return f"Analysis saved to {output_file}"
    
    except FileNotFoundError:
        return "Error: Input file not found"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format"
    except PermissionError:
        return f"Error: Cannot write to {output_file} (check permissions)"
    except Exception as e:
        return f"Error processing data: {str(e)}"