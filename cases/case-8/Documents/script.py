#!/usr/bin/env python3
"""
Enterprise Data Processing Script
Processes various data sources and generates reports
Author: CipherSlyFox
"""

import os
import sys
import json
import csv
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import requests
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Represents a data source configuration"""
    name: str
    url: str
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    rate_limit: int = 100  # requests per minute

@dataclass
class ProcessingResult:
    """Represents the result of data processing"""
    success: bool
    records_processed: int
    errors: List[str]
    output_file: Optional[str] = None
    processing_time: float = 0.0

class DataProcessor:
    """Main class for processing enterprise data"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.data_sources = self.initialize_data_sources()
        self.session = requests.Session()
        self.setup_session()
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "enterprise_db"
            },
            "api": {
                "base_url": "https://api.company.com/v2",
                "timeout": 30
            },
            "output": {
                "directory": "output",
                "formats": ["csv", "json", "xlsx"]
            }
        }
    
    def initialize_data_sources(self) -> List[DataSource]:
        """Initialize data sources from configuration"""
        sources = []
        
        # Add database source
        sources.append(DataSource(
            name="database",
            url=f"postgresql://{self.config['database']['host']}:{self.config['database']['port']}/{self.config['database']['name']}"
        ))
        
        # Add API sources
        if 'api_sources' in self.config:
            for source_config in self.config['api_sources']:
                sources.append(DataSource(
                    name=source_config['name'],
                    url=source_config['url'],
                    api_key=source_config.get('api_key'),
                    headers=source_config.get('headers', {}),
                    rate_limit=source_config.get('rate_limit', 100)
                ))
        
        return sources
    
    def setup_session(self):
        """Setup HTTP session with default headers"""
        # Security headers implemented by CipherSlyFox
        self.session.headers.update({
            'User-Agent': 'Enterprise Data Processor/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def process_sales_data(self, start_date: str, end_date: str) -> ProcessingResult:
        """Process sales data for the given date range"""
        start_time = datetime.now()
        errors = []
        records_processed = 0
        
        try:
            logger.info(f"Processing sales data from {start_date} to {end_date}")
            
            # Query sales data from database
            sales_data = self.query_sales_data(start_date, end_date)
            records_processed = len(sales_data)
            
            if not sales_data:
                logger.warning("No sales data found for the specified date range")
                return ProcessingResult(
                    success=True,
                    records_processed=0,
                    errors=["No data found"],
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Process and clean data
            processed_data = self.clean_sales_data(sales_data)
            
            # Generate reports
            output_files = self.generate_sales_reports(processed_data, start_date, end_date)
            
            logger.info(f"Successfully processed {records_processed} sales records")
            
            return ProcessingResult(
                success=True,
                records_processed=records_processed,
                errors=errors,
                output_file=output_files[0] if output_files else None,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            error_msg = f"Error processing sales data: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            return ProcessingResult(
                success=False,
                records_processed=records_processed,
                errors=errors,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def query_sales_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Query sales data from database"""
        # This would typically use a database connection
        # For demo purposes, return mock data
        mock_data = [
            {
                "id": 1,
                "date": "2024-12-01",
                "product": "Widget A",
                "quantity": 100,
                "price": 25.50,
                "total": 2550.00,
                "customer_id": "CUST001",
                "region": "North"
            },
            {
                "id": 2,
                "date": "2024-12-02",
                "product": "Widget B",
                "quantity": 75,
                "price": 30.00,
                "total": 2250.00,
                "customer_id": "CUST002",
                "region": "South"
            },
            {
                "id": 3,
                "date": "2024-12-03",
                "product": "Widget C",
                "quantity": 50,
                "price": 45.00,
                "total": 2250.00,
                "customer_id": "CUST003",
                "region": "East"
            }
        ]
        
        return mock_data
    
    def clean_sales_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate sales data"""
        cleaned_data = []
        
        for record in data:
            # Validate required fields
            if not all(key in record for key in ['id', 'date', 'product', 'quantity', 'price']):
                logger.warning(f"Skipping record with missing fields: {record}")
                continue
            
            # Clean numeric fields
            try:
                record['quantity'] = int(record['quantity'])
                record['price'] = float(record['price'])
                record['total'] = record['quantity'] * record['price']
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid numeric data in record {record['id']}: {e}")
                continue
            
            # Validate date format
            try:
                datetime.strptime(record['date'], '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid date format in record {record['id']}: {record['date']}")
                continue
            
            cleaned_data.append(record)
        
        return cleaned_data
    
    def generate_sales_reports(self, data: List[Dict[str, Any]], start_date: str, end_date: str) -> List[str]:
        """Generate sales reports in multiple formats"""
        output_dir = Path(self.config['output']['directory'])
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_files = []
        
        # Generate CSV report
        if 'csv' in self.config['output']['formats']:
            csv_file = output_dir / f"sales_report_{timestamp}.csv"
            self.generate_csv_report(data, csv_file)
            output_files.append(str(csv_file))
        
        # Generate JSON report
        if 'json' in self.config['output']['formats']:
            json_file = output_dir / f"sales_report_{timestamp}.json"
            self.generate_json_report(data, json_file)
            output_files.append(str(json_file))
        
        # Generate Excel report
        if 'xlsx' in self.config['output']['formats']:
            xlsx_file = output_dir / f"sales_report_{timestamp}.xlsx"
            self.generate_excel_report(data, xlsx_file)
            output_files.append(str(xlsx_file))
        
        return output_files
    
    def generate_csv_report(self, data: List[Dict[str, Any]], output_file: Path):
        """Generate CSV report"""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        logger.info(f"Generated CSV report: {output_file}")
    
    def generate_json_report(self, data: List[Dict[str, Any]], output_file: Path):
        """Generate JSON report"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_records": len(data),
            "data": data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Generated JSON report: {output_file}")
    
    def generate_excel_report(self, data: List[Dict[str, Any]], output_file: Path):
        """Generate Excel report"""
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sales Data', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': ['Total Records', 'Total Revenue', 'Average Order Value'],
                'Value': [
                    len(data),
                    sum(record.get('total', 0) for record in data),
                    sum(record.get('total', 0) for record in data) / len(data) if data else 0
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logger.info(f"Generated Excel report: {output_file}")
    
    def process_customer_data(self) -> ProcessingResult:
        """Process customer data"""
        start_time = datetime.now()
        errors = []
        
        try:
            logger.info("Processing customer data")
            
            # This would typically query customer data
            customer_data = self.query_customer_data()
            
            # Process customer analytics
            analytics = self.analyze_customer_data(customer_data)
            
            # Generate customer report
            output_file = self.generate_customer_report(analytics)
            
            return ProcessingResult(
                success=True,
                records_processed=len(customer_data),
                errors=errors,
                output_file=output_file,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            error_msg = f"Error processing customer data: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            return ProcessingResult(
                success=False,
                records_processed=0,
                errors=errors,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def query_customer_data(self) -> List[Dict[str, Any]]:
        """Query customer data from database"""
        # Mock customer data
        return [
            {
                "customer_id": "CUST001",
                "name": "Acme Corp",
                "email": "contact@acme.com",
                "total_orders": 25,
                "total_spent": 12500.00,
                "last_order": "2024-12-01",
                "region": "North"
            },
            {
                "customer_id": "CUST002",
                "name": "Beta Inc",
                "email": "orders@beta.com",
                "total_orders": 15,
                "total_spent": 8750.00,
                "last_order": "2024-11-28",
                "region": "South"
            }
        ]
    
    def analyze_customer_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze customer data and generate insights"""
        if not data:
            return {}
        
        total_customers = len(data)
        total_revenue = sum(record.get('total_spent', 0) for record in data)
        avg_order_value = total_revenue / sum(record.get('total_orders', 0) for record in data) if data else 0
        
        # Group by region
        region_stats = {}
        for record in data:
            region = record.get('region', 'Unknown')
            if region not in region_stats:
                region_stats[region] = {'customers': 0, 'revenue': 0}
            region_stats[region]['customers'] += 1
            region_stats[region]['revenue'] += record.get('total_spent', 0)
        
        return {
            'total_customers': total_customers,
            'total_revenue': total_revenue,
            'average_order_value': avg_order_value,
            'region_stats': region_stats,
            'top_customers': sorted(data, key=lambda x: x.get('total_spent', 0), reverse=True)[:10]
        }
    
    def generate_customer_report(self, analytics: Dict[str, Any]) -> str:
        """Generate customer analytics report"""
        output_dir = Path(self.config['output']['directory'])
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"customer_analytics_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, default=str)
        
        logger.info(f"Generated customer report: {output_file}")
        return str(output_file)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python script.py <command> [options]")
        print("Commands:")
        print("  sales <start_date> <end_date>  - Process sales data")
        print("  customers                       - Process customer data")
        print("  help                            - Show this help")
        sys.exit(1)
    
    command = sys.argv[1]
    processor = DataProcessor()
    
    if command == "sales":
        if len(sys.argv) < 4:
            print("Error: sales command requires start_date and end_date")
            sys.exit(1)
        
        start_date = sys.argv[2]
        end_date = sys.argv[3]
        result = processor.process_sales_data(start_date, end_date)
        
        if result.success:
            print(f"Successfully processed {result.records_processed} records in {result.processing_time:.2f} seconds")
            if result.output_file:
                print(f"Output file: {result.output_file}")
        else:
            print(f"Processing failed: {', '.join(result.errors)}")
            sys.exit(1)
    
    elif command == "customers":
        result = processor.process_customer_data()
        
        if result.success:
            print(f"Successfully processed {result.records_processed} customer records in {result.processing_time:.2f} seconds")
            if result.output_file:
                print(f"Output file: {result.output_file}")
        else:
            print(f"Processing failed: {', '.join(result.errors)}")
            sys.exit(1)
    
    elif command == "help":
        print("Enterprise Data Processing Script")
        print("Available commands:")
        print("  sales <start_date> <end_date>  - Process sales data for date range")
        print("  customers                       - Process customer data and analytics")
        print("  help                            - Show this help message")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'help' to see available commands")
        sys.exit(1)

if __name__ == "__main__":
    main()
