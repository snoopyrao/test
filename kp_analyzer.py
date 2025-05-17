import re
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KPAnalysis')

class KPAstrologyCleaner:
    def __init__(self):
        self.logger = logging.getLogger('KPCleaner')
        self.parsed_data = {
            'dasha': {
                'mahadasha': {},
                'antardasha': {},
                'paryantardasha': {}
            },
            'planets': {},
            'houses': {},
            'yogas': [],
            'current_periods': {}
        }

    def clean_data(self, files_content):
        try:
            for file_type, content in files_content.items():
                if not content:
                    raise ValueError(f"Empty content for {file_type}")
                    
                self.logger.info(f"Processing {file_type} data")
                
                if file_type == 'mahadasha':
                    self._parse_mahadasha(content)
                elif file_type == 'antardasha':
                    self._parse_antardasha(content)
                elif file_type == 'paryantardasha':
                    self._parse_paryantardasha(content)
                elif file_type in ['planet_position', 'planet_analysis']:
                    self._parse_planets(content)
                elif file_type == 'house_analysis':
                    self._parse_houses(content)
                elif file_type == 'yoga_details':
                    self._parse_yogas(content)
                    
            return self._consolidate_data()
            
        except Exception as e:
            self.logger.error(f"Cleaning failed: {str(e)}")
            raise

    def _parse_mahadasha(self, content):
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if 'Birth Dasa Period:' in line:
                current_section = 'birth'
                self.parsed_data['dasha']['mahadasha'][current_section] = {}
            elif 'Current Dasa Period:' in line:
                current_section = 'current'
                self.parsed_data['dasha']['mahadasha'][current_section] = {}
            elif current_section and ':' in line:
                key, val = [p.strip() for p in line.split(':', 1)]
                self.parsed_data['dasha']['mahadasha'][current_section][key.lower()] = val

    def _parse_antardasha(self, content):
        current_mahadasha = None
        for line in content.split('\n'):
            line = line.strip()
            if '✦' in line:
                match = re.search(r"✦ (\w+) Mahadasha", line)
                if match:
                    current_mahadasha = match.group(1)
                    self.parsed_data['dasha']['antardasha'][current_mahadasha] = []
            elif current_mahadasha and '-' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    period, date = parts
                    self.parsed_data['dasha']['antardasha'][current_mahadasha].append({
                        'period': period.strip(),
                        'date': date.strip()
                    })

    def _parse_paryantardasha(self, content):
        current_key = None
        for line in content.split('\n'):
            line = line.strip()
            if '✦' in line:
                parts = line.split('>')
                if len(parts) >= 2:
                    current_key = '>'.join([p.strip() for p in parts[0].split('✦')[-1].split('>')])
                    self.parsed_data['dasha']['paryantardasha'][current_key] = []
            elif current_key and '-' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    period, date = parts
                    self.parsed_data['dasha']['paryantardasha'][current_key].append({
                        'period': period.strip(),
                        'date': date.strip()
                    })

    def _parse_planets(self, content):
        current_planet = None
        for line in content.split('\n'):
            line = line.strip()
            if '✦' in line:
                match = re.search(r"✦ (\w+)", line)
                if match:
                    current_planet = match.group(1)
                    self.parsed_data['planets'][current_planet] = {}
            elif current_planet and ':' in line:
                key, val = [p.strip() for p in line.split(':', 1)]
                key = key.replace('(', '').replace(')', '').strip().lower()
                
                if 'house' in key:
                    self.parsed_data['planets'][current_planet]['house'] = val.split()[0]
                elif 'nakshatra' in key:
                    self.parsed_data['planets'][current_planet]['nakshatra'] = val.split('(')[0].strip()
                elif 'lord' in key:
                    self.parsed_data['planets'][current_planet]['lord'] = val.split('-')[-1].strip()
                elif 'retrograde' in key:
                    self.parsed_data['planets'][current_planet]['retrograde'] = val.strip()
                elif 'combust' in key:
                    self.parsed_data['planets'][current_planet]['combust'] = val.strip()
                elif 'sublord' in key:
                    self.parsed_data['planets'][current_planet]['sublord'] = val.strip()

    def _parse_houses(self, content):
        current_house = None
        for line in content.split('\n'):
            line = line.strip()
            if 'Bhava ' in line:
                match = re.search(r"Bhava (\d+)", line)
                if match:
                    current_house = match.group(1)
                    self.parsed_data['houses'][current_house] = []
            elif current_house and '✦' in line:
                match = re.search(r"✦ (\w+)", line)
                if match:
                    planet = match.group(1)
                    self.parsed_data['houses'][current_house].append(planet)

    def _parse_yogas(self, content):
        current_yoga = {}
        for line in content.split('\n'):
            line = line.strip()
            try:
                if '✦' in line:
                    # Handle previous yoga
                    if current_yoga.get('name'):
                        self.parsed_data['yogas'].append(current_yoga)
                        
                    # Match more flexible yoga patterns
                    yoga_match = re.search(
                        r"✦\s*([\w\s]+? Yoga(s?))\b", 
                        line,
                        re.IGNORECASE
                    )
                    if yoga_match:
                        current_yoga = {
                            'name': yoga_match.group(1).strip(),
                            'planets': [],
                            'strength': None
                        }
                    else:
                        current_yoga = {}
                        self.logger.warning(f"Skipping unparseable yoga line: {line}")
                        
                elif line.startswith('Strength:'):
                    if current_yoga:
                        current_yoga['strength'] = line.split(':')[-1].strip()
                        
                elif line.startswith('Planets:'):
                    if current_yoga:
                        planets = line.split(':')[-1].strip()
                        current_yoga['planets'] = [p.strip() for p in planets.split(',') if p.strip()]
                        
            except Exception as e:
                self.logger.error(f"Error parsing yoga line: {line} - {str(e)}")
                continue
                
        # Add the last yoga
        if current_yoga.get('name'):
            self.parsed_data['yogas'].append(current_yoga)

    def _consolidate_data(self):
        output = ["=== Consolidated KP Astrology Analysis ==="]
        
        # Dasha Periods
        output.append("\n1. DASA PERIODS")
        if 'current' in self.parsed_data['dasha']['mahadasha']:
            current = self.parsed_data['dasha']['mahadasha']['current']
            output.append(f"   - Current Mahadasha: {current.get('mahadasha', 'N/A')}")
            output.append(f"   - Start Date: {current.get('start date', 'N/A')}")

        # Planetary Positions
        output.append("\n2. PLANETARY POSITIONS")
        output.append("| Planet | House | Nakshatra | Lord | Retrograde | Combust |")
        for planet, data in self.parsed_data['planets'].items():
            output.append(
                f"| {planet.ljust(6)} | {data.get('house', '').ljust(5)} | "
                f"{data.get('nakshatra', '').ljust(15)} | {data.get('lord', '').ljust(10)} | "
                f"{data.get('retrograde', '').ljust(9)} | {data.get('combust', '').ljust(7)} |"
            )

        # Yogas
        output.append("\n3. SIGNIFICANT YOGAS")
        for yoga in self.parsed_data['yogas']:
            strength = 0
            try:
                strength = float(yoga.get('strength', '0%').replace('%', ''))
            except ValueError:
                pass
                
            if strength > 80:
                output.append(
                    f"   - {yoga['name']}: {', '.join(yoga['planets'])} "
                    f"(Strength: {yoga.get('strength', 'Unknown')})"
                )

        # Houses
        output.append("\n4. HOUSE ANALYSIS")
        for house, planets in self.parsed_data['houses'].items():
            if planets:
                output.append(f"   - House {house}: {', '.join(planets)}")

        return '\n'.join(output)

def analyze_kp_charts(
    mahadasha_file: str,
    antardasha_file: str,
    paryantardasha_file: str,
    planet_position_file: str,
    planet_analysis_file: str,
    house_analysis_file: str,
    yoga_details_file: str,
    output_file: str = "consolidated_kp_analysis.txt"
):
    """Process KP astrology files and generate consolidated analysis"""
    def read_file(path):
        try:
            with open(path, 'r') as f:
                content = f.read()
                if not content.strip():
                    raise ValueError(f"Empty file: {path}")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Critical file missing: {path}")
        except Exception as e:
            raise RuntimeError(f"Error reading {path}: {str(e)}")

    try:
        logger.info("Starting KP analysis")
        
        files_content = {
            'mahadasha': read_file(mahadasha_file),
            'antardasha': read_file(antardasha_file),
            'paryantardasha': read_file(paryantardasha_file),
            'planet_position': read_file(planet_position_file),
            'planet_analysis': read_file(planet_analysis_file),
            'house_analysis': read_file(house_analysis_file),
            'yoga_details': read_file(yoga_details_file)
        }

        cleaner = KPAstrologyCleaner()
        consolidated = cleaner.clean_data(files_content)
        
        with open(output_file, 'w') as f:
            f.write(consolidated)
            
        logger.info(f"Analysis saved to {output_file}")
        return {
            'status': 'success',
            'output_file': output_file,
            'generated_files': [
                mahadasha_file, antardasha_file, paryantardasha_file,
                planet_position_file, planet_analysis_file,
                house_analysis_file, yoga_details_file
            ]
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }