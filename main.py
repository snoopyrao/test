from kp_house_parser import get_kp_details
from kp_planet_parser import get_kp_planets
from kp_planet_details_parser import parse_kp_planet_details
from kp_mahadasha_parser import parse_kp_mahadasha
from kp_antardasha_parser import parse_kp_antardasha
from kp_paryantardasha_parser import parse_kp_paryantardasha
from kp_yoga_parser import parse_kp_yogas
from kp_analyzer import analyze_kp_charts
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_kp_analysis():
    """Main function to execute KP analysis workflow"""
    result = {
        'status': 'success',
        'output_file': '',
        'message': '',
        'generated_files': []
    }

    try:
        # Use absolute paths for production
        base_dir = os.path.abspath(os.path.dirname(__file__))
        input_dir = os.path.join(base_dir, 'user_data')
        output_dir = os.path.join(base_dir, 'user_data')
        
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Define file paths with absolute paths
        file_paths = {
            'planet_position': ('input_kp_planet_position_details.json', 'output_kp_planet_position_analysis.txt'),
            'house': ('input_kp_house_details.json', 'output_kp_house_analysis.txt'),
            'planet': ('input_kp_planet_details.json', 'output_kp_planet_analysis.txt'),
            'mahadasha': ('input_kp_mahadasha_details.json', 'output_kp_mahadasha_details.txt'),
            'antardasha': ('input_kp_antardasha_details.json', 'output_kp_antardasha_details.txt'),
            'paryantardasha': ('input_kp_paryantardasha_details.json', 'output_kp_paryantardasha_details.txt'),
            'yoga': ('input_kp_list_of_yogas_details.json', 'output_kp_list_of_yogas_details.txt')
        }

        # Processing pipeline
        processors = [
            (parse_kp_planet_details, 'planet_position'),
            (get_kp_details, 'house'),
            (get_kp_planets, 'planet'),
            (parse_kp_mahadasha, 'mahadasha'),
            (parse_kp_antardasha, 'antardasha'),
            (parse_kp_paryantardasha, 'paryantardasha'),
            (parse_kp_yogas, 'yoga')
        ]

        for processor, key in processors:
            input_file = os.path.join(input_dir, file_paths[key][0])
            output_file = os.path.join(output_dir, file_paths[key][1])
            
            logger.info(f"Processing {key} with {input_file}")
            
            processor_result = processor(input_file, output_file)
            if isinstance(processor_result, str) and processor_result.startswith("KP Analysis Error"):
                raise Exception(processor_result)
            
            result['generated_files'].append(output_file)

        # Generate comprehensive analysis
        final_output = os.path.join(output_dir, 'output_kp_comprehensive_analysis.txt')
        analyze_kp_charts(
            mahadasha_file=os.path.join(output_dir, file_paths['mahadasha'][1]),
            antardasha_file=os.path.join(output_dir, file_paths['antardasha'][1]),
            paryantardasha_file=os.path.join(output_dir, file_paths['paryantardasha'][1]),
            planet_position_file=os.path.join(output_dir, file_paths['planet_position'][1]),
            planet_analysis_file=os.path.join(output_dir, file_paths['planet'][1]),
            house_analysis_file=os.path.join(output_dir, file_paths['house'][1]),
            yoga_details_file=os.path.join(output_dir, file_paths['yoga'][1]),
            output_file=final_output
        )
        
        result['output_file'] = final_output
        result['generated_files'].append(final_output)
        logger.info("Analysis completed successfully")

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        result['status'] = 'error'
        result['message'] = str(e)
        return result

if __name__ == '__main__':
    analysis_result = run_kp_analysis()
    if analysis_result['status'] == 'success':
        print("Analysis completed successfully!")
        print(f"Final output: {analysis_result['output_file']}")
    else:
        print(f"Analysis failed: {analysis_result['message']}")