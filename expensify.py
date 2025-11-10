import os
import json
import requests
from datetime import datetime

# Server URL: https://integrations.expensify.com
# partnerUserID: aa_baoshenyi_gmail_com
# partnerUserSecret: 7ca35f6915fd05738a090612f435aefd9d05190d

# Expensify API
URL = "https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations"

PARTNER_USER_ID = "aa_baoshenyi_gmail_com"
PARTNER_USER_SECRET = "7ca35f6915fd05738a090612f435aefd9d05190d"
EMPLOYEE_EMAIL = "baoshenyi@gmail.com"

def fetch_expenses():
    # FreeMarker template for extracting expense data
    template = """<#if addHeader == true>
        merchant,amount,created,category<#lt>
        </#if>
        <#list reports as report>
            <#list report.transactionList as expense>
                <#if expense.modifiedMerchant?has_content>
                    <#assign merchant = expense.modifiedMerchant>
                <#else>
                    <#assign merchant = expense.merchant>
                </#if>
                <#if expense.convertedAmount?has_content>
                    <#assign amount = expense.convertedAmount/100>
                <#elseif expense.modifiedAmount?has_content>
                    <#assign amount = expense.modifiedAmount/100>
                <#else>
                    <#assign amount = expense.amount/100>
                </#if>
                <#if expense.modifiedCreated?has_content>
                    <#assign created = expense.modifiedCreated>
                <#else>
                    <#assign created = expense.created>
                </#if>
                "${merchant}",${amount},"${created}","${expense.category}"<#lt>
            </#list>
        </#list>"""

    payload = {
        "type": "file",
        "credentials": {
            "partnerUserID": PARTNER_USER_ID,
            "partnerUserSecret": PARTNER_USER_SECRET
        },
        "inputSettings": {
            "type": "combinedReportData",
            "filters": {
                "startDate": "2025-01-01",
                "endDate": "2025-12-31",
                "employeeEmail": EMPLOYEE_EMAIL
            }
        },
        "outputSettings": {
            "fileExtension": "csv"
        },
        "onReceive": {
            "immediateResponse": ["returnRandomFileName"]
        }
    }
    
    # Add template as a separate parameter in the POST data
    post_data = {
        "requestJobDescription": json.dumps(payload),
        "template": template
    }

    try:
        res = requests.post(URL, data=post_data, timeout=30)
        print(res.status_code)
        if res.status_code != 200:
            print(f"API Error {res.status_code}:", res.text)
            return []
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please check your network connection.")
        return []
    except requests.exceptions.ConnectionError:
        print("Error: Unable to connect to Expensify API. Please check your internet connection.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

    # Check if response contains a filename (async processing)
    response_text = res.text.strip()
    print("Raw response:")
    print(response_text)
    
    if response_text.endswith('.csv'):
        # This is a filename - need to download the file
        print(f"Export file generated: {response_text}")
        
        # Create download payload
        download_payload = {
            "type": "download",
            "credentials": {
                "partnerUserID": PARTNER_USER_ID,
                "partnerUserSecret": PARTNER_USER_SECRET
            },
            "fileName": response_text
        }
        
        try:
            download_res = requests.post(URL, data={"requestJobDescription": json.dumps(download_payload)}, timeout=30)
            if download_res.status_code == 200:
                csv_data = download_res.text
                print("Downloaded CSV data:")
                print(csv_data[:500] + "..." if len(csv_data) > 500 else csv_data)
            else:
                print(f"Error downloading file: {download_res.status_code} - {download_res.text}")
                return []
        except Exception as e:
            print(f"Error downloading export file: {e}")
            return []
    else:
        # Direct CSV response
        csv_data = response_text
    
    # Create receiptOutput directory if it doesn't exist
    output_dir = "receiptOutput"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Generate filename with datetime tag
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{output_dir}/expensify_export_{timestamp}.csv"
    
    # Save CSV data to file
    try:
        with open(csv_filename, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        print(f"✅ CSV data saved to: {csv_filename}")
    except Exception as e:
        print(f"⚠️ Error saving CSV file: {e}")
    
    # Extract only 4 fields for each expense from CSV
    extracted = []
    lines = csv_data.strip().split('\n')
    
    # Skip header if present
    if lines and lines[0].startswith('merchant,amount,created,category'):
        lines = lines[1:]
    
    for line in lines:
        if line.strip():  # Skip empty lines
            try:
                # Simple CSV parsing (assumes no commas in quoted fields)
                parts = []
                in_quotes = False
                current_part = ""
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        parts.append(current_part.strip())
                        current_part = ""
                    else:
                        current_part += char
                
                parts.append(current_part.strip())  # Add the last part
                
                if len(parts) >= 4:
                    item = {
                        "merchant": parts[0].strip('"'),
                        "amount": float(parts[1]) if parts[1] else 0.0,
                        "date": parts[2].strip('"'),
                        "category": parts[3].strip('"')
                    }
                    extracted.append(item)
            except (ValueError, IndexError) as e:
                print(f"Error parsing line: {line} - {e}")
                continue

    return extracted

if __name__ == "__main__":
    expenses = fetch_expenses()
    for e in expenses:
        print(f"{e['date']} | {e['merchant']} | ${e['amount']} | {e['category']}")
