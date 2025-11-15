"""
Visual Scraper Recorder - Backend Integration
Processes recorded actions and generates scraper configurations
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from collections import Counter
import re
from pathlib import Path


@dataclass
class RecordedAction:
    """Represents a single recorded user action"""
    type: str  # 'click', 'extract', 'navigate', 'wait', 'container'
    selector: str
    timestamp: int
    field: Optional[str] = None
    data: Optional[str] = None
    tag_name: Optional[str] = None
    attributes: Optional[Dict] = None


class RecordingAnalyzer:
    """Analyzes recorded actions to generate optimal scraper configuration"""
    
    def __init__(self, actions: List[Dict]):
        self.actions = [RecordedAction(**action) for action in actions]
        self.extracted_fields = {}
        self.container_selector = None
        self.pagination_selector = None
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze recorded actions and generate configuration"""
        
        # 1. Identify container (common parent of extracted elements)
        self.container_selector = self._detect_container()
        
        # 2. Extract field mappings
        self.extracted_fields = self._extract_fields()
        
        # 3. Detect pagination
        self.pagination_selector = self._detect_pagination()
        
        # 4. Optimize selectors for stability
        self.extracted_fields = self._optimize_selectors(self.extracted_fields)
        
        # 5. Generate final configuration
        config = self._generate_config()
        
        return config
    
    def _detect_container(self) -> str:
        """Detect the container selector by finding common parent"""
        extract_actions = [a for a in self.actions if a.type == 'extract']
        
        if not extract_actions:
            return 'body'
        
        # Check if user explicitly set container
        container_actions = [a for a in self.actions if a.type == 'container']
        if container_actions:
            return container_actions[-1].selector  # Use most recent
        
        # Analyze selectors to find common parent
        selectors = [a.selector for a in extract_actions]
        
        # Find common ancestor by analyzing selector patterns
        common_parts = self._find_common_selector_pattern(selectors)
        
        if common_parts:
            return common_parts
        
        # Fallback: use first two levels of first selector
        first_selector = selectors[0]
        parts = first_selector.split(' ')
        if len(parts) >= 2:
            return ' '.join(parts[:2])
        
        return first_selector.split(' ')[0] if ' ' in first_selector else 'body'
    
    def _find_common_selector_pattern(self, selectors: List[str]) -> Optional[str]:
        """Find common pattern in selectors"""
        if not selectors:
            return None
        
        # Split selectors into parts
        selector_parts = [s.split(' ') for s in selectors]
        
        # Find common prefix
        common_prefix = []
        for parts in zip(*selector_parts):
            if len(set(parts)) == 1:  # All same
                common_prefix.append(parts[0])
            else:
                break
        
        if len(common_prefix) >= 1:
            return ' '.join(common_prefix)
        
        # Look for common class patterns
        class_pattern = re.compile(r'\.([\w-]+)')
        common_classes = []
        
        for selector in selectors:
            classes = class_pattern.findall(selector)
            common_classes.extend(classes)
        
        # Find most common class
        if common_classes:
            most_common = Counter(common_classes).most_common(1)[0][0]
            return f'.{most_common}'
        
        return None
    
    def _extract_fields(self) -> Dict[str, str]:
        """Extract field name to selector mappings"""
        fields = {}
        
        for action in self.actions:
            if action.type == 'extract' and action.field:
                # If multiple extractions for same field, use most recent
                fields[action.field] = action.selector
        
        return fields
    
    def _detect_pagination(self) -> Optional[str]:
        """Detect pagination by looking for navigation clicks"""
        click_actions = [a for a in self.actions if a.type == 'click']
        
        # Look for common pagination patterns
        pagination_patterns = [
            'next', 'pagination', 'page', 'more', 
            'load-more', 'show-more', 'forward'
        ]
        
        for action in click_actions:
            selector_lower = action.selector.lower()
            for pattern in pagination_patterns:
                if pattern in selector_lower:
                    return action.selector
        
        return None
    
    def _optimize_selectors(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Optimize selectors for stability and reliability"""
        optimized = {}
        
        for field_name, selector in fields.items():
            # Remove absolute positioning (nth-child with numbers)
            optimized_selector = re.sub(r':nth-child\(\d+\)', '', selector)
            
            # Simplify if possible
            optimized_selector = self._simplify_selector(optimized_selector)
            
            optimized[field_name] = optimized_selector
        
        return optimized
    
    def _simplify_selector(self, selector: str) -> str:
        """Simplify selector while maintaining specificity"""
        parts = selector.split(' ')
        
        # If selector is too long, keep first and last 2 parts
        if len(parts) > 4:
            simplified = parts[:2] + parts[-2:]
            return ' '.join(simplified)
        
        return selector
    
    def _generate_config(self) -> Dict[str, Any]:
        """Generate final scraper configuration"""
        
        # Get target URL from first navigation action
        target_url = None
        for action in self.actions:
            if action.type == 'navigate':
                target_url = action.selector  # URL stored in selector field
                break
        
        config = {
            'name': 'Recorded Scraper',
            'description': f'Auto-generated from recording on {self._format_timestamp()}',
            'target_url': target_url or 'https://example.com',
            'container_selector': self.container_selector,
            'fields': [
                {
                    'name': field_name,
                    'selector': selector,
                    'required': True
                }
                for field_name, selector in self.extracted_fields.items()
            ],
            'pagination': {
                'enabled': self.pagination_selector is not None,
                'next_button_selector': self.pagination_selector or '',
                'max_pages': 10
            },
            'output': {
                'format': 'csv',
                'filename': 'recorded_scraper.csv'
            },
            'notes': f'Generated from {len(self.actions)} recorded actions'
        }
        
        return config
    
    def _format_timestamp(self) -> str:
        """Format current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M')


class RecorderConfigGenerator:
    """Generates configurations from recorded browser sessions"""
    
    def __init__(self, recordings_dir: str = 'data/recordings'):
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
    
    def save_recording(self, recording_id: str, actions: List[Dict]) -> str:
        """Save recorded actions to file"""
        filepath = self.recordings_dir / f"{recording_id}.json"
        
        recording_data = {
            'recording_id': recording_id,
            'actions': actions,
            'timestamp': actions[0]['timestamp'] if actions else None,
            'action_count': len(actions)
        }
        
        with open(filepath, 'w') as f:
            json.dump(recording_data, f, indent=2)
        
        return str(filepath)
    
    def load_recording(self, recording_id: str) -> Dict:
        """Load recorded actions from file"""
        filepath = self.recordings_dir / f"{recording_id}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Recording {recording_id} not found")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def generate_config_from_recording(self, recording_id: str) -> Dict[str, Any]:
        """Generate scraper config from saved recording"""
        recording = self.load_recording(recording_id)
        actions = recording['actions']
        
        analyzer = RecordingAnalyzer(actions)
        config = analyzer.analyze()
        
        return config
    
    def generate_config_from_actions(self, actions: List[Dict]) -> Dict[str, Any]:
        """Generate scraper config directly from actions"""
        analyzer = RecordingAnalyzer(actions)
        config = analyzer.analyze()
        
        return config
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated configuration"""
        errors = []
        warnings = []
        
        # Check required fields
        if not config.get('target_url'):
            errors.append("Target URL is required")
        
        if not config.get('container_selector'):
            errors.append("Container selector is required")
        
        if not config.get('fields') or len(config['fields']) == 0:
            errors.append("At least one field is required")
        
        # Check field selectors
        for field in config.get('fields', []):
            if not field.get('selector'):
                errors.append(f"Field '{field.get('name')}' missing selector")
        
        # Warnings
        if config.get('pagination', {}).get('enabled') and \
           not config['pagination'].get('next_button_selector'):
            warnings.append("Pagination enabled but no next button selector")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'config': config
        }
    
    def preview_data(self, config: Dict[str, Any]) -> List[Dict]:
        """Generate preview data based on configuration"""
        fields = config.get('fields', [])
        field_names = [f['name'] for f in fields]
        
        # Generate sample data
        preview = []
        for i in range(3):
            item = {field: f"Sample {field} {i+1}" for field in field_names}
            preview.append(item)
        
        return preview


if __name__ == '__main__':
    # Example usage
    sample_actions = [
        {
            'type': 'navigate',
            'selector': 'https://quotes.toscrape.com/',
            'timestamp': 1699564800000
        },
        {
            'type': 'container',
            'selector': '.quote',
            'timestamp': 1699564801000
        },
        {
            'type': 'extract',
            'selector': '.text',
            'field': 'quote_text',
            'data': 'The world as we have created it...',
            'timestamp': 1699564802000,
            'tag_name': 'span',
            'attributes': {'class': 'text'}
        },
        {
            'type': 'extract',
            'selector': '.author',
            'field': 'author',
            'data': 'Albert Einstein',
            'timestamp': 1699564803000,
            'tag_name': 'small',
            'attributes': {'class': 'author'}
        }
    ]
    
    generator = RecorderConfigGenerator()
    config = generator.generate_config_from_actions(sample_actions)
    validation = generator.validate_config(config)
    
    print("=" * 60)
    print("GENERATED CONFIGURATION")
    print("=" * 60)
    print(json.dumps(config, indent=2))
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
