from kp_house_parser import get_kp_details
from kp_planet_parser import get_kp_planets
from kp_planet_details_parser import parse_kp_planet_details
from kp_mahadasha_parser import parse_kp_mahadasha
from kp_antardasha_parser import parse_kp_antardasha
from kp_paryantardasha_parser import parse_kp_paryantardasha
from kp_yoga_parser import parse_kp_yogas
from kp_analyzer import analyze_kp_charts

def run_kp_analysis():
    """Main function to execute KP analysis workflow"""
    result = {
        'status': 'success',
        'output_file': '',
        'message': '',
        'generated_files': []
    }

    try:
        # Define file paths
        input_dir = 'user_data/'
        output_dir = 'user_data/'
        
        # Step 1: Parse planet position details
        planet_position_input = f"{input_dir}input_kp_planet_position_details.json"
        planet_position_output = f"{output_dir}output_kp_planet_position_analysis.txt"
        parse_kp_planet_details(planet_position_input, planet_position_output)
        result['generated_files'].append(planet_position_output)

        # Step 2: Parse KP House details
        house_input = f"{input_dir}input_kp_house_details.json"
        house_output = f"{output_dir}output_kp_house_analysis.txt"
        house_analysis = get_kp_details(house_input, house_output)
        if house_analysis.startswith("KP Analysis Error"):
            raise Exception(house_analysis)
        result['generated_files'].append(house_output)

        # Step 3: Parse KP Planet details
        planet_input = f"{input_dir}input_kp_planet_details.json"
        planet_output = f"{output_dir}output_kp_planet_analysis.txt"
        get_kp_planets(planet_input, planet_output)
        result['generated_files'].append(planet_output)

        # Step 4: Mahadasha parser
        mahadasha_input = f"{input_dir}input_kp_mahadasha_details.json"
        mahadasha_output = f"{output_dir}output_kp_mahadasha_details.txt"
        parse_kp_mahadasha(mahadasha_input, mahadasha_output)
        result['generated_files'].append(mahadasha_output)

        # Step 5: Antardasha parser
        antardasha_input = f"{input_dir}input_kp_antardasha_details.json"
        antardasha_output = f"{output_dir}output_kp_antardasha_details.txt"
        parse_kp_antardasha(antardasha_input, antardasha_output)
        result['generated_files'].append(antardasha_output)

        # Step 6: Paryantardasha
        paryantardasha_input = f"{input_dir}input_kp_paryantardasha_details.json"
        paryantardasha_output = f"{output_dir}output_kp_paryantardasha_details.txt"
        parse_kp_paryantardasha(paryantardasha_input, paryantardasha_output)
        result['generated_files'].append(paryantardasha_output)

        # Step 7: List of Yogas
        yoga_input = f"{input_dir}input_kp_list_of_yogas_details.json"
        yoga_output = f"{output_dir}output_kp_list_of_yogas_details.txt"
        parse_kp_yogas(yoga_input, yoga_output)
        result['generated_files'].append(yoga_output)

        # Generate comprehensive analysis
        final_output = f"{output_dir}output_kp_comprehensive_analysis.txt"
        analyze_kp_charts(
            mahadasha_file=mahadasha_output,
            antardasha_file=antardasha_output,
            paryantardasha_file=paryantardasha_output,
            planet_position_file=planet_position_output,
            planet_analysis_file=planet_output,
            house_analysis_file=house_output,
            yoga_details_file=yoga_output,
            output_file=final_output
        )
        result['output_file'] = final_output
        result['generated_files'].append(final_output)

        return result

    except Exception as e:
        result['status'] = 'error'
        result['message'] = str(e)
        return result

# For standalone execution
if __name__ == '__main__':
    analysis_result = run_kp_analysis()
    if analysis_result['status'] == 'success':
        print("Analysis completed successfully!")
        print(f"Final output: {analysis_result['output_file']}")
    else:
        print(f"Analysis failed: {analysis_result['message']}")