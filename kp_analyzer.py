import re
from datetime import datetime

class KPAstrologyCleaner:
    def __init__(self):
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
        for file_type, content in files_content.items():
            if file_type == 'mahadasha':
                self._parse_mahadasha(content)
            elif file_type == 'antardasha':
                self._parse_antardasha(content)
            elif file_type == 'paryantardasha':
                self._parse_paryantardasha(content)
            elif file_type in ['planet_position', 'planet_analysis']:  # Combined handling
                self._parse_planets(content)
            elif file_type == 'house_analysis':
                self._parse_houses(content)
            elif file_type == 'yoga_details':
                self._parse_yogas(content)
                
        return self._consolidate_data()

    def _parse_mahadasha(self, content):
        current_section = None
        for line in content.split('\n'):
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
            if '✦' in line:
                current_mahadasha = re.search(r"✦ (\w+) Mahadasha", line).group(1)
                self.parsed_data['dasha']['antardasha'][current_mahadasha] = []
            elif current_mahadasha and '-' in line:
                entry = line.strip().split(':')
                if len(entry) == 2:
                    period, date = entry
                    self.parsed_data['dasha']['antardasha'][current_mahadasha].append({
                        'period': period.strip(),
                        'date': date.strip()
                    })

    def _parse_paryantardasha(self, content):
        current_mahadasha = None
        current_antardasha = None
        for line in content.split('\n'):
            if '✦' in line:
                parts = line.split('>')
                if len(parts) == 2:
                    current_mahadasha, current_antardasha = [p.strip() for p in parts]
                    key = f"{current_mahadasha}>{current_antardasha}"
                    self.parsed_data['dasha']['paryantardasha'][key] = []
            elif current_mahadasha and '-' in line:
                entry = line.strip().split(':')
                if len(entry) == 2:
                    period, date = entry
                    self.parsed_data['dasha']['paryantardasha'][key].append({
                        'period': period.strip(),
                        'date': date.strip()
                    })

    def _parse_planets(self, content):
        current_planet = None
        for line in content.split('\n'):
            if '✦' in line:
                current_planet = re.search(r"✦ (\w+)", line).group(1)
                self.parsed_data['planets'][current_planet] = {}
            elif current_planet and ':' in line:
                key, val = [p.strip() for p in line.split(':', 1)]
                key = key.replace('(', '').replace(')', '').strip()
                
                # Handle both planet position and analysis formats
                if 'House' in key:
                    self.parsed_data['planets'][current_planet]['house'] = val.split()[0]
                elif 'Nakshatra' in key:
                    self.parsed_data['planets'][current_planet]['nakshatra'] = val.split('(')[0].strip()
                elif 'Lord' in key:
                    self.parsed_data['planets'][current_planet]['lord'] = val.split('-')[-1].strip()
                elif 'Retrograde' in key:
                    self.parsed_data['planets'][current_planet]['retrograde'] = val.strip()
                elif 'Combust' in key:
                    self.parsed_data['planets'][current_planet]['combust'] = val.strip()
                elif 'Sublord Chain' in key:
                    self.parsed_data['planets'][current_planet]['sublord'] = val.strip()

    def _parse_houses(self, content):
        current_house = None
        for line in content.split('\n'):
            if 'Bhava ' in line:
                current_house = re.search(r"Bhava (\d+)", line).group(1)
                self.parsed_data['houses'][current_house] = []
            elif current_house and '✦' in line:
                planet = re.search(r"✦ (\w+)", line).group(1)
                self.parsed_data['houses'][current_house].append(planet)

    def _parse_yogas(self, content):
        current_yoga = {}
        for line in content.split('\n'):
            if '✦' in line:
                if current_yoga:
                    self.parsed_data['yogas'].append(current_yoga)
                current_yoga = {
                    'name': re.search(r"✦ (.*? Yoga)", line).group(1),
                    'planets': [],
                    'strength': None
                }
            elif 'Strength:' in line:
                current_yoga['strength'] = line.split(':')[-1].strip()
            elif 'Planets:' in line:
                current_yoga['planets'] = [p.strip() for p in line.split(':')[-1].split(',')]

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
            if yoga['strength'] and float(yoga['strength'].replace('%', '')) > 80:
                output.append(
                    f"   - {yoga['name']}: {', '.join(yoga['planets'])} "
                    f"(Strength: {yoga['strength']})"
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
    """
    Process KP astrology files and generate consolidated analysis
    """
    def read_file(path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: File {path} not found. Skipping...")
            return ''

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
    
    return consolidated