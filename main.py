# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# main.py - POBOLJŠANI MVP
import pandas as pd
from datetime import datetime, timedelta
import sys

print("=" * 70)
print("💰 DYNAMIC PRICING & INVENTORY MANAGEMENT SYSTEM")
print("=" * 70)

class Product:
    def __init__(self, id, name, cost, current_price, days_old, quantity, category="General"):
        self.id = id
        self.name = name
        self.cost = cost
        self.current_price = current_price
        self.days_old = days_old
        self.quantity = quantity
        self.category = category
    
    def get_inventory_status(self):
        """Determine inventory status based on age"""
        if self.days_old > 180:
            return "DEAD_STOCK"
        elif self.days_old > 90:
            return "SLOW_MOVING"
        elif self.days_old > 30:
            return "NORMAL"
        else:
            return "FRESH"
    
    def calculate_financing_cost(self, dso=83, supplier_terms=60):
        """Calculate financing cost based on cash gap"""
        cash_gap = max(dso - supplier_terms, 0)  # Days we need to finance
        annual_interest = 0.08  # 8%
        daily_interest = annual_interest / 365
        return self.current_price * daily_interest * cash_gap
    
    def calculate_storage_cost(self):
        """Calculate storage cost (0.5% monthly)"""
        monthly_rate = 0.005
        months_stored = self.days_old / 30
        return self.cost * monthly_rate * months_stored
    
    def get_price_recommendation(self, dso=83):
        """Get pricing recommendation with all costs included"""
        status = self.get_inventory_status()
        
        # Base price multipliers by status
        multipliers = {
            "FRESH": 1.5,        # 50% margin
            "NORMAL": 1.3,       # 30% margin
            "SLOW_MOVING": 1.1,  # 10% margin
            "DEAD_STOCK": 0.95   # 5% loss - sell quickly!
        }
        
        # Calculate base recommended price
        base_price = self.cost * multipliers[status]
        
        # Adjust for costs
        financing_cost = self.calculate_financing_cost(dso)
        storage_cost = self.calculate_storage_cost()
        
        # Final recommended price
        recommended_price = base_price - financing_cost - storage_cost
        
        # Make sure we don't go below certain thresholds
        if status == "DEAD_STOCK":
            recommended_price = min(recommended_price, self.cost * 0.95)  # Max 5% loss
        elif recommended_price < self.cost * 1.05:  # At least 5% margin
            recommended_price = self.cost * 1.05
        
        # Determine action and message
        if status == "DEAD_STOCK":
            action = "SELL_IMMEDIATELY"
            urgency = "🔴 CRITICAL"
            message = f"PRODAJ ODMAH! Roba stara {self.days_old} dana"
        elif status == "SLOW_MOVING":
            action = "OFFER_DISCOUNT"
            urgency = "🟠 HIGH"
            discount_pct = ((self.current_price - recommended_price) / self.current_price * 100)
            message = f"Ponudi {discount_pct:.0f}% popusta ({recommended_price:.2f} KM)"
        elif status == "NORMAL":
            action = "HOLD_OR_SMALL_DISCOUNT"
            urgency = "🟡 MEDIUM"
            message = f"Možeš držati cijenu ili ponuditi mali popust"
        else:  # FRESH
            action = "HOLD_PRICE"
            urgency = "🟢 LOW"
            message = f"Drži cijenu - roba se brzo kreće"
        
        # Calculate profitability metrics
        gross_margin = recommended_price - self.cost
        margin_pct = (gross_margin / self.cost) * 100
        total_value = self.quantity * recommended_price
        total_cost = self.quantity * self.cost
        total_profit = total_value - total_cost
        
        return {
            "ID": self.id,
            "Product": self.name,
            "Status": status,
            "Urgency": urgency,
            "Current_Price": self.current_price,
            "Recommended_Price": round(recommended_price, 2),
            "Action": action,
            "Message": message,
            "Days_Old": self.days_old,
            "Quantity": self.quantity,
            "Unit_Profit": round(gross_margin, 2),
            "Margin_%": round(margin_pct, 1),
            "Total_Value": round(total_value, 2),
            "Total_Profit": round(total_profit, 2)
        }

def load_products_from_csv(filename="products.csv"):
    """Load products from CSV file"""
    try:
        df = pd.read_csv(filename)
        products = []
        
        for _, row in df.iterrows():
            product = Product(
                id=row['id'],
                name=row['name'],
                cost=float(row['cost']),
                current_price=float(row['price']),
                days_old=int(row['days']),
                quantity=int(row['quantity'])
            )
            products.append(product)
        
        return products
    except Exception as e:
        print(f"⚠️  Error loading CSV: {e}")
        print("Using sample data instead...")
        return get_sample_products()

def get_sample_products():
    """Get sample products if CSV doesn't exist"""
    return [
        Product(1, "Cement 25kg", 10.50, 15.75, 45, 100, "Construction"),
        Product(2, "Šperploča 18mm", 8.20, 13.50, 120, 50, "Construction"),
        Product(3, "Gvozdeni šip 6mm", 15.00, 22.50, 210, 20, "Metal"),
        Product(4, "Boja bijela 10L", 18.00, 27.00, 15, 30, "Paint"),
        Product(5, "PVC cijev 50mm", 3.50, 6.00, 250, 150, "Plumbing"),
    ]

def display_analysis(products, dso=83):
    """Display analysis results"""
    print(f"\n📊 INVENTORY ANALYSIS (DSO: {dso} days, Supplier terms: 60 days)")
    print("-" * 100)
    
    recommendations = []
    total_profit = 0
    dead_stock_count = 0
    
    for product in products:
        rec = product.get_price_recommendation(dso)
        recommendations.append(rec)
        total_profit += rec["Total_Profit"]
        
        if rec["Status"] == "DEAD_STOCK":
            dead_stock_count += 1
    
    # Convert to DataFrame for nice display
    df = pd.DataFrame(recommendations)
    
    # Display in a nice format
    print("\n" + "=" * 100)
    print("🎯 PRICING RECOMMENDATIONS:")
    print("=" * 100)
    
    for rec in recommendations:
        print(f"\n{rec['Urgency']} {rec['Product']}")
        print(f"   📅 Status: {rec['Status']} ({rec['Days_Old']} days old)")
        print(f"   💰 Current: {rec['Current_Price']} KM → Recommended: {rec['Recommended_Price']} KM")
        print(f"   📈 Profit/unit: {rec['Unit_Profit']} KM ({rec['Margin_%']}%)")
        print(f"   📦 Quantity: {rec['Quantity']} → Total value: {rec['Total_Value']} KM")
        print(f"   📢 Action: {rec['Action']}")
        print(f"   💬 {rec['Message']}")
    
    # Summary statistics
    print("\n" + "=" * 100)
    print("📈 SUMMARY STATISTICS:")
    print("=" * 100)
    
    print(f"\n📊 Inventory Status:")
    status_counts = df['Status'].value_counts()
    for status, count in status_counts.items():
        print(f"   {status}: {count} products")
    
    print(f"\n💰 Financial Summary:")
    print(f"   Total Products: {len(df)}")
    print(f"   Total Inventory Value: {df['Total_Value'].sum():.2f} KM")
    print(f"   Total Potential Profit: {total_profit:.2f} KM")
    print(f"   Average Margin: {df['Margin_%'].mean():.1f}%")
    
    if dead_stock_count > 0:
        print(f"\n🚨 URGENT ATTENTION NEEDED:")
        print(f"   {dead_stock_count} products are DEAD STOCK (>180 days)")
        print(f"   These should be sold immediately, even at a loss!")
    
    # Export to CSV
    output_file = "pricing_recommendations.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 Recommendations exported to: {output_file}")
    
    return df

def main():
    """Main function"""
    print("\n🔄 Loading products...")
    
    # Ask for DSO input
    try:
        dso = float(input("Enter average DSO (Days Sales Outstanding) [default: 83]: ") or "83")
    except:
        dso = 83
        print("Using default DSO: 83 days")
    
    # Load products
    products = load_products_from_csv()
    
    print(f"📦 Loaded {len(products)} products for analysis")
    print(f"📊 DSO: {dso} days | Supplier payment terms: 60 days")
    print(f"💡 Interest rate: 8% annual | Storage cost: 0.5% monthly")
    
    # Perform analysis
    recommendations_df = display_analysis(products, dso)
    
    # Additional insights
    print("\n" + "=" * 100)
    print("💡 BUSINESS INSIGHTS:")
    print("=" * 100)
    
    # Find most urgent items
    urgent_items = recommendations_df[recommendations_df['Status'] == 'DEAD_STOCK']
    if len(urgent_items) > 0:
        print(f"\n🚨 TOP PRIORITY - Sell these immediately:")
        for _, item in urgent_items.iterrows():
            print(f"   • {item['Product']}: {item['Recommended_Price']} KM ({item['Days_Old']} days old)")
    
    # Find best performing items
    fresh_items = recommendations_df[recommendations_df['Status'] == 'FRESH']
    if len(fresh_items) > 0:
        print(f"\n✅ BEST PERFORMERS - Hold these prices:")
        for _, item in fresh_items.head(3).iterrows():
            print(f"   • {item['Product']}: {item['Margin_%']}% margin")
    
    print("\n" + "=" * 100)
    print("🎉 ANALYSIS COMPLETE!")
    print("=" * 100)
    
    print("\nNext steps:")
    print("1. Review pricing_recommendations.csv")
    print("2. For web dashboard: streamlit run app.py")
    print("3. Share recommendations with sales team")
    
    # Pause before exit
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()