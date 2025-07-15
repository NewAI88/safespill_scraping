import openai
import json
import time
from typing import List, Dict, Any
import math

class HangarArticleAnalyzer:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = 250  # Safe batch size for 50-token articles
        
    def create_batch_prompt(self, articles: List[Dict[str, str]]) -> str:
        """Create optimized batch prompt for multiple articles"""
        
        system_prompt = """Analyze aircraft hangar articles and return structured JSON.

DETAILED FIELD EXPLANATIONS:

1. **is_hangar_related** (boolean):
   - True ONLY if article is directly related to:
     * Aircraft hangar construction (new builds)
     * Aircraft hangar renovation/expansion/demolition
     * Aircraft maintenance facilities (MRO - Maintenance, Repair, Overhaul)
     * Hangar equipment, doors, systems, infrastructure
     * Hangar operations, leasing, management,
     * Airport infrastructure projects that INCLUDE hangar facilities
     * Maintenance base construction or expansion
   - False for:
     * General aviation news
     * Aircraft purchases/sales
     * Flight operations and schedules
     * Airport terminals, runways ONLY (without hangar components)
     * Airline business news
     * Aircraft repairs happening IN a hangar (focus on repair, not hangar facility)
     * Emergency aircraft situations that happen to mention hangar location

2. **region** (string):
   - Must be exactly ONE of these: "UK_NA", "EMEA", "APAC", "LATAM"
   - UK_NA: United Kingdom, United States, Canada
   - EMEA: Europe (except UK), Middle East, Africa
   - APAC: Asia-Pacific (including Australia, New Zealand)
   - LATAM: Latin America (Mexico, Central America, South America)

3. **country** (string):
   - 2-letter ISO country code (US, CA, UK, FR, DE, AU, JP, etc.)
   - Use "N/A" if country cannot be determined from title/summary

4. **completion_status** (boolean):
   - True: Project is already completed/finished/opened
   - False: Project is planned, under construction, or in progress
   - Look for keywords: "opens", "completed", "inaugurated" vs "planned", "will build", "under construction"

For each article, return:
{
    "article_id": number,
    "is_hangar_related": boolean,
    "region": string,
    "country": string,
    "completion_status": boolean
}

Articles to analyze:
"""
        
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"\n{i}. Title: {article['title']}\nSummary: {article['summary']}\n"
        
        response_format = f"""
Return JSON array:
{{
    "results": [
        // {len(articles)} objects with article_id 1-{len(articles)}
        // Each object must have: article_id, is_hangar_related, region, country, completion_status
    ]
}}"""
        
        return system_prompt + articles_text + response_format
    
    def validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean result fields"""
        
        # Validate region
        valid_regions = ["UK_NA", "EMEA", "APAC", "LATAM"]
        if result.get('region') not in valid_regions:
            result['region'] = "N/A"  # Default if invalid
        
        # Validate country (2-letter code or N/A)
        country = result.get('country', 'N/A')
        if country and len(country) != 2 and country != 'N/A':
            result['country'] = 'N/A'
        
        # Ensure boolean fields
        result['is_hangar_related'] = bool(result.get('is_hangar_related', False))
        result['completion_status'] = bool(result.get('completion_status', False))
        
        return result

    def analyze_batch(self, articles: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Analyze a batch of articles"""
        
        try:
            prompt = self.create_batch_prompt(articles)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
                # max_tokens=len(articles) * 200  # Increased for detailed responses
            )
            
            result = json.loads(response.choices[0].message.content)
            raw_results = result.get("results", [])
            
            # Validate each result
            validated_results = []
            for raw_result in raw_results:
                validated_result = self.validate_result(raw_result)
                validated_results.append(validated_result)
            
            return validated_results
            
        except Exception as e:
            print(f"Error in batch analysis: {e}")
            return []
    
    def process_all_articles(self, articles: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process all articles in batches"""
        
        all_results = []
        total_batches = math.ceil(len(articles) / self.batch_size)
        
        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} articles)")
            
            batch_results = self.analyze_batch(batch)
            
            if batch_results:
                # Add original article data to results
                for j, result in enumerate(batch_results):
                    if j < len(batch):
                        result['original_title'] = batch[j]['title']
                        result['original_summary'] = batch[j]['summary']
                
                all_results.extend(batch_results)
            
            # Rate limiting - be respectful to API
            time.sleep(1)
        
        return all_results
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed summary report"""
        
        total_articles = len(results)
        hangar_related = [r for r in results if r.get('is_hangar_related', False)]
        completed_projects = [r for r in hangar_related if r.get('completion_status', False)]
        
        # Region breakdown
        region_counts = {}
        for result in hangar_related:
            region = result.get('region', 'N/A')
            region_counts[region] = region_counts.get(region, 0) + 1
        
        # Country breakdown
        country_counts = {}
        for result in hangar_related:
            country = result.get('country', 'N/A')
            country_counts[country] = country_counts.get(country, 0) + 1
                
        return {
            'summary': {
                'total_articles': total_articles,
                'hangar_related': len(hangar_related),
                'not_hangar_related': total_articles - len(hangar_related),
                'completed_projects': len(completed_projects),
                'in_progress_projects': len(hangar_related) - len(completed_projects)
            },
            'region_breakdown': region_counts,
            'country_breakdown': country_counts,
            'sample_results': results[:5]  # First 5 results as examples
        }

# Usage example
def main():
    # Sample articles (replace with your data)
    articles = [
        # 1
        {
            'title': 'Lincoln Airport gets welcome surprises with runway project, added flights',
            'summary': 'The airport received bids, several under initial estimates, for one of the largest projects in its history. More good news: United is prepared to add more flights out of Lincoln.'
        },
        # 2
        {
            'title': 'Flydubai Breaks Ground On MRO Facility At Dubai South',
            'summary': 'Flydubai said construction is due to be completed in the last quarter of 2026. The maintenance center at DWC coincides with ...'
        },
        # 3
        {
            'title': 'Bombardier Inaugurates Expanded London Biggin Hill Service Centre, the Largest Business Jet Maintenance Repair and Overhaul (MRO) Facility in the UK',
            'summary': ''
        },
        # 4
        {
            'title': "UK’s stranded F-35B fighter jet moved to Air India hangar in Kerala as British team arrives for repairs",
            'summary': ''
        },
        # 5
        {
            'title': 'Furore over allocation of land for aircraft hangar',
            'summary': ''
        },
        # 6
        {
            'title': 'Luxaviation Unveils New Belgium Hangar',
            'summary': ''
        },
        # 7
        {
            'title': 'Ledcor hosts CAWIC on Hamilton hangar project tour',
            'summary': ''
        },
        # 8
        {
            'title': 'Rs 50-crore project aims to turn Kochi into premier aircraft maintenance hub',
            'summary': ''
        },
        # 9
        {
            'title': 'Sanad expands MRO services for CFM LEAP engines',
            'summary': 'The move, in partnership with GE Aerospace and Safran Aircraft Engines, enables full CFM LEAP engine overhaul and test ...'
        }
        # ... add your articles
    ]
    
    import os
    import dotenv
    dotenv.load_dotenv()

    analyzer = HangarArticleAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Process all articles
    results = analyzer.process_all_articles(articles)
    
    # Generate detailed report
    report = analyzer.generate_summary_report(results)
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()